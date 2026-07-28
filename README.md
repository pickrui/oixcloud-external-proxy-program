# oixCloud Surge / OpenSurge 助手 / helper

把 oixCloud 节点接入 Surge，或使用 OpenSurge GUI 构建 DHCP/DNS 全屋网关

Connect oixCloud nodes to Surge, or build a DHCP/DNS gateway with the OpenSurge GUI

**[中文](#中文) · [English](#english)**

---

## 中文

### 选择部署方式

| 场景 | 文档 |
|---|---|
| 在当前 Mac 使用 Surge | 继续阅读本页 |
| 使用 OpenSurge GUI 与 DHCP/DNS 接管 | [OpenSurge 接入指南](docs/opensurge.md) |
| 部署到 Linux、NAS 或家用服务器 | [Docker 部署](docs/docker.md) |
| 保留现有 Surge 配置或自定义规则 | [配置参考](docs/configuration.md) |
| 安装或连接失败 | [排错](docs/troubleshooting.md) |

### macOS 快速开始

准备：

- Surge for Mac
- oixCloud 账户和 Access Token
- macOS 11 或更高版本

1. 下载并解压仓库

   [下载 ZIP](https://github.com/pickrui/oixcloud-external-proxy-program/archive/refs/heads/main.zip)

2. 双击 `启动 oixCloud.command`

   首次使用选择「常驻启动」

3. 点击菜单栏云朵图标，打开「账户 › 登录…」

   粘贴 Access Token，也可使用邮箱和密码

4. 打开「连接设置 › 接入 Surge」

   Surge 首次要求安装时确认，然后开启 `Set as System Proxy`

默认使用本地多端口映射，节点直接在 Surge 策略组中选择

完成标志：

- 菜单栏显示云朵图标
- Surge 出现 oixCloud 配置和节点策略组
- 切换节点后可以正常访问网络

macOS 11、12、13 自动使用 legacy 通用版，该版本尚未经过充分实机测试

### OpenSurge 全屋网关

OpenSurge 可提供 Web GUI、mihomo TUN、DHCP/DNS、设备策略和流量观察，本助手继续负责 oixCloud 账户、节点与本地出站

1. 在菜单栏打开「连接设置 › 导出 OpenSurge 配置」
2. 在 OpenSurge 的「来源」页面导入 Finder 中选中的 `OpenSurge.yaml`
3. 在 OpenSurge 的「网络设置」中选择局域网 DHCP 接管、旁路由或独立下游 LAN

局域网 DHCP 接管不会自动修改路由器，必须按 OpenSurge 恢复状态机人工关闭和恢复路由器 DHCP，禁止同时运行两个 DHCP 服务器

详细步骤、运行边界与排错见 [OpenSurge 接入与 DHCP/DNS 接管](docs/opensurge.md)

### 更新

菜单栏「工具 › 检查更新」可直接更新

`启动 oixCloud.command` 每次运行也会检查更新

更新器会校验 SHA-256、Developer ID 和版本号，安装失败时自动恢复旧版本

Docker 使用 `latest`，更新命令见 [Docker 部署](docs/docker.md)

### 常用操作

| 需求 | 入口 |
|---|---|
| 查看账户与流量 | 账户 |
| 切换接入模式 | 连接设置 › 接入模式… |
| 修改规则后同步 | 连接设置 › 接入 Surge |
| 导出 OpenSurge profile | 连接设置 › 导出 OpenSurge 配置 |
| 检查运行状态 | 工具 › 诊断… |
| 更新程序 | 工具 › 检查更新 |
| 停止自动启动 | 重新运行 `启动 oixCloud.command`，选择「卸载自动启动」 |

### 更多

- [配置、接入模式、现有 Surge 配置和局域网访问](docs/configuration.md)
- [OpenSurge GUI 与 DHCP/DNS 接管](docs/opensurge.md)
- [Docker 部署与更新](docs/docker.md)
- [常见问题与日志](docs/troubleshooting.md)
- [Surge 官方手册](https://manual.nssurge.com/)

### 许可

专有软件，详见 [NOTICE](NOTICE)

第三方许可证见 [ThirdPartyNotices](ThirdPartyNotices/THIRD-PARTY-NOTICES.txt)

---

## English

### Choose a deployment

| Scenario | Guide |
|---|---|
| Use Surge on this Mac | Continue on this page |
| Use the OpenSurge GUI and DHCP/DNS takeover | [OpenSurge integration](docs/opensurge.md#english) |
| Run on Linux, a NAS, or a home server | [Docker deployment](docs/docker.md#english) |
| Keep an existing Surge profile or add custom rules | [Configuration](docs/configuration.md#english) |
| Fix installation or connection problems | [Troubleshooting](docs/troubleshooting.md#english) |

### macOS quick start

Requirements:

- Surge for Mac
- An oixCloud account and Access Token
- macOS 11 or later

1. Download and extract the repository

   [Download ZIP](https://github.com/pickrui/oixcloud-external-proxy-program/archive/refs/heads/main.zip)

2. Double-click `启动 oixCloud.command`

   Choose persistent startup on first use

3. Click the cloud icon in the menu bar and open "Account > Log in..."

   Paste the Access Token, or use email and password

4. Open "Connection > Connect Surge"

   Confirm installation if Surge asks, then enable `Set as System Proxy`

Local multi-port mapping is the default; select nodes directly in Surge policy groups

The setup is complete when:

- The cloud icon is visible in the menu bar
- Surge shows the oixCloud profile and node policy groups
- Network access works after selecting a node

macOS 11, 12, and 13 use the universal legacy build, which has not been fully tested on physical hardware

### OpenSurge whole-home gateway

OpenSurge provides the Web GUI, mihomo TUN, DHCP/DNS, device policies, and traffic visibility. This helper continues to own the oixCloud account, nodes, and local egress

1. Open "Connection > Export OpenSurge Config" from the menu bar
2. Import the selected `OpenSurge.yaml` from OpenSurge's Sources page
3. Choose DHCP takeover, manual same-LAN gateway, or an isolated downstream LAN in OpenSurge Network Settings

DHCP takeover never changes the router automatically. Follow the OpenSurge recovery state machine to disable and restore router DHCP manually, and never run two DHCP servers on one LAN

See [OpenSurge integration and DHCP/DNS takeover](docs/opensurge.md#english) for setup, operating boundaries, and troubleshooting

### Updates

Use "Tools > Check for Updates" from the menu bar

`启动 oixCloud.command` also checks for updates whenever it runs

The updater verifies SHA-256, the Developer ID, and the exact version; failed installation checks restore the previous version

Docker uses `latest`; see [Docker deployment](docs/docker.md#english) for update commands

### Common tasks

| Task | Menu |
|---|---|
| View account and traffic | Account |
| Change connection mode | Connection > Connection Mode... |
| Apply changed settings | Connection > Connect Surge |
| Export an OpenSurge profile | Connection > Export OpenSurge Config |
| Check runtime status | Tools > Diagnostics... |
| Update the helper | Tools > Check for Updates |
| Disable automatic startup | Run `启动 oixCloud.command` and choose Remove Autostart |

### More

- [Configuration, connection modes, existing Surge profiles, and LAN access](docs/configuration.md#english)
- [OpenSurge GUI and DHCP/DNS takeover](docs/opensurge.md#english)
- [Docker deployment and updates](docs/docker.md#english)
- [Common issues and logs](docs/troubleshooting.md#english)
- [Surge manual](https://manual.nssurge.com/)

### License

Proprietary software; see [NOTICE](NOTICE)

Third-party licenses are in [ThirdPartyNotices](ThirdPartyNotices/THIRD-PARTY-NOTICES.txt)
