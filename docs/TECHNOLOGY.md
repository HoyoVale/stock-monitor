# 技术选型指南

> 每个版本的版本规划阶段，必须基于本文档做出有理由的技术决策。
> 本文档随项目演进持续更新。

## 核心原则

1. **优先复用现有依赖** — 不引入新库除非现有库无法满足需求
2. **轻量优先** — 同等功能选体积更小的
3. **异步兼容** — Python 选型必须支持 async/await
4. **TypeScript 优先** — 前端选型必须有好的 TS 类型支持
5. **有活跃维护** — 最近 6 个月内有 release

## 现有依赖

### 后端 (Python)

| 库 | 用途 | 不可替换 |
|----|------|---------|
| fastapi | Web 框架 | ✅ |
| uvicorn | ASGI 服务器 | ✅ |
| sqlalchemy[asyncio] | ORM | ✅ |
| aiosqlite | 异步 SQLite | 可替换为 asyncpg (PostgreSQL) |
| alembic | 数据库迁移 | ✅ |
| akshare | A 股数据源 | ✅ 核心依赖 |
| pandas | 数据处理 | ✅ |
| pandas-ta | 技术指标 | 可考虑 ta-lib (C 扩展, 更快) |
| scikit-learn | 机器学习 | 可替换为 xgboost/lightgbm |
| numpy | 数值计算 | ✅ |
| httpx | HTTP 客户端 | ✅ |
| apscheduler | 定时任务 | 可替换为 celery+redis (分布式) |
| python-jose | JWT | ✅ |
| passlib[bcrypt] | 密码哈希 | ✅ |
| slowapi | 速率限制 | ✅ |

### 前端 (Vue 3 + TypeScript)

| 库 | 用途 | 不可替换 |
|----|------|---------|
| vue | 框架 | ✅ |
| vue-router | 路由 | ✅ |
| pinia | 状态管理 | ✅ |
| naive-ui | UI 组件库 | 可替换为 Element Plus / Ant Design Vue |
| echarts + vue-echarts | 图表 | 可替换为 Chart.js (更轻) 或 Highcharts (更丰富) |
| axios | HTTP 客户端 | 可替换为 ofetch / ky |
| vite | 构建工具 | ✅ |
| vitest | 测试 | ✅ |

## 选型决策记录

### 数据源: akshare vs tushare vs 东方财富 API

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| akshare | 免费、数据全、纯 Python、活跃维护 | 速度一般、部分接口不稳定 | ✅ 主数据源 |
| tushare | 速度快、数据质量高 | 需要积分、部分收费 | ❌ |
| 东方财富 API | 实时性好 | 无官方文档、接口可能变动 | ✅ 备用数据源 (已实现) |

### 机器学习: scikit-learn vs PyTorch vs TensorFlow

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| scikit-learn | 轻量 (30MB)、快速训练、够用 | 无深度学习 | ✅ 默认选择 |
| PyTorch | 灵活、生态好 | 体积大 (~800MB)、训练慢 | 仅在需要 LSTM/Transformer 时考虑 |
| TensorFlow | 生产部署成熟 | 体积更大、API 复杂 | ❌ |

### 图表: ECharts vs Chart.js

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| ECharts | 功能全、中文文档好、K 线图原生支持 | 体积较大 (~1MB) | ✅ 已有 |
| Chart.js | 轻量 (~60KB)、简洁 | K 线图需插件 | 仅在移动端需要极致体积时考虑 |

### 数据库: SQLite vs PostgreSQL

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| SQLite | 零配置、文件存储、够用 | 并发写锁、不适多进程 | ✅ 当前 |
| PostgreSQL | 并发好、功能全 | 需要安装和运维 | 仅当用户量>100 或需要全文搜索时迁移 |

## 禁止引入的依赖

以下依赖明确不引入，除非有充分理由推翻：

- **Redis / Celery** — 单人项目不需要分布式任务队列
- **Django** — 已经选了 FastAPI，不再混用
- **MongoDB** — SQLite 满足需求，不需要 NoSQL
- **React** — 已经选了 Vue 3
- **Ant Design Vue** — Naive UI 够用，不引入第二套 UI 库
- **GraphQL** — REST + WebSocket 已覆盖所有场景
- **gRPC** — 没有微服务间通信需求
- **Kubernetes / Helm** — Docker Compose 够用
- **Elasticsearch** — 不需要全文搜索
- **Sentry** — stdlib logging 够用

## 新增依赖评审清单

当版本规划需要引入新依赖时，回答以下问题：

1. 这个库解决了什么现有依赖无法解决的问题？
2. 它的体积多大？(pip install 下载量 / npm 包大小)
3. 最近一次 release 是什么时候？
4. GitHub stars / 社区活跃度如何？
5. 是否与 async/await 兼容？(Python)
6. 是否支持 TypeScript？(前端)
7. License 是否兼容 MIT？
8. 有没有更轻的替代方案？

所有回答记录在版本规划文档中。
