from datetime import datetime, timezone

from who_knows.http import get_json
from who_knows.normalize import make_game

EPIC_URL = (
    "https://store-site-backend-static-ipv4.ak.epicgames.com/"
    "freeGamesPromotions?locale=zh-CN&country=US&allowCountries=US"
)


def fetch_epic(load_json=get_json) -> list[dict]:
    raw = load_json(EPIC_URL)
    now = datetime.now(timezone.utc).isoformat()
    return parse_epic(raw, fetched_at=now)


def parse_epic(raw: dict, fetched_at: str = "") -> list[dict]:
    elements = (
        ((raw.get("data") or {}).get("Catalog") or {}).get("searchStore") or {}
    ).get("elements") or []
    games = []
    for item in elements:
        title = item.get("title") or ""
        store_id = str(item.get("id") or item.get("urlSlug") or "")
        if not title or not store_id:
            continue
        total = (item.get("price") or {}).get("totalPrice") or {}
        price = _cents(total.get("discountPrice"))
        original = _cents(total.get("originalPrice"))
        discount = 0.0
        if original and price is not None and original > 0 and price < original:
            discount = round((1.0 - price / original) * 100.0, 1)
        slug = item.get("productSlug") or item.get("urlSlug") or ""
        store_url = f"https://store.epicgames.com/p/{slug}" if slug else "https://store.epicgames.com/"
        games.append(
            make_game(
                platform="epic",
                store_id=store_id,
                title=title,
                cover=_epic_cover(item.get("keyImages") or []),
                genres=[t.get("name") or "" for t in item.get("tags") or []],
                player_tags=["Single-player"],
                released_at=item.get("effectiveDate") or "",
                rating=0,
                popularity=0,
                price=price,
                original_price=original,
                discount=discount,
                store_url=store_url,
                currency=total.get("currencyCode") or "USD",
                fetched_at=fetched_at,
            )
        )
    return games


def _cents(value) -> float | None:
    if value is None:
        return None
    return round(float(value) / 100.0, 2)


def _epic_cover(images: list) -> str:
    preferred = ("DieselGameBox", "OfferImageWide", "Thumbnail", "DieselGameBoxTall")
    by_type = {img.get("type"): img.get("url") or "" for img in images}
    for key in preferred:
        if by_type.get(key):
            return by_type[key]
    for img in images:
        if img.get("url"):
            return img["url"]
    return ""
