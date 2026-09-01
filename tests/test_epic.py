from who_knows.epic import parse_epic


def test_parse_epic_promotions():
    raw = {
        "data": {
            "Catalog": {
                "searchStore": {
                    "elements": [
                        {
                            "title": "Breathedge",
                            "id": "abc",
                            "productSlug": "breathedge",
                            "urlSlug": "breathedge",
                            "keyImages": [
                                {
                                    "type": "DieselGameBox",
                                    "url": "https://cdn.example/breathedge.jpg",
                                }
                            ],
                            "categories": [{"path": "games"}],
                            "tags": [{"name": "Adventure"}, {"name": "Action"}],
                            "price": {
                                "totalPrice": {
                                    "discountPrice": 999,
                                    "originalPrice": 1999,
                                    "currencyCode": "USD",
                                }
                            },
                            "effectiveDate": "2024-01-01T00:00:00.000Z",
                        }
                    ]
                }
            }
        }
    }
    games = parse_epic(raw, fetched_at="2026-09-01T00:00:00+00:00")
    assert len(games) == 1
    game = games[0]
    assert game["platform"] == "epic"
    assert game["title"] == "Breathedge"
    assert game["price"] == 9.99
    assert game["original_price"] == 19.99
    assert game["discount"] == 50.0
    assert game["currency"] == "USD"
    assert "store.epicgames.com" in game["store_url"]
    assert "adventure" in game["genres"]
