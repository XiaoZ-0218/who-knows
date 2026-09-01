from who_knows.apple import parse_apple


def test_parse_apple_rss_paid_game():
    raw = {
        "feed": {
            "entry": [
                {
                    "im:name": {"label": "潜水员戴夫"},
                    "im:price": {
                        "label": "¥30.00",
                        "attributes": {"amount": "30.00", "currency": "CNY"},
                    },
                    "id": {
                        "attributes": {"im:id": "6755228041"},
                    },
                    "link": [
                        {
                            "attributes": {
                                "rel": "alternate",
                                "href": "https://apps.apple.com/cn/app/id6755228041",
                            }
                        }
                    ],
                    "category": {"attributes": {"label": "游戏", "term": "Games"}},
                    "im:releaseDate": {"label": "2026-02-06T00:00:00-07:00"},
                    "im:image": [
                        {"label": "https://example.com/small.png"},
                        {"label": "https://example.com/dave.png"},
                    ],
                }
            ]
        }
    }
    lookups = {
        "6755228041": {
            "averageUserRating": 4.6,
            "userRatingCount": 1200,
            "genres": ["游戏", "冒险"],
        }
    }
    games = parse_apple(raw, lookups, platform="apple-cn", fetched_at="2026-09-01T00:00:00+00:00")
    assert len(games) == 1
    game = games[0]
    assert game["id"] == "apple-cn:6755228041"
    assert game["platform"] == "apple-cn"
    assert game["title"] == "潜水员戴夫"
    assert game["price"] == 30.0
    assert game["currency"] == "CNY"
    assert game["genres"] == ["adventure"]
    assert "apps.apple.com" in game["store_url"]
    assert game["rating"] == 92.0
