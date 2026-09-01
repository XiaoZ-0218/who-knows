from datetime import datetime, timezone

from who_knows.http import encode_query, get_json
from who_knows.normalize import make_game

NINTENDO_SEARCH = "https://searching.nintendo-europe.com/en/select"
NINTENDO_FQ = "type:GAME AND playable_on_txt:HAC"


def fetch_nintendo(load_json=get_json) -> list[dict]:
    sorts = ("hits_i desc", "date_from desc", "price_discount_percentage_f desc")
    docs = []
    seen = set()
    errors = []
    for sort in sorts:
        url = encode_query(
            NINTENDO_SEARCH,
            {"q": "*", "fq": NINTENDO_FQ, "sort": sort, "rows": "24", "wt": "json"},
        )
        try:
            raw = load_json(url)
        except Exception as exc:
            errors.append(str(exc))
            continue
        for doc in (raw.get("response") or {}).get("docs") or []:
            key = str(doc.get("fs_id") or doc.get("title"))
            if key and key not in seen:
                seen.add(key)
                docs.append(doc)
    if not docs and errors:
        raise RuntimeError("; ".join(errors))
    now = datetime.now(timezone.utc).isoformat()
    return parse_nintendo({"response": {"docs": docs}}, fetched_at=now)


def parse_nintendo(raw: dict, fetched_at: str = "") -> list[dict]:
    docs = (raw.get("response") or {}).get("docs") or []
    games = []
    for doc in docs:
        title = doc.get("title") or ""
        store_id = str(doc.get("fs_id") or doc.get("orig_nsuid_s") or "")
        if not title or not store_id:
            continue
        player_tags = []
        players_from = int(doc.get("players_from") or 0)
        players_to = int(doc.get("players_to") or 0)
        if players_from <= 1:
            player_tags.append("1 player")
        if players_to == 2 or players_from == 2:
            player_tags.append("2 player")
        if players_to >= 3:
            player_tags.append("multiplayer")
        path = doc.get("url") or ""
        if path.startswith("http"):
            store_url = path
        else:
            store_url = "https://www.nintendo.com/en-gb" + path
        released = ""
        dates = doc.get("dates_released_dts") or []
        if dates:
            released = dates[0]
        elif doc.get("pretty_date_s"):
            released = doc["pretty_date_s"]
        price = doc.get("price_lowest_f")
        if price is not None and float(price) < 0:
            price = None
        original = doc.get("price_regular_f")
        if original is not None and float(original) < 0:
            original = None
        games.append(
            make_game(
                platform="switch",
                store_id=store_id,
                title=title,
                cover=doc.get("image_url_sq_s") or doc.get("image_url") or "",
                genres=doc.get("pretty_game_categories_txt") or [],
                player_tags=player_tags,
                released_at=released,
                rating=float(doc.get("pretty_user_rating") or 0) * 20.0,
                popularity=float(doc.get("hits_i") or 0),
                price=price,
                original_price=original,
                discount=doc.get("price_discount_percentage_f") or 0,
                store_url=store_url,
                fetched_at=fetched_at,
            )
        )
    return games
