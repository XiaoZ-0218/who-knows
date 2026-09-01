from who_knows.nintendo import parse_nintendo


def test_parse_nintendo_europe_docs():
    raw = {
        "response": {
            "docs": [
                {
                    "fs_id": "123",
                    "title": "Zelda",
                    "image_url_sq_s": "https://cdn.example/zelda.jpg",
                    "pretty_date_s": "12/05/2023",
                    "price_lowest_f": 35.99,
                    "price_regular_f": 59.99,
                    "price_discount_percentage_f": 40,
                    "pretty_game_categories_txt": ["Adventure", "Puzzle"],
                    "players_to": 2,
                    "players_from": 1,
                    "url": "/Games/Zelda",
                    "dates_released_dts": ["2023-05-12T00:00:00Z"],
                    "change_date": "2023-05-12T00:00:00Z",
                    "nsuid_txt": ["70010000012345"],
                    "orig_nsuid_s": "70010000012345",
                }
            ]
        }
    }
    games = parse_nintendo(raw, fetched_at="2026-09-01T00:00:00+00:00")
    assert len(games) == 1
    game = games[0]
    assert game["platform"] == "switch"
    assert game["title"] == "Zelda"
    assert game["genres"] == ["adventure", "puzzle"]
    assert "duo" in game["players"]
    assert "solo" in game["players"]
    assert game["price"] == 35.99
    assert game["discount"] == 40.0
    assert "nintendo.com" in game["store_url"] or "nintendo.co.uk" in game["store_url"]
