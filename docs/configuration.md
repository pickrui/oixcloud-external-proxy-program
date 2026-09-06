# 配置参考 / Configuration

[中文](#中文) · [English](#english)

## 中文

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

### 手动安装

`启动 oixCloud.command` 已包含下载、签名校验、安装和启动流程，通常无需手动安装

需要纯命令行安装时运行：

```bash
MAJOR=$(sw_vers -productVersion | cut -d. -f1)
if [ "$MAJOR" -ge 14 ]; then
  ASSET=$([ "$(uname -m)" = arm64 ] && echo arm64 || echo amd64)
else
  ASSET=legacy
fi
curl -fL "https://dl.dler.io/oixcloud-external-proxy-program-$ASSET" -o oixcloud-external-proxy-program
chmod +x oixcloud-external-proxy-program
xattr -dr com.apple.quarantine oixcloud-external-proxy-program
sudo cp oixcloud-external-proxy-program /usr/local/bin/oixcloud-external-proxy-program.new
sudo mv -f /usr/local/bin/oixcloud-external-proxy-program.new /usr/local/bin/oixcloud-external-proxy-program
```

临时启动菜单栏程序：

```bash
oixcloud-external-proxy-program --tray
```

### 账户配置

推荐在菜单栏「账户 › 登录…」填写 Access Token

配置文件位于：

```text
~/.config/oixcloud-external-proxy-program/config.json
```

最小配置：

```json
{ "accessToken": "你的 Access Token" }
```

用邮箱密码登录时，助手换取并保存 Token，不保存密码

### 接入模式

| 模式 | 节点选择位置 | 本地端口 |
|---|---|---|
| `map`，默认 | Surge 策略组 | 从 `7200` 起，每个节点一个端口 |
| `single` | 菜单栏「节点」 | 默认 `7100` |

修改模式后重新点「连接设置 › 接入 Surge」

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
| 精简规则 | 仅保留基础规则 |
| 海外网络环境 | 使用海外节点级别 |
| 应急模式 | 使用套餐支持的备用节点 |
| 可选项参数 | 编辑 `&area=hk` 等订阅参数 |
| 允许局域网访问 | 让同一网络设备访问本机服务 |

上述设置变更后重新接入 Surge

### 保留现有 Surge 配置

不使用「接入 Surge」时，可在现有策略组中使用本地节点列表：

```ini
香港 = select, policy-path=http://127.0.0.1:6172/list, policy-regex-filter="香港|HK", update-interval=600
Premium = select, policy-path=http://127.0.0.1:6172/list, policy-regex-filter="Premium", update-interval=600
```

菜单栏「连接设置 › 复制本机节点列表 URL」可复制该地址

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
oixcloud-external-proxy-program --serve --listen 6172
oixcloud-external-proxy-program --serve --mode map --listen 6172
```

### 停止自动启动

推荐重新运行 `启动 oixCloud.command` 并选择「卸载自动启动」

也可手动运行：

```bash
launchctl bootout "gui/$(id -u)/com.oixcloud.external-proxy-program.tray"
rm -f ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
```

## English

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

### Manual installation

`启动 oixCloud.command` already handles download, signature verification, installation, and startup

For a command-line-only installation:

```bash
MAJOR=$(sw_vers -productVersion | cut -d. -f1)
if [ "$MAJOR" -ge 14 ]; then
  ASSET=$([ "$(uname -m)" = arm64 ] && echo arm64 || echo amd64)
else
  ASSET=legacy
fi
curl -fL "https://dl.dler.io/oixcloud-external-proxy-program-$ASSET" -o oixcloud-external-proxy-program
chmod +x oixcloud-external-proxy-program
xattr -dr com.apple.quarantine oixcloud-external-proxy-program
sudo cp oixcloud-external-proxy-program /usr/local/bin/oixcloud-external-proxy-program.new
sudo mv -f /usr/local/bin/oixcloud-external-proxy-program.new /usr/local/bin/oixcloud-external-proxy-program
```

Start the menu bar app temporarily:

```bash
oixcloud-external-proxy-program --tray
```

### Account configuration

Use "Account > Log in..." in the menu bar and enter an Access Token

The configuration file is:

```text
~/.config/oixcloud-external-proxy-program/config.json
```

Minimal configuration:

```json
{ "accessToken": "your Access Token" }
```

Email and password login exchanges them for a stored token; the password is not saved

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
| Simple Rules | Keep only basic rules |
| Overseas Network Environment | Use the overseas node tier |
| Emergency Mode | Use backup nodes supported by the plan |
| Optional Parameters | Edit subscription parameters such as `&area=hk` |
| Allow LAN Access | Serve other devices on the same network |

Reconnect Surge after changing these settings

### Keep an existing Surge profile

Use the local node list in existing policy groups instead of installing a generated profile:

```ini
Hong Kong = select, policy-path=http://127.0.0.1:6172/list, policy-regex-filter="香港|HK", update-interval=600
Premium = select, policy-path=http://127.0.0.1:6172/list, policy-regex-filter="Premium", update-interval=600
```

"Connection > Copy Local Node List URL" copies this address

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

After enabling "Allow LAN Access" and "LAN Access Authentication...", other devices can use:

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
oixcloud-external-proxy-program --serve --listen 6172
oixcloud-external-proxy-program --serve --mode map --listen 6172
```

### Disable automatic startup

Run `启动 oixCloud.command` again and choose "Remove Autostart"

Manual alternative:

```bash
launchctl bootout "gui/$(id -u)/com.oixcloud.external-proxy-program.tray"
rm -f ~/Library/LaunchAgents/com.oixcloud.external-proxy-program.tray.plist
```
