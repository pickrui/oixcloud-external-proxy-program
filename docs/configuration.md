# 配置参考 / Configuration

[中文](#中文) · [English](#english)

## 中文

### 协议版本与传输选择

v0.0.43 起支持新版加密传输协议；请先更新服务端，再刷新助手订阅，原有 ECH 密钥和证书可继续使用

传输省略时使用 TCP，`auto` 允许 HTTP/3 与 TCP 竞速，`h3` 仅使用 HTTP/3；v6 要求 Identity v2、ECH 和证书验证，不接受旧身份版本或 Legacy 回退

TCP TLS 握手被对端重置或关闭时，约 300 毫秒后换新连接重试一次；重试发生在代理鉴权和业务数据发送前，计入原有拨号时限，不重放已发送的请求，证书错误、TLS 告警、超时和取消不触发此重试，HTTP/3 保持原有行为

### Homebrew 安装

通过 Homebrew tap 安装：

```bash
brew tap pickrui/oixcloud-external-proxy-program https://github.com/pickrui/oixcloud-external-proxy-program
brew install oixcloud-external-proxy-program
```

安装后也可使用命令别名 `oixcloud-helper`

使用 Homebrew 服务在后台运行菜单栏程序：

```bash
brew services start oixcloud-external-proxy-program
```

停止后台服务：

```bash
brew services stop oixcloud-external-proxy-program
```

更新并重启 Homebrew 服务：

```bash
brew update
brew upgrade oixcloud-external-proxy-program
brew services restart oixcloud-external-proxy-program
```

命令是 `brew services`（复数）；它只管理 Homebrew 服务，不能重启手动运行或启动器安装的另一份程序

v0.0.56 起，Homebrew 版本的更新与开机启动均由 Homebrew 管理，菜单栏会显示对应命令；不再通过内置更新器替换 Cellar 中的程序，也不再创建第二份独立启动项

首次改用 Homebrew 服务前，先退出手动启动的 Helper；如果曾用启动器安装常驻启动，先运行启动器并选择「卸载自动启动」，再运行 `brew services start`；已有冲突的排查步骤见 [Homebrew 重启没有生效](troubleshooting.md#homebrew-重启没有生效)

Homebrew 服务使用默认配置路径；自定义配置请使用 `oixcloud-external-proxy-program --tray --config /绝对路径/config.json` 手动启动，并在升级后退出再按原方式打开

### 手动安装

`启动 oixCloud.command` 已包含下载、签名校验、安装和启动流程，通常无需手动安装

在下载并解压的仓库目录中，通过命令行安装并临时启动：

```bash
OIX_LAUNCH_MODE=temporary zsh "./启动 oixCloud.command"
```

启动器会选择匹配系统与架构的产物并执行校验；macOS 12、13 使用 legacy 通用版，macOS 14 及以上按架构选择，macOS 11 不受支持

已安装命令时，也可临时启动菜单栏程序：

```bash
oixcloud-external-proxy-program --tray
```

### 账户配置

在菜单栏「登录…」选择 Access Token 或邮箱密码登录；窗口提供「使用 Google 登录」时，也可通过浏览器登录，Google 登录仅限已注册账号

配置文件位于：

```text
~/.config/oixcloud-external-proxy-program/config.json
```

最小配置：

```json
{ "accessToken": "你的 Access Token" }
```

获取节点时，助手会自动登记当前设备，用邮箱密码登录时，助手会保存换取的令牌，密码仅用于登录

macOS 保存配置时优先把访问令牌移入登录钥匙串，并在文件中保留 `accessTokenInKeychain` 标记；若钥匙串写入或读回失败，令牌仍保存在权限为 `0600` 的配置文件中；手写的 `accessToken` 优先使用

节点缓存密钥同样优先使用登录钥匙串，不可用时回退到权限为 `0600` 的本地密钥文件；Linux 容器继续使用配置文件保存令牌，身份密钥与节点缓存保存在持久卷

### 界面语言

默认跟随系统，菜单栏「设置 › 语言」可选中文、English 或跟随系统，选择会保存并立即生效

配置文件的 `"language": "zh"` 或 `"language": "en"` 可固定语言，`"auto"` 或省略该字段则跟随系统

环境变量 `OIXCLOUD_LANG=zh` 或 `OIXCLOUD_LANG=en` 优先于配置，适用于命令行与 Docker；修改容器环境后需重建容器

### 接入模式

| 模式 | 节点选择位置 | 本地端口 |
|---|---|---|
| `map`，默认 | Surge 策略组 | 从 `7200` 起，每个节点一个端口 |
| `single` | 菜单栏「节点」 | 默认 `7100` |

修改模式后重新点「客户端接入 › 接入 Surge」

```json
{
  "proxyMode": "map",
  "mapBasePort": 7200
}
```

固定节点端口：

```json
{
  "proxyMode": "map",
  "listeners": [
    { "name": "香港", "port": 7801, "node": "香港 01" },
    { "name": "日本", "type": "socks5", "port": 7802, "node": "日本 01" }
  ]
}
```

`type` 可选 `mixed`、`socks5`、`http`，默认 `mixed`

### 常用连接设置

| 设置 | 用途 |
|---|---|
| 接入模式 | 切换 `map` 与 `single` |
| 节点 › 节点筛选… | 按线路、地区和名称选择下发的节点，面板支持筛选时显示 |
| 客户端接入 › 精简规则 | 仅保留基础规则 |
| 允许局域网访问 | 让同一网络设备访问本机服务 |

上述设置变更后重新接入 Surge

### MITM 证书

macOS 14 及以上可在「客户端接入 › MITM 证书」启用账户证书，默认关闭；账户尚无证书时可按提示创建，然后重新接入 Surge

也可在配置中设置 `"mitm": true`；证书只用于用户模块添加的主机名，上游证书校验保持开启；仍需在 Surge 或系统中信任账户证书

官网「规则管理 › MITM 证书」提供「下载证书」；下载的是不含私钥的 `.cer` 证书，可核对页面上的 SHA-256 指纹后按设备说明安装并信任

通过局域网读取包含证书的配置须通过局域网鉴权；仅在可信设备和网络上开启此功能

### 节点筛选

Helper 默认每 24 小时在后台更新节点，也可从「节点 › 更新节点」立即刷新

程序拉取节点时只请求 `nodes=auto`，由面板决定下发哪些节点：

- 未设置筛选时节点来自「智能优选」
- 设置筛选后按筛选下发

在「节点 › 节点筛选…」中点按线路或地区，可在「不筛选 → 仅保留 → 排除」之间切换，也可填写名称包含 / 名称排除，例如 `香港|日本`、`测试|维护`

读取过筛选后，菜单项显示「节点筛选 · 智能优选」或「节点筛选 · 已自定义 · 保留 N / M 个节点」

窗口会预览保留的节点数量和列表，预览未完成、失败或自定义筛选保留 0 个节点时无法保存；「恢复默认」先清空草稿，点击保存后回到「智能优选」，当前没有节点也可清除旧筛选

保存后程序自动刷新节点和本地映射端口，重新接入 Surge 即可使用新的节点

筛选保存在账户上并跟随登录令牌：使用同一账号或同一 Access Token 登录本程序的设备共用一份筛选，包括 Docker 部署；也可在网页用户中心修改

旧版的「海外网络环境」「应急模式」「可选项参数」及配置项 `oixParams` 已移除，旧配置中的该字段会被忽略

### 保留现有 Surge 配置

不使用「接入 Surge」时，保持 Helper 为 `map` 模式，在现有配置的 `[Proxy Group]` 段中添加本地节点列表：

```ini
[Proxy Group]
香港 = select, policy-path=http://127.0.0.1:6172/list, policy-regex-filter="香港|HK", update-interval=600
Premium = select, policy-path=http://127.0.0.1:6172/list, policy-regex-filter="Premium", update-interval=600
自动选择 = url-test, policy-path=http://127.0.0.1:6172/list, url=http://cp.cloudflare.com/generate_204, interval=600, update-interval=600
```

菜单栏「客户端接入 › 复制本机节点列表 URL」可复制实际地址；修改过本机服务端口时，以复制的地址替换示例；把需要代理的原有规则指向这些策略组即可，不需要替换整份配置

`/list` 只提供节点，不会给现有配置补充直连规则；请把以下规则放在 `[Rule]` 顶部，早于可能命中的代理规则和 `FINAL`，避免 Helper 的出站连接再次进入自己的本地代理：

```ini
[Rule]
PROCESS-NAME,oixcloud-helper,DIRECT
PROCESS-NAME,oixcloud-external-proxy-program,DIRECT
```

这两条分别覆盖正式应用包和独立命令；重命名程序时须使用实际可执行文件名，也可在 Surge 请求详情中核对完整进程路径后改用路径规则；通过「接入 Surge」生成的配置已自动加入实际路径规则

「设置为系统代理」和「增强模式」可以同时开启，前者接管遵循系统代理设置的应用，后者补充接管其他连接；Helper 不要求日常关闭任一开关；上述进程规则用于 Surge 规则模式，`skip-proxy` 不能代替增强模式下的直连规则

保留原配置中已验证可用的 DNS 设置，确保 DNS 上游本身可达，不要让 DNS 上游依赖尚未连通的 Helper 节点；进程规则不参与 DNS 查询阶段的匹配，也不会把 fake IP 变成真实地址；不应靠给所有域名添加 `always-real-ip` 或跳过证书校验来处理解析故障；遇到 DNS 失败请保留诊断阶段和错误码，参见[排查指南](troubleshooting.md)

Helper 默认每 24 小时更新节点；「节点 › 更新节点」可立即刷新；示例中的 `update-interval=600` 是 Surge 每 10 分钟重新读取本地列表，`interval=600` 是自动选择组的测速周期，两者都不会把 Helper 的后台更新周期改成 10 分钟；Helper 更新节点后，在 Surge 刷新外部策略组才能立即取得新的名称和端口；不要手工推算映射端口；测速 URL 应返回预期的 HTTP 响应，`/health` 只表示本地服务状态，不能证明节点能访问外网

Surge 参数说明：[外部策略列表](https://manual.nssurge.com/policy-groups/policy-including.html)、[进程规则](https://manual.nssurge.com/rules/process.html)、[流量接管](https://manual.nssurge.com/getting-started/how-surge-works.html)、[增强模式](https://manual.nssurge.com/features/enhanced-mode.html)

### 自定义 Surge 配置

文件位置：

```text
~/.config/oixcloud-external-proxy-program/custom.conf
```

裸行和 `[Rule]` 内容插入规则段顶部，其他段追加到对应段末尾：

```ini
IP-CIDR,192.168.0.0/16,DIRECT,no-resolve

[Proxy Group]
流媒体 = select, Auto - UrlTest, 香港 01, 日本 01, Direct

[Rule]
DOMAIN-SUFFIX,netflix.com,流媒体
DOMAIN-SUFFIX,mycompany.com,DIRECT
DOMAIN-KEYWORD,tracker,REJECT
```

直接修改 Surge 内的 oixCloud 托管配置会在刷新时被覆盖

### 局域网访问

默认仅监听 `127.0.0.1`

菜单栏开启「允许局域网访问」和「局域网访问鉴权…」后，其他设备可使用：

```text
http://用户名:密码@本机IP:6172/
http://用户名:密码@本机IP:6172/list
```

也可使用命令行：

```bash
oixcloud-external-proxy-program --serve --mode map --listen 0.0.0.0:6172 --bind 0.0.0.0
```

这些 URL 使用 HTTP，鉴权凭据仅做 Base64 编码而非加密，必须由防火墙限制在可信局域网内，禁止直接暴露公网

### 命令行

```bash
oixcloud-external-proxy-program --help
oixcloud-external-proxy-program --version
oixcloud-external-proxy-program --check-config
oixcloud-external-proxy-program --diagnose-config
oixcloud-external-proxy-program --serve --listen 6172
oixcloud-external-proxy-program --serve --mode map --listen 6172
```

### 停止自动启动

Homebrew 服务请运行 `brew services stop oixcloud-external-proxy-program`

启动器或手动安装的版本可关闭菜单栏「设置 › 开机启动」；也可重新运行 `启动 oixCloud.command` 并选择「卸载自动启动」

仅针对启动器或助手创建的独立启动项，也可手动运行：

```bash
launchctl bootout "gui/$(id -u)/com.oixcloud.external-proxy-program.tray"
rm -f ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
```

## English

### Protocol version and transport selection

The newer encrypted transport protocol is supported from v0.0.43. Update the server before refreshing the helper subscription; existing ECH keys and certificates remain usable.

The default transport is TCP. `auto` races HTTP/3 with TCP, while `h3` uses HTTP/3 only. v6 requires Identity v2, ECH and certificate verification; older identity versions and legacy fallback are rejected.

If the peer resets or closes a TCP connection during the TLS handshake, Helper retries once on a new connection after about 300 ms. The retry happens before proxy authentication or application data is sent and remains within the original dial deadline. Sent requests are never replayed. Certificate errors, TLS alerts, timeouts and cancellation do not trigger this retry; HTTP/3 behavior is unchanged.

### Homebrew installation

Install via Homebrew tap:

```bash
brew tap pickrui/oixcloud-external-proxy-program https://github.com/pickrui/oixcloud-external-proxy-program
brew install oixcloud-external-proxy-program
```

You can also use the shorthand command alias `oixcloud-helper`

Run the menu bar app as a background service:

```bash
brew services start oixcloud-external-proxy-program
```

Stop the background service:

```bash
brew services stop oixcloud-external-proxy-program
```

Update and restart the Homebrew service:

```bash
brew update
brew upgrade oixcloud-external-proxy-program
brew services restart oixcloud-external-proxy-program
```

The command is `brew services` (plural). It manages the Homebrew service only, not another copy started manually or installed by the launcher

Starting with v0.0.56, Homebrew owns updates and login startup for Homebrew installations. The menu shows the appropriate commands instead of replacing the binary in the Cellar or creating a second independent login item

Before switching to the Homebrew service, quit any manually started Helper. If the launcher previously installed persistent startup, run it and choose Remove Autostart before `brew services start`. See [Homebrew restart has no effect](troubleshooting.md#homebrew-restart-has-no-effect) for existing conflicts

The Homebrew service uses the default config path. For a custom config, launch `oixcloud-external-proxy-program --tray --config /absolute/path/config.json` manually, then quit and relaunch the same way after upgrading

### Manual installation

`启动 oixCloud.command` already handles download, signature verification, installation, and startup

From the downloaded and extracted repository directory, install and start temporarily from the command line:

```bash
OIX_LAUNCH_MODE=temporary zsh "./启动 oixCloud.command"
```

The launcher selects and verifies the build for the OS and architecture: universal legacy on macOS 12/13, architecture-specific on macOS 14 or later; macOS 11 is unsupported

If the command is already installed, start the menu bar app temporarily:

```bash
oixcloud-external-proxy-program --tray
```

### Account configuration

Open "Sign in…" in the menu bar to use an Access Token or email and password. When "Sign in with Google" is available, you can also sign in through your browser; registered accounts only

The configuration file is:

```text
~/.config/oixcloud-external-proxy-program/config.json
```

Minimal configuration:

```json
{ "accessToken": "your Access Token" }
```

Helper registers this device automatically when it loads nodes. When you sign in with your email and password, Helper saves the resulting token and discards the password.

On macOS, saving the configuration prefers the login keychain and leaves an `accessTokenInKeychain` marker in the file. If writing or reading back the keychain token fails, the token stays in the `0600` configuration file. A manually supplied `accessToken` takes precedence

Node-cache keys also prefer the login keychain, falling back to a `0600` local key file when unavailable. Linux containers keep the token in the configuration file and identity keys and node cache in the persistent volume

### Interface language

The interface follows the system by default. Choose 中文, English, or Follow system under Settings > Language; the selection is saved and takes effect immediately

Set `"language": "zh"` or `"language": "en"` in the config to pin a language; use `"auto"` or omit the field to follow the system

`OIXCLOUD_LANG=zh` or `OIXCLOUD_LANG=en` overrides the config for CLI and Docker use; recreate a container after changing its environment

### Connection modes

| Mode | Pick nodes in | Local ports |
|---|---|---|
| `map`, default | Surge policy groups | One port per node from `7200` |
| `single` | Menu bar "Nodes" | `7100` by default |

Reconnect Surge after changing modes

```json
{
  "proxyMode": "map",
  "mapBasePort": 7200
}
```

Fixed node ports:

```json
{
  "proxyMode": "map",
  "listeners": [
    { "name": "Hong Kong", "port": 7801, "node": "香港 01" },
    { "name": "Japan", "type": "socks5", "port": 7802, "node": "日本 01" }
  ]
}
```

`type` can be `mixed`, `socks5`, or `http`; the default is `mixed`

### Common connection settings

| Setting | Purpose |
|---|---|
| Connection Mode | Switch between `map` and `single` |
| Nodes > Node Filter… | Choose nodes by line, region, and name when the panel supports filtering |
| Client Setup > Lean rules | Keep only basic rules |
| Allow LAN access | Serve other devices on the same network |

Reconnect Surge after changing these settings

### MITM certificate

On macOS 14+, enable Client Setup > MITM certificate to include the account's CA. It is off by default. If the account has no CA, follow the prompt to create one, then apply the profile in Surge again

The configuration equivalent is `"mitm": true`. The CA is used only for hostnames added by the user's modules, and upstream certificate verification stays enabled. The CA must still be trusted in Surge or the system

On the website, Rule Management > MITM Certificate > Download Certificate provides a `.cer` file without the private key. Compare its SHA-256 fingerprint with the page, then follow the device instructions to install and trust it

LAN clients need LAN authentication to read a profile containing the CA. Enable this only on trusted devices and networks

### Node Filter

The helper refreshes nodes every 24 hours by default. For an immediate refresh, choose Nodes > Refresh nodes

The helper requests nodes with `nodes=auto` and lets the panel decide which nodes to send:

- Without a filter, nodes come from Smart Selection
- With a filter, the panel sends the nodes the filter keeps

In "Nodes > Node Filter…", click a line or region to cycle Any → Only → Exclude, and optionally fill in Name contains / Name excludes. Node names are in Chinese, so use patterns such as `香港|日本` or `测试|维护`

Once the filter has been read, the menu item shows "Node Filter · Smart Selection" or "Node Filter · Customized · N of M nodes kept"

The window previews how many nodes are kept and which ones. Saving is unavailable while the preview is pending or failed, or when a custom filter keeps no nodes. Restore Default clears the draft; click Save to return to Smart Selection, even when no nodes are currently available

After saving, the helper refreshes its nodes and local mapped ports; reconnect Surge to use the new nodes

The filter is saved to your account and follows the sign-in token: every device signed in to this app with the same account or Access Token shares it, Docker deployments included. It can also be edited in the web user center

The older Overseas Network Environment, Emergency Mode, and Optional Parameters settings and the `oixParams` config field have been removed; existing configs keep working and the field is ignored

### Keep an existing Surge profile

Keep Helper in `map` mode and add the local node list to the `[Proxy Group]` section of your existing profile:

```ini
[Proxy Group]
Hong Kong = select, policy-path=http://127.0.0.1:6172/list, policy-regex-filter="香港|HK", update-interval=600
Premium = select, policy-path=http://127.0.0.1:6172/list, policy-regex-filter="Premium", update-interval=600
Auto = url-test, policy-path=http://127.0.0.1:6172/list, url=http://cp.cloudflare.com/generate_204, interval=600, update-interval=600
```

Client Setup > Copy local node list URL copies the actual address. Replace the example URL if you changed the local service port. Point your existing proxy rules at these groups; you do not need to replace the whole profile

`/list` supplies policies only. It does not add bypass rules to your profile. Put these at the top of `[Rule]`, before matching proxy rules and `FINAL`, so Helper's outbound connections do not loop back through its own local proxy:

```ini
[Rule]
PROCESS-NAME,oixcloud-helper,DIRECT
PROCESS-NAME,oixcloud-external-proxy-program,DIRECT
```

These cover the official app bundle and standalone command respectively. If you rename the executable, use its actual filename, or inspect the full process path in Surge's request details and use a path rule. Profiles generated by Apply in Surge already include rules for the actual executable paths

Set as System Proxy and Enhanced Mode can both be enabled. The former handles apps that follow system proxy settings; the latter captures other connections. Helper does not require either to stay disabled. The process rules above apply in Surge's rule mode; `skip-proxy` does not replace a DIRECT rule under Enhanced Mode

Keep DNS settings that already work in your profile. DNS upstreams must be reachable without depending on a Helper node that has not connected yet. Process rules do not match at the DNS-query stage or turn fake IPs into real addresses. Do not work around resolution failures by adding every domain to `always-real-ip` or disabling certificate verification. Retain the diagnostic stage and error code and see [Troubleshooting](troubleshooting.md)

Helper refreshes nodes every 24 hours by default; Nodes > Refresh nodes updates them immediately. In the example, `update-interval=600` makes Surge reread the local list every 10 minutes, while `interval=600` controls the automatic group's testing interval. Neither changes Helper's background refresh schedule. Refresh the external policy group in Surge after updating Helper's nodes to pick up new names and ports immediately; do not calculate mapped ports manually. Test URLs should return the expected HTTP response. `/health` reports local service status, not Internet connectivity through a node

Surge references: [external policies](https://manual.nssurge.com/policy-groups/policy-including.html), [process rules](https://manual.nssurge.com/rules/process.html), [traffic capture](https://manual.nssurge.com/getting-started/how-surge-works.html), and [Enhanced Mode](https://manual.nssurge.com/features/enhanced-mode.html)

### Custom Surge configuration

File location:

```text
~/.config/oixcloud-external-proxy-program/custom.conf
```

Bare lines and `[Rule]` entries are inserted at the top of the rule section; other sections are appended to their matching sections:

```ini
IP-CIDR,192.168.0.0/16,DIRECT,no-resolve

[Proxy Group]
Streaming = select, Auto - UrlTest, 香港 01, 日本 01, Direct

[Rule]
DOMAIN-SUFFIX,netflix.com,Streaming
DOMAIN-SUFFIX,mycompany.com,DIRECT
DOMAIN-KEYWORD,tracker,REJECT
```

Direct edits to the managed oixCloud profile in Surge are overwritten on refresh

### LAN access

The default bind address is `127.0.0.1`

After enabling "Allow LAN access" and "LAN authentication…", other devices can use:

```text
http://username:password@this-Mac-IP:6172/
http://username:password@this-Mac-IP:6172/list
```

Command-line alternative:

```bash
oixcloud-external-proxy-program --serve --mode map --listen 0.0.0.0:6172 --bind 0.0.0.0
```

These URLs use HTTP, so authentication credentials are Base64-encoded rather than encrypted; restrict access to a trusted LAN with a firewall and never expose it directly to the Internet

### CLI

```bash
oixcloud-external-proxy-program --help
oixcloud-external-proxy-program --version
oixcloud-external-proxy-program --check-config
oixcloud-external-proxy-program --diagnose-config
oixcloud-external-proxy-program --serve --listen 6172
oixcloud-external-proxy-program --serve --mode map --listen 6172
```

### Disable automatic startup

For a Homebrew service, run `brew services stop oixcloud-external-proxy-program`

For launcher/manual installations, turn off "Settings > Start at login", or run `启动 oixCloud.command` and choose 卸载自动启动 (Remove Autostart)

Manual alternative for the independent login item created by the launcher or helper:

```bash
launchctl bootout "gui/$(id -u)/com.oixcloud.external-proxy-program.tray"
rm -f ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
```
