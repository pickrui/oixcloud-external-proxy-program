# oixCloud Surge 助手 / oixCloud helper for Surge

让 Surge 用上 oixCloud 节点：**打开菜单栏 → 弹窗登录 → 接入 Surge → 选节点**。除了你的账号，其余全部内置。

Bring oixCloud nodes into Surge: **open the menu bar app → log in in the popup → connect Surge → pick a node.** Everything but your login is built in.

## ① 安装 / Install

把下面整段粘进「终端」运行（自动识别芯片、去隔离、装好）：
Paste this whole block into Terminal (auto-detects your chip, de-quarantines, installs):

```bash
ARCH=$([ "$(uname -m)" = arm64 ] && echo arm64 || echo amd64)
curl -fL "https://dl.dler.io/oixcloud-external-proxy-program-$ARCH" -o oixcloud-external-proxy-program
chmod +x oixcloud-external-proxy-program
xattr -dr com.apple.quarantine oixcloud-external-proxy-program
sudo cp oixcloud-external-proxy-program /usr/local/bin/oixcloud-external-proxy-program
```

## ② 三步上手 / Get started in 3 steps

**1. 打开菜单栏 / Open the menu bar app** —— 在终端运行下面这行，选 **`1) 打开菜单栏登录`**：
Run this in Terminal and choose **`1) open menu bar login`**:

```bash
oixcloud-external-proxy-program
```

**2. 弹窗登录 / Log in from the popup** —— 点屏幕右上角的 ☁️ 图标，选 **登录…**，粘贴 **Access Token**；也可留空 Token，填写邮箱 + 密码。
Click the ☁️ icon at the top-right, choose **Log in…**, then paste your **Access Token**. Or leave Token empty and use email + password.

**3. 接入 Surge / Connect Surge** —— 登录成功后，在 ☁️ 菜单里点 **接入 Surge**。Surge 弹出配置后点 **安装 / Install**，再打开 **Set as System Proxy**。
After login, click **Connect Surge** in the ☁️ menu. When Surge shows the profile, click **Install**, then turn on **Set as System Proxy**.

如需避开端口冲突，先在 ☁️ 菜单里点 **本地端口…** 改端口，再点 **接入 Surge**。
If you need a different local port, click **Local Port…** in the ☁️ menu first, then click **Connect Surge**.

完成 ✅ 之后日常只需在**菜单栏**操作。
Done ✅ From now on everything happens in the **menu bar**.

## ③ 菜单栏（日常使用）/ Menu bar (daily use)

点屏幕右上角的 ☁️ 图标：
Click the ☁️ icon at the top-right of your screen:

| 菜单项 | 作用 / What it does |
|---|---|
| **登录… / Log in…** | 未登录时显示，弹窗输入 Access Token 或邮箱密码。Shown when logged out; opens the login popup. |
| **接入 Surge / Connect Surge** | 导入 Surge 配置。Imports the Surge profile. |
| **自动选择 / Auto-select** | 自动测速并切到延迟最低的节点，定期复测。Auto-pick & keep the fastest node. |
| **延迟测试 / Latency test** | 立刻给所有节点测速，延迟按 🟢绿/🟡黄/🔴红 标注。Test all nodes now, colored by speed. |
| **节点列表 / Node list** | 点一下即切换。Click any node to switch. |
| **开机启动 / Launch at login** | 开关登录时自动启动。Toggle auto-start at login. |
| **本地端口… / Local Port…** | 修改本地 SOCKS5 端口，默认 `7100`。Change the local SOCKS5 port; default is `7100`. |
| **更新节点 / 注销 / 退出** | 刷新列表 / 退出登录 / 退出。Refresh / log out / quit. |

想换服务器，点一下节点即可；懒得管就开「自动选择」。
To switch servers just click a node — or turn on **Auto-select** and forget it.

## 登录与配置 / Login & config

- **首选 Access Token**（菜单和配置文件都先用它）；也支持邮箱 + 密码。Access Token is preferred; email + password also works.
- 用邮箱 + 密码登录时，本机会换取并保存长期 token，不保存密码。When logging in with email + password, the helper saves a long-lived token, not the password.
- 账号保存在 `~/.config/oixcloud-external-proxy-program/config.json`（权限 `600`）。Saved to `config.json` (chmod 600).
- 自定义端口会保存为 `localPort`；改完端口后请重新点 **接入 Surge**，让 Surge 配置也同步端口。Custom port is saved as `localPort`; after changing it, click **Connect Surge** again so Surge uses the same port.
- 也可手动填 / or edit it by hand:

```json
{ "accessToken": "你的 Access Token" }
```
或 / or：`{ "email": "you@example.com", "password": "你的密码" }`

## 更换账号 / 注销 / Switch account / Log out

- **菜单栏**：点 **注销** → 清除本机登录与节点缓存，托盘图标会保留，可马上重新登录。Menu bar: **Log out** → clears local login and node cache; the tray stays available for logging in again.
- **终端菜单**：仍可用 `2) 终端登录` 作为备用。Terminal login remains available as a fallback.

## 排错 / Troubleshooting

- **菜单栏没图标 / no ☁️ icon**：重新运行 `oixcloud-external-proxy-program`，选 `1) 打开菜单栏登录`。Run `oixcloud-external-proxy-program` again and choose `1) open menu bar login`.
- **未登录 / logged out**：点 ☁️ 图标里的 **登录…** 即可，不需要删配置。Click **Log in…** from the ☁️ menu; no need to delete config files.
- **Surge 里连不上 / can't connect in Surge**：确认 ☁️ 图标在、已在菜单栏选了节点（或开了自动选择），Surge 里已 Set as System Proxy。Make sure the ☁️ icon is present, a node is selected (or Auto-select is on), and Surge has Set as System Proxy on.

## 许可 / License

专有软件，详见 [NOTICE](NOTICE)。Proprietary; see [NOTICE](NOTICE).

