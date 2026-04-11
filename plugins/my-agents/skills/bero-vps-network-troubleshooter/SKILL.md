---
name: bero-vps-network-troubleshooter
description: 当用户要求 "排查 SSH 连不上", "修复 Debian 13 网络配置", "检查 Bero 服务器网络", "分析公网 IP 和内网 DHCP 冲突", "修复默认路由错误", "排查 kex_exchange_identification", 或提到 Debian 13、Bero、VPS、SSH closed、Address already assigned、networking.service failed 等问题时应使用此技能
---

# Bero VPS 网络与 SSH 排障

用于排查 Debian 13 在 Bero 服务商环境下的 SSH 无法连接、`networking.service` 启动失败、公网静态 IP 与私网 DHCP 冲突、以及 `/etc/network/interfaces` 配置错误.

## 先判断问题类型

- `ssh -vvv` 已经 `Connection established`, 但马上 `kex_exchange_identification: Connection closed by remote host`:
  优先检查 `sshd` 配置权限、服务状态、默认路由是否错误
- `systemctl restart networking` 失败:
  优先检查接口名、地址是否重复、是否有 DHCP 还在抢默认路由
- `ifconfig.me` 出口 IP 与服务器公网 IP 不一致:
  不一定是 DNS 或 `resolv.conf` 问题, 优先看默认路由和 DHCP

## 本次案例的典型根因

### 1. sshd 附加配置文件权限不安全

典型现象:

- `ssh -vvv` 在握手初期就被关闭
- `sshd` 能启动异常或重载失败

重点检查:

```bash
ls -l /etc/ssh/sshd_config.d
sshd -t
journalctl -u ssh -b --no-pager | tail -n 100
```

如果 `custom.conf` 权限过宽, 先修正到安全权限, 再测试 `sshd -t`.

### 2. 同一网卡同时有公网静态 IP 和私网 DHCP

典型现象:

- `ip addr show ens18` 同时出现公网 IP 和 `10.x.x.x` 动态地址
- `ip route` 默认路由走私网网关
- `curl -4 ifconfig.me` 显示的出口 IP 不是服务器实际公网 IP
- `ssh` 偶发连上即断
- `networking.service` 报 `Address already assigned`
- `ip -br addr` 一眼能看到同一网卡同时存在公网地址和 `10.x.x.x/24`

重点检查:

```bash
ip -br addr
ip addr show ens18
ip route
systemctl status networking --no-pager -l
ps aux | grep -E 'dhclient|systemd-networkd|NetworkManager|cloud-init' | grep -v grep
```

一旦发现:

```text
ens18:
  109.71.253.129/24
  10.x.x.x/24 dynamic

default via 10.x.x.1
```

就优先判断为:

- 公网地址是静态加上的
- 私网地址是 DHCP 下发的
- 默认路由被 DHCP 抢走
- SSH 回包路径异常

### 运行时快速恢复

如果已经确认 `ens18` 上存在公网静态 IP 和 `10.x.x.x` 动态地址, 可以先在控制台临时恢复网络:

```bash
ip addr del 10.207.0.147/24 dev ens18
ip route replace default via 109.71.253.1 dev ens18 src 109.71.253.129
ip addr show ens18
ip route
```

判断依据:

- 删除私网 DHCP 地址后 SSH 立即恢复, 说明根因就是同网卡双栈 IPv4 冲突
- 这只是运行时修复, 如果 DHCP 来源未关闭, 私网地址还会再次回来

### 永久修复方向

- 保留 `/etc/network/interfaces` 中的公网静态配置
- 停止继续给 `ens18` 下发 DHCP 的来源
- 优先排查 `dhclient`、`cloud-init`、`systemd-networkd`、`NetworkManager`
- 如果 `networking.service` 启动失败且报 `Address already assigned`, 不要继续反复 `ifup`, 先清理当前运行时重复地址

### 3. `/etc/network/interfaces` 写法错误

常见错误:

- 写错接口名, 例如把真实接口 `ens18` 写成 `eth0`
- 使用了错误或重复的 IPv6 默认路由写法
- 接口当前已经有同地址, 再次 `ifup` 报 `Address already assigned`

重点判断:

- `Cannot find device "eth0"`: 接口名写错
- `Address already assigned`: 不是权限问题, 是地址重复

## Bero Debian 13 配置模板

以下模板适用于本次 Bero 服务器信息:

- IPv4: `109.71.253.129`
- Netmask: `255.255.255.0`
- Gateway: `109.71.253.1`
- IPv6: `2a0e:6a80:3:214::`
- IPv6 Netmask: `/64`
- IPv6 Gateway: `fe80::1`

### 推荐 IPv4 + IPv6 模板

```ini
auto lo
iface lo inet loopback

auto ens18
allow-hotplug ens18

iface ens18 inet static
    address 109.71.253.129
    netmask 255.255.255.0
    gateway 109.71.253.1
    dns-nameservers 8.8.8.8 1.1.1.1

iface ens18 inet6 static
    address 2a0e:6a80:3:214::
    netmask 64
    gateway fe80::1
    dns-nameservers 2001:4860:4860::8888 2001:4860:4860::8844
```

### IPv6 配置说明

- `fe80::1` 是链路本地网关, 这是正常写法
- `ifupdown` 下优先使用 `address` + `netmask 64` + `gateway fe80::1`
- 不要同时保留 `gateway fe80::1` 和重复的 `up ip -6 route add default ...`, 避免重复默认路由
- 如果服务商环境特殊, 需要手工补默认路由时, 优先使用:

```bash
ip -6 route replace default via fe80::1 dev ens18
```

### 只恢复 IPv4 时的最小模板

当 SSH 还未恢复时, 先只恢复 IPv4, 确认连通性后再补 IPv6:

```ini
auto lo
iface lo inet loopback

auto ens18
allow-hotplug ens18

iface ens18 inet static
    address 109.71.253.129
    netmask 255.255.255.0
    gateway 109.71.253.1
    dns-nameservers 8.8.8.8 1.1.1.1
```

### IPv6 验证命令

补完 IPv6 后, 使用以下命令确认状态:

```bash
ip -6 addr show ens18
ip -6 route
ping -6 -c 3 fe80::1%ens18
ping -6 -c 3 2001:4860:4860::8888
```

理想状态:

- 接口上存在 `2a0e:6a80:3:214::/64`
- 默认 IPv6 路由为 `default via fe80::1 dev ens18`
- `fe80::1%ens18` 可达

### 配套示例文件

- `examples/debian13-bero-interfaces.conf`: Debian 13 在 Bero 环境下的完整 `interfaces` 模板

## 推荐排查顺序

1. 先看 `ssh -vvv`, 判断失败是在握手前、握手中还是认证阶段
2. 再看 `sshd -t` 与 `journalctl -f -t sshd`, 排除 sshd 配置和权限问题
3. 查看 `ip addr` 和 `ip route`, 检查是否存在公网静态 + 私网 DHCP 混用
4. 优先看 `ip -br addr`, 是否一眼就能看到 `10.x.x.x/24 dynamic`
5. 如果 `networking.service` 失败, 先看报错内容, 不要直接猜权限问题
6. 如果报 `Address already assigned`, 直接判断为接口当前已存在重复地址
7. 确认网卡真实名称后再写 `/etc/network/interfaces`

## 关键结论

- 用 IP 直连 SSH 时, `resolv.conf` 通常不是根因
- `ip_forward` 通常不是这类 VPS 自身 SSH 故障的根因
- `Address already assigned` 优先判断为重复配置, 不是权限错误
- 当服务商明确给出公网 `IP/Mask/Gateway`, 应优先按服务商文档校验路由和接口配置
- 出口公网 IP 与服务器公网 IP 不一致时, 先看默认路由是否被私网 DHCP 抢走
