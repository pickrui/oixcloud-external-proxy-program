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
