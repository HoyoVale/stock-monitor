# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-07-13

### Added (Phase 5)
- 用户数据隔离
  - WatchlistItem / AlertRule / AlertRecord / BacktestResult 关联 user_id 外键
  - 数据库迁移脚本 (migration_user_isolation.py)
  - API 端点统一过滤当前用户数据 (get_current_user 依赖)
  - 回测结果持久化 + GET /api/backtest/history + DELETE 端点
- 系统监控与日志
  - 结构化 JSON 日志 (logging_config.py, LOG_LEVEL / LOG_FILE / LOG_FORMAT 环境变量)
  - 请求日志中间件 (RequestLoggingMiddleware: 方法 + 路径 + 状态码 + 耗时)
  - 数据源调用统计 (DatasourceStats: 成功/失败/平均耗时)
  - GET /api/health/detailed 系统状态 API (版本/运行时间/数据源统计)
  - 前端 SystemHealthPanel 组件 (Naive UI 卡片)
  - 日志按日轮转 (TimedRotatingFileHandler, 保留30天)

## [0.3.0] - 2026-07-13

### Added (Phase 4)
- 多数据源抽象层: BaseDataSource + AkshareDataSource + EastmoneyDataSource
  - 数据源故障自动 fallback (主→备切换)
  - DATA_SOURCE / BACKUP_DATA_SOURCE / DS_FAILURE_THRESHOLD 环境变量配置
  - 数据源健康检查 (datasource_health)
- WebSocket 实时行情推送
  - WebSocketManager 连接管理 + 后台广播循环
  - /ws/quotes 端点: subscribe/ping/unsubscribe 协议
  - useWebSocket composable: 自动重连(10次) + 心跳(25s) + 4种连接状态
  - ConnectionStatus 组件: 实时/连接中/重连中/离线
  - HTTP polling 降级支持
- JWT 用户认证系统
  - User 模型 + bcrypt 密码哈希
  - POST /api/auth/register + /api/auth/login + /api/auth/refresh + GET /api/auth/me
  - Login/Register 页面 + 表单验证
  - 路由守卫: requiresAuth → 自动跳转登录
  - Axios 拦截器: 自动注入 Bearer token + 401 自动登出

## [0.2.0] - 2026-07-13

### Added
- Phase 2: 技术分析 + 决策建议引擎
  - 技术指标计算服务 (MACD, RSI, KDJ, BOLL, MA 排列)
  - 多因子加权评分决策引擎 (0-100 评分 → 五档建议)
  - IndicatorPanel / DecisionCard / StockSearch / KLineChart 前端组件
  - 价格预警 CRUD API + 调度器实时检查
  - 性能优化: 指标缓存、API 去重、组件懒加载、自适应轮询
  - 前端测试套件: Vitest 组件测试 + Store 测试
- CI/CD 工作流 (GitHub Actions)
  - CI: Python 3.10-12 测试 + 前端构建 (Node 18-22)
  - Security: CodeQL 扫描 + 依赖审查
  - Release: 标签自动发布 + 前端 GitHub Pages 部署
- Dependabot 配置 (Python + npm + GitHub Actions)
- Issue/PR 模板, CODEOWNERS, SECURITY.md

### Added (Phase 3)
- 价格预警通知: SMTP 邮件 + 企业微信/DingTalk Webhook 推送
- 前端预警管理页面: 创建规则 + 规则列表 + 触发历史 + 铃铛提醒
- 历史回测系统: 滚动窗口模拟评分 + 收益率/胜率/最大回撤/夏普比率
- 回测可视化页面: 参数配置 + ECharts 收益曲线

## [0.1.0] - 2026-07-11

### Added
- Phase 1: 项目骨架
  - FastAPI 后端
  - Vue 3 + Naive UI 前端
  - 大盘指数实时行情展示
  - 自选股 CRUD 管理
  - 股票搜索
  - SQLite 数据库
  - APScheduler 定时任务
  - akshare 数据源集成
