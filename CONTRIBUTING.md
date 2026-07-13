# 贡献指南

## 开发环境

```bash
git clone https://github.com/HoyoVale/stock-monitor.git
cd stock-monitor
make install        # pip install + npm install
make dev-backend    # http://localhost:8000
make dev-frontend   # http://localhost:5173
```

## Pre-commit 检查

提交前本地运行以下检查，与 CI 门禁一致：

```bash
# 后端
cd backend
ruff check . --exit-non-zero
mypy app/ --config-file mypy.ini
pytest tests/ -m "not e2e" --cov=app --cov-fail-under=70

# 前端
cd frontend
npx eslint src/ --max-warnings 0
npx prettier --check "src/**/*.{ts,vue,css}"
npm test
npx vue-tsc -b --noEmit
```

## 分支策略

- `master` — 稳定版本，自动化开发合入
- `feature/*` / `auto/*` — 新功能开发分支
- `fix/*` — Bug 修复分支
- `release/v*` — 发布分支（自动创建，触发 release workflow）

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/)，commitlint 在 CI 中强制检查：

```
feat(scope): 描述
fix(scope): 描述
docs: 描述
test: 描述
chore: 描述
ci: 描述
refactor(scope): 描述
perf(scope): 描述
```

允许的类型: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

## 数据库迁移

本项目使用 Alembic 管理数据库迁移。如需修改模型：

```bash
cd backend
# 创建迁移脚本
alembic revision --autogenerate -m "描述"
# 检查生成的脚本正确后
alembic upgrade head
```

## 测试

```bash
# 后端单元测试 + 集成测试
cd backend && pytest tests/ -m "not e2e" -v --tb=short

# E2E 烟雾测试 (需要网络和 akshare)
cd backend && pytest tests/e2e/ -v

# 前端测试
cd frontend && npm test
```

## 发布流程

由 auto-dev 自动完成，或手动触发：

1. 所有 phase Issue 关闭，文档更新完毕
2. 确认 `VERSION` 文件为正确的目标版本号
3. auto-dev 创建 `release/v{version}` 分支 → push → 自动打 tag → 创建 GitHub Release
4. Release workflow 生成 Release Notes + 前端构建产物

## 代码风格

- **Python**: PEP 8 + type hints + mypy 类型检查
- **TypeScript/Vue**: ESLint + Prettier，Composition API
