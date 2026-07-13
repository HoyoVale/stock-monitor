"""预警通知服务。

支持多渠道推送:
- SMTP 邮件通知
- 企业微信 Webhook
- 钉钉 Webhook

所有渠道通过环境变量配置，未配置时静默跳过。
"""

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)


class NotificationService:
    """多渠道通知分发器。"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", self.smtp_user)
        self.email_to = os.getenv("ALERT_EMAIL_TO", "")

        self.wechat_webhook = os.getenv("WECHAT_WEBHOOK_URL", "")
        self.dingtalk_webhook = os.getenv("DINGTALK_WEBHOOK_URL", "")

    # ------------------------------------------------------------------
    # SMTP
    # ------------------------------------------------------------------

    async def send_email(self, subject: str, body: str) -> bool:
        """发送邮件通知。

        配置环境变量 SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASSWORD / ALERT_EMAIL_TO 后生效。
        """
        if not self.smtp_host or not self.email_to:
            logger.debug("SMTP 未配置，跳过邮件通知")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_from
            msg["To"] = self.email_to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            # 使用同步 smtplib，run_in_executor 避免阻塞
            loop = __import__("asyncio").get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._send_smtp_sync(msg),
            )
            logger.info(f"邮件已发送: {subject}")
            return True
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False

    def _send_smtp_sync(self, msg: MIMEMultipart):
        """同步 SMTP 发送（在 executor 中运行）。"""
        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
            server.starttls()
            if self.smtp_user:
                server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)

    # ------------------------------------------------------------------
    # Webhook
    # ------------------------------------------------------------------

    async def send_wechat_webhook(self, message: str) -> bool:
        """发送企业微信机器人消息。

        配置环境变量 WECHAT_WEBHOOK_URL 后生效。
        """
        if not self.wechat_webhook:
            logger.debug("企业微信 Webhook 未配置")
            return False

        try:
            import httpx
            payload = {
                "msgtype": "markdown",
                "markdown": {"content": message},
            }
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(self.wechat_webhook, json=payload)
                if resp.status_code == 200:
                    logger.info("企业微信通知已发送")
                    return True
                logger.warning(f"企业微信通知失败: {resp.status_code} {resp.text}")
                return False
        except Exception as e:
            logger.error(f"企业微信通知异常: {e}")
            return False

    async def send_dingtalk_webhook(self, message: str) -> bool:
        """发送钉钉机器人消息。

        配置环境变量 DINGTALK_WEBHOOK_URL 后生效。
        """
        if not self.dingtalk_webhook:
            logger.debug("钉钉 Webhook 未配置")
            return False

        try:
            import httpx
            payload = {
                "msgtype": "markdown",
                "markdown": {"title": "股票预警", "text": message},
            }
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(self.dingtalk_webhook, json=payload)
                if resp.status_code == 200:
                    logger.info("钉钉通知已发送")
                    return True
                logger.warning(f"钉钉通知失败: {resp.status_code} {resp.text}")
                return False
        except Exception as e:
            logger.error(f"钉钉通知异常: {e}")
            return False

    # ------------------------------------------------------------------
    # 统一发送
    # ------------------------------------------------------------------

    async def notify_alert(
        self,
        stock_code: str,
        stock_name: str,
        alert_type: str,
        threshold: float,
        current_price: float,
    ) -> dict[str, bool]:
        """对一条预警向所有已配置渠道发送通知。

        Returns:
            {"email": bool, "wechat": bool, "dingtalk": bool}
        """
        direction = "上穿" if alert_type == "price_above" else "下穿"
        subject = f"[股票预警] {stock_code} {stock_name} 价格{direction} {threshold}"
        body = (
            f"股票预警触发\n"
            f"================\n"
            f"代码: {stock_code}\n"
            f"名称: {stock_name}\n"
            f"条件: 价格{direction} {threshold}\n"
            f"当前价: {current_price:.2f}\n"
            f"时间: {__import__('datetime').datetime.now().isoformat()}\n"
        )

        # Markdown 格式用于 Webhook
        md = (
            f"## ⚠️ 股票预警触发\n\n"
            f"> 代码: **{stock_code}**\n\n"
            f"> 名称: **{stock_name}**\n\n"
            f"> 条件: 价格{direction} {threshold}\n\n"
            f"> 当前价: <font color=\"warning\">{current_price:.2f}</font>\n\n"
            f"> 时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        email_ok, wechat_ok, dingtalk_ok = False, False, False

        # 并行发送所有渠道
        import asyncio
        tasks = []
        if self.smtp_host and self.email_to:
            tasks.append(("email", self.send_email(subject, body)))
        if self.wechat_webhook:
            tasks.append(("wechat", self.send_wechat_webhook(md)))
        if self.dingtalk_webhook:
            tasks.append(("dingtalk", self.send_dingtalk_webhook(md)))

        results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
        for (name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"{name} 通知异常: {result}")
            elif name == "email":
                email_ok = result
            elif name == "wechat":
                wechat_ok = result
            elif name == "dingtalk":
                dingtalk_ok = result

        return {"email": email_ok, "wechat": wechat_ok, "dingtalk": dingtalk_ok}


# 单例
notification_service = NotificationService()
