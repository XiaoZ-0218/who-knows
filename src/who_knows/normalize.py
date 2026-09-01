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
