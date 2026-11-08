# 排错 / Troubleshooting

[中文](#中文) · [English](#english)

## 中文

### 快速检查

先打开菜单栏「工具 › 诊断…」

诊断会检查账户、节点、监听端口和 Surge 状态

菜单顶部会显示最近操作的进度或结果；失败提示说明出错阶段、原因和处理建议

HTTP 407 表示网络代理要求鉴权，请检查系统代理凭据；HTTP 403 也可能是网络拦截，先尝试备用网络；仅在提示登录失效时重新登录

提示「配置已写入，Surge 未自动切换」时，在 Surge 手动选择 oixCloud 配置并重载

自 v0.0.61 起，本地 Surge 配置复用最近取得的远端模板，减少重复等待；手动刷新节点同时清除模板缓存，注销也会清除缓存；「接入 Surge」直接访问本机配置服务，所有重试共用 60 秒等待预算；首次生成仍可能需要等待面板和订阅响应

### 常见问题

| 现象 | 处理 |
|---|---|
| 看不到菜单栏图标 | 在本机图形会话运行 `oixcloud-external-proxy-program --tray`，并检查菜单栏是否隐藏了图标 |
| 提示未登录 | 打开「登录…」，使用 Access Token、邮箱密码或窗口提供的 Google 登录 |
| Surge 没有流量 | 确认已接入 Surge、已选择节点，并开启 `Set as System Proxy` |
| 修改设置后没有变化 | 重新点「客户端接入 › 接入 Surge」 |
| 提示已有实例 | 托盘和 `--serve` 不能同时运行，停止其中一个 |
| Docker 返回 `401` | 检查 URL 和 `config.json` 中的 `lanAuth` 是否一致 |
| Docker 状态不健康 | 运行 `docker compose logs -f`，再检查 `curl http://127.0.0.1:6172/health` |

### 手动创建的 Access Token 无法保存节点筛选

到网页「Access Token 管理」，将当前 Token 的「订阅配置」设为非主订阅地址，再返回 Helper 保存节点筛选

未绑定非主地址的 Token 不能自动创建客户端订阅；已绑定的 Token 可直接编辑对应地址，无需退出登录；若提示套餐不支持，请先在用户中心确认套餐

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

### 启动项存在，但常驻程序没有运行

新版脚本会在加载前重新启用本程序的启动项，检查菜单栏日志是否可写，并检查加载、启动命令的返回值；只有连续两次检测到同一个存活进程才提示启动成功

如果进程启动后立即退出，脚本会记录运行状态和最近退出码，而不是仅凭启动项存在就提示成功；这项检查不代表账号登录或代理连接已经就绪

重新下载当前启动脚本后复测，如仍失败，请提供以下状态输出，以及启动脚本日志和菜单栏日志中对应时间的错误行，先隐藏账号、凭据与用户名：

```bash
launchctl print "gui/$(id -u)/com.oixcloud.external-proxy-program.tray" | awk '/^[[:space:]]*(state|pid|last exit code|last terminating signal) = /'
```

如果日志显示路径不可写，检查 `~/Library/Logs/oixcloud/` 及其中 `com.oixcloud.external-proxy-program.tray.log` 的权限；不要通过 `sudo` 运行整个启动脚本

### 更新失败

更新器会校验 SHA-256、Developer ID 和版本号

安装复验失败时会自动恢复旧版本

启动器或手动安装的版本可重新运行 `启动 oixCloud.command`，或选择菜单栏「工具 › 检查更新」；Homebrew 安装请使用「工具 › 通过 Homebrew 更新…」中的命令，详见 [Homebrew 安装](configuration.md#homebrew-安装)

若 GitHub API 匿名配额耗尽或 API 暂不可用，当前启动脚本会改从官方发布页读取稳定版本，并下载同一版本的 `SHA256SUMS`；二进制仍需通过摘要、Developer ID 和版本号校验，不需要在脚本中填写 GitHub Token

发布页或校验清单也无法获取时，脚本保留原有本地缓存/已安装命令的回退行为；首次安装且没有本地程序时会明确失败

### 日志

| 日志 | 路径 |
|---|---|
| 启动器或助手启动项 | `~/Library/Logs/oixcloud/com.oixcloud.external-proxy-program.tray.log` |
| Homebrew 服务 | `$(brew --prefix)/var/log/oixcloud-external-proxy-program.log` |
| 手动命令行启动 | 当前终端的标准输出与错误输出 |
| 启动脚本 | 脚本同目录的 `oixcloud-external-proxy-program.log` |
| Surge 拉起的节点进程 | Surge 日志中搜索 `oixcloud-external-proxy-program` |
| macOS 崩溃报告 | `~/Library/Logs/DiagnosticReports/` |

反馈问题时附上：

```bash
oixcloud-external-proxy-program --version
```

不要公开 Access Token、邮箱密码或局域网鉴权密码

### macOS 连接诊断

macOS「诊断…」还会显示 IPv4 / IPv6 出口选择、面板取节点耗时和本机服务状态，并检测运行中的节点连接

单节点模式检测当前节点，逐节点模式按端口顺序抽检最多 5 个映射，最多同时检测 3 个；不需要先选中「当前节点」

报告分别记录新 DNS 查询、隧道建立（含 TLS/ECH）、首次 HTTP 往返的耗时和失败类别，再通过映射实际使用的 SOCKS5 或 HTTP 端口完成一次代理请求，区分端口未监听、代理协商失败、超时及 HTTP 错误响应

窗口会显示检查进度，完成后可拷贝报告

连接测试使用 `http://cp.cloudflare.com/generate_204`，仅完整的 HTTP 204 响应视为成功

节点检测使用独立 DNS 缓存和新的代理流，TCP 不复用旧隧道，HTTP/3 可能复用既有 QUIC 会话；不切换节点或修改 Surge 配置

本机代理测试沿用当前监听协议和鉴权设置

面板取节点可能使用缓存，报告中的耗时不等同于实时网络延迟

HTTP 抽检不覆盖 UDP、所有节点或所有网站；测试目标失败本身不能确认节点全部故障

若节点检测成功而本机代理失败，应检查监听与映射；两者成功但 Surge 仍全红，应核对 Surge 当前配置、端口和测试 URL，并提供发生时间及同期 `[Network]` 日志

### 网络与 DNS 诊断

从 v0.0.46 开始，main 和 Legacy 会将网络失败写入 `[Network]` 日志

- `stage=select`：出口选择失败，查看 `reason` 和 `route`
- `stage=bind`：网卡查询或绑定失败，查看 `operation`、`errno` 和 `route`
- `stage=query`：DNS 解析过程失败，查看 `operation`、错误码及 `elapsed_ms`

v0.0.61 起，macOS 14 及以上和 Linux 的托管 DNS 日志以 `oix DNS` 标识解析服务，`transport=dot` 或 `transport=doh` 标识传输方式：`operation=bootstrap` 为解析服务自身的地址解析失败，`operation=connect` 为 TCP 建立失败，`operation=handshake` 为 TLS 阶段失败，`operation=lookup` 为整次解析超时；TCP 失败保留 `errno`，可区分连接拒绝等原因；Legacy 的认证 DNS 继续用相同 `query` 标识关联 UDP / TCP 回退

保持出现问题时的 Surge 系统代理、增强模式与配置，复现一次失败，并附上版本、失败时间及附近完整的 `[Network]` 和 DNS 错误日志

菜单栏日志通常为 `~/Library/Logs/oixcloud/com.oixcloud.external-proxy-program.tray.log`，Homebrew 服务日志为 `$(brew --prefix)/var/log/oixcloud-external-proxy-program.log`；Docker 使用 `docker compose logs --tail=200`，由 Surge 拉起时查看对应进程日志

新增诊断省略签名查询名、凭据和实际节点地址；分享其他日志时仍需检查并遮盖 Access Token、密码和私人节点信息，保留阶段、错误码及路由状态

### 订阅响应格式异常

当前版本会自动尝试备用域名，并在每次请求结束后释放会话；格式异常本身不能证明网络被劫持

若持续失败，请提供发生时间与附近的 `[Panel] endpoint=managed_config` 日志，日志使用固定原因码、域名序号、网络路径、HTTP 状态、响应类型、字节数和耗时，不包含 token、URL、正文或节点信息

域名序号按 `apiDomains` 配置顺序，从 1 开始；0 表示整条直连或代理路径超时

### Homebrew 重启没有生效

先确认安装和服务状态：

```bash
brew list --versions oixcloud-external-proxy-program
brew services info oixcloud-external-proxy-program
launchctl list | awk '$3 == "sh.brew.oixcloud-external-proxy-program" || $3 == "homebrew.mxcl.oixcloud-external-proxy-program" || $3 == "com.oixcloud.external-proxy-program.tray"'
```

Homebrew 新版对应 `sh.brew.oixcloud-external-proxy-program`，旧版对应 `homebrew.mxcl.oixcloud-external-proxy-program`；启动器和旧版菜单栏创建的独立启动项对应 `com.oixcloud.external-proxy-program.tray`

如果运行的是独立启动项或手动副本，`brew services restart` 不会重启它；决定改用 Homebrew 后，先在 Helper 中退出，再用启动器的「卸载自动启动」移除独立启动项，最后运行：

```bash
brew update
brew upgrade oixcloud-external-proxy-program
brew services restart oixcloud-external-proxy-program
```

不要用 `sudo brew services` 运行菜单栏程序；检查 `$(brew --prefix)/var/log/oixcloud-external-proxy-program.log` 中是否仍提示已有实例或端口被占用

### 文件与文件夹权限中出现多个同名项目

同名权限项本身不能证明有多个 Helper 同时运行；先核对是否曾从 Homebrew、启动器及不同下载目录运行程序，并固定使用一种安装方式

更新不会自动清除系统已保存的权限项，不需要为此重置所有应用的隐私权限；若固定安装方式后仍不断新增，请反馈 macOS 版本、Helper 版本、安装方式及程序路径，路径中的用户名可隐藏

### 重启菜单栏程序

Homebrew 安装使用 `brew services restart oixcloud-external-proxy-program`；手动运行的程序退出后按原方式重新打开

以下命令仅适用于已加载的独立启动项：

```bash
launchctl kickstart -k "gui/$(id -u)/com.oixcloud.external-proxy-program.tray"
```

### 重新安装

启动器安装的版本可重新运行 `启动 oixCloud.command`，脚本会检查版本并按需更新或安装

Homebrew 安装请运行 `brew reinstall oixcloud-external-proxy-program`；由 Homebrew 服务运行时，完成后再运行 `brew services restart oixcloud-external-proxy-program`

macOS 12、13 使用 legacy 通用版，该版本尚未经过充分实机测试；macOS 11 不再受支持

legacy 版 v0.0.31–v0.0.52 启动时可能弹出「需要代理认证」，指向 127.0.0.1 的随机端口；该端口是 Helper 内部的直连服务，点「以后」不影响使用；v0.0.53 起不再弹出

## English

### Quick check

Open "Tools > Diagnostics…" from the menu bar first

Diagnostics checks the account, nodes, listeners, and Surge status

The top of the menu shows the latest action's progress or result; failures explain the step, cause, and suggested next action

HTTP 407 means the network proxy requires authentication: check its credentials. HTTP 403 can also come from network filtering, so try another network first; sign in again when the helper reports an expired sign-in

If the helper says the config was written but Surge did not switch, select the oixCloud profile in Surge and reload it

From v0.0.61, local Surge profiles reuse the last valid remote template to avoid repeated waits. Refreshing nodes manually or signing out clears this cache. Apply in Surge reads directly from the local config service, with one 60-second budget shared by all retries. The first profile may still need to wait for the panel and subscription

### Common issues

| Symptom | Action |
|---|---|
| No menu bar icon | Run `oixcloud-external-proxy-program --tray` in a local graphical session and check whether the menu bar hid the icon |
| Logged out | Open "Sign in…" and use an Access Token, email/password, or Google sign-in when offered |
| No traffic in Surge | Confirm the profile is connected, a node is selected, and `Set as System Proxy` is enabled |
| Settings did not change | Use "Client Setup > Apply in Surge" again |
| Another instance is running | The tray and `--serve` cannot run together; stop one of them |
| Docker returns `401` | Match the URL credentials with `lanAuth` in `config.json` |
| Docker is unhealthy | Run `docker compose logs -f`, then check `curl http://127.0.0.1:6172/health` |

### Cannot save node filters with a manually created Access Token

On the website, open Access Token Management and set the current token's Subscription Configuration to a non-primary subscription URL, then return to the Helper and save the node filter

An unbound token cannot automatically create a client subscription. A bound token can edit its subscription without signing out. If the message says your plan does not support node filters, check your plan in the user center

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

### Login item exists but the persistent process is not running

The current launcher re-enables its own service before loading it, checks that the tray log is writable, and checks load/start command results. Startup is reported only after two samples show the same live process

A process that exits immediately produces a service state and last exit code instead of a success notification. A running process does not imply that account login or upstream connectivity is ready

Download the current launcher and retry. If it still fails, include this output and the relevant error lines at that time from the launcher and tray logs, with account data, credentials, and usernames redacted:

```bash
launchctl print "gui/$(id -u)/com.oixcloud.external-proxy-program.tray" | awk '/^[[:space:]]*(state|pid|last exit code|last terminating signal) = /'
```

For an unwritable log, inspect `~/Library/Logs/oixcloud/` and its `com.oixcloud.external-proxy-program.tray.log`. Do not run the entire launcher with `sudo`

### Update failure

The updater verifies SHA-256, the Developer ID, and the exact version

A failed post-install check automatically restores the previous version

For launcher/manual installations, run `启动 oixCloud.command` again or choose "Tools > Check for updates". For Homebrew installations, follow "Tools > Update with Homebrew…"; see [Homebrew installation](configuration.md#homebrew-installation)

If the GitHub API is rate-limited or unavailable, the current launcher reads the stable tag from the official release page and downloads that tag's `SHA256SUMS`. The binary must still pass checksum, Developer ID, and exact-version verification; no GitHub token is needed in the launcher

If the release page or checksum manifest is also unavailable, the existing local-cache/installed-command fallback remains. A first installation without a local binary fails explicitly

### Logs

| Log | Path |
|---|---|
| Launcher/helper login item | `~/Library/Logs/oixcloud/com.oixcloud.external-proxy-program.tray.log` |
| Homebrew service | `$(brew --prefix)/var/log/oixcloud-external-proxy-program.log` |
| Manual CLI launch | Standard output and error in the current terminal |
| Launcher | `oixcloud-external-proxy-program.log` beside the launcher |
| Node processes started by Surge | Search for `oixcloud-external-proxy-program` in Surge logs |
| macOS crash reports | `~/Library/Logs/DiagnosticReports/` |

Include this output when reporting an issue:

```bash
oixcloud-external-proxy-program --version
```

Never publish an Access Token, email password, or LAN authentication password

### macOS connection diagnostics

Tools > Diagnostics… reports IPv4/IPv6 egress selection, node-fetch timing and local service status, and probes active node connections

Single-port mode tests the current node. Port-mapping mode samples up to five active mappings in port order, with up to three concurrent probes; no current-node selection is needed

Each sample measures a fresh DNS query, tunnel establishment including TLS/ECH, and the first HTTP round trip, then sends a request through the actual SOCKS5 or HTTP listener using its current authentication settings

The window shows progress and lets you copy the completed report. Only a complete HTTP 204 response from `http://cp.cloudflare.com/generate_204` counts as success

Probes use an independent DNS cache and fresh proxy streams. TCP does not reuse an old tunnel; HTTP/3 may reuse an existing QUIC session. The helper does not switch nodes or change the Surge profile

Node fetching may use cached results, so its timing is not a live latency measurement. HTTP samples do not test UDP, every node, or every website; one failed test target does not establish that all nodes are down

If node probes pass but the local proxy fails, inspect listeners and mappings. If both pass while Surge stays red, check its active profile, ports and test URL, and include the failure time and matching `[Network]` logs

### Network and DNS diagnostics

Starting with v0.0.46, both main and Legacy emit network failures with a `[Network]` prefix

- `stage=select`: egress selection failed; inspect `reason` and `route`
- `stage=bind`: interface lookup or binding failed; inspect `operation`, `errno`, and `route`
- `stage=query`: DNS resolution failed; inspect `operation`, the error code, and `elapsed_ms`

From v0.0.61, managed DNS logs on macOS 14+ and Linux identify the service as `oix DNS` and the transport as `dot` or `doh`. `operation=bootstrap` means the resolver's own address lookup failed, `connect` means TCP setup failed, `handshake` identifies a TLS failure, and `lookup` marks the whole lookup's deadline. TCP failures preserve `errno` to distinguish causes such as connection refusal. Legacy authentication DNS continues to share a `query` identifier across UDP/TCP fallback

Keep the Surge system proxy, enhanced mode, and configuration that reproduce the issue. Reproduce one failure and include the application, macOS, and Surge versions, the failure time, and surrounding `[Network]` and DNS error lines

The menu bar log is normally `~/Library/Logs/oixcloud/com.oixcloud.external-proxy-program.tray.log`. Homebrew services log to `$(brew --prefix)/var/log/oixcloud-external-proxy-program.log`. For Docker, run `docker compose logs --tail=200`; for processes started by Surge, check the corresponding process log

New diagnostics omit signed query names, credentials, and actual node addresses. Before sharing other logs, redact Access Tokens, passwords, and private node details while preserving stages, error codes, and route state

### Unexpected subscription response format

The helper automatically tries the backup domain and releases each request session when finished. An unexpected format alone does not establish network interception.

If failures persist, provide the time and nearby `[Panel] endpoint=managed_config` logs. They contain fixed reason codes, domain indexes, network routes, HTTP status, content type, byte counts and timing, without tokens, URLs, response bodies or node details.

Domain indexes follow the `apiDomains` configuration order, starting at 1; index 0 identifies a whole-route timeout.

### Homebrew restart has no effect

Check the installation and service state:

```bash
brew list --versions oixcloud-external-proxy-program
brew services info oixcloud-external-proxy-program
launchctl list | awk '$3 == "sh.brew.oixcloud-external-proxy-program" || $3 == "homebrew.mxcl.oixcloud-external-proxy-program" || $3 == "com.oixcloud.external-proxy-program.tray"'
```

Current Homebrew uses `sh.brew.oixcloud-external-proxy-program`, while older versions use `homebrew.mxcl.oixcloud-external-proxy-program`; the launcher and older menu bar versions use the independent `com.oixcloud.external-proxy-program.tray` job

`brew services restart` cannot restart an independent job or a manually started copy. To switch to Homebrew, quit Helper, use the launcher's Remove Autostart option to remove the independent login item, then run:

```bash
brew update
brew upgrade oixcloud-external-proxy-program
brew services restart oixcloud-external-proxy-program
```

Do not use `sudo brew services` for the menu bar app. Check `$(brew --prefix)/var/log/oixcloud-external-proxy-program.log` for another instance or an occupied port

### Duplicate entries in Files and Folders permissions

Identically named permission entries alone do not prove that multiple Helpers are running. Check whether the program has been run through Homebrew, the launcher, or different download directories, and keep one installation method

Updating does not automatically remove permissions already stored by macOS. There is no need to reset every app's privacy permissions. If new entries keep appearing with one installation method, report the macOS version, Helper version, installation method, and executable path; redact your username if needed

### Restart the menu bar app

For Homebrew, use `brew services restart oixcloud-external-proxy-program`. For a manually started copy, quit and launch it the same way again

The following command applies only to a loaded independent login item:

```bash
launchctl kickstart -k "gui/$(id -u)/com.oixcloud.external-proxy-program.tray"
```

### Reinstall

For launcher installations, run `启动 oixCloud.command` again to check the version and update or install as needed

For Homebrew installations, run `brew reinstall oixcloud-external-proxy-program`, followed by `brew services restart oixcloud-external-proxy-program` if managed as a Homebrew service

macOS 12 and 13 use the universal legacy build, which has not been fully tested on physical hardware. macOS 11 is no longer supported

Legacy v0.0.31–v0.0.52 may show "Proxy Authentication Required" for a random 127.0.0.1 port at launch. The port is Helper's internal direct service; choosing "Not Now" does not affect anything. The prompt no longer appears from v0.0.53
