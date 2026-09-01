from who_knows.refresh import refresh_catalog


def _game(platform, store_id, title):
    return {
        "id": f"{platform}:{store_id}",
        "title": title,
        "platform": platform,
        "genres": [],
        "players": [],
        "discount": 0,
        "mood": {"hot": 1, "new": 1, "sleeper": 1},
    }


def test_refresh_replaces_successful_platform_only():
    old = {
        "games": [
            _game("steam", "1", "Old Steam"),
            _game("ps5", "1", "Old PS"),
        ],
        "status": {},
    }

    def steam_ok():
        return [_game("steam", "2", "New Steam")]

    def ps_down():
        raise RuntimeError("ps down")

    payload = refresh_catalog(
        old,
        {"steam": steam_ok, "ps5": ps_down},
        fetched_at="2026-09-01T00:00:00+00:00",
    )
    titles = {item["title"] for item in payload["games"]}
    assert titles == {"New Steam", "Old PS"}
    assert payload["status"]["steam"]["ok"] is True
    assert payload["status"]["ps5"]["ok"] is False
    assert "ps down" in payload["status"]["ps5"]["error"]
