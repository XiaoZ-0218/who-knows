from datetime import datetime, timezone

from who_knows.http import get_json
from who_knows.normalize import make_game

GOG_URLS = (
    "https://catalog.gog.com/v1/catalog?limit=30&order=desc:trending&productType=game",
    "https://catalog.gog.com/v1/catalog?limit=20&order=desc:discount&productType=game",
)


def fetch_gog(load_json=get_json) -> list[dict]:
    products = []
    seen = set()
    errors = []
    for url in GOG_URLS:
        try:
            raw = load_json(url)
        except Exception as exc:
            errors.append(str(exc))
            continue
        for item in raw.get("products") or []:
            store_id = str(item.get("id") or "")
            if store_id and store_id not in seen:
                seen.add(store_id)
                products.append(item)
    if not products and errors:
        raise RuntimeError("; ".join(errors))
    now = datetime.now(timezone.utc).isoformat()
    return parse_gog({"products": products}, fetched_at=now)


def parse_gog(raw: dict, fetched_at: str = "") -> list[dict]:
    games = []
    for item in raw.get("products") or []:
        title = item.get("title") or ""
        store_id = str(item.get("id") or "")
        if not title or not store_id:
            continue
        final = (item.get("price") or {}).get("finalMoney") or {}
        base = (item.get("price") or {}).get("baseMoney") or {}
        price = _money(final.get("amount"))
        original = _money(base.get("amount"))
        discount = 0.0
        if original and price is not None and original > 0 and price < original:
            discount = round((1.0 - price / original) * 100.0, 1)
        rating_raw = float(item.get("reviewsRating") or 0)
        if rating_raw <= 5:
            rating = rating_raw * 20.0
        elif rating_raw <= 50:
            rating = rating_raw * 2.0
        else:
            rating = rating_raw
        games.append(
            make_game(
                platform="gog",
                store_id=store_id,
                title=title,
                cover=item.get("coverHorizontal") or "",
                genres=[g.get("name") or "" for g in item.get("genres") or []],
                player_tags=["Single-player"],
                released_at=item.get("releaseDate") or item.get("storeReleaseDate") or "",
                rating=rating,
                popularity=float(item.get("reviewsCount") or 0),
                price=price,
                original_price=original,
                discount=discount,
                store_url=item.get("storeLink")
                or f"https://www.gog.com/game/{item.get('slug') or store_id}",
                currency=final.get("currency") or "USD",
                fetched_at=fetched_at,
            )
        )
    return games


def _money(value) -> float | None:
    if value is None or value == "":
        return None
    return round(float(value), 2)
