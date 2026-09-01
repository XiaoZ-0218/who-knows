from who_knows.http import get_json

FRANKFURTER = "https://api.frankfurter.app/latest"


def to_cny(price: float | None, currency: str, fx: dict) -> float | None:
    if price is None:
        return None
    rate = fx.get(currency)
    if not rate:
        return None
    return round(float(price) * float(rate), 2)


def fetch_fx(load_json=get_json) -> dict:
    usd = load_json(f"{FRANKFURTER}?from=USD&to=CNY")
    eur = load_json(f"{FRANKFURTER}?from=EUR&to=CNY")
    return {
        "USD": float((usd.get("rates") or {})["CNY"]),
        "EUR": float((eur.get("rates") or {})["CNY"]),
    }
