# 架构

数据单向流动：商店 → 适配器 → 缓存 → HTTP → 页面。

```
Steam / PS Store / eShop
        │
   platform adapters
        │
  normalize + merge
        │
  catalog.json + fx
        │
   GET /api/board
        │
     static UI
```

## 模块

| 模块 | 职责 |
| --- | --- |
| `steam.py` / `playstation.py` / `nintendo.py` / `apple.py` / `epic.py` / `gog.py` | 拉各自公开目录，输出统一 `Game` |
| `normalize.py` | 人数、分类、口味分数、卡片字段 |
| `catalog.py` | 按平台合并、筛选、人民币与讨论链接 |
| `refresh.py` | 一家失败不影响另外两家的旧缓存 |
| `fx.py` | USD / EUR → CNY |
| `http.py` | JSON GET，可选 HTTP 代理 |
| `server.py` | 静态页 + `/api/board` + 后台刷新 |
| `web/` | 零构建前端，每 60 秒再读缓存 |

## 刷新

启动时拉一轮，之后按 `WHO_KNOWS_REFRESH`（默认 30 分钟）重复。写入缓存时先写临时文件再替换，避免读到半份 JSON。

## 接口

- `GET /api/board?platform=&genre=&players=&mood=`：筛选后的推荐、特价条、状态、汇率
- `GET /api/status`：各平台上次成功 / 失败
- `GET /api/refresh`：立即刷新（无鉴权，公网请在反代限制）
