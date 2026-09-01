def merge_platform(old: list[dict], platform: str, fresh: list[dict]) -> list[dict]:
    kept = [item for item in old if item.get("platform") != platform]
    return kept + list(fresh)


def filter_games(
    games: list[dict],
    platform: str | None = None,
    genre: str | None = None,
    players: str | None = None,
    mood: str = "hot",
) -> list[dict]:
    found = []
    for item in games:
        if platform and item.get("platform") != platform:
            continue
        if genre and genre not in item.get("genres", []):
            continue
        if players and players not in item.get("players", []):
            continue
        found.append(item)
    key = mood if mood in ("hot", "new", "sleeper") else "hot"
    return sorted(found, key=lambda item: item.get("mood", {}).get(key, 0), reverse=True)


def deals(games: list[dict]) -> list[dict]:
    discounted = [item for item in games if (item.get("discount") or 0) > 0]
    return sorted(discounted, key=lambda item: item.get("discount") or 0, reverse=True)
