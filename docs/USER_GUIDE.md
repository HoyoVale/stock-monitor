# stock-monitor 用户手册

> 当前版本: v0.4.0 | 本项目由 AI Agent 团队全自动维护

## 一、项目简介

股市监控系统是一个基于 FastAPI + Vue 3 的 A 股实时监控与智能决策辅助系统。支持大盘指数实时行情、自选股管理、K 线图表、技术指标分析（MACD/RSI/KDJ/布林带/均线排列）、智能决策建议（多因子加权评分引擎）、价格预警（邮件/Webhook 通知）、历史回测等功能。

## 二、快速开始（Docker，无需安装开发环境）

### 方式一：docker-compose（推荐）

```bash
# 下载 docker-compose.yml
curl -O https://raw.githubusercontent.com/HoyoVale/stock-monitor/master/docker-compose.yml

# 启动
docker compose up -d

# 浏览器打开 http://localhost
```

### 方式二：直接运行镜像

```bash
docker run -d -p 8000:8000 --name stock-backend ghcr.io/HoyoVale/stock-monitor-backend:latest
docker run -d -p 80:80 --name stock-frontend ghcr.io/HoyoVale/stock-monitor-frontend:latest
```

浏览器打开 http://localhost 即可使用。

## 三、主要功能

### 大盘指数
打开首页即可看到上证指数、深证成指、创业板指、科创50 的实时行情卡片和 K 线走势图。

### 自选股管理
点击左侧菜单「自选股」→ 搜索并添加股票代码 → 自动显示实时行情。支持分组管理和排序。

### 技术指标分析
在个股详情页，系统自动计算 MACD、RSI、KDJ、布林带、均线排列五个技术指标并展示信号。

### 决策建议
在个股详情页下方，系统根据五个指标的综合评分（0-100 分）给出买入/持有/卖出建议及仓位提示。

| 评分 | 建议 |
|------|------|
| 80-100 | 强烈买入 |
| 60-80 | 买入 |
| 40-60 | 持有 |
| 20-40 | 卖出 |
| 0-20 | 强烈卖出 |

### 价格预警
在「预警管理」页面创建价格预警规则，设置目标价位。当股价达到阈值时自动触发邮件或 Webhook 通知。

### 历史回测
在「回测」页面选择股票和时间范围，系统模拟评分引擎的历史表现，输出收益率、胜率、最大回撤、夏普比率等指标。

## 四、环境变量配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATA_SOURCE` | akshare | 主数据源 |
| `BACKUP_DATA_SOURCE` | eastmoney | 备用数据源 |
| `REFRESH_INTERVAL` | 300 | 行情刷新间隔(秒) |
| `SMTP_HOST` | (空) | SMTP 服务器 |
| `SMTP_PORT` | 587 | SMTP 端口 |
| `SMTP_USER` | (空) | 邮件账号 |
| `SMTP_PASSWORD` | (空) | 邮件密码 |
| `SECRET_KEY` | dev-secret | JWT 密钥(生产环境必须修改) |
| `CORS_ORIGINS` | * | 允许的跨域域名(生产环境改为具体域名) |
| `RATE_LIMIT` | 60/minute | API 限流 |

## 五、常见问题

**Q: 为什么数据不刷新？**
A: 默认只在交易时间(工作日 9:30-11:30, 13:00-15:00)刷新。设置 `TRADING_ONLY=false` 可关闭此限制。

**Q: 如何添加自选股？**
A: 进入「自选股」页面 → 搜索股票代码或名称 → 点击添加。

**Q: 预警功能需要什么配置？**
A: 需要设置 SMTP 环境变量（邮件通知）或 WEBHOOK_URL（企业微信/钉钉通知）。

**Q: 回测数据从哪里来？**
A: 通过 akshare 获取真实历史数据，首次查询可能较慢，后续有缓存。

**Q: 如何注册账号？**
A: 打开登录页面 → 点击「注册」→ 填写用户名、邮箱、密码。

## 六、技术支持

- Issue: https://github.com/HoyoVale/stock-monitor/issues
- Release: https://github.com/HoyoVale/stock-monitor/releases
