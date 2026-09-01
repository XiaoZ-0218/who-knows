from who_knows.fx import to_cny


def test_to_cny_converts_usd_and_eur():
    fx = {"USD": 7.0, "EUR": 8.0}
    assert to_cny(10, "USD", fx) == 70.0
    assert to_cny(10, "EUR", fx) == 80.0


def test_to_cny_keeps_cny_prices():
    assert to_cny(30, "CNY", {"USD": 7}) == 30.0
