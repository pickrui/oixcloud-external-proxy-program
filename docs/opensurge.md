# OpenSurge 接入与 DHCP/DNS 接管

本指南将 oixCloud helper 作为 OpenSurge 的用户态本地出站

- oixCloud helper 管理账户、节点、ECH-TLS 连接和本地 SOCKS5/HTTP 端口
- OpenSurge 管理 Web GUI、mihomo TUN、DHCP/DNS、PF、IPv4 forwarding 和设备策略
- 两者通过 `127.0.0.1` 上的 HTTP proxy provider 与本地代理端口通信

2026-11-04 已使用 OpenSurge v0.3.2 官方 arm64 安装包内的 `omg` 和 mihomo `1.19.30-opensurge.1`，配合 Helper v0.0.57 Linux arm64 镜像完成实际集成验证，使用新版直接生成的配置

覆盖导入配置的合成与校验、带鉴权 provider 加载、节点切换、HTTP/HTTPS 204 请求、连接出口链、provider 刷新及刷新后保留节点选择；provider 加载 34 个节点，出口仅抽检其中 1 个，不代表全部节点可用

运行测试时只绑定回环地址，并使用独立 DNS 端口；TUN、DHCP、PF、系统 DNS 和系统代理切换不在本轮验证范围；操作步骤依据 [OpenSurge v0.3.2 用户指南](https://github.com/YTwsy/OpenSurge-for-Mac/blob/v0.3.2/docs/user/app-user-guide.zh-CN.md)

## 准备

- 已安装并登录 oixCloud helper
- macOS 13 或更高版本可安装 OpenSurge
- 从 [OpenSurge Releases](https://github.com/YTwsy/OpenSurge-for-Mac/releases) 下载与 Mac 架构匹配的安装包
- 在尝试局域网 DHCP 接管前准备路由器管理入口、原 DHCP 配置和备用恢复设备

[OpenSurge v0.3.2 安装包](https://github.com/YTwsy/OpenSurge-for-Mac/releases/tag/v0.3.2)未进行 Developer ID 签名或公证，按其说明使用系统设置中的「仍要打开」，不要全局关闭 Gatekeeper

## 导入

1. 点击菜单栏 oixCloud 图标
2. 打开「连接设置 › 导出 OpenSurge 配置」
3. helper 会将 profile 写入以下位置；启动器或手动安装的版本会同时启用登录时启动，Homebrew 版本请用 `brew services start oixcloud-external-proxy-program` 管理启动：

   ```text
   ~/.config/oixcloud-external-proxy-program/OpenSurge.yaml
   ```

4. Finder 会选中该文件
5. 打开 OpenSurge Web GUI 的「来源」页面
6. 在「来源」页面的完整 YAML 导入入口选择或拖入 `OpenSurge.yaml`，点击「导入为草稿」
7. 结构校验通过后，网关停止时设为下次启动版本，网关运行时选择应用并重载

不要把 `http://127.0.0.1:6172/opensurge` 粘贴到 OpenSurge 的 HTTPS 订阅框

OpenSurge 会拒绝 loopback HTTP URL 导入，这是其 SSRF 安全边界

`/opensurge` 仅用于检查生成结果，正式接入使用本地导出的 YAML

## 升级到 v0.0.57 与 provider 刷新修正

实测发现，选中真实节点后，默认 provider 下载请求也会进入 `oixCloud` 策略组，把本机 `/clash` 请求送到远端节点，导致刷新报 `503` / `EOF`

在导出的 YAML 中找到 `proxy-providers` 下的 `oixcloud-nodes`，新增与 `type` 同级的 `proxy: DIRECT`，保留原有 URL、鉴权、路径及其他字段，然后在 OpenSurge 中重新导入并应用：

```yaml
proxy-providers:
  oixcloud-nodes:
    type: http
    proxy: DIRECT
    # 保留原有 url、path、interval、health-check 等字段
```

这是 [mihomo 的 provider 下载策略](https://wiki.metacubex.one/en/config/proxy-providers/#proxy)，只指定订阅下载与刷新直连；节点选择和业务流量仍由 `oixCloud` 策略组控制

v0.0.57 起自动生成该字段；升级后请重新执行「连接设置 › 导出 OpenSurge 配置」，再在 OpenSurge 中导入并应用；旧 YAML 不会因程序升级而自动更新

尚未升级的 v0.0.56 及更早版本可按上面的步骤手动补上该字段，再次从旧版本导出时也需补上

## Profile 内容

导出的 profile 包含：

- `oixcloud-nodes` HTTP proxy provider，读取 `http://127.0.0.1:6172/clash`
- `oixCloud` Selector，候选为 provider 节点与 `DIRECT`
- helper 的 `PROCESS-NAME` 与 `PROCESS-PATH` 直连规则，避免 TUN 回环
- `MATCH,oixCloud` 终止规则
- 每 10 分钟刷新 provider，每 5 分钟进行一次延迟健康检查

provider 只暴露本地端口，不包含远端节点地址、PSK 或 ECH 参数

节点切换和面板节点更新通常不需要重新导出，OpenSurge 可在 Provider 页面手动刷新

修改配置服务端口、局域网鉴权或自定义 helper 路径后，需要重新导出并在 OpenSurge 中重新应用

## 网络模式

| 模式 | 路由器 DHCP | 客户端设置 | 适合场景 |
|---|---|---|---|
| 局域网 DHCP 接管 | 人工关闭，停止时人工恢复 | 自动获取 | 同一家庭 LAN 自动使用网关 |
| 旁路由模式 | 保持开启 | 手工将网关和 DNS 指向 Mac | 先让少量设备试用 |
| 独立下游 LAN | 主 LAN 不变 | 连接独立 AP、SSID、网口或 VLAN | 最稳妥的正式部署 |

### 局域网 DHCP 接管

OpenSurge 会引导完成以下 Mac 侧步骤：

1. 保存网络快照与离线恢复卡
2. 将 Mac 切换为固定 IPv4
3. 等待用户关闭路由器 DHCP
4. 主动探测并拒绝任何仍存在的 DHCP OFFER
5. 启动 dnsmasq、mihomo TUN、PF 和 IPv4 forwarding
6. 验收客户端 DHCP 租约、DNS 与 TUN 流量
7. 停止后等待用户恢复路由器 DHCP，再将 Mac 恢复为自动 DHCP

OpenSurge 不会登录或修改未知路由器

路由器 DHCP 与 OpenSurge DHCP 绝不能同时运行

不要在没有备用恢复设备和路由器管理入口时直接测试家庭主网络

以上基础流程以 IPv4 为主；OpenSurge v0.3.2 另提供实验性下游 IPv6 接管，须按[上游指南](https://github.com/YTwsy/OpenSurge-for-Mac/blob/v0.3.2/docs/user/app-user-guide.zh-CN.md)单独配置并验收；未接管的 IPv6、手工指定其他网关的设备，以及部分 DoH / Private Relay 路径仍可能绕过预期的网关或 DNS 策略

### 旁路由模式

路由器 DHCP 保持开启，OpenSurge 不在主 LAN 发放地址

需要在客户端或路由器的静态 DHCP 配置中，将目标设备的默认网关和 DNS 指向 Mac 的固定 LAN IPv4

适合先验证少量设备，不代表全屋自动接管

### 独立下游 LAN

Mac 的下游接口与上游接口分离，由 OpenSurge 为独立网络提供 DHCP/DNS 和网关

该模式不会与主路由 DHCP 竞争，推荐用于独立 AP、测试 SSID、以太网口或 VLAN

## GUI 能力

导入并启动后，OpenSurge GUI 可用于：

- 查看网关、DHCP/DNS、mihomo、PF 与 forwarding 状态
- 查看 DHCP 租约、活跃设备和当前会话流量
- 检测 provider 节点延迟与可达性
- 切换全局或每设备 Selector
- 刷新 provider
- 查看命中规则、出口链、连接和脱敏日志

节点健康检测从网关 Mac 发起，不能替代某台下游设备的 DHCP、DNS 与 TUN 验收

oixCloud 登录、套餐、流量、节点筛选和精简规则仍在 oixCloud 菜单中管理

## 安全与故障恢复

- oixCloud 账户凭据由助手管理，macOS 访问令牌优先保存在登录钥匙串，不能使用钥匙串时回退到本地配置文件，不交给 OpenSurge root helper
- 导出目录权限为 `0700`，YAML 权限为 `0600`
- 开启局域网鉴权时，YAML 会包含访问本地 provider 所需的 Basic Auth userinfo，请勿转发
- OpenSurge 启动和配置校验前，oixCloud helper 必须正在运行
- helper 退出时现有 OpenSurge 连接会失败，重新打开或启动 helper 后刷新 provider
- OpenSurge 网关停止不等于路由器 DHCP 和 Mac 网络设置已经恢复，必须完成恢复状态机再退出

检查 helper：

```sh
curl -f http://127.0.0.1:6172/health
```

`/health` 仅证明本地 HTTP 服务能响应，不验证登录或节点出口

检查 wrapper：

```sh
curl -f http://127.0.0.1:6172/opensurge
```

开启局域网鉴权后，检查 `/opensurge` 需提供同一组凭据，例如 `curl -f -u 用户名 http://127.0.0.1:6172/opensurge`，按提示输入密码

如果 `/health` 正常但 OpenSurge 显示 provider 不可用：

1. 确认 oixCloud 菜单仍处于登录状态
2. 在 OpenSurge Provider 页面执行刷新
3. 重新导出 YAML 并应用
4. 查看 oixCloud「工具 › 诊断…」与 OpenSurge 诊断页

## 许可边界

OpenSurge 采用 GPL-3.0-only，oixCloud helper 为独立专有进程

当前集成仅通过 HTTP、SOCKS5 和 HTTP CONNECT 接口通信，不链接或复制 OpenSurge 源码

修改并分发 OpenSurge 时，应遵守其 GPL 源码与许可证义务

---

## English

### OpenSurge Integration and DHCP/DNS Takeover

This integration runs the oixCloud helper as an unprivileged local egress for OpenSurge

- The oixCloud helper owns account access, nodes, ECH-TLS connections, and local SOCKS5/HTTP listeners
- OpenSurge owns the Web GUI, mihomo TUN, DHCP/DNS, PF, IPv4 forwarding, and device policies
- They communicate through a loopback HTTP proxy provider and local proxy ports

On 2026-11-04, the `omg` executable and mihomo `1.19.30-opensurge.1` from the official OpenSurge v0.3.2 arm64 installer were tested with the Helper v0.0.57 Linux arm64 image and its automatically generated profile

Validation covered imported-profile rendering and validation, authenticated provider loading, node selection, HTTP/HTTPS 204 requests, the connection egress chain, provider refresh and selection retention after refresh. The provider loaded 34 nodes; egress was sampled on one node, not every node

Runtime tests used loopback listeners and a separate DNS port. TUN, DHCP, PF, and changes to system DNS or proxy settings were outside this validation scope. UI steps follow the [OpenSurge v0.3.2 user guide](https://github.com/YTwsy/OpenSurge-for-Mac/blob/v0.3.2/docs/user/app-user-guide.zh-CN.md)

### Requirements

- The oixCloud helper is installed and logged in
- OpenSurge requires macOS 13 or later
- Download the matching package from [OpenSurge Releases](https://github.com/YTwsy/OpenSurge-for-Mac/releases)
- Before DHCP takeover, preserve router access, the original DHCP settings, and a static recovery device

The [OpenSurge v0.3.2 installers](https://github.com/YTwsy/OpenSurge-for-Mac/releases/tag/v0.3.2) are not Developer ID signed or notarized. Follow OpenSurge's Open Anyway instructions instead of disabling Gatekeeper globally

### Import

1. Click the oixCloud icon in the menu bar
2. Open "Connection > Export OpenSurge config"
3. The helper writes the profile below and enables launch at login for launcher/manual installations. For Homebrew installations, manage startup with `brew services start oixcloud-external-proxy-program`:

   ```text
   ~/.config/oixcloud-external-proxy-program/OpenSurge.yaml
   ```

4. Finder selects the generated file
5. Open the Sources page in the OpenSurge Web GUI
6. Select or drop `OpenSurge.yaml` in the full YAML import area on the Sources page, then import it as a draft
7. After structural validation, set it as the next-start version or apply and reload the running gateway

Do not paste `http://127.0.0.1:6172/opensurge` into the HTTPS subscription field

OpenSurge intentionally rejects loopback HTTP source imports as an SSRF boundary

The endpoint is for inspection; local YAML import is the supported setup path

### Upgrading to v0.0.57 and correcting provider refresh

Testing reproduced a refresh failure after selecting a real node: the provider download followed the `oixCloud` group and sent its local `/clash` request through the remote node, returning `503` / `EOF`

In the exported YAML, find `proxy-providers` → `oixcloud-nodes` and add `proxy: DIRECT` at the same indentation as `type`. Keep the existing URL, authentication, path and other fields, then import and apply the file again in OpenSurge:

```yaml
proxy-providers:
  oixcloud-nodes:
    type: http
    proxy: DIRECT
    # Keep the existing url, path, interval, health-check and other fields
```

This is [mihomo's provider download policy](https://wiki.metacubex.one/en/config/proxy-providers/#proxy): it sends subscription downloads and refreshes directly while node selection and application traffic still use the `oixCloud` group

Starting with v0.0.57, generated profiles include this field. After upgrading, use "Connection > Export OpenSurge config", then import and apply the file in OpenSurge again; upgrading the helper does not automatically update an existing YAML file

Users staying on v0.0.56 or earlier can add the field manually as shown above, including after exporting the file again from an older binary

### Generated profile

The profile contains:

- An `oixcloud-nodes` HTTP proxy provider backed by `http://127.0.0.1:6172/clash`
- An `oixCloud` Selector containing the provider nodes and `DIRECT`
- `PROCESS-NAME` and `PROCESS-PATH` direct rules for the helper to prevent a TUN loop
- A terminal `MATCH,oixCloud` rule
- A ten-minute provider interval and five-minute health checks

The provider exposes only local ports, not remote server addresses, PSKs, or ECH parameters

Node selection and panel-side node updates normally do not require another export. OpenSurge can refresh the provider manually

Export and apply the profile again after changing the config server port, LAN authentication, or a custom helper path

### Network modes

| Mode | Router DHCP | Client setup | Recommended use |
|---|---|---|---|
| DHCP takeover | Disable manually and restore during shutdown | Automatic | Automatic gateway use on one home LAN |
| Manual same-LAN gateway | Keep enabled | Point gateway and DNS to the Mac | A small trial group |
| Isolated downstream LAN | Main LAN unchanged | Join a separate AP, SSID, port, or VLAN | Safest production topology |

#### DHCP takeover

OpenSurge guides the Mac-side sequence:

1. Save a network snapshot and offline recovery card
2. Give the Mac a static IPv4 address
3. Wait for the operator to disable router DHCP
4. Probe for and reject any remaining DHCP OFFER
5. Start dnsmasq, mihomo TUN, PF, and IPv4 forwarding
6. Validate a client lease, DNS, and TUN traffic
7. Stop the gateway, wait for router DHCP to return, and restore automatic DHCP on the Mac

OpenSurge does not log in to or modify an unknown router

Never run the router DHCP server and OpenSurge DHCP server together on one LAN

Do not begin on the primary home network without a recovery device and verified router access

The basic flow above focuses on IPv4. OpenSurge v0.3.2 also offers experimental downstream IPv6 takeover, which requires separate setup and validation using the [upstream guide](https://github.com/YTwsy/OpenSurge-for-Mac/blob/v0.3.2/docs/user/app-user-guide.zh-CN.md). Unmanaged IPv6, clients using another static gateway, and some DoH / Private Relay paths can still bypass the intended gateway or DNS policy

#### Manual same-LAN gateway

Router DHCP remains active and OpenSurge does not issue addresses on the main LAN

Point selected clients, or static DHCP records on the router, to the Mac's stable LAN IPv4 for both gateway and DNS

This is useful for a small trial and is not automatic whole-home takeover

#### Isolated downstream LAN

The Mac uses separate downstream and upstream interfaces, and OpenSurge provides DHCP/DNS and gateway service to the downstream network

This avoids competing with main-router DHCP and is recommended for a separate AP, test SSID, Ethernet port, or VLAN

### GUI capabilities

After import and startup, the OpenSurge GUI can:

- Show gateway, DHCP/DNS, mihomo, PF, and forwarding status
- Show DHCP leases, active devices, and live session traffic
- Test provider node reachability and delay
- Switch global and per-device Selectors
- Refresh the provider
- Inspect matched rules, egress chains, connections, and redacted logs

Health tests originate from the gateway Mac and do not replace DHCP, DNS, and TUN validation from a downstream device

Continue to manage oixCloud login, plan details, traffic, the node filter, and simple rules from the oixCloud menu

### Security and recovery

- The helper manages oixCloud account credentials and prefers the login keychain for saved macOS access tokens, falling back to the local config when unavailable; they are never passed to the OpenSurge root helper
- The export directory is `0700` and the YAML is `0600`
- When LAN authentication is enabled, the YAML includes Basic Auth userinfo for the local provider; do not share it
- The oixCloud helper must be running before OpenSurge starts or validates the profile
- If the helper exits, existing OpenSurge egress fails; restart the helper and refresh the provider
- Stopping the OpenSurge gateway does not by itself restore router DHCP or Mac network settings; finish the recovery state machine before quitting

Check the helper:

```sh
curl -f http://127.0.0.1:6172/health
```

`/health` checks only that the local HTTP service responds, not sign-in or upstream node connectivity

Check the wrapper:

```sh
curl -f http://127.0.0.1:6172/opensurge
```

With LAN authentication enabled, `/opensurge` requires the same credentials; for example, run `curl -f -u username http://127.0.0.1:6172/opensurge` and enter the password when prompted

If `/health` works but the provider is unavailable:

1. Confirm that the oixCloud menu is still logged in
2. Refresh the provider in OpenSurge
3. Export and apply the YAML again
4. Check Tools > Diagnostics in the oixCloud menu and the OpenSurge Diagnostics page

### Licensing boundary

OpenSurge is GPL-3.0-only and the oixCloud helper remains a separate proprietary process

The integration communicates only through HTTP, SOCKS5, and HTTP CONNECT, without linking or copying OpenSurge source code

Comply with OpenSurge's GPL source and license obligations when distributing a modified OpenSurge build