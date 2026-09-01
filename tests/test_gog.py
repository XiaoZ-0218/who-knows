from who_knows.gog import parse_gog


def test_parse_gog_catalog():
    raw = {
        "products": [
            {
                "id": 1889754300,
                "title": "The Blood of Dawnwalker",
                "slug": "the_blood_of_dawnwalker",
                "storeLink": "https://www.gog.com/en/game/the_blood_of_dawnwalker",
                "coverHorizontal": "https://cdn.example/cover.png",
                "genres": [{"name": "Role-playing", "slug": "rpg"}],
                "price": {
                    "finalMoney": {"amount": "69.99", "currency": "USD"},
                    "baseMoney": {"amount": "69.99", "currency": "USD"},
                },
                "reviewsRating": 45,
                "reviewsCount": 200,
                "releaseDate": "2026-01-01T00:00:00Z",
            }
        ]
    }
    games = parse_gog(raw, fetched_at="2026-09-01T00:00:00+00:00")
    assert len(games) == 1
    game = games[0]
    assert game["id"] == "gog:1889754300"
    assert game["platform"] == "gog"
    assert game["genres"] == ["rpg"]
    assert game["price"] == 69.99
    assert game["currency"] == "USD"
    assert game["rating"] == 90.0
    assert "gog.com" in game["store_url"]
