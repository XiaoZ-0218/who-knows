from who_knows.http import proxy_url


def test_proxy_url_reads_https_proxy(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://192.168.1.100:7890")
    assert proxy_url() == "http://192.168.1.100:7890"


def test_proxy_url_is_none_without_env(monkeypatch):
    for key in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy", "WHO_KNOWS_PROXY"):
        monkeypatch.delenv(key, raising=False)
    assert proxy_url() is None
