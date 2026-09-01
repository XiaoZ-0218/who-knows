from datetime import datetime, timezone

from who_knows.http import get_json
from who_knows.normalize import make_game


def fetch_apple(country: str, platform: str, load_json=get_json) -> list[dict]:
    entries = []
    seen: set[str] = set()
    for chart in ("toppaidapplications", "topfreeapplications"):
        url = f"https://itunes.apple.com/{country}/rss/{chart}/limit=25/genre=6014/json"
        try:
            raw = load_json(url)
        except Exception:
            continue
        for entry in _entries(raw):
            store_id = _apple_id(entry)
            if store_id and store_id not in seen:
                seen.add(store_id)
                entries.append(entry)
    lookups = {}
    ids = [store_id for store_id in seen if store_id]
    for i in range(0, len(ids), 20):
        chunk = ",".join(ids[i : i + 20])
        try:
            data = load_json(f"https://itunes.apple.com/lookup?country={country}&id={chunk}")
        except Exception:
            continue
        for item in data.get("results") or []:
            lookups[str(item.get("trackId") or "")] = item
    now = datetime.now(timezone.utc).isoformat()
    return parse_apple({"feed": {"entry": entries}}, lookups, platform=platform, fetched_at=now)


def parse_apple(
    raw: dict,
    lookups: dict | None = None,
    platform: str = "apple-cn",
    fetched_at: str = "",
) -> list[dict]:
    lookups = lookups or {}
    games = []
    for entry in _entries(raw):
        store_id = _apple_id(entry)
        title = ((entry.get("im:name") or {}).get("label")) or ""
        if not store_id or not title:
            continue
        info = lookups.get(store_id) or {}
        price_info = (entry.get("im:price") or {}).get("attributes") or {}
        price = float(price_info.get("amount") or 0)
        currency = price_info.get("currency") or ("CNY" if platform == "apple-cn" else "USD")
        images = entry.get("im:image") or []
        cover = ""
        if images:
            cover = (images[-1] or {}).get("label") or ""
        cover = info.get("artworkUrl512") or cover
        genres = info.get("genres") or [
            ((entry.get("category") or {}).get("attributes") or {}).get("label") or ""
        ]
        rating = float(info.get("averageUserRating") or 0) * 20.0
        popularity = float(info.get("userRatingCount") or 0)
        games.append(
            make_game(
                platform=platform,
                store_id=store_id,
                title=info.get("trackName") or title,
                cover=cover,
                genres=genres,
                player_tags=["Single-player"],
                released_at=((entry.get("im:releaseDate") or {}).get("label") or ""),
                rating=rating,
                popularity=popularity,
                price=price,
                original_price=price if price else None,
                discount=0,
                store_url=_apple_url(entry, store_id, platform),
                currency=currency,
                fetched_at=fetched_at,
            )
        )
    return games


def _entries(raw: dict) -> list:
    entry = (raw.get("feed") or {}).get("entry")
    if not entry:
        return []
    if isinstance(entry, dict):
        return [entry]
    return list(entry)


def _apple_id(entry: dict) -> str:
    return str(((entry.get("id") or {}).get("attributes") or {}).get("im:id") or "")


def _apple_url(entry: dict, store_id: str, platform: str) -> str:
    links = entry.get("link") or []
    if isinstance(links, dict):
        links = [links]
    for link in links:
        href = (link.get("attributes") or {}).get("href") or ""
        if "apps.apple.com" in href:
            return href
    region = "cn" if platform == "apple-cn" else "us"
    return f"https://apps.apple.com/{region}/app/id{store_id}"
