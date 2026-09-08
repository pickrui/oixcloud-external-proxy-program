# Docker 部署 / Docker deployment

[中文](#中文) · [English](#english)

## 中文

适用于 Linux 主机、NAS 和家用服务器，支持 `linux/amd64` 与 `linux/arm64`

### 准备

需要 Docker Engine 和 Docker Compose

下载仓库后进入目录：

```bash
git clone https://github.com/pickrui/oixcloud-external-proxy-program.git
cd oixcloud-external-proxy-program
cp config.example.json config.json
touch custom.conf
chmod 600 config.json
chmod 644 custom.conf
```

编辑 `config.json`：

- 替换 `accessToken`
- 替换 `lanAuth.username` 和 `lanAuth.password`
- 不需要鉴权时删除整个 `lanAuth`

### 启动

```bash
docker compose up -d
docker compose ps
```

健康状态应显示 `healthy`

### 接入 Surge

同一局域网设备使用 Docker 主机 IP：

```text
完整配置    http://用户名:密码@Docker主机IP:6172/
节点列表    http://用户名:密码@Docker主机IP:6172/list
Clash       http://用户名:密码@Docker主机IP:6172/clash
```

未配置 `lanAuth` 时删除 URL 中的 `用户名:密码@`

### Clash / Mihomo UDP 转发

仅映射 SOCKS5 的 TCP 端口还不够，UDP 需要单独的端口范围和客户端可达的地址

在现有 `config.json` 中加入以下字段，将示例 IP 改为 Docker 主机的局域网 IPv4 地址：

```json
{
  "udpPortRange": { "start": 10000, "end": 10099 },
  "udpAdvertiseAddress": "192.168.1.10"
}
```

新版 `compose.yaml` 已映射 `10000-10099:10000-10099/udp`，自定义部署也需按相同端口号映射，并允许客户端通过防火墙访问

v0.0.31 及更早版本的远程 `/clash` 输出未自动声明 UDP，Mihomo 可在现有 provider 中添加 `override`：

```yaml
proxy-providers:
  oixcloud:
    type: http
    url: "http://用户名:密码@192.168.1.10:6172/clash"
    path: ./providers/oixcloud.yaml
    interval: 3600
    override:
      udp: true
```

`override.udp` 见 [Mihomo 官方文档](https://wiki.metacubex.one/config/proxy-providers/)，请替换鉴权信息，仅对 SOCKS5 / mixed 监听使用；HTTP 代理不支持此 UDP 转发

更新配置后重新创建容器并刷新 provider；修改端口范围时须同时修改配置、Compose 和防火墙，NAT 需要保持 TCP 与 UDP 来源地址一致

### 更新

Compose 固定使用 `latest`，以后无需修改版本号：

```bash
docker compose pull
docker compose up -d
```

### 日志与状态

```bash
docker compose logs -f
docker compose ps
curl http://127.0.0.1:6172/health
```

`/health` 不返回账户、节点或配置内容

### 文件与端口

| 项目 | 用途 |
|---|---|
| `config.json` | 账户与运行配置，只读挂载 |
| `custom.conf` | 自定义 Surge 配置，只读挂载 |
| `oixcloud-data` | 身份密钥与节点缓存 |
| `6172/tcp` | 配置、节点列表和健康检查 |
| `7200-7299/tcp` | 默认节点映射端口 |
| `10000-10099/udp` | 配置范围内的 SOCKS5 UDP 转发端口 |

节点超过 100 个或使用范围外的固定端口时，扩大 `compose.yaml` 的端口范围

镜像以非 root 用户运行，根文件系统只读，并移除所有 Linux capabilities

这些 URL 使用 HTTP，HTTP Basic 仅做 Base64 编码而非加密，必须由防火墙限制在可信局域网内，禁止直接暴露公网

### 停止

```bash
docker compose down
```

同时删除持久数据：

```bash
docker compose down -v
```

## English

Use this deployment on a Linux host, NAS, or home server; both `linux/amd64` and `linux/arm64` are supported

### Prepare

Docker Engine and Docker Compose are required

Clone the repository and enter its directory:

```bash
git clone https://github.com/pickrui/oixcloud-external-proxy-program.git
cd oixcloud-external-proxy-program
cp config.example.json config.json
touch custom.conf
chmod 600 config.json
chmod 644 custom.conf
```

Edit `config.json`:

- Replace `accessToken`
- Replace `lanAuth.username` and `lanAuth.password`
- Remove the entire `lanAuth` object when authentication is not needed

### Start

```bash
docker compose up -d
docker compose ps
```

The health status should become `healthy`

### Connect Surge

Use the Docker host IP from devices on the same LAN:

```text
Full profile  http://username:password@Docker-host-IP:6172/
Node list     http://username:password@Docker-host-IP:6172/list
Clash         http://username:password@Docker-host-IP:6172/clash
```

Remove `username:password@` when `lanAuth` is not configured

### Clash / Mihomo UDP relay

Publishing a SOCKS5 TCP port does not publish its UDP relay. Add these fields to the existing `config.json`, replacing the address with the Docker host's reachable LAN IPv4 address:

```json
{
  "udpPortRange": { "start": 10000, "end": 10099 },
  "udpAdvertiseAddress": "192.168.1.10"
}
```

The current Compose file maps `10000-10099:10000-10099/udp`. Custom deployments must publish the same port numbers and allow client access through the firewall

Remote `/clash` output in v0.0.31 and earlier does not automatically advertise UDP. Mihomo can enable it on an existing SOCKS5 provider:

```yaml
proxy-providers:
  oixcloud:
    type: http
    url: "http://username:password@192.168.1.10:6172/clash"
    path: ./providers/oixcloud.yaml
    interval: 3600
    override:
      udp: true
```

See the [official Mihomo provider documentation](https://wiki.metacubex.one/en/config/proxy-providers/). Replace the credentials and use SOCKS5 / mixed listeners; HTTP proxies cannot relay UDP this way

Recreate the container and refresh the provider after changing the configuration. Keep the configured range, published ports, and firewall in sync; NAT must preserve matching TCP and UDP client source addresses

### Update

Compose uses `latest`, so no version edit is required:

```bash
docker compose pull
docker compose up -d
```

### Logs and status

```bash
docker compose logs -f
docker compose ps
curl http://127.0.0.1:6172/health
```

`/health` exposes no account, node, or profile data

### Files and ports

| Item | Purpose |
|---|---|
| `config.json` | Account and runtime configuration, mounted read-only |
| `custom.conf` | Custom Surge configuration, mounted read-only |
| `oixcloud-data` | Identity keys and node cache |
| `6172/tcp` | Profiles, node lists, and health checks |
| `7200-7299/tcp` | Default mapped node ports |
| `10000-10099/udp` | Configured SOCKS5 UDP relay ports |

Expand the port range in `compose.yaml` for more than 100 nodes or fixed ports outside the default range

The image runs as a non-root user with a read-only root filesystem and no Linux capabilities

These URLs use HTTP, so HTTP Basic credentials are Base64-encoded rather than encrypted; restrict access to a trusted LAN with a firewall and never expose the service directly to the Internet

### Stop

```bash
docker compose down
```

Also delete persistent data:

```bash
docker compose down -v
```
