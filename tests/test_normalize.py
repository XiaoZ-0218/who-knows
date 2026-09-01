from datetime import datetime, timezone

from who_knows.normalize import classify_players, map_genres, mood_scores


def test_single_player_tag_is_solo():
    assert classify_players(["Single-player"]) == ["solo"]


def test_split_screen_is_duo():
    assert classify_players(["Shared/Split Screen Co-op"]) == ["duo"]


def test_online_multiplayer_is_multi():
    assert classify_players(["Online Multiplayer"]) == ["multi"]


def test_mixed_tags_keep_each_mode():
    assert classify_players(["Single-player", "Online Multiplayer", "Local Co-Op"]) == [
        "solo",
        "duo",
        "multi",
    ]


def test_empty_tags_are_unknown():
    assert classify_players([]) == []


def test_map_genres_keeps_known_slugs():
    assert map_genres(["Action", "Role-Playing", "RPG", "Foo"]) == ["action", "rpg"]


def test_hot_mood_prefers_high_rating_and_popularity():
    hot = mood_scores(90, 1000, "2020-01-01", now=datetime(2026, 9, 1, tzinfo=timezone.utc))
    quiet = mood_scores(90, 2, "2020-01-01", now=datetime(2026, 9, 1, tzinfo=timezone.utc))
    assert hot["hot"] > quiet["hot"]


def test_new_mood_prefers_recent_release():
    now = datetime(2026, 9, 1, tzinfo=timezone.utc)
    fresh = mood_scores(80, 10, "2026-08-01", now=now)
    old = mood_scores(80, 10, "2018-01-01", now=now)
    assert fresh["new"] > old["new"]


def test_sleeper_mood_prefers_high_rating_low_popularity():
    now = datetime(2026, 9, 1, tzinfo=timezone.utc)
    gem = mood_scores(92, 3, "2022-01-01", now=now)
    hit = mood_scores(92, 9000, "2022-01-01", now=now)
    assert gem["sleeper"] > hit["sleeper"]
