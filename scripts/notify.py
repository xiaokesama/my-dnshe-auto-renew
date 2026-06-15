import os
import json
from datetime import datetime, timezone

def send_wecom_notification(job_status, run_url):
    """发送企业微信通知（纯Markdown格式，无日志链接，修复状态映射bug）"""
    webhook_url = os.environ.get("WECOM_WEBHOOK")
    if not webhook_url:
        print("⚠️ 未配置 WECOM_WEBHOOK，跳过通知")
        return

    state_path = "state/domains-state.json"
    raw_state = {}
    domain_blocks = []

    # 1. 读取状态文件（适配接口返回的 {domains: {...}} 结构）
    if os.path.exists(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                raw_state = json.load(f)
        except Exception as e:
            domain_blocks.append(f"❌ 状态文件解析失败：{str(e)}")
    else:
        domain_blocks.append("⚠️ 状态文件不存在，首次运行可能尚未生成数据")

    # 2. 提取域名数据并生成单个域名的Markdown块
    domains_data = raw_state.get("domains", {})
    if domains_data:
        for domain, info in domains_data.items():
            expires_at = info.get("expires_at", "N/A")
            renew_before = info.get("renew_before_days", "N/A")
            source = info.get("source", "N/A")
            
            # 计算剩余天数并匹配颜色标识
            days_left = "N/A"
            status_color = "comment"
            status_icon = "⚠️"
            if expires_at != "N/A":
                try:
                    exp_dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    days_left = (exp_dt - now).days
                    
                    if days_left < 30:
                        status_color = "warning"
                        status_icon = "🔴"
                    elif days_left < 90:
                        status_color = "comment"
                        status_icon = "🟡"
                    else:
                        status_color = "info"
                        status_icon = "🟢"
                except:
                    days_left = "解析失败"
                    status_color = "warning"
                    status_icon = "⚠️"

            # 单个域名的Markdown块（用分割线隔离，适配多域名场景）
            block = f"""---
<font color="{status_color}">{status_icon} 域名状态</font><br>
▸ 域名：<code>{domain}</code><br>
▸ 到期时间：<code>{expires_at}</code><br>
▸ 剩余天数：<code>{days_left}</code> 天<br>
▸ 提前续期阈值：<code>{renew_before}</code> 天<br>
▸ 数据来源：<code>{source}</code>
"""
            domain_blocks.append(block)

    # 3. 修复核心bug：状态映射键改为大写，匹配GitHub Actions返回的JOB_STATUS（SUCCESS/FAILED等）
    emoji_map = {
        "SUCCESS": "✅",
        "FAILURE": "❌",
        "CANCELLED": "⛔",
        "SKIPPED": "⏭️"
    }
    status_map = {
        "SUCCESS": "执行成功",
        "FAILURE": "执行失败",
        "CANCELLED": "已取消",
        "SKIPPED": "已跳过"
    }
    emoji = emoji_map.get(job_status, "❓")
    status_desc = status_map.get(job_status, "未知状态")

    # 4. 组装最终Markdown内容（完全删除日志链接，符合你的要求）
    content = f"""## {emoji} DNSHE 自动续期任务 · {status_desc}
<font color="comment">运行时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC</font><br><br>

### 📋 域名状态明细
{''.join(domain_blocks)}
---"""

    # 5. 发送请求
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": content.strip()
        }
    }

    try:
        import requests
        resp = requests.post(webhook_url, json=payload, timeout=15)
        if resp.status_code == 200:
            print("✅ 企业微信通知发送成功")
        else:
            print(f"❌ 通知发送失败，状态码: {resp.status_code}，响应: {resp.text}")
    except Exception as e:
        print(f"❌ 发送通知异常: {str(e)}")

if __name__ == "__main__":
    JOB_STATUS = os.environ.get("STATUS", "UNKNOWN")
    # 保留参数但不使用，避免报错
    RUN_URL = os.environ.get("RUN_URL", "#")
    send_wecom_notification(JOB_STATUS, RUN_URL)
