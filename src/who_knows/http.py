import json
import os
from urllib.parse import urlencode
from urllib.request import ProxyHandler, Request, build_opener


USER_AGENT = "Mozilla/5.0 (compatible; who-knows-board/0.1)"


def proxy_url() -> str | None:
    for key in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy", "WHO_KNOWS_PROXY"):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return None


def get_json(url: str, timeout: int = 20) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    last_error: Exception | None = None
    opener = _opener()
    for _ in range(2):
        try:
            with opener.open(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
    raise last_error or RuntimeError(url)


def _opener():
    proxy = proxy_url()
    if not proxy:
        return build_opener()
    return build_opener(ProxyHandler({"http": proxy, "https": proxy}))


def encode_query(url: str, params: dict) -> str:
    return url + ("&" if "?" in url else "?") + urlencode(params)
