# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Phase 2: 技术分析 + 决策建议引擎
  - 技术指标计算服务 (MACD, RSI, KDJ, BOLL, MA 排列)
  - 多因子加权评分决策引擎
  - IndicatorPanel 组件 (技术指标展示)
  - DecisionCard 组件 (决策建议展示)
  - StockSearch 组件 (股票搜索)
  - KLineChart 组件 (ECharts K 线图)
- CI/CD 工作流 (GitHub Actions)
  - CI: Python 后端测试 + 前端构建
  - Security: CodeQL 扫描 + 依赖审查
  - Release: 自动发布
- Dependabot 配置 (Python + npm + GitHub Actions)
- Issue/PR 模板

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
