from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import os
import threading
import time

from who_knows.apple import fetch_apple
from who_knows.cache import read_catalog, write_catalog
from who_knows.catalog import board_payload
from who_knows.deployhook import handle_deploy
from who_knows.epic import fetch_epic
from who_knows.fx import fetch_fx
from who_knows.gog import fetch_gog
from who_knows.nintendo import fetch_nintendo
from who_knows.playstation import fetch_playstation
from who_knows.refresh import refresh_catalog
from who_knows.steam import fetch_steam

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
DEFAULT_DATA = Path(os.environ.get("WHO_KNOWS_DATA", ROOT / "data" / "catalog.json"))
REFRESH_SECONDS = int(os.environ.get("WHO_KNOWS_REFRESH", "1800"))
PORT = int(os.environ.get("WHO_KNOWS_PORT", "8765"))


def default_fetchers() -> dict:
    return {
        "steam": fetch_steam,
        "ps5": fetch_playstation,
        "switch": fetch_nintendo,
        "apple-cn": lambda: fetch_apple("cn", "apple-cn"),
        "apple-us": lambda: fetch_apple("us", "apple-us"),
        "epic": fetch_epic,
        "gog": fetch_gog,
    }


class Board:
    def __init__(self, path: Path, fetchers: dict | None = None):
        self.path = path
        self.fetchers = fetchers or default_fetchers()
        self.lock = threading.Lock()

    def load(self) -> dict:
        with self.lock:
            return read_catalog(self.path)

    def refresh_now(self) -> dict:
        from datetime import datetime, timezone

        fetched_at = datetime.now(timezone.utc).isoformat()
        with self.lock:
            old = read_catalog(self.path)
        try:
            fx = fetch_fx()
        except Exception:
            fx = old.get("fx") or {}
        payload = refresh_catalog(old, self.fetchers, fetched_at, fx=fx)
        with self.lock:
            write_catalog(self.path, payload)
        return payload


def make_handler(board: Board):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path in ("/api/board", "/api/games"):
                query = parse_qs(parsed.query)
                payload = board_payload(
                    board.load(),
                    platform=_one(query, "platform"),
                    genre=_one(query, "genre"),
                    players=_one(query, "players"),
                    mood=_one(query, "mood") or "hot",
                )
                self._json(payload)
                return
            if parsed.path == "/api/status":
                self._json(board.load().get("status") or {})
                return
            if parsed.path == "/api/refresh":
                self._json(board.refresh_now().get("status") or {})
                return
            self._static(parsed.path)

        def do_POST(self):
            parsed = urlparse(self.path)
            if parsed.path != "/api/deploy":
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else b""
            status, payload = handle_deploy(self.headers, body)
            self._json(payload, status=status)

        def _json(self, payload, status=200):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _static(self, path: str):
            relative = "index.html" if path in ("", "/") else path.lstrip("/")
            target = (WEB / relative).resolve()
            if WEB.resolve() not in target.parents and target != WEB.resolve():
                self.send_error(404)
                return
            if not target.exists() or not target.is_file():
                self.send_error(404)
                return
            data = target.read_bytes()
            types = {
                ".html": "text/html; charset=utf-8",
                ".css": "text/css; charset=utf-8",
                ".js": "text/javascript; charset=utf-8",
                ".svg": "image/svg+xml",
            }
            self.send_response(200)
            self.send_header("Content-Type", types.get(target.suffix, "application/octet-stream"))
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return Handler


def _one(query: dict, key: str) -> str:
    values = query.get(key) or []
    return values[0] if values else ""


def _loop_refresh(board: Board, seconds: int, stop: threading.Event):
    board.refresh_now()
    while not stop.wait(seconds):
        board.refresh_now()


def main() -> None:
    board = Board(DEFAULT_DATA)
    stop = threading.Event()
    worker = threading.Thread(
        target=_loop_refresh, args=(board, REFRESH_SECONDS, stop), daemon=True
    )
    worker.start()
    handler = make_handler(board)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), handler)
    print(f"who knows board http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        stop.set()
        server.shutdown()


if __name__ == "__main__":
    main()
