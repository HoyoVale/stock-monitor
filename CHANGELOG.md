# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
