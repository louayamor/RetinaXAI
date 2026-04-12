from __future__ import annotations

from app.components.imaging import data_ingestion as module


class FakeDataset:
    def __init__(self, labels: list[int]):
        self._labels = labels
        self.saved_to: str | None = None
        self.features = {"label_code": "int64"}

    def __len__(self) -> int:
        return len(self._labels)

    def __getitem__(self, key: str):
        if key != "label_code":
            raise KeyError(key)
        return self._labels

    def save_to_disk(self, path: str) -> None:
        self.saved_to = path


def test_run_appends_only_missing_samples(monkeypatch, tmp_path):
    existing = FakeDataset([0, 1, 2])
    new = FakeDataset([3, 4])
    saved = {"path": None, "dataset": None}

    config = type(
        "Cfg",
        (),
        {
            "root_dir": tmp_path,
            "dataset_name": "bumbledeep/eyepacs",
            "train_split": "train",
            "max_samples": 5,
        },
    )()

    save_path = tmp_path / "huggingface" / "train"
    save_path.mkdir(parents=True)

    calls: list[str] = []

    monkeypatch.setattr(module, "load_from_disk", lambda _path: existing)
    monkeypatch.setattr(
        module,
        "load_dataset",
        lambda _name, split: calls.append(split) or new,
    )
    monkeypatch.setattr(
        module,
        "concatenate_datasets",
        lambda datasets: FakeDataset(sum((ds["label_code"] for ds in datasets), [])),
    )

    original_save = FakeDataset.save_to_disk

    def capture_save(self, path: str) -> None:
        saved["path"] = path
        saved["dataset"] = list(self["label_code"])
        original_save(self, path)

    monkeypatch.setattr(FakeDataset, "save_to_disk", capture_save)

    result = module.ImagingDataIngestion(config).run()

    assert calls == ["train[3:5]"]
    assert result is None
    assert saved["path"] == str(save_path)
    assert saved["dataset"] == [0, 1, 2, 3, 4]


def test_run_skips_when_existing_dataset_is_large_enough(monkeypatch, tmp_path):
    existing = FakeDataset([0, 1, 2, 3, 4])

    config = type(
        "Cfg",
        (),
        {
            "root_dir": tmp_path,
            "dataset_name": "bumbledeep/eyepacs",
            "train_split": "train",
            "max_samples": 5,
        },
    )()

    save_path = tmp_path / "huggingface" / "train"
    save_path.mkdir(parents=True)

    monkeypatch.setattr(module, "load_from_disk", lambda _path: existing)

    called = {"load_dataset": False}

    def fake_load_dataset(*_args, **_kwargs):
        called["load_dataset"] = True
        raise AssertionError("should not download when enough samples already exist")

    monkeypatch.setattr(module, "load_dataset", fake_load_dataset)

    module.ImagingDataIngestion(config).run()

    assert called["load_dataset"] is False
