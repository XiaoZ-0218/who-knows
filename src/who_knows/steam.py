from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from who_knows.http import get_json
from who_knows.normalize import make_game

STEAM_FEATURED = "https://store.steampowered.com/api/featuredcategories?cc=us&l=schinese"
STEAM_DETAILS = "https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=schinese"


def fetch_steam(load_json=get_json, limit: int = 30) -> list[dict]:
    featured = load_json(STEAM_FEATURED)
    appids = []
    for bucket in featured.values():
        if not isinstance(bucket, dict):
            continue
        for item in bucket.get("items") or []:
            appid = str(item.get("id") or "")
            if appid and appid not in appids:
                appids.append(appid)
    details = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [
            pool.submit(load_json, STEAM_DETAILS.format(appid=appid))
            for appid in appids[:limit]
        ]
        for future in as_completed(futures):
            try:
                details.update(future.result())
            except Exception:
                continue
    now = datetime.now(timezone.utc).isoformat()
    return parse_steam(featured, details, fetched_at=now)


def parse_steam(featured: dict, details: dict, fetched_at: str = "") -> list[dict]:
    items = {}
    for bucket in featured.values():
        if not isinstance(bucket, dict):
            continue
        for item in bucket.get("items") or []:
            appid = str(item.get("id") or "")
            if not appid:
                continue
            items[appid] = item
    games = []
    for appid, item in items.items():
        info = (details.get(appid) or {}).get("data") or {}
        if not info and not item.get("name"):
            continue
        title = info.get("name") or item.get("name") or ""
        if not title:
            continue
        genres = [g.get("description", "") for g in info.get("genres") or []]
        player_tags = [c.get("description", "") for c in info.get("categories") or []]
        price, original, discount = _steam_price(item, info)
        games.append(
            make_game(
                platform="steam",
                store_id=appid,
                title=title,
                cover=info.get("header_image") or item.get("header_image") or "",
                genres=genres,
                player_tags=player_tags,
                released_at=(info.get("release_date") or {}).get("date") or "",
                rating=float((info.get("metacritic") or {}).get("score") or 0),
                popularity=float((info.get("recommendations") or {}).get("total") or 0),
                price=price,
                original_price=original,
                discount=discount,
                store_url=f"https://store.steampowered.com/app/{appid}",
                fetched_at=fetched_at,
            )
        )
    return games


def _steam_price(item: dict, info: dict) -> tuple[float | None, float | None, float | None]:
    final = item.get("final_price")
    original = item.get("original_price")
    if final is None:
        overview = (info.get("price_overview") or {})
        final = overview.get("final")
        original = overview.get("initial")
    if final is None:
        return None, None, None
    price = round(float(final) / 100.0, 2)
    original_price = round(float(original) / 100.0, 2) if original else None
    discount = item.get("discount_percent")
    if discount is None and original_price and original_price > 0 and price < original_price:
        discount = round((1.0 - price / original_price) * 100.0, 1)
    return price, original_price, float(discount) if discount is not None else 0.0
