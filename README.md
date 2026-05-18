# DNSHE 自动续期

[中文](./README.md) | [English](./README.en.md)

一句话说明：这个仓库会每周检查一次你在 DNSHE 的域名，进入续期窗口后自动调用 DNSHE API 续期。

## 3 分钟部署

### 第 0 步：先在 DNSHE 后台开通 API

先去这里：

- https://my.dnshe.com

准备好这两个值：

- `DNSHE_API_KEY`
- `DNSHE_API_SECRET`

### 第 1 步：用 GitHub Importer 转成私有仓库

1. 登录 GitHub，打开 <https://github.com/new/import>
2. 按以下信息填写：

| 字段 | 填什么 |
| --- | --- |
| `Your old repository's clone URL` | `https://github.com/OUBIGFA/dnshe-auto-renew` |
| `Owner` | 你的 GitHub 账号 |
| `Repository name` | 你的仓库名，例如 `my-dnshe-auto-renew` |
| `Privacy` | 选 `Private` |

1. 点击 `Begin import`，等待导入完成（通常几十秒到几分钟）
2. 导入完成后，GitHub 会生成一个属于你自己的私有仓库，后续的 Secret、Variable 和 workflow 都在这个仓库的网页里设置

### 第 2 步：在 GitHub 添加 2 个 Secret 和 1 个 Variable

进入：

- `Settings -> Secrets and variables -> Actions`

添加这两个 Secrets：

- `DNSHE_API_KEY`
- `DNSHE_API_SECRET`

再添加这个 Variable：

- `DNSHE_DOMAINS`

### 第 3 步：把域名写进 `DNSHE_DOMAINS`

格式很简单，一行一个域名：

```text
abc88.cc.cd
12366.cc.cd
```

### 第 4 步：手动运行一次 workflow

打开：

- `Actions`

手动运行一次 `DNSHE Auto Renew`，确认：

- 能正常读取域名
- 能正常生成 `state/domains-state.json`

## 你真正要填的只有 3 处

1. `DNSHE_API_KEY`
2. `DNSHE_API_SECRET`
3. `DNSHE_DOMAINS`

除此之外，其他内容基本都不用动。

## `DNSHE_DOMAINS` 怎么写

就是一行一个域名，例如：

```text
abc88.cc.cd
12366.cc.cd
444.cc.cd
```

你以后要维护域名时：

- 新增域名：新增一行
- 删除域名：删除一行

## 新增域名怎么处理

假设你现在有两个域名：

```text
abc88.cc.cd
12366.cc.cd
```

30 天后你又新增一个：

```text
444.cc.cd
```

你只需要把 `DNSHE_DOMAINS` 改成：

```text
abc88.cc.cd
12366.cc.cd
444.cc.cd
```

下一次 workflow 运行时，它会自动：

1. 发现 `444.cc.cd` 是新域名
2. 从 DNSHE API 读取这个域名的 `created_at`
3. 自动计算初始到期时间：`created_at + 365 天`
4. 把结果写入 `state/domains-state.json`

你不需要手动填写注册时间，也不需要手动填写到期时间。

## 为什么不用手填到期时间

这套方案是自动算的：

- 第一次发现某个域名时，用 `created_at + 365 天` 推算初始到期时间
- 续期成功后，用 API 返回的 `new_expires_at` 更新状态

所以后续会一直自动滚动计算，不需要你每年去改日期。

## 续期什么时候触发

默认规则是：

- 到期前 `175 天` 开始允许续期
- workflow 每周检查一次
- 一旦进入窗口，就会自动续期

## 如果你重新生成了 DNSHE API

如果你在 DNSHE 后台重新生成了 API 凭据，只需要同步更新 GitHub Secrets：

- `DNSHE_API_KEY`
- `DNSHE_API_SECRET`

## 改自动执行时间

如果你要修改执行时间，改这个文件里的 `cron`：

- `.github/workflows/dnshe-auto-renew.yml`

当前是每周运行一次，时间使用 UTC。

## 文件说明

- `scripts/dnshe_auto_renew.py`
- `.github/workflows/dnshe-auto-renew.yml`
- `state/domains-state.json`

## 官方文档

- [DNSHE 后台](https://my.dnshe.com)
- [DNSHE API 手册](https://my.dnshe.com/knowledgebase/1/Free-Domain-Name-Service-API-User-Manual.html)

