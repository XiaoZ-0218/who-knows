from who_knows.steam import parse_steam


def test_parse_steam_featured_and_details():
    featured = {
        "specials": {
            "items": [
                {
                    "id": 1091500,
                    "name": "Cyberpunk 2077",
                    "discount_percent": 50,
                    "original_price": 5999,
                    "final_price": 2999,
                    "header_image": "https://cdn.example/cp.jpg",
                }
            ]
        },
        "top_sellers": {"items": []},
        "new_releases": {"items": []},
    }
    details = {
        "1091500": {
            "success": True,
            "data": {
                "name": "Cyberpunk 2077",
                "header_image": "https://cdn.example/cp.jpg",
                "genres": [{"description": "Action"}, {"description": "RPG"}],
                "categories": [
                    {"description": "Single-player"},
                    {"description": "Online Multiplayer"},
                ],
                "metacritic": {"score": 86},
                "recommendations": {"total": 5000},
                "release_date": {"date": "10 Dec, 2020"},
            },
        }
    }
    games = parse_steam(featured, details, fetched_at="2026-09-01T00:00:00+00:00")
    assert len(games) == 1
    game = games[0]
    assert game["id"] == "steam:1091500"
    assert game["platform"] == "steam"
    assert game["genres"] == ["action", "rpg"]
    assert game["players"] == ["solo", "multi"]
    assert game["price"] == 29.99
    assert game["original_price"] == 59.99
    assert game["discount"] == 50.0
    assert "store.steampowered.com/app/1091500" in game["store_url"]
