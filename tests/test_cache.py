from pathlib import Path

from who_knows.cache import read_catalog, write_catalog


def test_read_missing_catalog_is_empty(tmp_path: Path):
    payload = read_catalog(tmp_path / "missing.json")
    assert payload == {"games": [], "status": {}}


def test_write_catalog_replaces_atomically(tmp_path: Path):
    path = tmp_path / "catalog.json"
    write_catalog(path, {"games": [{"id": "a"}], "status": {"steam": "ok"}})
    payload = read_catalog(path)
    assert payload["games"][0]["id"] == "a"
    assert payload["status"]["steam"] == "ok"
