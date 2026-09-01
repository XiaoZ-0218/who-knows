# 自托管

Who Knows 是一个无构建步骤的小服务：Python 定时拉三家商店，把结果写进本地 JSON，再提供静态页和只读 API。

## Docker

```bash
docker compose up -d --build
```

默认把 `8765` 映射到主机。数据在名为 `board-data` 的 volume 里。

环境变量可写在仓库根目录的 `.env`（不要提交）：

```
WHO_KNOWS_PORT=8765
WHO_KNOWS_REFRESH=1800
HTTP_PROXY=
HTTPS_PROXY=
```

若运行环境访问 Steam 不稳定，给 `HTTP_PROXY` / `HTTPS_PROXY` 填 HTTP 代理。PlayStation 与 Nintendo 通常可以直连。

更新镜像或源码后：

```bash
docker compose up -d --build
```

`deploy/update.sh` 会在 git 的 `origin/main` 有新提交时执行上面这条命令，适合自己做拉取部署。按你的调度系统每 10–30 分钟跑一次即可。

## 本机（不用 Docker）

```bash
uv sync
uv run python serve.py
```

## 反代

前面可以接 Caddy、nginx 或 Cloudflare Tunnel。指到服务监听的端口（默认 `8765`）。服务只提供看板和 JSON，没有账号系统。

`GET /api/refresh` 会立刻向商店拉一轮。若看板暴露在公网，请在反代层限制该路径，或关掉它。

## 端口被占用

把 `WHO_KNOWS_PORT` 和 compose 的宿主机端口一起改掉。容器内仍监听 `WHO_KNOWS_PORT`。
