from who_knows.playstation import parse_playstation


def test_parse_playstation_chihiro_links():
    raw = {
        "links": [
            {
                "id": "UP0001-PPSA12345_00-DEMO",
                "name": "Astro Demo",
                "playable_platform": ["PS5"],
                "images": [{"type": "master", "url": "https://cdn.example/astro.jpg"}],
                "default_sku": {
                    "price": 1999,
                    "display_price": "$19.99",
                    "rewards": [{"discount": 50}],
                },
                "release_date": "2024-06-01T00:00:00Z",
                "metadata": {
                    "game_genre": {"values": ["Action", "Adventure"]},
                    "playable_platform": {"values": ["PS5"]},
                },
                "star_rating": {"score": "4.5", "total": "2000"},
                "gameContentTypesList": [{"name": "Full Game"}],
            }
        ]
    }
    games = parse_playstation(raw, fetched_at="2026-09-01T00:00:00+00:00")
    assert len(games) == 1
    game = games[0]
    assert game["platform"] == "ps5"
    assert game["title"] == "Astro Demo"
    assert game["genres"] == ["action", "adventure"]
    assert game["price"] == 19.99
    assert game["discount"] == 50.0
    assert game["store_url"].startswith("https://store.playstation.com/")
