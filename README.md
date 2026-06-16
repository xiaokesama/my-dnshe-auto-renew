<div align="center">
  <h1>DNSHE 免费域名自动续期</h1>
  <p>每周自动检查 DNSHE 域名，到期前自动免费续期</p>
  <p>简体中文 | <a href="README.en.md">English</a></p>
  <p>
    <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-3776AB">
    <img alt="Platform" src="https://img.shields.io/badge/platform-GitHub%20Actions-2088FF">
    <img alt="License" src="https://img.shields.io/badge/license-MIT-111827">
    <img alt="Schedule" src="https://img.shields.io/badge/schedule-Weekly-22c55e">
  </p>
</div>

> 只需 3 分钟部署，之后每周自动检查并续期你的 DNSHE 免费域名。

## 3 分钟部署

### 第 0 步：获取 DNSHE API 凭证

1. 访问 https://my.dnshe.com，登陆成功

2. 点击【免费域名  -> API 管理  -> 创建API密钥】
3. 输入密钥名称，点击【创建】，获取到`DNSHE_API_KEY`和`DNSHE_API_SECRET`，后面的步骤会使用到这两个值。

### 第 1 步：用 GitHub Importer 将目标仓库转成自己的仓库

1. 使用自己的账号登录 GitHub
2. 新开一个浏览器页面访问 [https://github.com/new/import](https://github.com/new/import)
3. 按以下信息填写：

| 输入框 | 填什么 |
| --- | --- |
| `The URL for your source repository*` | `https://github.com/yinchaoqun/my-dnshe-auto-renew` |
| `Repository name` | 你即将新建仓库的仓库名，推荐: `my-dnshe-auto-renew` |

3. 点击 `Begin import`，等待导入完成（通常几十秒到几分钟）
4. 导入完成后，GitHub 会生成一个属于你自己的仓库

### 第 2 步：添加 GitHub Secrets 和 Variable

1. 进入这个仓库,点击【Settings -> Secrets and variables -> Actions】进入 Actions secrets and variables 设置页面
2. 点击 Secrets / Repository secrets 中的绿色按钮【 New repository secret】添加键值对(一次只能添加一个键值对)：

| Name * | Secret *|
| --- | --- |
| DNSHE_API_KEY | 第 0 步获取的DNSHE_API_KEY值 |
| DNSHE_API_SECRET | 第 0 步获取的DNSHE_API_SECRET值 |
| WECOM_WEBHOOK | (选填)企业微信群通知地址。如果没有，请先完成第3步再回来继续 |

3. 还是该页面，点击 Variables / Repository variable 中的绿色按钮【New repository variable】添加键值对：

| Name * | Secret *|
| --- | --- |
| DNSHE_DOMAINS | my.dnshe.com中申请的域名，形如：xxxyy.cc.cd<br>可填写多个，一行一个域名|

### 第 3 步：配置企业微信通知（推荐）

1. 打开企业微信 → 进入需要接收通知的群聊
2. 点击右上角 `...` → `群机器人` → `添加机器人`
3. 设置机器人名称为 `DNSHE 续期通知`，点击添加
4. 复制 Webhook 地址，添加到 GitHub Secrets 的 `WECOM_WEBHOOK` 中

> 💡 提示：如果不配置 `WECOM_WEBHOOK`，续期任务仍会正常运行，但不会发送通知。

### 第 4 步：手动运行一次

1. 项目主页，点击【Actions  -> DNSHE Auto Renew  -> Run workflow -> Run workflow】，开始运行
2. 等待约15s运行完成，查看项目的state目录，会生成`state/domains-state.json`文件，里面存放此次检测的结果

## 域名管理

### 填写格式

一行一个域名，新增就加一行，删除就删一行：

```text
abc88.cc.cd
12366.cc.cd
444.cc.cd
```

### 新增域名

只需把新域名追加到 `DNSHE_DOMAINS`。下一次 workflow 运行时，会自动发现新域名、从 API 读取 `created_at`，自动计算初始到期时间（`created_at + 365` 天），将结果写入 `state/domains-state.json`。不需要手动填注册时间或到期时间。

### 为什么不用手填到期时间

- 第一次发现域名时，用 `created_at + 365` 天推算初始到期时间
- 续期成功后，用 API 返回的 `new_expires_at` 更新状态
- 后续自动滚动计算，不需要每年改日期

## 续期规则

默认规则：

- 免费续期窗口：到期前 `175` 天
- 每周检查一次
- 只有进入窗口后才会请求续期
- 续期成功/失败都会通过企业微信推送通知

## 通知内容示例

企业微信会收到格式化的通知消息：
✅ DNSHE 自动续期任务 · 执行成功
运行时间：2026-06-15 09:22:47 UTC
📋 域名状态明细
🟢 域名状态
▸ 域名：chowking.cc.cd
▸ 到期时间：2027-06-15 10:57
▸ 剩余天数：365天
▸ 提前续期阈值：175天
▸ 数据来源：created_at_plus_365_days
通知包含以下信息：
🟢 状态正常（剩余 > 90 天）
🟡 临近续期窗口（剩余 30-90 天）
🔴 即将过期（剩余 < 30 天）
✅ 续期成功标识

## 重新生成 API 凭证

如果你在 DNSHE 后台重新生成了 API 凭据，同步更新 GitHub Secrets 即可：

- `DNSHE_API_KEY`
- `DNSHE_API_SECRET`

## 修改执行时间

编辑 `.github/workflows/dnshe-auto-renew.yml` 中的 `cron` 字段。当前为每周一次，时间使用 UTC。

## 文件说明

- `scripts/dnshe_auto_renew.py`：续期脚本
- `scripts/notify.py`：企业微信通知脚本，格式化并发送 Markdown 消息
- `.github/workflows/dnshe-auto-renew.yml`：每周 GitHub Actions 工作流
- `state/domains-state.json`：运行后自动生成的状态文件

### 常见问题

**Q：为什么没有收到企业微信通知？**
A：请检查：

1. `WECOM_WEBHOOK` Secret 是否正确配置
2. 企业微信群机器人是否被禁用
3. 查看 Actions 运行日志，确认 `Send WeCom Notification` 步骤是否成功执行

**Q：状态文件 `state/domains-state.json` 没有生成？**
A：首次运行需要手动触发 Actions，确保 `DNSHE_API_KEY` 和 `DNSHE_API_SECRET` 配置正确。

**Q：推送通知显示 "未知状态"？**
A：这是正常现象，首次运行或状态文件为空时会显示此信息。后续运行会显示正确的域名状态。

## 官方文档

- [DNSHE 后台](https://my.dnshe.com)
- [DNSHE API 手册](https://my.dnshe.com/knowledgebase/1/Free-Domain-Name-Service-API-User-Manual.html)

## 许可证

MIT License


