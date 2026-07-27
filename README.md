# oixCloud Surge 助手 / oixCloud helper for Surge

把 oixCloud 节点接入 Surge，可运行在 Mac 菜单栏或 Docker

Connect oixCloud nodes to Surge from the macOS menu bar or Docker

**[中文](#中文) · [English](#english)**

---

## 中文

### 选择部署方式

| 场景 | 文档 |
|---|---|
| 在当前 Mac 使用 Surge | 继续阅读本页 |
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
| 检查运行状态 | 工具 › 诊断… |
| 更新程序 | 工具 › 检查更新 |
| 停止自动启动 | 重新运行 `启动 oixCloud.command`，选择「卸载自动启动」 |

### 更多

- [配置、接入模式、现有 Surge 配置和局域网访问](docs/configuration.md)
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
| Check runtime status | Tools > Diagnostics... |
| Update the helper | Tools > Check for Updates |
| Disable automatic startup | Run `启动 oixCloud.command` and choose Remove Autostart |

### More

- [Configuration, connection modes, existing Surge profiles, and LAN access](docs/configuration.md#english)
- [Docker deployment and updates](docs/docker.md#english)
- [Common issues and logs](docs/troubleshooting.md#english)
- [Surge manual](https://manual.nssurge.com/)

### License

Proprietary software; see [NOTICE](NOTICE)

Third-party licenses are in [ThirdPartyNotices](ThirdPartyNotices/THIRD-PARTY-NOTICES.txt)
