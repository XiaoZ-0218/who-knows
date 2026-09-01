from datetime import datetime, timezone


def classify_players(tags: list[str]) -> list[str]:
    text = " ".join(tags).lower().replace("-", " ").replace("/", " ")
    modes: list[str] = []
    if _mentions(text, ("single player", "singleplayer", "solo", "1 player", "单人")):
        modes.append("solo")
    if _mentions(
        text,
        (
            "split screen",
            "shared screen",
            "local co op",
            "local coop",
            "local multiplayer",
            "2 player",
            "two player",
            "1 2 player",
            "couch",
            "双人",
        ),
    ):
        modes.append("duo")
    if _mentions(
        text,
        (
            "online multiplayer",
            "multiplayer",
            "massively",
            "mmo",
            "online co op",
            "online coop",
            "4 player",
            "pvp",
            "多人",
        ),
    ):
        modes.append("multi")
    return modes


def _mentions(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


GENRE_ALIASES = {
    "action": "action",
    "adventure": "adventure",
    "rpg": "rpg",
    "role playing": "rpg",
    "role-playing": "rpg",
    "jrpg": "rpg",
    "shooter": "shooter",
    "fps": "shooter",
    "sports": "sports",
    "racing": "racing",
    "puzzle": "puzzle",
    "horror": "horror",
    "indie": "indie",
    "strategy": "strategy",
    "simulation": "simulation",
    "sim": "simulation",
    "fighting": "fighting",
    "music": "music",
    "rhythm": "music",
}


def map_genres(names: list[str]) -> list[str]:
    found: list[str] = []
    for name in names:
        key = name.lower().replace("_", " ").strip()
        slug = GENRE_ALIASES.get(key)
        if slug and slug not in found:
            found.append(slug)
    return found


def mood_scores(
    rating: float,
    popularity: float,
    released_at: str,
    now: datetime | None = None,
) -> dict[str, float]:
    now = now or datetime.now(timezone.utc)
    age_days = _age_days(released_at, now)
    pop = max(popularity, 0.0)
    hot = rating * (1.0 + pop)
    new = max(0.0, 1.0 - age_days / 365.0) * 100.0
    sleeper = rating / (1.0 + pop)
    return {"hot": hot, "new": new, "sleeper": sleeper}


def _age_days(released_at: str, now: datetime) -> float:
    if not released_at:
        return 3650.0
    try:
        released = datetime.fromisoformat(released_at.replace("Z", "+00:00"))
    except ValueError:
        return 3650.0
    if released.tzinfo is None:
        released = released.replace(tzinfo=timezone.utc)
    return max((now - released).total_seconds() / 86400.0, 0.0)


def make_game(
    *,
    platform: str,
    store_id: str,
    title: str,
    cover: str = "",
    genres: list[str] | None = None,
    player_tags: list[str] | None = None,
    released_at: str = "",
    rating: float = 0.0,
    popularity: float = 0.0,
    price: float | None = None,
    original_price: float | None = None,
    discount: float | None = None,
    store_url: str = "",
    currency: str = "USD",
    fetched_at: str = "",
    now: datetime | None = None,
) -> dict:
    iso_date = to_iso_date(released_at)
    if discount is None:
        discount = 0.0
        if price is not None and original_price and original_price > 0 and price < original_price:
            discount = round((1.0 - price / original_price) * 100.0, 1)
    return {
        "id": f"{platform}:{store_id}",
        "title": title,
        "cover": cover,
        "platform": platform,
        "genres": map_genres(genres or []),
        "players": classify_players(player_tags or []),
        "released_at": iso_date,
        "rating": float(rating or 0),
        "popularity": float(popularity or 0),
        "price": price,
        "original_price": original_price,
        "discount": float(discount or 0),
        "store_url": store_url,
        "currency": currency or "USD",
        "fetched_at": fetched_at,
        "mood": mood_scores(float(rating or 0), float(popularity or 0), iso_date, now=now),
    }


def to_iso_date(value: str) -> str:
    if not value:
        return ""
    value = value.strip()
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.date().isoformat()
    except ValueError:
        pass
    for fmt in ("%d %b, %Y", "%b %d, %Y", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value[: len("10 Dec, 2020")], fmt).date().isoformat()
        except ValueError:
            continue
    # pretty_date_s is often dd/mm/yyyy; try full string
    for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%d %b, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return ""
