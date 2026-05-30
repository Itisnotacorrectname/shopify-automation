"""
Notifications Module - 通知模块
支持 Slack、Email 通知
"""

import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests


class NotificationManager:
    """通知管理器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.slack_webhook = self.config.get("slack_webhook")
        self.email_enabled = self.config.get("email_enabled", False)
    
    def send_slack(self, message: str, status: str = "info") -> bool:
        """
        发送 Slack 通知
        
        Args:
            message: 消息内容
            status: 状态 (success, error, warning, info)
        
        Returns:
            是否成功
        """
        if not self.slack_webhook:
            print("Slack webhook not configured")
            return False
        
        # 颜色映射
        colors = {
            "success": "#36a64f",
            "error": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8"
        }
        
        payload = {
            "attachments": [{
                "color": colors.get(status, "#17a2b8"),
                "text": message,
                "footer": f"Shopify Automation | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }]
        }
        
        try:
            resp = requests.post(self.slack_webhook, json=payload)
            return resp.status_code == 200
        except Exception as e:
            print(f"Failed to send Slack notification: {e}")
            return False
    
    def send_deploy_notification(self, stats: Dict, success: bool = True):
        """发送部署完成通知"""
        status = "success" if success else "error"
        message = f"""
*Theme Deployment {'✓' if success else '✗'}*

Uploaded: {stats.get('uploaded', 0)}
Skipped:  {stats.get('skipped', 0)}
Errors:   {stats.get('errors', 0)}
        """.strip()
        
        return self.send_slack(message, status)
    
    def send_backup_notification(self, backup_path: str, stats: Dict):
        """发送备份完成通知"""
        total_files = sum(stats.values()) - stats.get('errors', 0)
        message = f"""
*Theme Backup Complete ✓*

Location: `{backup_path}`
Files: {total_files}
Errors: {stats.get('errors', 0)}
        """.strip()
        
        return self.send_slack(message, "success")
    
    def send_error_notification(self, operation: str, error: str):
        """发送错误通知"""
        message = f"""
*Operation Failed ✗*

Operation: {operation}
Error: {error}
        """.strip()
        
        return self.send_slack(message, "error")