import hashlib
import hmac
import json
import os
import subprocess
import threading
from pathlib import Path
from urllib.request import Request, urlopen


def verify_signature(secret: str, body: bytes, header: str | None) -> bool:
    if not secret or not header or not header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header)


def should_deploy(event: str, payload: dict) -> bool:
    return event == "push" and payload.get("ref") == "refs/heads/main"


def handle_deploy(headers, body: bytes) -> tuple[int, dict]:
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "").strip()
    if not secret:
        return 404, {"error": "disabled"}
    signature = headers.get("X-Hub-Signature-256") or headers.get("x-hub-signature-256")
    if not verify_signature(secret, body, signature):
        return 401, {"error": "bad signature"}
    event = headers.get("X-GitHub-Event") or headers.get("x-github-event") or ""
    if event == "ping":
        return 200, {"ok": True, "pong": True}
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return 400, {"error": "bad json"}
    if not should_deploy(event, payload):
        return 200, {"ok": True, "skipped": True}
    repo = os.environ.get("WHO_KNOWS_HOST_REPO", "").strip()
    if not repo:
        return 503, {"error": "host repo not configured"}
    threading.Thread(target=run_update, args=(repo,), daemon=True).start()
    return 202, {"ok": True, "accepted": True}


def run_update(repo: str) -> None:
    _sync_mirror()
    script = Path(repo) / "deploy" / "update.sh"
    subprocess.run(["/bin/sh", str(script)], cwd=repo, check=False)


def _sync_mirror() -> None:
    token = os.environ.get("GITEA_TOKEN", "").strip()
    url = os.environ.get("GITEA_MIRROR_URL", "").strip()
    if not token or not url:
        return
    request = Request(
        url,
        data=b"",
        method="POST",
        headers={"Authorization": "token " + token},
    )
    try:
        with urlopen(request, timeout=60):
            return
    except Exception:
        return
