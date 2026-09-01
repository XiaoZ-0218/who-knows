# who knows

今晚玩什么：一块会自己刷新的游戏推荐看板。

按口味（热门 / 新发 / 冷门好活）、平台（Steam / PS5 / Switch）、人数（单人 / 双人 / 多人）和分类筛。特价是同一批货里的折扣轨道，不是另一套数据。

## 本机

```
uv sync
uv run python serve.py
```

打开 http://127.0.0.1:8765

后端大约 30 分钟拉一次商店；页面每 60 秒再读一次缓存。数据写在 `data/catalog.json`。

```
uv run pytest
```

## NAS

```
docker compose up -d --build
```

环境变量：

- `WHO_KNOWS_PORT` 默认 `8765`
- `WHO_KNOWS_DATA` 默认 `data/catalog.json`
- `WHO_KNOWS_REFRESH` 秒，默认 `1800`

Steam 走官方 featured + appdetails。PS5 和 Switch 走商店公开目录接口，接口改版时只动对应适配器；一家失败会留下上一份缓存。
