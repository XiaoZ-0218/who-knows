from who_knows.catalog import deals, filter_games, merge_platform


def _game(**overrides):
    item = {
        "id": "steam:1",
        "title": "Alpha",
        "cover": "",
        "platform": "steam",
        "genres": ["action"],
        "players": ["solo"],
        "released_at": "2024-01-01",
        "rating": 80.0,
        "popularity": 10.0,
        "price": 10.0,
        "original_price": 20.0,
        "discount": 50.0,
        "store_url": "https://example.com",
        "mood": {"hot": 1.0, "new": 2.0, "sleeper": 3.0},
    }
    item.update(overrides)
    return item


def test_merge_replaces_one_platform_and_keeps_others():
    old = [
        _game(id="steam:1", platform="steam", title="Old Steam"),
        _game(id="ps5:1", platform="ps5", title="Old PS"),
    ]
    fresh = [_game(id="steam:2", platform="steam", title="New Steam")]
    merged = merge_platform(old, "steam", fresh)
    titles = {item["title"] for item in merged}
    assert titles == {"New Steam", "Old PS"}


def test_filter_by_platform_genre_and_players():
    games = [
        _game(id="a", platform="steam", genres=["action"], players=["solo"]),
        _game(id="b", platform="ps5", genres=["rpg"], players=["multi"]),
        _game(id="c", platform="steam", genres=["action"], players=["solo", "duo"]),
    ]
    found = filter_games(games, platform="steam", genre="action", players="duo")
    assert [item["id"] for item in found] == ["c"]


def test_filter_sorts_by_mood():
    games = [
        _game(id="low", mood={"hot": 1, "new": 9, "sleeper": 1}),
        _game(id="high", mood={"hot": 8, "new": 1, "sleeper": 1}),
    ]
    found = filter_games(games, mood="hot")
    assert [item["id"] for item in found] == ["high", "low"]


def test_deals_are_discounted_and_sorted():
    games = [
        _game(id="full", discount=0, title="Full"),
        _game(id="small", discount=10, title="Small"),
        _game(id="big", discount=70, title="Big"),
    ]
    found = deals(games)
    assert [item["id"] for item in found] == ["big", "small"]
