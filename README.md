# oixcloud-external-proxy-program

Surge 外部代理 Helper:登录面板、拉取并解析节点、本地起 SOCKS5 出站,供 Surge 接入。账号之外全部内置。

External-proxy helper for Surge: logs in, fetches and resolves a node, and serves a local SOCKS5 egress. Everything but your credentials is built in.

## 安装 / Install

自动识别芯片,下载、去隔离并放入 PATH:
Auto-detect your chip, download, de-quarantine, and install:

```bash
# 自动识别芯片 / detect chip (Apple Silicon → arm64, Intel → amd64)
ARCH=$([ "$(uname -m)" = arm64 ] && echo arm64 || echo amd64)
curl -fL "https://dl.dler.io/oixcloud-external-proxy-program-$ARCH" -o oixcloud-external-proxy-program
chmod +x oixcloud-external-proxy-program
xattr -dr com.apple.quarantine oixcloud-external-proxy-program   # 解未签名拦截 / unsigned gatekeeper
sudo cp oixcloud-external-proxy-program /usr/local/bin/oixcloud-external-proxy-program
```

## 使用 / Usage

三步接入 Surge / three steps to Surge:

**1. 登入 / Log in** — 终端运行（无参数即进入交互菜单），首次按提示登入，**先粘贴 Access Token**（也可改用邮箱密码，均不回显）：
Run it in a terminal (no args → interactive menu); on first run **paste your Access Token** first (email + password also works, both hidden):

```bash
oixcloud-external-proxy-program
```

未登入时菜单只有「账号设置 / 登入」，登入后才解锁其余功能。凭据存于 `~/.config/oixcloud-external-proxy-program/config.json`（chmod 600）。
When not logged in, the menu only offers "account login"; signing in unlocks the rest. Credentials are saved to `config.json` (chmod 600).

**2. 一键接入 / Import** — 菜单选「1) 一键接入 Surge」，自动下载配置并打开 Surge。
Pick "1) one-click import" — it downloads the config and opens Surge.

**3. 在 Surge 完成 / Finish in Surge** — 点安装配置、选节点、开启系统代理（Set as System Proxy）。
In Surge: install the config, pick a node, and turn on the system proxy.

完成后日常只需在 Surge 选节点上网，helper 在后台按需出站。
After that, just pick a node in Surge — the helper egresses on demand in the background.

### 登入方式 / Logging in

**Access Token 为首要登入方式** —— 菜单与配置文件都先用它；也可改用邮箱密码。
**Access Token is the primary login method** — tried first in both the menu and the config file; email + password also works.

- **菜单 / menu**：选「账号设置 / 登入」，先粘贴 Access Token（留空才改用邮箱密码）。paste your Access Token (leave empty to use email + password instead).
- **手动编辑 / edit `config.json`**：

```json
{ "accessToken": "<access token>" }
```
或用邮箱密码 / or email + password: `{ "email": "you@example.com", "password": "your-password" }`

可选字段 / optional: `nodeName`、`localPort`、`oixParams`、`servePort`、`helperPath`。

### 菜单 / Menu（登入后 / once logged in）

1. 一键接入 Surge（推荐）/ one-click import
2. 查看节点列表 / list nodes（仅名称 / names only）
3. 账号设置 / 登入 — 切换账号 / switch account
4. 高级选项 / advanced — 见下 / see below
0. 退出 / quit

## 高级 / Advanced

### 本地订阅服务 / Serve mode

让 Surge 直接从 helper 取整份配置（Surge 看到的节点与实际出站同源一致），而不是连远程面板。菜单「4) 高级选项」可前台运行或装为开机常驻，也可手动：
Serve the whole config from the helper (so Surge's node list matches the actual egress) instead of the remote panel. Use "4) advanced", or run it manually:

```bash
oixcloud-external-proxy-program --serve --listen 6171
```

然后在 Surge 把托管配置地址指向 / then point Surge's managed-config URL at `http://127.0.0.1:6171/`。

开机常驻 / autostart (launchd):
```bash
cp launchd/com.oixcloud.external-proxy-program.serve.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.serve.plist
```

### 手动 Surge 配置 / Manual [Proxy]

不用一键导入时，可在 Surge `[Proxy]` 手动加一行：
Without one-click import, add a line under Surge `[Proxy]`:
```
Snell-ECH = external, exec = "/usr/local/bin/oixcloud-external-proxy-program", args = "--port", args = "7100", local-port = 7100
```

### 命令行参数 / CLI

- `--port <n>` — SOCKS5 端口（Surge 注入）/ port (passed by Surge)
- `--config <path>` — 配置路径 / config path
- `--node <name>` — 指定节点 / pick node
- `--serve` — 本地订阅服务 / serve mode
- `--listen <port>` — 订阅服务端口，默认 6171 / serve port (default 6171)
- *(无参数 / no args)* — 终端进入交互菜单 / interactive menu in a terminal

## 排错 / Troubleshooting

- 启动即退 / exits immediately：多为未登入或缺配置，先在菜单登入。usually not logged in — sign in via the menu first.
- 换节点 / switch node：Surge 里直接选；或命令行 `--node "🇭🇰 香港 IXP 02"`（留空取首个）。pick in Surge, or pass `--node` (empty = first).

## 许可 / License

专有软件,详见 [NOTICE](NOTICE)。
Proprietary; see [NOTICE](NOTICE).
