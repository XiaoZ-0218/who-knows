from datetime import datetime, timezone
import json

from who_knows.http import get_json
from who_knows.normalize import make_game

PS_URLS = (
    "https://store.playstation.com/store/api/chihiro/00_09_000/tumbler/US/en/999/ps5?suggested_size=30&mode=game",
    "https://store.playstation.com/store/api/chihiro/00_09_000/container/US/en/999/STORE-MSF77008-ALLDEALS?size=20",
    "https://store.playstation.com/store/api/chihiro/00_09_000/container/US/en/999/STORE-MSF77008-NEWGAMES?size=20",
)


def fetch_playstation(load_json=get_json) -> list[dict]:
    links = []
    seen = set()
    errors = []
    for url in PS_URLS:
        try:
            raw = load_json(url)
        except Exception as exc:
            errors.append(str(exc))
            continue
        for item in raw.get("links") or []:
            store_id = item.get("id")
            if store_id and store_id not in seen:
                seen.add(store_id)
                links.append(item)
    if not links and errors:
        raise RuntimeError("; ".join(errors))
    now = datetime.now(timezone.utc).isoformat()
    return parse_playstation({"links": links}, fetched_at=now)


def parse_playstation(raw: dict, fetched_at: str = "") -> list[dict]:
    games = []
    for item in raw.get("links") or []:
        title = item.get("name") or item.get("title_name") or ""
        store_id = str(item.get("id") or "")
        if not title or not store_id:
            continue
        sku = item.get("default_sku") or {}
        price_cents = sku.get("price")
        price = round(float(price_cents) / 100.0, 2) if price_cents is not None else None
        rewards = sku.get("rewards") or []
        discount = 0.0
        if rewards:
            discount = float(rewards[0].get("discount") or 0)
        original = None
        if price is not None and discount and discount < 100:
            original = round(price / (1.0 - discount / 100.0), 2)
        metadata = item.get("metadata") or {}
        genres = (metadata.get("game_genre") or {}).get("values") or []
        cover = ""
        for image in item.get("images") or []:
            if image.get("url"):
                cover = image["url"]
                if str(image.get("type", "")).lower() in ("master", "10"):
                    break
        rating_info = item.get("star_rating") or {}
        score = float(rating_info.get("score") or 0) * 20.0
        popularity = float(str(rating_info.get("total") or "0").replace(",", "") or 0)
        player_tags = _player_tags(metadata, sku)
        games.append(
            make_game(
                platform="ps5",
                store_id=store_id,
                title=title,
                cover=cover,
                genres=genres,
                player_tags=player_tags,
                released_at=item.get("release_date") or "",
                rating=score,
                popularity=popularity,
                price=price,
                original_price=original,
                discount=discount,
                store_url=f"https://store.playstation.com/en-us/product/{store_id}",
                currency="USD",
                fetched_at=fetched_at,
            )
        )
    return games


def _player_tags(metadata: dict, sku: dict) -> list[str]:
    values = (metadata.get("cn_numberOfPlayers") or {}).get("values") or []
    tags = []
    blob = " ".join(str(v) for v in values) + " " + json.dumps(sku)
    if "1" in values or "1 Player" in blob:
        tags.append("Single-player")
    if any(v in ("2", "1-2", "2 Players") for v in values):
        tags.append("2 player")
    if any(str(v).isdigit() and int(v) >= 3 for v in values) or "4" in values:
        tags.append("Online Multiplayer")
    if not tags:
        tags.append("Single-player")
    return tags
