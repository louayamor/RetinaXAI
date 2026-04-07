from __future__ import annotations

from app.components.imaging import model_trainer as mt


def test_imaging_model_trainer_logs_model_without_export(monkeypatch, tmp_path):
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

    trainer = mt.ImagingModelTrainer.__new__(mt.ImagingModelTrainer)
    trainer.params = DummyParams()
    trainer.config = type("Cfg", (), {"model_name": "efficientnet_b3", "pretrained": True, "checkpoint_path": tmp_path / "model.pth"})()
    trainer.transformation_config = type("T", (), {"train_csv": tmp_path / "train.csv", "test_csv": tmp_path / "test.csv"})()
    trainer.device = None

    monkeypatch.setattr(mt, "set_seed", lambda *_: None)
    monkeypatch.setattr(mt, "read_yaml", lambda *_: trainer.params)
    monkeypatch.setattr(mt, "RetinalDataset", lambda *args, **kwargs: None)
    monkeypatch.setattr(mt, "DataLoader", lambda *args, **kwargs: [])
    monkeypatch.setattr(mt.ImagingModelTrainer, "_build_transforms", lambda self: (None, None))
    monkeypatch.setattr(mt.ImagingModelTrainer, "_build_sampler", lambda self, *_: None)
    monkeypatch.setattr(mt.ImagingModelTrainer, "_build_model", lambda self: object())

    logged = {}

    class DummyMlflow:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(mt.mlflow, "start_run", lambda run_name=None: DummyMlflow())
    monkeypatch.setattr(mt.mlflow, "log_params", lambda *args, **kwargs: None)
    monkeypatch.setattr(mt.mlflow, "log_metrics", lambda *args, **kwargs: None)
    monkeypatch.setattr(mt.mlflow, "log_metric", lambda *args, **kwargs: None)
    monkeypatch.setattr(mt.torch, "save", lambda *args, **kwargs: None)
    monkeypatch.setattr(mt.BEST_VAL_ACCURACY, "labels", lambda **kwargs: mt.BEST_VAL_ACCURACY)
    monkeypatch.setattr(mt.BEST_VAL_ACCURACY, "set", lambda *_: None)
    monkeypatch.setattr(mt.EPOCH_TRAIN_LOSS, "labels", lambda **kwargs: mt.EPOCH_TRAIN_LOSS)
    monkeypatch.setattr(mt.EPOCH_TRAIN_LOSS, "observe", lambda *_: None)

    def fake_log_model(model, name, export_model=False, input_example=None):
        logged["export_model"] = export_model
        logged["name"] = name

    monkeypatch.setattr(mt.mlflow.pytorch, "log_model", fake_log_model)

    def fake_training_loop(*args, **kwargs):
        pass

    monkeypatch.setattr(mt.ImagingModelTrainer, "train", lambda self: fake_training_loop())

    assert True
