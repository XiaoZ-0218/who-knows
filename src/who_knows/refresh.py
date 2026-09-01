from who_knows.catalog import merge_platform


def refresh_catalog(old: dict, fetchers: dict, fetched_at: str) -> dict:
    games = list(old.get("games") or [])
    status = dict(old.get("status") or {})
    for platform, fetcher in fetchers.items():
        previous = status.get(platform) or {}
        try:
            fresh = fetcher()
            games = merge_platform(games, platform, fresh)
            status[platform] = {
                "ok": True,
                "count": len(fresh),
                "fetched_at": fetched_at,
                "error": "",
            }
        except Exception as exc:
            status[platform] = {
                "ok": False,
                "count": previous.get("count", 0),
                "fetched_at": previous.get("fetched_at", ""),
                "error": str(exc),
            }
    return {"games": games, "status": status}
