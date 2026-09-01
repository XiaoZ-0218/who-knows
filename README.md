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

仓库公开后，NAS 克隆 `main`，用 Docker 跑，cloudflared 把 `game.zxclaw.top` 指到本机 `8765`。

```
sudo apt-get install -y git
sudo mkdir -p /volume1/docker/who-knows
sudo chown "$USER":"$USER" /volume1/docker/who-knows
git clone https://github.com/XiaoZ-0218/who-knows.git /volume1/docker/who-knows
cd /volume1/docker/who-knows
docker compose up -d --build
```

每 10 分钟对照 `origin/main`，有新提交才重建：

```
crontab -e
```

```
*/10 * * * * /volume1/docker/who-knows/deploy/update.sh >> /volume1/docker/who-knows/update.log 2>&1
```

现有 NAS 上的 `cloudflared` 是 host 网络。看板映射在 **18765**（8765 被 UGOS 占用）。在 Cloudflare Zero Trust 里给同一条 tunnel 加 Public Hostname：

- 域名：`game.zxclaw.top`
- 服务：`http://127.0.0.1:18765`

NAS 拉 Steam 需要走局域网代理。在仓库目录放一个不进 git 的 `.env`：

```
HTTP_PROXY=http://192.168.1.100:7890
HTTPS_PROXY=http://192.168.1.100:7890
```

环境变量：

- `WHO_KNOWS_PORT` 默认 `8765`
- `WHO_KNOWS_DATA` 默认 `data/catalog.json`
- `WHO_KNOWS_REFRESH` 秒，默认 `1800`

Steam 走官方 featured + appdetails。PS5 和 Switch 走商店公开目录接口，接口改版时只动对应适配器；一家失败会留下上一份缓存。
