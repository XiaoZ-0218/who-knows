from who_knows.social import discussion_links


def test_steam_game_gets_review_and_discussion_links():
    links = discussion_links(
        {"id": "steam:1091500", "title": "Cyberpunk 2077", "platform": "steam"}
    )
    by_id = {item["id"]: item["url"] for item in links}
    assert "1091500" in by_id["steam-reviews"]
    assert "1091500" in by_id["steam-discuss"]
    assert "Cyberpunk" in by_id["bilibili"]
    assert "douban" in by_id
    assert "reddit" in by_id
    assert "xiaohongshu" in by_id


def test_console_game_skips_steam_community():
    links = discussion_links({"id": "ps5:abc", "title": "Astro", "platform": "ps5"})
    ids = [item["id"] for item in links]
    assert "steam-reviews" not in ids
    assert "bilibili" in ids
