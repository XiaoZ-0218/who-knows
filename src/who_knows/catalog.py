from who_knows.fx import to_cny
from who_knows.social import discussion_links


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


def board_payload(
    catalog: dict,
    platform: str | None = None,
    genre: str | None = None,
    players: str | None = None,
    mood: str = "hot",
) -> dict:
    platform = platform or None
    genre = genre or None
    players = players or None
    mood = mood or "hot"
    games = catalog.get("games") or []
    fx = catalog.get("fx") or {}
    filtered = [
        present_game(item, fx)
        for item in filter_games(games, platform=platform, genre=genre, players=players, mood=mood)
    ]
    deal_pool = [
        present_game(item, fx)
        for item in deals(filter_games(games, platform=platform, genre=genre, players=players, mood="hot"))[:12]
    ]
    genres = sorted({g for item in games for g in item.get("genres") or []})
    return {
        "games": filtered,
        "deals": deal_pool,
        "status": catalog.get("status") or {},
        "genres": genres,
        "fx": fx,
    }


def present_game(game: dict, fx: dict) -> dict:
    item = dict(game)
    currency = item.get("currency") or "USD"
    item["price_cny"] = to_cny(item.get("price"), currency, fx)
    item["original_price_cny"] = to_cny(item.get("original_price"), currency, fx)
    item["links"] = discussion_links(item)
    return item
