# DNSHE 自动续期

[中文](./README.md) | [English](./README.en.md)

## 快速开始总结

其实只需要两步：

1. 创建一个新的 GitHub 私有仓库，并复制本仓库内容
2. 在你的 GitHub 仓库中添加对应的 `Secrets` 和 `Variables`

在执行这两步之前，你必须先在 DNSHE 后台启用并创建 `DNSHE API` 凭据。

DNSHE 后台直达：

- https://my.dnshe.com

这是一个基于 GitHub Actions 的 DNSHE 免费域名自动续期方案。工作流每周检查一次，仅当域名进入续期窗口后才会调用 DNSHE API 自动续期。

## 功能说明

- 域名列表不写死在代码里，而是从 GitHub 仓库变量 `DNSHE_DOMAINS` 读取
- `DNSHE_DOMAINS` 按“一行一个域名”维护，新增和删除都只需要改仓库变量
- 首次发现某个域名时，脚本会根据 DNSHE API 返回的 `created_at` 自动推算初始到期时间：`created_at + 365 天`
- 续期成功后，脚本会把 API 返回的 `new_expires_at` 写入 `state/domains-state.json`
- 后续每周检查时，会基于最新的到期时间继续自动计算，不需要手工改日期

## 仓库设置

在 GitHub 仓库里添加以下设置：

- Secret: `DNSHE_API_KEY`
- Secret: `DNSHE_API_SECRET`
- Variable: `DNSHE_DOMAINS`

其中 `DNSHE_DOMAINS` 的内容格式如下，一行一个域名：

```text
abc88.cc.cd
12366.cc.cd
```

使用方式：

- 添加域名：在 `DNSHE_DOMAINS` 末尾新增一行
- 删除域名：从 `DNSHE_DOMAINS` 中删除对应那一行

## 续期规则

每个域名都会按以下逻辑处理：

1. 从 `DNSHE_DOMAINS` 读取域名
2. 调用 DNSHE `subdomains/list` 查询该域名
3. 如果该域名是首次出现，则用 `created_at + 365 天` 推导初始到期时间
4. 计算续期触发时间：`renew_at = expires_at - renew_before_days`
5. 当前时间未到 `renew_at` 时跳过
6. 当前时间到达或超过 `renew_at` 时执行续期
7. 续期成功后，用 `new_expires_at` 更新状态文件

当前默认的提前续期天数是 `175 天`。

## 新增域名示例

假设你现在有两个域名：

```text
abc88.cc.cd
12366.cc.cd
```

30 天后你又新注册了一个域名：

```text
444.cc.cd
```

此时你只需要把仓库变量 `DNSHE_DOMAINS` 改成：

```text
abc88.cc.cd
12366.cc.cd
444.cc.cd
```

下一次工作流自动运行时，脚本会这样处理：

1. 调用 DNSHE `subdomains/list`
2. 发现 `444.cc.cd` 是新域名，当前还不在 `state/domains-state.json` 中
3. 读取这个新域名的 `created_at`
4. 自动计算初始到期时间：`created_at + 365 天`
5. 将这个结果写入 `state/domains-state.json`
6. 之后继续按 `expires_at - 175 天` 计算续期窗口

也就是说，你新增域名时不需要手动填写注册时间，也不需要手动填写到期时间。

## 文件说明

- `scripts/dnshe_auto_renew.py`：续期主脚本
- `.github/workflows/dnshe-auto-renew.yml`：GitHub Actions 工作流
- `state/domains-state.json`：运行后自动生成或更新的状态文件，保存每个域名当前已知的到期时间

## 部署步骤

1. 新建一个 GitHub 私有仓库
2. 把本目录内容上传到仓库根目录
3. 在仓库 `Settings -> Secrets and variables -> Actions` 中添加：
   - Secret `DNSHE_API_KEY`
   - Secret `DNSHE_API_SECRET`
   - Variable `DNSHE_DOMAINS`
4. 打开仓库的 `Actions` 页面
5. 手动运行一次 `DNSHE Auto Renew`，确认能正常读取域名和生成状态文件

说明：

- GitHub 当前不支持直接把一个 `fork` 仓库改成私有仓库
- 如果上游仓库是公开仓库，最稳妥的做法就是自己新建一个私有仓库，再把本仓库内容复制进去

## 工作流行为

- 默认每周运行一次
- 使用 GitHub Hosted Runner
- 定时任务使用 UTC 时间
- 工作流文件需要位于默认分支
- 如果 DNSHE API Key / Secret 被你重新生成，需要同步更新 GitHub Secrets

## 首次运行说明

首次运行时，如果某个域名还没有状态记录：

- 脚本会从 DNSHE API 响应中读取 `created_at`
- 自动推算到期时间为 `created_at + 365 天`
- 将结果写入 `state/domains-state.json`

之后如果续期成功：

- 脚本会读取 DNSHE API 返回的 `new_expires_at`
- 自动覆盖旧的到期时间
- 下一次续期窗口会基于新的到期时间重新计算

## 本地手动测试

```powershell
$env:DNSHE_API_KEY='your_key'
$env:DNSHE_API_SECRET='your_secret'
$env:DNSHE_DOMAINS="abc88.cc.cd`n12366.cc.cd`n444.cc.cd"
python .\scripts\dnshe_auto_renew.py --state .\state\domains-state.json --dry-run
```

说明：

- `--dry-run` 只做检查和计算
- 不会实际调用续期接口
- 不会修改状态文件

## 注意事项

- 当前“首次到期时间”的计算依赖 DNSHE API 返回的 `created_at`
- 这个方案默认将域名有效期按 `365 天` 处理
- 如果 DNSHE 后续修改了有效期规则，脚本里的这段推导逻辑也需要同步调整
