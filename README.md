# 股市监控系统 (Stock Monitor)

基于 FastAPI + Vue 3 的 A 股实时监控与智能决策辅助系统。

## 功能特性

- **大盘指数实时监控** — 上证指数、深证成指、创业板指、科创50 实时行情
- **自选股管理** — 自定义自选股列表，支持分组与排序
- **K 线图表** — ECharts 交互式 K 线图，支持多周期切换
- **技术指标分析** — MACD、RSI、KDJ、布林带 (BOLL)、均线排列
- **智能决策建议** — 多因子加权评分引擎，输出买入/持有/卖出建议与仓位提示

## 技术架构

```
stock-monitor/
├── backend/                  # FastAPI 后端 (Python)
│   ├── app/
│   │   ├── api/              # REST API 路由
│   │   │   ├── indices.py    # GET /api/indices         大盘指数
│   │   │   ├── stocks.py     # GET /api/stocks          股票搜索 & 行情
│   │   │   ├── watchlist.py  # CRUD /api/watchlist       自选股管理
│   │   │   ├── indicators.py # GET /api/indicators/{code} 技术指标
│   │   │   │                 # GET /api/suggestions/{code} 决策建议
│   │   │   └── alerts.py     # 价格预警 (计划中)
│   │   ├── models/           # SQLAlchemy ORM 模型
│   │   ├── schemas/          # Pydantic 数据校验
│   │   ├── services/         # 业务逻辑层
│   │   │   ├── stock_service.py      # 股票数据 (akshare)
│   │   │   ├── indicator_service.py  # 技术指标计算 (pandas-ta)
│   │   │   ├── suggestion_service.py # 决策评分引擎
│   │   │   └── scheduler.py          # 定时任务 (APScheduler)
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 数据库连接 (SQLite + aiosqlite)
│   │   └── main.py           # FastAPI 应用入口
│   ├── tests/
│   │   ├── unit/             # 单元测试
│   │   ├── integration/      # 集成测试
│   │   └── functional/       # 功能测试
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/                 # Vue 3 前端 (TypeScript)
│   ├── src/
│   │   ├── views/            # 页面视图
│   │   │   ├── Dashboard.vue    # 大盘概览
│   │   │   ├── StockDetail.vue  # 个股详情 + 技术分析
│   │   │   └── Watchlist.vue    # 自选股管理
│   │   ├── components/       # UI 组件
│   │   │   ├── MarketCard.vue      # 指数卡片
│   │   │   ├── KLineChart.vue      # K 线图 (ECharts)
│   │   │   ├── IndicatorPanel.vue  # 技术指标面板
│   │   │   ├── DecisionCard.vue    # 决策建议卡片
│   │   │   ├── StockSearch.vue     # 股票搜索
│   │   │   ├── StockTable.vue      # 股票列表
│   │   │   └── Layout.vue          # 页面布局
│   │   ├── api/              # API 客户端 (axios)
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── types/            # TypeScript 类型定义
│   │   └── router/           # Vue Router
│   ├── package.json
│   └── vite.config.ts
├── Makefile
└── README.md
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 pnpm

### 安装

```bash
# 克隆仓库
git clone https://github.com/HoyoVale/stock-monitor.git
cd stock-monitor

# 安装所有依赖
make install
# 或手动:
# pip install -r backend/requirements.txt
# cd frontend && npm install
```

### 开发运行

```bash
# 启动后端 (http://localhost:8000)
make dev-backend

# 启动前端 (http://localhost:5173)
make dev-frontend
```

### 运行测试

```bash
# 后端测试
make test
# 或: cd backend && pytest tests/ -v

# 前端构建
make build
```

## API 接口

| Method | Path | 说明 |
|--------|------|------|
| GET | `/api/indices` | 大盘指数实时行情 |
| GET | `/api/indices/{code}/bars` | 指数 K 线历史数据 |
| GET | `/api/stocks?search=` | 股票搜索 |
| GET | `/api/stocks/{code}/quotes` | 个股实时行情 |
| GET | `/api/stocks/{code}/bars` | 个股 K 线历史数据 |
| GET | `/api/watchlist` | 获取自选股列表 |
| POST | `/api/watchlist` | 添加自选股 |
| PUT | `/api/watchlist/{id}` | 更新自选股 |
| DELETE | `/api/watchlist/{id}` | 删除自选股 |
| GET | `/api/indicators/{code}` | 技术指标 (MACD/RSI/KDJ/BOLL/MA) |
| GET | `/api/suggestions/{code}` | 智能决策建议 |

## 决策引擎评分模型

| 指标 | 权重 | 买入信号 | 卖出信号 |
|------|------|---------|----------|
| MACD | 30% | 金叉 (DIF 上穿 DEA) | 死叉 (DIF 下穿 DEA) |
| RSI | 20% | 超卖 (RSI < 30) | 超买 (RSI > 70) |
| KDJ | 20% | K 上穿 D 且 J < 80 | K 下穿 D 且 J > 20 |
| BOLL | 15% | 价格低于下轨 | 价格高于上轨 |
| MA 排列 | 15% | 多头排列 (MA5>MA10>MA20>MA60) | 空头排列 |

评分配比: `score = Σ(signal_weight × indicator_weight) / Σ(indicator_weight)`，输出 0-100 分，映射为 strongly_sell / sell / hold / buy / strongly_buy 五档。

## 开发阶段

| 阶段 | 状态 | 内容 |
|------|------|------|
| Phase 1 | ✅ 完成 | 项目骨架：FastAPI + Vue3 基础架构，大盘指数、自选股管理 |
| Phase 2 | 🔄 进行中 | 技术分析 + 决策建议引擎 + 前端组件 |
| Phase 3 | 📋 计划中 | 价格预警、推送通知、历史回测 |

## 许可证

MIT License — 详见 [LICENSE](./LICENSE)
