# oixCloud Surge 助手 / oixCloud helper for Surge

菜单栏 App，把 oixCloud 节点接入 Surge。登录、接入 Surge、切换节点都在菜单栏 ☁️ 完成；除账号外全部内置。

A menu bar app that brings oixCloud nodes into Surge. Log in, connect Surge, and switch nodes from the ☁️ menu; everything but your login is built in.

**[中文](#中文) · [English](#english)**

---

## 中文

### 第 1 步 · 安装

在终端运行（自动识别芯片架构）：

```bash
ARCH=$([ "$(uname -m)" = arm64 ] && echo arm64 || echo amd64)
curl -fL "https://dl.dler.io/oixcloud-external-proxy-program-$ARCH" -o oixcloud-external-proxy-program
chmod +x oixcloud-external-proxy-program
xattr -dr com.apple.quarantine oixcloud-external-proxy-program
sudo cp oixcloud-external-proxy-program /usr/local/bin/oixcloud-external-proxy-program.new
sudo mv -f /usr/local/bin/oixcloud-external-proxy-program.new /usr/local/bin/oixcloud-external-proxy-program
```

> 更新时不要直接 `cp` 覆盖 `/usr/local/bin/oixcloud-external-proxy-program`：正在运行的旧进程会因代码签名失效被系统终止（Surge 会提示客户端已终止）。按上面先 `cp` 到临时名再 `mv` 原子替换。

也可以双击仓库里的 `启动 oixCloud.command`：脚本会检查最新发布版本、校验 Developer ID 签名后更新 `/usr/local/bin/oixcloud-external-proxy-program`，再让你选择临时启动、常驻启动，或卸载自动启动。

### 第 2 步 · 启动菜单栏 App

临时运行（关闭终端即退出）：

```bash
oixcloud-external-proxy-program --tray
```

常驻并开机自启（推荐，装为 LaunchAgent）：

```bash
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.oixcloud.external-proxy-program.tray</string>
<key>ProgramArguments</key><array>
<string>/usr/local/bin/oixcloud-external-proxy-program</string><string>--tray</string></array>
<key>RunAtLoad</key><true/><key>KeepAlive</key><true/></dict></plist>
EOF
# 若之前加载过，先卸载再加载（首次可忽略这行报错）
launchctl bootout   "gui/$(id -u)/com.oixcloud.external-proxy-program.tray" 2>/dev/null
launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
```

菜单栏出现 ☁️ 图标即成功；由 launchd 托管，关终端、注销重登都不受影响。

> 更新二进制或改了 plist 后，重启托盘到新版本：`launchctl kickstart -k "gui/$(id -u)/com.oixcloud.external-proxy-program.tray"`。

### 第 3 步 · 在 ☁️ 菜单里完成

点屏幕右上角的 ☁️ 图标，依次：

1. **登录** —— 选「登录…」，粘贴 **Access Token**（推荐）；也可留空 Token，改填邮箱 + 密码。
2. **接入 Surge** —— 选「接入 Surge」；**首次**会打开 Surge，点「安装」确认后再开启「Set as System Proxy」。装好后换节点是透明的，无需再次接入。

完成 ✅ 日常在 ☁️ 菜单选节点，或开「自动选择」。

### ☁️ 菜单一览

| 菜单项 | 作用 |
|---|---|
| 登录… | 未登录时显示，弹窗填 Access Token 或邮箱 + 密码 |
| 自动选择 | 自动测速并切到延迟最低的节点，定期复测 |
| 延迟测试 | 立刻给所有节点测速，延迟按 🟢 绿 / 🟡 黄 / 🔴 红 标注 |
| 节点列表 | 点一下即切换 |
| SOCKS5 127.0.0.1:7100 | 当前本地出站地址（供 Surge 连接）|
| 开机启动 | 开关登录时自动启动 ☁️ |
| 本地端口… | 修改本地 SOCKS5 端口，默认 `7100` |
| 接入模式… | 在「现有单端口」和「本地多端口映射」之间切换 |
| 接入 Surge | 把配置装进 Surge（首次需在 Surge 点「安装」确认；之后自动同步）|
| 更新节点 | 重新拉取节点列表 |
| 注销 | 退出登录并清除本机缓存（☁️ 保留，可立即重新登录）|
| 退出 | 退出 ☁️ App |

> 改「本地端口」或「接入模式」后，重新点一次「接入 Surge」同步。
> 「本地多端口映射」模式下节点在 Surge 内选择，菜单不显示「自动选择 / 延迟测试 / 节点列表」。

### 登录与配置

- **首选 Access Token**（菜单和配置文件都优先用它），也支持邮箱 + 密码。
- 用邮箱 + 密码登录时，本机会换取并保存长期 token，**不保存密码**。
- 账号保存在 `~/.config/oixcloud-external-proxy-program/config.json`（权限 `600`）。
- 也可手动填写该文件：

```json
{ "accessToken": "你的 Access Token" }
```

或改用邮箱密码：`{ "email": "you@example.com", "password": "你的密码" }`

可选模式配置（默认单端口）：

```json
{
	"proxyMode": "single",
	"mapBasePort": 7200
}
```

- `proxyMode = "single"`：现有方式（单本地端口，默认 `7100`）。
- `proxyMode = "map"`：本地多端口映射（每个节点一个本地端口，起始端口由 `mapBasePort` 控制，每个端口同时支持 SOCKS5 与 HTTP），Surge 配置保留原有规则，只把节点替换为本地端口。

`map` 模式还可用 `listeners` 声明固定端口，把指定节点绑定到指定本地端口（端口不随节点增删漂移）；不填则自动分配：

```json
{
	"proxyMode": "map",
	"listeners": [
		{ "name": "香港", "port": 7801, "node": "香港 01" },
		{ "name": "日本", "type": "socks5", "port": 7802, "node": "日本 01" }
	]
}
```

- `type`：`mixed`（默认，同端口 SOCKS5 + HTTP）/ `socks5` / `http`；`node`：要绑定的节点名；`listen`：默认 `127.0.0.1`。

### 停止 / 卸载

停止并取消开机自启：

```bash
launchctl bootout "gui/$(id -u)/com.oixcloud.external-proxy-program.tray"
rm ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
```

仅临时退出：点 ☁️ 菜单「退出」。

### 排错

- **查日志**：托盘运行日志在 `~/Library/Logs/oixcloud/`；安装脚本日志在脚本同目录的 `oixcloud-external-proxy-program.log`；由 Surge 拉起的节点进程日志在 Surge 自己的日志里（搜 `oixcloud-external-proxy-program`）；若怀疑闪退，看 `~/Library/Logs/DiagnosticReports/` 下 `oixcloud-*` 开头的崩溃报告。反馈问题时请附 `oixcloud-external-proxy-program --version` 的输出。
- **看不到 ☁️ 图标**：重新运行 `oixcloud-external-proxy-program --tray`；确认是在本机图形界面（非 SSH／远程会话）下运行；刘海屏若菜单栏图标太多，☁️ 可能被折叠，退掉一些其他菜单栏图标或用菜单栏管理工具查看。另注意：同一时间只允许一个客户端（托盘或 `--serve`）运行，后启动的会自动退出并在日志里说明。
- **提示未登录**：点 ☁️ 里的「登录…」即可，无需删配置。
- **Surge 里连不上**：确认 ☁️ 在、已选好节点（或开了「自动选择」），且 Surge 已开「Set as System Proxy」。
- **双击 `启动 oixCloud.command` 提示没有正确的访问权限**：这是 macOS 在运行脚本前发现文件没有执行权限，脚本本身还没启动，无法在脚本内部自动修复。请在脚本所在目录打开终端后运行：

  ```bash
  chmod +x "启动 oixCloud.command"
  xattr -d com.apple.quarantine "启动 oixCloud.command" 2>/dev/null || true
  ```

  然后再双击脚本。
- **完全打不开／闪退**：重新执行第 1 步（重新下载覆盖），并确认已运行 `xattr -dr com.apple.quarantine`。

### 进阶（可选，命令行）

不带参数运行会进入终端文字菜单，涵盖下列能力；日常用不到：

```bash
oixcloud-external-proxy-program                          # 终端文字菜单（一键接入 / 菜单栏切换器 / 节点列表 / 高级选项）
oixcloud-external-proxy-program --serve --listen 6171    # 本地订阅服务：Surge 从 http://127.0.0.1:6171/ 取整份配置
oixcloud-external-proxy-program --serve --mode map --listen 6171
														 # 多端口映射模式（Surge: /map, Clash provider: /clash）
oixcloud-external-proxy-program --help                  # 查看全部参数
oixcloud-external-proxy-program --version               # 输出版本指纹
```

### 局域网共享（可选）

默认只监听 `127.0.0.1`。要让同网络的其他设备也能访问托管配置和代理，把监听地址设为 `0.0.0.0`：

```bash
# 配置服务器与各代理端口都监听 0.0.0.0；其他设备用本机局域网 IP 访问
oixcloud-external-proxy-program --serve --mode map --listen 0.0.0.0:6171 --bind 0.0.0.0
```

- `--listen [host:]port`：本地订阅服务器的监听地址（默认 `127.0.0.1`）。
- `--bind <host>`：各代理端口的监听地址；也可用配置项 `"listenAddress"`，`map` 模式下 `listeners` 内每条还能单独设 `listen`。
- **生成配置里的节点 server 跟随请求来源地址**：设备从 `http://<本机IP>:6171/` 拉取配置时，Surge/Clash 里的节点会自动指向 `<本机IP>` 而非 `127.0.0.1`（本机访问仍为 `127.0.0.1`）。
- ⚠️ 监听 `0.0.0.0` 的端口**没有鉴权**，请仅在可信网络中使用。

### 许可

专有软件，详见 [NOTICE](NOTICE)。

---

## English

### Step 1 · Install

Run in Terminal (auto-detects your chip architecture):

```bash
ARCH=$([ "$(uname -m)" = arm64 ] && echo arm64 || echo amd64)
curl -fL "https://dl.dler.io/oixcloud-external-proxy-program-$ARCH" -o oixcloud-external-proxy-program
chmod +x oixcloud-external-proxy-program
xattr -dr com.apple.quarantine oixcloud-external-proxy-program
sudo cp oixcloud-external-proxy-program /usr/local/bin/oixcloud-external-proxy-program.new
sudo mv -f /usr/local/bin/oixcloud-external-proxy-program.new /usr/local/bin/oixcloud-external-proxy-program
```

> When updating, do not `cp` directly over `/usr/local/bin/oixcloud-external-proxy-program`: overwriting the binary in place invalidates the code signature of already-running processes and the system kills them (Surge reports the client terminated). Use the `cp` + `mv` atomic replace above.

You can also double-click `启动 oixCloud.command` from this repo: it checks the latest release, verifies the Developer ID signature, updates `/usr/local/bin/oixcloud-external-proxy-program`, then lets you choose temporary startup, persistent startup, or removing autostart.

### Step 2 · Start the menu bar app

Temporary (quits when the terminal closes):

```bash
oixcloud-external-proxy-program --tray
```

Persistent + start at login (recommended — a LaunchAgent):

```bash
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.oixcloud.external-proxy-program.tray</string>
<key>ProgramArguments</key><array>
<string>/usr/local/bin/oixcloud-external-proxy-program</string><string>--tray</string></array>
<key>RunAtLoad</key><true/><key>KeepAlive</key><true/></dict></plist>
EOF
# If it was loaded before, unload first (safe to ignore this error on first run)
launchctl bootout   "gui/$(id -u)/com.oixcloud.external-proxy-program.tray" 2>/dev/null
launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
```

The ☁️ icon appears in the menu bar. Managed by launchd, so closing the terminal or logging out/in won't stop it.

> After updating the binary or editing the plist, restart the tray to the new version: `launchctl kickstart -k "gui/$(id -u)/com.oixcloud.external-proxy-program.tray"`.

### Step 3 · Finish in the ☁️ menu

Click the ☁️ icon at the top-right, then:

1. **Log in** — choose "Log in…", paste your **Access Token** (recommended); or leave it empty and use email + password.
2. **Connect Surge** — choose "Connect Surge"; the **first time**, Surge opens so you can click "Install" to confirm, then turn on "Set as System Proxy". After that, switching nodes is transparent — no need to reconnect.

Done ✅ Day to day, pick a node in the ☁️ menu, or enable "Auto-select".

### The ☁️ menu at a glance

| Item | What it does |
|---|---|
| Log in… | Shown when logged out; popup for an Access Token or email + password |
| Auto-select | Speed-tests and switches to the fastest node, re-checking periodically |
| Latency test | Tests every node now; latency shown 🟢 green / 🟡 yellow / 🔴 red |
| Node list | Click a node to switch |
| SOCKS5 127.0.0.1:7100 | The local egress address Surge connects to |
| Launch at login | Toggle auto-start of ☁️ at login |
| Local Port… | Change the local SOCKS5 port (default `7100`) |
| Connection Mode… | Switch between "Single Port" and "Local Multi-Port Mapping" |
| Connect Surge | Installs the profile into Surge (first time: click "Install" to confirm; then it auto-syncs) |
| Refresh | Re-fetch the node list |
| Log out | Sign out and clear the local cache (☁️ stays; log in again anytime) |
| Quit | Quit the ☁️ app |

> After changing "Local Port" or "Connection Mode", click "Connect Surge" again.
> In "Local Multi-Port Mapping" mode you pick nodes in Surge, so the menu hides "Auto-select / Latency test / node list".

### Login & config

- **Access Token is preferred** (used first by both the menu and the config file); email + password also works.
- When you log in with email + password, the helper exchanges and stores a long-lived token, **not the password**.
- Credentials are saved to `~/.config/oixcloud-external-proxy-program/config.json` (mode `600`).
- You can also edit that file by hand:

```json
{ "accessToken": "your Access Token" }
```

Or use email + password: `{ "email": "you@example.com", "password": "your password" }`

Optional mode config (single-port by default):

```json
{
	"proxyMode": "single",
	"mapBasePort": 7200
}
```

- `proxyMode = "single"`: existing one-port behavior (`7100` by default).
- `proxyMode = "map"`: local multi-port mapping (one local port per node, starting at `mapBasePort`, each port serving both SOCKS5 and HTTP); the Surge profile keeps the original rules and swaps proxies to local ports.

In `map` mode you can also declare fixed ports with `listeners`, binding a named node to a specific local port (ports don't drift as nodes are added or removed); omit it to auto-assign:

```json
{
	"proxyMode": "map",
	"listeners": [
		{ "name": "hk", "port": 7801, "node": "香港 01" },
		{ "name": "jp", "type": "socks5", "port": 7802, "node": "日本 01" }
	]
}
```

- `type`: `mixed` (default, SOCKS5 + HTTP on one port) / `socks5` / `http`; `node`: the node name to bind; `listen`: `127.0.0.1` by default.

### Stop / uninstall

Stop and disable autostart:

```bash
launchctl bootout "gui/$(id -u)/com.oixcloud.external-proxy-program.tray"
rm ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
```

Just quit the current instance: "Quit" in the ☁️ menu.

### Troubleshooting

- **Check the logs**: tray runtime logs live in `~/Library/Logs/oixcloud/` (timestamped); the installer script logs next to itself as `oixcloud-external-proxy-program.log`; per-node processes spawned by Surge log into Surge's own log (search `oixcloud-external-proxy-program`); for suspected crashes check `~/Library/Logs/DiagnosticReports/` for reports starting with `oixcloud-`. Please include the output of `oixcloud-external-proxy-program --version` when reporting issues.
- **No ☁️ icon**: run `oixcloud-external-proxy-program --tray` again; make sure you're in a local graphical session (not SSH/remote); on notch Macs a crowded menu bar can hide the icon — quit some other menu bar apps or use a menu bar manager. Also note: only one client (tray or `--serve`) may run at a time — a second one exits immediately and says so in the log.
- **Shown as logged out**: click "Log in…" from the ☁️ menu — no need to delete any files.
- **Can't connect in Surge**: make sure ☁️ is present, a node is selected (or Auto-select is on), and Surge has "Set as System Proxy" on.
- **Double-clicking `启动 oixCloud.command` says you do not have the correct access permissions**: macOS checks the executable bit before it starts the script, so the script has not run yet and cannot fix its own permissions. Open Terminal in the folder that contains the script and run:

  ```bash
  chmod +x "启动 oixCloud.command"
  xattr -d com.apple.quarantine "启动 oixCloud.command" 2>/dev/null || true
  ```

  Then double-click the script again.
- **Nothing happens / it crashes on launch**: redo Step 1 (re-download over the old file) and make sure you ran `xattr -dr com.apple.quarantine`.

### Advanced (optional, CLI)

Running with no arguments opens a text menu that covers everything below; you won't normally need it:

```bash
oixcloud-external-proxy-program                          # text menu (one-click import / menu bar switcher / node list / advanced)
oixcloud-external-proxy-program --serve --listen 6171    # serve mode: Surge pulls the whole profile from http://127.0.0.1:6171/
oixcloud-external-proxy-program --serve --mode map --listen 6171
														 # mapped mode (Surge: /map, Clash provider: /clash)
oixcloud-external-proxy-program --help                  # show all options
oixcloud-external-proxy-program --version               # print version fingerprint
```

### LAN sharing (optional)

By default only `127.0.0.1` is bound. To let other devices on your network reach the managed config and the proxies, bind `0.0.0.0`:

```bash
# Bind the config server and every proxy port to 0.0.0.0; other devices use this Mac's LAN IP
oixcloud-external-proxy-program --serve --mode map --listen 0.0.0.0:6171 --bind 0.0.0.0
```

- `--listen [host:]port`: bind address of the local subscription server (default `127.0.0.1`).
- `--bind <host>`: bind address for the proxy ports; you can also set `"listenAddress"` in the config, and in `map` mode each entry in `listeners` can set its own `listen`.
- **Node servers follow the request address**: when a device fetches the config from `http://<this-Mac-IP>:6171/`, the nodes in Surge/Clash automatically point at `<this-Mac-IP>` instead of `127.0.0.1` (local access stays `127.0.0.1`).
- ⚠️ A port bound to `0.0.0.0` has **no authentication** — use it only on trusted networks.

### License

Proprietary software; see [NOTICE](NOTICE).
