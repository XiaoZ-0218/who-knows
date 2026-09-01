from urllib.parse import quote


def discussion_links(game: dict) -> list[dict]:
    title = quote(game.get("title") or "")
    links = []
    if game.get("platform") == "steam":
        appid = str(game.get("id") or "").split(":", 1)[-1]
        links.append(
            {
                "id": "steam-reviews",
                "label": "Steam评测",
                "url": f"https://steamcommunity.com/app/{appid}/reviews/",
            }
        )
        links.append(
            {
                "id": "steam-discuss",
                "label": "Steam讨论",
                "url": f"https://steamcommunity.com/app/{appid}/discussions/",
            }
        )
    links.extend(
        [
            {
                "id": "bilibili",
                "label": "B站",
                "url": f"https://search.bilibili.com/all?keyword={title}",
            },
            {
                "id": "douban",
                "label": "豆瓣",
                "url": f"https://search.douban.com/game/subject_search?search_text={title}",
            },
            {
                "id": "reddit",
                "label": "Reddit",
                "url": f"https://www.reddit.com/search/?q={title}",
            },
            {
                "id": "xiaohongshu",
                "label": "小红书",
                "url": f"https://www.xiaohongshu.com/search_result?keyword={title}",
            },
        ]
    )
    return links
