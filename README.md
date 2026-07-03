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
sudo cp oixcloud-external-proxy-program /usr/local/bin/oixcloud-external-proxy-program
```

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
launchctl load -w ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
```

菜单栏出现 ☁️ 图标即成功；由 launchd 托管，关终端、注销重登都不受影响。

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
| 接入 Surge | 把配置装进 Surge（首次需在 Surge 点「安装」确认；之后自动同步）|
| 更新节点 | 重新拉取节点列表 |
| 注销 | 退出登录并清除本机缓存（☁️ 保留，可立即重新登录）|
| 退出 | 退出 ☁️ App |

> 改「本地端口」后重新点「接入 Surge」同步。

### 登录与配置

- **首选 Access Token**（菜单和配置文件都优先用它），也支持邮箱 + 密码。
- 用邮箱 + 密码登录时，本机会换取并保存长期 token，**不保存密码**。
- 账号保存在 `~/.config/oixcloud-external-proxy-program/config.json`（权限 `600`）。
- 也可手动填写该文件：

```json
{ "accessToken": "你的 Access Token" }
```

或改用邮箱密码：`{ "email": "you@example.com", "password": "你的密码" }`

### 停止 / 卸载

停止并取消开机自启：

```bash
launchctl unload -w ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
rm ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
```

仅临时退出：点 ☁️ 菜单「退出」。

### 排错

- **看不到 ☁️ 图标**：重新运行 `oixcloud-external-proxy-program --tray`；确认是在本机图形界面（非 SSH／远程会话）下运行；刘海屏若菜单栏图标太多，☁️ 可能被折叠，退掉一些其他菜单栏图标或用菜单栏管理工具查看。
- **提示未登录**：点 ☁️ 里的「登录…」即可，无需删配置。
- **Surge 里连不上**：确认 ☁️ 在、已选好节点（或开了「自动选择」），且 Surge 已开「Set as System Proxy」。
- **完全打不开／闪退**：重新执行第 1 步（重新下载覆盖），并确认已运行 `xattr -dr com.apple.quarantine`。

### 进阶（可选，命令行）

不带参数运行会进入终端文字菜单，涵盖下列能力；日常用不到：

```bash
oixcloud-external-proxy-program                          # 终端文字菜单（一键接入 / 菜单栏切换器 / 节点列表 / 高级选项）
oixcloud-external-proxy-program --serve --listen 6171    # 本地订阅服务：Surge 从 http://127.0.0.1:6171/ 取整份配置
```

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
sudo cp oixcloud-external-proxy-program /usr/local/bin/oixcloud-external-proxy-program
```

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
launchctl load -w ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
```

The ☁️ icon appears in the menu bar. Managed by launchd, so closing the terminal or logging out/in won't stop it.

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
| Connect Surge | Installs the profile into Surge (first time: click "Install" to confirm; then it auto-syncs) |
| Refresh | Re-fetch the node list |
| Log out | Sign out and clear the local cache (☁️ stays; log in again anytime) |
| Quit | Quit the ☁️ app |

> After changing "Local Port", click "Connect Surge" again so Surge uses the new port.

### Login & config

- **Access Token is preferred** (used first by both the menu and the config file); email + password also works.
- When you log in with email + password, the helper exchanges and stores a long-lived token, **not the password**.
- Credentials are saved to `~/.config/oixcloud-external-proxy-program/config.json` (mode `600`).
- You can also edit that file by hand:

```json
{ "accessToken": "your Access Token" }
```

Or use email + password: `{ "email": "you@example.com", "password": "your password" }`

### Stop / uninstall

Stop and disable autostart:

```bash
launchctl unload -w ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
rm ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
```

Just quit the current instance: "Quit" in the ☁️ menu.

### Troubleshooting

- **No ☁️ icon**: run `oixcloud-external-proxy-program --tray` again; make sure you're in a local graphical session (not SSH/remote); on notch Macs a crowded menu bar can hide the icon — quit some other menu bar apps or use a menu bar manager.
- **Shown as logged out**: click "Log in…" from the ☁️ menu — no need to delete any files.
- **Can't connect in Surge**: make sure ☁️ is present, a node is selected (or Auto-select is on), and Surge has "Set as System Proxy" on.
- **Nothing happens / it crashes on launch**: redo Step 1 (re-download over the old file) and make sure you ran `xattr -dr com.apple.quarantine`.

### Advanced (optional, CLI)

Running with no arguments opens a text menu that covers everything below; you won't normally need it:

```bash
oixcloud-external-proxy-program                          # text menu (one-click import / menu bar switcher / node list / advanced)
oixcloud-external-proxy-program --serve --listen 6171    # serve mode: Surge pulls the whole profile from http://127.0.0.1:6171/
```

### License

Proprietary software; see [NOTICE](NOTICE).

