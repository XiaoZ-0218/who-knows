from http.server import ThreadingHTTPServer
from pathlib import Path
import json
import threading
import urllib.request

from who_knows.cache import write_catalog
from who_knows.server import Board, make_handler


def test_api_board_over_http(tmp_path: Path):
    path = tmp_path / "catalog.json"
    write_catalog(
        path,
        {
            "games": [
                {
                    "id": "steam:1",
                    "title": "Hades",
                    "cover": "",
                    "platform": "steam",
                    "genres": ["action"],
                    "players": ["solo"],
                    "released_at": "2020-09-17",
                    "rating": 93,
                    "popularity": 100,
                    "price": 10,
                    "original_price": 25,
                    "discount": 60,
                    "store_url": "https://store.steampowered.com/app/1",
                    "mood": {"hot": 5, "new": 1, "sleeper": 2},
                }
            ],
            "status": {"steam": {"ok": True, "count": 1}},
        },
    )
    board = Board(path, fetchers={})
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(board))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        raw = urllib.request.urlopen(
            f"http://127.0.0.1:{port}/api/board?mood=hot&players=solo", timeout=5
        ).read()
        payload = json.loads(raw)
        assert payload["games"][0]["title"] == "Hades"
        assert payload["deals"][0]["discount"] == 60
    finally:
        server.shutdown()
