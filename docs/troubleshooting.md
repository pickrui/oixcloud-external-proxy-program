# 排错 / Troubleshooting

[中文](#中文) · [English](#english)

## 中文

### 快速检查

先打开菜单栏「工具 › 诊断…」

诊断会检查账户、节点、监听端口和 Surge 状态

### 常见问题

| 现象 | 处理 |
|---|---|
| 看不到菜单栏图标 | 在本机图形会话运行 `oixcloud-external-proxy-program --tray`，并检查菜单栏是否隐藏了图标 |
| 提示未登录 | 打开「账户 › 登录…」重新填写 Access Token |
| Surge 没有流量 | 确认已接入 Surge、已选择节点，并开启 `Set as System Proxy` |
| 修改设置后没有变化 | 重新点「连接设置 › 接入 Surge」 |
| 提示已有实例 | 托盘和 `--serve` 不能同时运行，停止其中一个 |
| Docker 返回 `401` | 检查 URL 和 `config.json` 中的 `lanAuth` 是否一致 |
| Docker 状态不健康 | 运行 `docker compose logs -f`，再检查 `curl http://127.0.0.1:6172/health` |

### 启动脚本没有权限

在脚本所在目录运行：

```bash
chmod +x "启动 oixCloud.command"
xattr -d com.apple.quarantine "启动 oixCloud.command" 2>/dev/null || true
```

然后重新双击脚本

### 常驻启动提示添加启动项失败

重新下载仓库中的 `启动 oixCloud.command` 再选择常驻启动，仅更新程序二进制不会更新这个脚本

新版脚本会先生成并校验临时 plist，再原子替换本程序的启动项，避免直接覆盖只读旧文件导致权限错误；写入失败时保留原配置和正在运行的服务

如果仍提示 `permission denied`，请检查目录权限并反馈以下输出，可先隐藏用户名：

```bash
ls -ldOe "$HOME/Library/LaunchAgents" "$HOME/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist"
```

不要通过 `sudo` 运行整个启动脚本，也不要递归修改 `Library` 下其他文件的权限

### 更新失败

更新器会校验 SHA-256、Developer ID 和版本号

安装复验失败时会自动恢复旧版本

可重新运行 `启动 oixCloud.command`，或在菜单栏选择「工具 › 检查更新」

### 日志

| 日志 | 路径 |
|---|---|
| 菜单栏程序 | `~/Library/Logs/oixcloud/` |
| 启动脚本 | 脚本同目录的 `oixcloud-external-proxy-program.log` |
| Surge 拉起的节点进程 | Surge 日志中搜索 `oixcloud-external-proxy-program` |
| macOS 崩溃报告 | `~/Library/Logs/DiagnosticReports/` |

反馈问题时附上：

```bash
oixcloud-external-proxy-program --version
```

不要公开 Access Token、邮箱密码或局域网鉴权密码

### 重启菜单栏程序

```bash
launchctl kickstart -k "gui/$(id -u)/com.oixcloud.external-proxy-program.tray"
```

### 重新安装

重新运行 `启动 oixCloud.command` 即可覆盖安装

macOS 11、12、13 使用 legacy 通用版，该版本尚未经过充分实机测试

## English

### Quick check

Open "Tools > Diagnostics..." from the menu bar first

Diagnostics checks the account, nodes, listeners, and Surge status

### Common issues

| Symptom | Action |
|---|---|
| No menu bar icon | Run `oixcloud-external-proxy-program --tray` in a local graphical session and check whether the menu bar hid the icon |
| Logged out | Open "Account > Log in..." and enter the Access Token again |
| No traffic in Surge | Confirm the profile is connected, a node is selected, and `Set as System Proxy` is enabled |
| Settings did not change | Use "Connection > Connect Surge" again |
| Another instance is running | The tray and `--serve` cannot run together; stop one of them |
| Docker returns `401` | Match the URL credentials with `lanAuth` in `config.json` |
| Docker is unhealthy | Run `docker compose logs -f`, then check `curl http://127.0.0.1:6172/health` |

### Launcher permission error

Run this in the directory containing the launcher:

```bash
chmod +x "启动 oixCloud.command"
xattr -d com.apple.quarantine "启动 oixCloud.command" 2>/dev/null || true
```

Then double-click the launcher again

### Persistent startup cannot add the login item

Download the current `启动 oixCloud.command` from this repository and select persistent startup again; updating the binary alone does not update this launcher

The launcher validates a temporary plist and atomically replaces its own launch agent, including a read-only old plist. A failed write preserves the existing configuration and running service

If `permission denied` remains, inspect the directory permissions and include this output in the issue, with your username redacted if preferred:

```bash
ls -ldOe "$HOME/Library/LaunchAgents" "$HOME/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist"
```

Do not run the entire launcher with `sudo` or recursively change permissions on unrelated files in `Library`

### Update failure

The updater verifies SHA-256, the Developer ID, and the exact version

A failed post-install check automatically restores the previous version

Run `启动 oixCloud.command` again or choose "Tools > Check for Updates" from the menu bar

### Logs

| Log | Path |
|---|---|
| Menu bar app | `~/Library/Logs/oixcloud/` |
| Launcher | `oixcloud-external-proxy-program.log` beside the launcher |
| Node processes started by Surge | Search for `oixcloud-external-proxy-program` in Surge logs |
| macOS crash reports | `~/Library/Logs/DiagnosticReports/` |

Include this output when reporting an issue:

```bash
oixcloud-external-proxy-program --version
```

Never publish an Access Token, email password, or LAN authentication password

### Restart the menu bar app

```bash
launchctl kickstart -k "gui/$(id -u)/com.oixcloud.external-proxy-program.tray"
```

### Reinstall

Run `启动 oixCloud.command` again to replace the current installation

macOS 11, 12, and 13 use the universal legacy build, which has not been fully tested on physical hardware
