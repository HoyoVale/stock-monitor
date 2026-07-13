# 股市监控系统 (Stock Monitor)

[![CI](https://github.com/HoyoVale/stock-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/HoyoVale/stock-monitor/actions/workflows/ci.yml)
[![Security](https://github.com/HoyoVale/stock-monitor/actions/workflows/security.yml/badge.svg)](https://github.com/HoyoVale/stock-monitor/actions/workflows/security.yml)
[![Release](https://github.com/HoyoVale/stock-monitor/actions/workflows/release.yml/badge.svg)](https://github.com/HoyoVale/stock-monitor/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

基于 FastAPI + Vue 3 的 A 股实时监控与智能决策辅助系统。

## 功能特性

- **大盘指数实时监控** — 上证指数、深证成指、创业板指、科创50 实时行情
- **自选股管理** — 自定义自选股列表，支持分组与排序
- **K 线图表** — ECharts 交互式 K 线图，支持多周期切换
- **技术指标分析** — MACD、RSI、KDJ、布林带 (BOLL)、均线排列
- **智能决策建议** — 多因子加权评分引擎，输出买入/持有/卖出建议与仓位提示
- **价格预警** — 自定义价格阈值，触发邮件/Webhook 通知
- **历史回测** — 滚动窗口回测，收益率/胜率/最大回撤/夏普比率
- **性能优化** — 指标缓存、API 去重、组件懒加载、自适应轮询
- **多数据源** — akshare + 东方财富双数据源，故障自动切换
- **WebSocket 实时推送** — 行情实时推送，断线自动重连 + HTTP 降级
- **用户认证** — JWT 登录/注册，路由守卫
- **用户数据隔离** — 自选股/预警/回测历史按用户隔离
- **系统监控** — 结构化日志 + 请求中间件 + 数据源统计 + 健康面板

## 技术架构

```
stock-monitor/
├── backend/                  # FastAPI 后端 (Python)
│   ├── app/
│   │   ├── api/              # REST API 路由 + WebSocket
│   │   ├── models/           # SQLAlchemy ORM 模型
│   │   ├── schemas/          # Pydantic 数据校验
│   │   ├── services/         # 业务逻辑 + 数据源抽象层
│   │   ├── websocket/        # WebSocket 连接管理
│   │   ├── auth.py           # JWT 认证工具
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 数据库连接 (SQLite + aiosqlite)
│   │   └── main.py           # FastAPI 应用入口
│   ├── tests/
│   │   ├── unit/             # 单元测试
│   │   ├── integration/      # 集成测试
│   │   ├── e2e/              # E2E 烟雾测试
│   │   └── functional/       # 功能测试
│   ├── alembic/              # 数据库迁移
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/                 # Vue 3 前端 (TypeScript)
│   ├── src/
│   │   ├── views/            # 页面视图
│   │   ├── components/       # UI 组件
│   │   ├── composables/      # 组合式函数 (useWebSocket)
│   │   ├── api/              # API 客户端 (axios + 缓存)
│   │   ├── stores/           # Pinia 状态管理 (含认证)
│   │   ├── types/            # TypeScript 类型定义
│   │   └── router/           # Vue Router (懒加载 + 路由守卫)
│   ├── package.json
│   └── vite.config.ts
├── .github/                  # CI/CD 工作流 + 模板
├── Makefile
└── README.md
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 安装

```bash
git clone https://github.com/HoyoVale/stock-monitor.git
cd stock-monitor
make install
```

### 开发运行

```bash
make dev-backend   # http://localhost:8000
make dev-frontend  # http://localhost:5173
```

### 测试

```bash
make test          # 后端 pytest
cd frontend && npm test  # 前端 vitest
```

## API 接口

| Method | Path | 说明 |
|--------|------|------|
| GET | `/api/indices` | 大盘指数实时行情 |
| GET | `/api/indices/{code}/bars` | 指数 K 线 |
| GET | `/api/stocks?search=` | 股票搜索 |
| GET | `/api/stocks/{code}/quotes` | 个股行情 |
| GET | `/api/stocks/{code}/bars` | 个股 K 线 |
| GET/POST/PUT/DELETE | `/api/watchlist[/{id}]` | 自选股 CRUD |
| GET/POST/DELETE | `/api/alerts/rules[/{id}]` | 预警规则 CRUD |
| GET | `/api/alerts/records` | 预警触发历史 |
| GET | `/api/indicators/{code}` | 技术指标 (MACD/RSI/KDJ/BOLL/MA) |
| GET | `/api/suggestions/{code}` | 决策建议 (0-100 评分) |
| POST | `/api/backtest` | 历史回测 |
| GET | `/api/backtest/history` | 回测历史 |
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 (JWT) |
| GET | `/api/auth/me` | 当前用户信息 |
| GET | `/api/health` | 系统健康检查 |
| GET | `/api/health/detailed` | 详细系统状态 |
| WS | `/ws/quotes?codes=` | WebSocket 实时行情 |

## 决策引擎评分模型

| 指标 | 权重 | 买入信号 | 卖出信号 |
|------|------|---------|----------|
| MACD | 30% | 金叉 (DIF 上穿 DEA) | 死叉 (DIF 下穿 DEA) |
| RSI | 20% | 超卖 (RSI < 30) | 超买 (RSI > 70) |
| KDJ | 20% | K 上穿 D 且 J < 80 | K 下穿 D 且 J > 20 |
| BOLL | 15% | 价格低于下轨 | 价格高于上轨 |
| MA 排列 | 15% | 多头排列 (MA5>MA10>MA20>MA60) | 空头排列 |

## 版本路线图

| 版本 | 阶段 | 状态 | 内容 |
|------|------|------|------|
| **v0.4.0** 🚀 | Phase 1-5 | ✅ 已发布 | 项目骨架 + 技术分析 + 决策引擎 + 预警通知 + 历史回测 + WebSocket + 用户认证 + 数据隔离 + 系统监控 |
| **v0.5.0** 🔄 | Phase 6 | 🔄 进行中 | AI 预测 + 基金/ETF + 自定义策略 + E2E 测试 + i18n |
| | Phase 7 | 📋 计划中 | 可观测性 / 性能压测 / 热重载 / PWA |
| **v0.6.0** 📋 | Phase 8-9 | 📋 计划中 | 待 v0.5.0 发布后规划 |

## 许可证

MIT License — 详见 [LICENSE](./LICENSE)
