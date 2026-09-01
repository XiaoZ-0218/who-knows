from pathlib import Path
import json
import os
import tempfile


def read_catalog(path: Path) -> dict:
    if not path.exists():
        return {"games": [], "status": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def write_catalog(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".catalog.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise
