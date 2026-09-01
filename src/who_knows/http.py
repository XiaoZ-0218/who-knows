import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


USER_AGENT = "Mozilla/5.0 (compatible; who-knows-board/0.1)"


def get_json(url: str, timeout: int = 20) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    last_error: Exception | None = None
    for _ in range(2):
        try:
            with urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
    raise last_error or RuntimeError(url)


def encode_query(url: str, params: dict) -> str:
    return url + ("&" if "?" in url else "?") + urlencode(params)
