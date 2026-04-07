import mlflow
import mlflow.pytorch
import time
import timm
import torch
import torch.nn as nn
import torch.nn.functional as F
from loguru import logger
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from torchvision import transforms
import pandas as pd
from PIL import Image
import numpy as np

from app.entity.config_entity import ImagingModelTrainerConfig, ImagingTransformationConfig
from app.utils.common import read_yaml, set_seed
from app.constants import PARAMS_FILE_PATH, SCHEMA_FILE_PATH
from monitoring.prometheus_metrics import BEST_VAL_ACCURACY, EPOCH_TRAIN_LOSS


class RetinalDataset(Dataset):
    def __init__(self, csv_path: Path, transform=None):
        self.df = pd.read_csv(csv_path)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img = Image.open(row["image_path"]).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, int(row["label"])


class FocalLoss(nn.Module):
    def __init__(self, gamma: float = 2.0, num_classes: int = 5):
        super().__init__()
        self.gamma = gamma
        self.num_classes = num_classes

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce_loss = F.cross_entropy(inputs, targets, reduction="none")
        pt = torch.exp(-ce_loss)
        focal_loss = ((1 - pt) ** self.gamma) * ce_loss
        return focal_loss.mean()


class ImagingModelTrainer:
    def __init__(
        self,
        config: ImagingModelTrainerConfig,
        transformation_config: ImagingTransformationConfig,
    ):
        self.config = config
        self.transformation_config = transformation_config
        self.params = read_yaml(PARAMS_FILE_PATH)
        self.schema = read_yaml(SCHEMA_FILE_PATH)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"training device: {self.device}")

    def _build_transforms(self):
        aug = self.params.augmentation
        norm = aug.normalize
        train_tf = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(aug.random_rotation),
            transforms.ColorJitter(
                brightness=aug.color_jitter.brightness,
                contrast=aug.color_jitter.contrast,
                saturation=aug.color_jitter.saturation,
                hue=aug.color_jitter.hue,
            ),
            transforms.ToTensor(),
            transforms.Normalize(mean=norm.mean, std=norm.std),
        ])
        val_tf = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=norm.mean, std=norm.std),
        ])
        return train_tf, val_tf

    def _build_model(self) -> nn.Module:
        p = self.params.dl_training
        model = timm.create_model(
            self.config.model_name,
            pretrained=self.config.pretrained,
            num_classes=p.num_classes,
            drop_rate=p.dropout,
        )

        blocks = list(model.blocks.children()) if hasattr(model, "blocks") else []
        freeze_until = min(3, len(blocks))
        for i, block in enumerate(blocks):
            if i < freeze_until:
                for param in block.parameters():
                    param.requires_grad = False
        logger.info(f"frozen first {freeze_until} blocks of {self.config.model_name}")

        model.set_grad_checkpointing(enable=True)
        logger.info("gradient checkpointing enabled")

        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total = sum(p.numel() for p in model.parameters())
        logger.info(f"trainable params: {trainable:,} / {total:,}")

        return model.to(self.device)

    def _build_sampler(self, dataset: RetinalDataset) -> WeightedRandomSampler:
        labels = [int(dataset.df.iloc[i]["label"]) for i in range(len(dataset))]
        class_counts = np.bincount(labels, minlength=self.params.dl_training.num_classes)
        class_weights = 1.0 / (class_counts + 1e-6)
        sample_weights = [class_weights[lbl] for lbl in labels]
        return WeightedRandomSampler(
            weights=sample_weights,
            num_samples=len(sample_weights),
            replacement=True,
        )

    def _log_best_model_to_mlflow(self, checkpoint_path: Path, num_classes: int) -> None:
        if not checkpoint_path.exists():
            logger.warning("best checkpoint missing; skipping mlflow model log")
            return

        mlflow_cfg = self.params.get("mlflow", {}) or {}
        logger.info(f"preparing best checkpoint for mlflow: {checkpoint_path}")

        # Rebuild a CPU model from the best checkpoint once to avoid
        # expensive per-epoch deepcopy/logging overhead inside the train loop.
        model = timm.create_model(
            self.config.model_name,
            pretrained=False,
            num_classes=num_classes,
            drop_rate=self.params.dl_training.dropout,
        )
        logger.info("loading checkpoint state_dict on cpu")
        state_dict = torch.load(checkpoint_path, map_location="cpu")
        model.load_state_dict(state_dict)
        model.eval()

        input_example = np.zeros((1, 3, 224, 224), dtype=np.float32)
        timeout_seconds = int(mlflow_cfg.get("model_log_timeout_seconds", 300))
        timeout_seconds = max(1, timeout_seconds)

        logger.info(f"starting mlflow model upload (timeout={timeout_seconds}s)")
        start_time = time.perf_counter()

        def _upload_model() -> None:
            try:
                mlflow.pytorch.log_model(
                    model,
                    name="imaging_model",
                    export_model=True,
                    input_example=input_example,
                )
                logger.info("mlflow model logged with export_model=True")
            except Exception as exc:
                logger.warning(
                    f"mlflow export_model=True failed ({type(exc).__name__}); "
                    "falling back to export_model=False"
                )
                mlflow.pytorch.log_model(
                    model,
                    name="imaging_model",
                    export_model=False,
                    input_example=input_example,
                )
                logger.info("mlflow model logged with export_model=False fallback")

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_upload_model)
                future.result(timeout=timeout_seconds)
            elapsed = time.perf_counter() - start_time
            logger.info(f"best imaging model logged to mlflow in {elapsed:.1f}s")
        except FuturesTimeoutError:
            elapsed = time.perf_counter() - start_time
            logger.warning(
                f"mlflow model upload timed out after {elapsed:.1f}s; skipping artifact log"
            )

    def train(self) -> Path:
        set_seed(self.params.dl_training.seed)
        p = self.params.dl_training
        train_tf, val_tf = self._build_transforms()

        train_dataset = RetinalDataset(self.transformation_config.train_csv, train_tf)
        val_dataset = RetinalDataset(self.transformation_config.test_csv, val_tf)

        sampler = self._build_sampler(train_dataset)

        train_loader = DataLoader(
            train_dataset,
            batch_size=p.batch_size,
            sampler=sampler,
            num_workers=p.num_workers,
            pin_memory=True,
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=p.batch_size,
            shuffle=False,
            num_workers=p.num_workers,
            pin_memory=True,
        )

        model = self._build_model()
        optimizer = torch.optim.AdamW(
            filter(lambda p: p.requires_grad, model.parameters()),
            lr=p.learning_rate,
            weight_decay=p.weight_decay,
        )
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=p.epochs
        )
        criterion = FocalLoss(gamma=2.0, num_classes=p.num_classes)

        best_val_acc = 0.0
        patience_counter = 0
        checkpoint_path = self.config.checkpoint_path
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        with mlflow.start_run(run_name=self.params.get("mlflow", {}).get("imaging_run_name", "efficientnet_b3")):
            mlflow.log_params({
                "model": self.config.model_name,
                "pretrained": self.config.pretrained,
                "epochs": p.epochs,
                "batch_size": p.batch_size,
                "lr": p.learning_rate,
                "weight_decay": p.weight_decay,
                "scheduler": p.scheduler,
                "num_classes": p.num_classes,
                "dropout": p.dropout,
                "seed": p.seed,
                "loss": "focal_loss",
                "focal_gamma": 2.0,
                "freeze_blocks": 3,
                "device": str(self.device),
            })

            for epoch in range(p.epochs):
                model.train()
                train_loss, train_correct, train_total = 0.0, 0, 0

                for images, labels in train_loader:
                    images, labels = images.to(self.device), labels.to(self.device)
                    optimizer.zero_grad()
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                    optimizer.step()

                    train_loss += loss.item() * images.size(0)
                    train_correct += (outputs.argmax(1) == labels).sum().item()
                    train_total += images.size(0)

                scheduler.step()

                model.eval()
                val_correct, val_total = 0, 0
                with torch.no_grad():
                    for images, labels in val_loader:
                        images, labels = images.to(self.device), labels.to(self.device)
                        outputs = model(images)
                        val_correct += (outputs.argmax(1) == labels).sum().item()
                        val_total += images.size(0)

                train_acc = train_correct / train_total
                val_acc = val_correct / val_total
                avg_loss = train_loss / train_total
                EPOCH_TRAIN_LOSS.labels(pipeline="imaging").observe(avg_loss)
                lr = scheduler.get_last_lr()[0]

                mlflow.log_metrics({
                    "train_loss": avg_loss,
                    "train_acc": train_acc,
                    "val_acc": val_acc,
                    "lr": lr,
                }, step=epoch)

                logger.info(
                    f"epoch={epoch + 1}/{p.epochs} "
                    f"loss={avg_loss:.4f} "
                    f"train_acc={train_acc:.4f} "
                    f"val_acc={val_acc:.4f} "
                    f"lr={lr:.6f}"
                )

                if val_acc > best_val_acc:
                    best_val_acc = val_acc
                    patience_counter = 0
                    torch.save(model.state_dict(), checkpoint_path)
                    BEST_VAL_ACCURACY.labels(pipeline="imaging").set(best_val_acc)
                    logger.info(f"checkpoint saved: val_acc={val_acc:.4f}")
                else:
                    patience_counter += 1
                    if patience_counter >= p.early_stopping_patience:
                        logger.info(f"early stopping at epoch {epoch + 1}")
                        break

            mlflow.log_metric("best_val_acc", best_val_acc)
            self._log_best_model_to_mlflow(checkpoint_path, p.num_classes)

        logger.info(f"training complete. best_val_acc={best_val_acc:.4f}")
        logger.info(f"model saved: {checkpoint_path}")
        return checkpoint_path
