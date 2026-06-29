# oixcloud-external-proxy-program

Surge 外部代理 Helper:登录面板、拉取并解析节点、本地起 SOCKS5 出站,供 Surge 接入。账号之外全部内置。

External-proxy helper for Surge: logs in, fetches and resolves a node, and serves a local SOCKS5 egress. Everything but your credentials is built in.

## 安装 / Install

一键安装(自动识别芯片)/ one command (auto-detects chip):

```bash
A=$([ "$(uname -m)" = arm64 ] && echo arm64 || echo amd64); curl -fsSL https://dl.dler.io/oixcloud-external-proxy-program-$A -o /tmp/oepp && sudo install -m755 /tmp/oepp /usr/local/bin/oixcloud-external-proxy-program && sudo xattr -dr com.apple.quarantine /usr/local/bin/oixcloud-external-proxy-program
```

## 配置 / Config

一条命令写好账号(推荐用 accessToken)/ one command, accessToken recommended:

```bash
mkdir -p ~/.config/oixcloud-external-proxy-program && cat > ~/.config/oixcloud-external-proxy-program/config.json <<'EOF'
{ "accessToken": "<access token>" }
EOF
chmod 600 ~/.config/oixcloud-external-proxy-program/config.json
```

也可用邮箱+密码 `{ "email": "...", "password": "..." }`;可选 `nodeName`、`localPort`、`oixParams`。
Or use email + password instead; optional: `nodeName`, `localPort`, `oixParams`.

## 运行 / Run

首次直接运行,按提示一键导入 Surge;之后由 Surge 自行拉起。
Run once and follow the prompt to import into Surge; afterwards Surge launches it.

```bash
oixcloud-external-proxy-program            # 提示导入 Surge / prompts to import
```

## Surge

`[Proxy]`:
```
Snell-ECH = external, exec = "/usr/local/bin/oixcloud-external-proxy-program", args = "--port", args = "7100", local-port = 7100, addresses = <node-ip>
```

## CLI

- `--port <n>` — SOCKS5 端口（Surge 注入）/ port (passed by Surge)
- `--config <path>` — 配置路径 / config path
- `--node <name>` — 指定节点 / pick node

## 工作流程 / Flow

登录或 token → 拉节点 → 解析 IP → 出站 → Surge 经 SOCKS5 接入；本地缓存先用后台刷。
Login or token → fetch node → resolve IP → egress → Surge via SOCKS5; cached first, refreshed in background.

## 排错 / Troubleshooting

- 启动即退 / exits immediately: 缺 config / missing config.
- 节点切换 / switch node: `--node "🇭🇰 IXP 02"` 或留空取首个 / or empty for first.

## 许可 / License

专有软件,详见 [NOTICE](NOTICE)。
Proprietary; see [NOTICE](NOTICE).

