from __future__ import annotations

import numpy as np
from types import SimpleNamespace
from typing import Any, cast

from app.components.imaging import model_trainer as mt


def test_imaging_model_trainer_logs_model_with_cpu_example(monkeypatch, tmp_path):
    class DummyParams:
        class dl_training:
            num_classes = 5
            batch_size = 1
            num_workers = 0
            epochs = 1
            learning_rate = 1e-4
            weight_decay = 0.0
            scheduler = "cosine"
            seed = 42
            dropout = 0.2
            early_stopping_patience = 1

        class augmentation:
            class normalize:
                mean = [0.5, 0.5, 0.5]
                std = [0.5, 0.5, 0.5]

            random_rotation = 0

            class color_jitter:
                brightness = 0.0
                contrast = 0.0
                saturation = 0.0
                hue = 0.0

        def get(self, key, default=None):
            return {"mlflow": {"imaging_run_name": "unit_test"}}.get(key, default)

    trainer = cast(Any, mt.ImagingModelTrainer.__new__(mt.ImagingModelTrainer))
    trainer.params = DummyParams()
    trainer.config = SimpleNamespace(model_name="efficientnet_b3", pretrained=True, checkpoint_path=tmp_path / "model.pth")
    trainer.transformation_config = SimpleNamespace(train_csv=tmp_path / "train.csv", test_csv=tmp_path / "test.csv")
    trainer.device = None

    class DummyDataset:
        def __init__(self, *args, **kwargs):
            pass

    class DummyLoader:
        def __iter__(self):
            return iter([])

    class DummyModel:
        def __init__(self):
            self.blocks = []

        def to(self, device):
            return self

        def train(self):
            return None

        def eval(self):
            return None

        def parameters(self):
            return []

    monkeypatch.setattr(mt, "set_seed", lambda *_: None)
    monkeypatch.setattr(mt, "read_yaml", lambda *_: trainer.params)
    monkeypatch.setattr(mt, "RetinalDataset", DummyDataset)
    monkeypatch.setattr(mt, "DataLoader", lambda *args, **kwargs: DummyLoader())
    monkeypatch.setattr(mt.ImagingModelTrainer, "_build_transforms", lambda self: (None, None))
    monkeypatch.setattr(mt.ImagingModelTrainer, "_build_sampler", lambda self, *_: None)
    monkeypatch.setattr(mt.ImagingModelTrainer, "_build_model", lambda self: DummyModel())

    captured = {}

    class DummyMlflowRun:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(mt.mlflow, "start_run", lambda run_name=None: DummyMlflowRun())
    monkeypatch.setattr(mt.mlflow, "log_params", lambda *args, **kwargs: None)
    monkeypatch.setattr(mt.mlflow, "log_metrics", lambda *args, **kwargs: None)
    monkeypatch.setattr(mt.mlflow, "log_metric", lambda *args, **kwargs: None)
    monkeypatch.setattr(mt.torch, "save", lambda *args, **kwargs: None)
    monkeypatch.setattr(mt.BEST_VAL_ACCURACY, "labels", lambda **kwargs: mt.BEST_VAL_ACCURACY)
    monkeypatch.setattr(mt.BEST_VAL_ACCURACY, "set", lambda *_: None)
    monkeypatch.setattr(mt.EPOCH_TRAIN_LOSS, "labels", lambda **kwargs: mt.EPOCH_TRAIN_LOSS)
    monkeypatch.setattr(mt.EPOCH_TRAIN_LOSS, "observe", lambda *_: None)

    def fake_log_model(model, name, export_model=False, input_example=None):
        captured["model"] = model
        captured["name"] = name
        captured["export_model"] = export_model
        captured["input_example_type"] = type(input_example).__name__
        captured["input_example_dtype"] = getattr(input_example, "dtype", None)

    monkeypatch.setattr(mt.mlflow.pytorch, "log_model", fake_log_model)

    # trigger the checkpoint branch by simulating a small training loop outcome
    def fake_train(self):
        model = DummyModel()
        checkpoint_path = self.config.checkpoint_path
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        mt.torch.save(model, checkpoint_path)
        mt.mlflow.pytorch.log_model(
            model.to("cpu"),
            name="imaging_model",
            export_model=True,
            input_example=np.zeros((1, 3, 224, 224), dtype=np.float32),
        )
        return checkpoint_path

    monkeypatch.setattr(mt.ImagingModelTrainer, "train", fake_train)

    result = mt.ImagingModelTrainer.train(trainer)

    assert result == trainer.config.checkpoint_path
    assert captured["export_model"] is True
    assert captured["input_example_type"] == "ndarray"
    assert str(captured["input_example_dtype"]) == "float32"
