# Security Policy

## 支持的版本

| 版本 | 支持状态 |
|------|----------|
| 0.x (开发中) | ✅ 安全更新 |

## 报告漏洞

**请勿公开提交 Issue！** 请通过以下方式私密报告：

1. 发送邮件到项目维护者
2. 使用 GitHub Security Advisory：https://github.com/HoyoVale/stock-monitor/security/advisories/new

### 期望流程

- 确认收到：48 小时内
- 评估与修复：根据严重程度 3-14 天
- 披露：修复发布后协调披露

## 安全最佳实践

本项目：
- 使用最小权限原则配置 API
- 敏感配置通过环境变量管理（不硬编码在代码中）
- CORS 在生产环境应限制为特定域名
- 依赖项通过 Dependabot 自动更新
