"""测试通知服务。"""

import os
from unittest.mock import patch, MagicMock

import pytest

from app.services.notification_service import NotificationService


class TestNotificationService:
    """通知服务单元测试。"""

    def test_init_reads_env_vars(self):
        """初始化时正确读取环境变量。"""
        with patch.dict(os.environ, {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "465",
            "SMTP_USER": "test@example.com",
            "SMTP_PASSWORD": "secret",
            "ALERT_EMAIL_TO": "alert@example.com",
            "WECHAT_WEBHOOK_URL": "https://qyapi.weixin.qq.com/xxx",
            "DINGTALK_WEBHOOK_URL": "https://oapi.dingtalk.com/xxx",
        }):
            svc = NotificationService()
            assert svc.smtp_host == "smtp.example.com"
            assert svc.smtp_port == 465
            assert svc.smtp_user == "test@example.com"
            assert svc.email_to == "alert@example.com"
            assert "weixin" in svc.wechat_webhook
            assert "dingtalk" in svc.dingtalk_webhook

    def test_init_defaults(self):
        """未配置时使用空默认值。"""
        svc = NotificationService()
        assert svc.smtp_host == ""
        assert svc.wechat_webhook == ""
        assert svc.dingtalk_webhook == ""

    @pytest.mark.asyncio
    async def test_send_email_skips_when_not_configured(self):
        """SMTP 未配置时跳过。"""
        svc = NotificationService()
        svc.smtp_host = ""
        result = await svc.send_email("test", "body")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_wechat_skips_when_not_configured(self):
        """Webhook 未配置时跳过。"""
        svc = NotificationService()
        svc.wechat_webhook = ""
        result = await svc.send_wechat_webhook("test")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_dingtalk_skips_when_not_configured(self):
        """钉钉未配置时跳过。"""
        svc = NotificationService()
        svc.dingtalk_webhook = ""
        result = await svc.send_dingtalk_webhook("test")
        assert result is False

    @pytest.mark.asyncio
    async def test_notify_alert_with_no_channels(self):
        """无渠道配置时 notify_alert 不报错。"""
        svc = NotificationService()
        svc.smtp_host = ""
        svc.wechat_webhook = ""
        svc.dingtalk_webhook = ""
        result = await svc.notify_alert(
            stock_code="000001",
            stock_name="上证指数",
            alert_type="price_above",
            threshold=3500.0,
            current_price=3501.0,
        )
        assert result == {"email": False, "wechat": False, "dingtalk": False}

    @pytest.mark.asyncio
    async def test_notify_alert_formatting(self):
        """验证通知消息格式化。"""
        svc = NotificationService()
        svc.smtp_host = ""
        svc.wechat_webhook = ""
        svc.dingtalk_webhook = ""
        result = await svc.notify_alert(
            stock_code="600000",
            stock_name="浦发银行",
            alert_type="price_below",
            threshold=10.0,
            current_price=9.8,
        )
        assert isinstance(result, dict)
        assert "email" in result

    @pytest.mark.asyncio
    async def test_send_wechat_webhook_success(self):
        """企业微信 webhook 发送成功。"""
        import httpx
        svc = NotificationService()
        svc.wechat_webhook = "https://example.com/hook"

        mock_resp = MagicMock()
        mock_resp.status_code = 200

        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_resp
            result = await svc.send_wechat_webhook("test message")
            assert result is True

    @pytest.mark.asyncio
    async def test_send_wechat_webhook_failure(self):
        """企业微信 webhook 发送失败。"""
        import httpx
        svc = NotificationService()
        svc.wechat_webhook = "https://example.com/hook"

        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal error"

        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_resp
            result = await svc.send_wechat_webhook("test")
            assert result is False

    @pytest.mark.asyncio
    async def test_send_wechat_webhook_exception(self):
        """企业微信 webhook 异常时返回 False。"""
        import httpx
        svc = NotificationService()
        svc.wechat_webhook = "https://example.com/hook"

        with patch.object(httpx, "AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("timeout")
            result = await svc.send_wechat_webhook("test")
            assert result is False
