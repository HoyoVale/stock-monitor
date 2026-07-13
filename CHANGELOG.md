# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-07-13

### Added (Phase 5)
- 用户数据隔离: user_id 外键 + API 端点用户过滤 + 数据库迁移脚本
- 系统监控: 结构化 JSON 日志 + 请求中间件 + 数据源统计 + 健康面板

## [0.3.0] - 2026-07-13

### Added (Phase 4)
- 多数据源抽象层 (akshare + 东方财富) + 故障自动 fallback
- WebSocket 实时行情推送 + 连接管理 + HTTP 降级
- JWT 用户认证系统 (登录/注册/路由守卫/token 刷新)

## [0.2.0] - 2026-07-13

### Added
- Phase 2: 技术指标计算 + 多因子决策评分引擎 + 前端组件
- Phase 3: 价格预警通知 (SMTP/Webhook) + 历史回测系统
- CI/CD、安全扫描、Dependabot、GitHub Pages 部署

## [0.1.0] - 2026-07-11

### Added
- Phase 1: FastAPI + Vue 3 项目骨架、大盘指数、自选股管理
