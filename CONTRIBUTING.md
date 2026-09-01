# 贡献

谢谢你愿意改这个看板。

## 开发

```bash
uv sync
uv run python serve.py
uv run pytest
```

从 `main` 拉一条 `feature/`、`fix/` 或 `docs/` 分支。提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/)：`feat:`、`fix:`、`docs:`、`chore:` 等。

## 范围

- 适配器（`src/who_knows/steam.py`、`playstation.py`、`nintendo.py`）各自负责一家商店，不要把解析逻辑揉进 HTTP 层。
- 筛选、汇率、讨论链接放在服务端，前端只渲染。
- 不要在文档或示例里写入私人主机名、内网 IP、代理地址或隧道令牌。

## 测试

新行为先补失败测试，再写实现。`uv run pytest` 需要全绿。

商店接口会变。解析函数用夹具测试；不要把联网拉取写进默认单测。
