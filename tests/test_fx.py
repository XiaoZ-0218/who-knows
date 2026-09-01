from who_knows.fx import to_cny


def test_to_cny_converts_usd_and_eur():
    fx = {"USD": 7.0, "EUR": 8.0}
    assert to_cny(10, "USD", fx) == 70.0
    assert to_cny(10, "EUR", fx) == 80.0


def test_to_cny_missing_price_or_rate_is_none():
    assert to_cny(None, "USD", {"USD": 7}) is None
    assert to_cny(10, "USD", {}) is None
