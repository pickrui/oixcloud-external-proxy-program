# OpenSurge 接入与 DHCP/DNS 接管

本指南将 oixCloud helper 作为 OpenSurge 的用户态本地出站

- oixCloud helper 管理账户、节点、ECH-TLS 连接和本地 SOCKS5/HTTP 端口
- OpenSurge 管理 Web GUI、mihomo TUN、DHCP/DNS、PF、IPv4 forwarding 和设备策略
- 两者通过 `127.0.0.1` 上的 HTTP proxy provider 与本地代理端口通信

当前适配已使用 OpenSurge v0.1.21 与其内置 mihomo 1.19.27 完成配置 overlay、provider 加载和真实本地代理出口验证

## 准备

- 已安装并登录 oixCloud helper
- macOS 13 或更高版本可安装 OpenSurge
- 从 [OpenSurge Releases](https://github.com/YTwsy/OpenSurge-for-Mac/releases) 下载与 Mac 架构匹配的安装包
- 在尝试局域网 DHCP 接管前准备路由器管理入口、原 DHCP 配置和备用恢复设备

OpenSurge 的 GitHub 安装包当前未签名，按其说明使用系统设置中的「仍要打开」，不要全局关闭 Gatekeeper

## 导入

1. 点击菜单栏云朵图标
2. 打开「连接设置 › 导出 OpenSurge 配置」
3. helper 会启用登录时启动，并将 profile 写入：

   ```text
   ~/.config/oixcloud-external-proxy-program/OpenSurge.yaml
   ```

4. Finder 会选中该文件
5. 打开 OpenSurge Web GUI 的「来源」页面
6. 在「本地 mihomo YAML」中选择或拖入 `OpenSurge.yaml`
7. 结构校验通过后，网关停止时设为下次启动版本，网关运行时选择应用并重载

不要把 `http://127.0.0.1:6172/opensurge` 粘贴到 OpenSurge 的 HTTPS 订阅框

OpenSurge 会拒绝 loopback HTTP URL 导入，这是其 SSRF 安全边界

`/opensurge` 仅用于检查生成结果，正式接入使用本地导出的 YAML

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

当前接管以协作式 IPv4 为主，IPv6、手工静态网关、DoH 和 Private Relay 可能绕过 Mac

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

oixCloud 登录、套餐、流量、海外网络环境、应急模式和可选参数仍在云朵菜单中管理

## 安全与故障恢复

- oixCloud 凭据留在用户配置中，不交给 OpenSurge root helper
- 导出目录权限为 `0700`，YAML 权限为 `0600`
- 开启局域网鉴权时，YAML 会包含访问本地 provider 所需的 Basic Auth userinfo，请勿转发
- OpenSurge 启动和配置校验前，云朵 helper 必须正在运行
- helper 退出时现有 OpenSurge 连接会失败，重新打开或启动 helper 后刷新 provider
- OpenSurge 网关停止不等于路由器 DHCP 和 Mac 网络设置已经恢复，必须完成恢复状态机再退出

检查 helper：

```sh
curl -f http://127.0.0.1:6172/health
```

检查 wrapper：

```sh
curl -f http://127.0.0.1:6172/opensurge
```

如果 `/health` 正常但 OpenSurge 显示 provider 不可用：

1. 确认云朵菜单仍处于登录状态
2. 在 OpenSurge Provider 页面执行刷新
3. 重新导出 YAML 并应用
4. 查看云朵「工具 › 诊断…」与 OpenSurge 诊断页

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

The integration has been validated with OpenSurge v0.1.21 and its bundled mihomo 1.19.27, including config overlay, provider loading, and a real local proxy egress check

### Requirements

- The oixCloud helper is installed and logged in
- OpenSurge requires macOS 13 or later
- Download the matching package from [OpenSurge Releases](https://github.com/YTwsy/OpenSurge-for-Mac/releases)
- Before DHCP takeover, preserve router access, the original DHCP settings, and a static recovery device

The current GitHub packages are unsigned. Follow OpenSurge's Open Anyway instructions instead of disabling Gatekeeper globally

### Import

1. Click the cloud icon in the menu bar
2. Open "Connection > Export OpenSurge Config"
3. The helper enables launch at login and writes:

   ```text
   ~/.config/oixcloud-external-proxy-program/OpenSurge.yaml
   ```

4. Finder selects the generated file
5. Open the Sources page in the OpenSurge Web GUI
6. Select or drop `OpenSurge.yaml` under Local mihomo YAML
7. After structural validation, set it as the next-start version or apply and reload the running gateway

Do not paste `http://127.0.0.1:6172/opensurge` into the HTTPS subscription field

OpenSurge intentionally rejects loopback HTTP source imports as an SSRF boundary

The endpoint is for inspection; local YAML import is the supported setup path

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

The current design is cooperative IPv4. IPv6, static gateways, DoH, and Private Relay may bypass the Mac

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

Continue to manage oixCloud login, plan details, traffic, overseas mode, emergency mode, and optional parameters from the cloud menu

### Security and recovery

- oixCloud credentials remain in the user's config and are never passed to the OpenSurge root helper
- The export directory is `0700` and the YAML is `0600`
- When LAN authentication is enabled, the YAML includes Basic Auth userinfo for the local provider; do not share it
- The cloud helper must be running before OpenSurge starts or validates the profile
- If the helper exits, existing OpenSurge egress fails; restart the helper and refresh the provider
- Stopping the OpenSurge gateway does not by itself restore router DHCP or Mac network settings; finish the recovery state machine before quitting

Check the helper:

```sh
curl -f http://127.0.0.1:6172/health
```

Check the wrapper:

```sh
curl -f http://127.0.0.1:6172/opensurge
```

If `/health` works but the provider is unavailable:

1. Confirm that the cloud menu is still logged in
2. Refresh the provider in OpenSurge
3. Export and apply the YAML again
4. Check Tools > Diagnostics in the cloud menu and the OpenSurge Diagnostics page

### Licensing boundary

OpenSurge is GPL-3.0-only and the oixCloud helper remains a separate proprietary process

The integration communicates only through HTTP, SOCKS5, and HTTP CONNECT, without linking or copying OpenSurge source code

Comply with OpenSurge's GPL source and license obligations when distributing a modified OpenSurge build