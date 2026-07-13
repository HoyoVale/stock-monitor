# 开发指南

> 本文档描述 stock-monitor 的开发约定和自动化工作流。

## 开发周期

项目采用**版本化开发**模型：

```
版本规划 → 阶段开发 → 所有阶段完成 → 版本发布 → 下一版本规划 → ...
```

每个版本包含 2 个阶段 (Phase)，每个阶段包含 8-12 个细粒度 Issue。

## 版本规划

每个新版本/新阶段开始前，auto-dev 会执行版本规划，生成：

1. **版本规划文档** (`docs/version-plans/v{X.Y.Z}-phase{N}.md`)
   - 版本目标
   - 技术选型（含候选方案对比）
   - 架构设计（新增/修改模块、数据流、数据库变更）
   - 组件拆解（每个功能 2-4 个细粒度 Issue）
   - 风险与回滚

2. **细粒度 Issue** (每个 2-4 小时工作量)
   - 单向依赖链
   - 明确的验收标准
   - 测试要求

## 分支策略

- `master` — 稳定版本，自动化开发合入
- `auto/issue-{N}-keyword` — 自动化开发分支
- `release/v*` — 发布分支（推送自动触发 release workflow）

## 提交规范

所有提交必须遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

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

CI 中 commitlint 强制检查。

## 代码门禁

### 后端
1. `ruff check backend/ --exit-non-zero` — 代码风格
2. `mypy app/` — 类型检查
3. `pytest tests/ -m "not e2e" --cov=app --cov-fail-under=70` — 测试 + 覆盖率

### 前端
1. `eslint src/ --max-warnings 0` — 代码风格
2. `prettier --check "src/**/*.{ts,vue,css}"` — 格式化
3. `vitest run` — 测试
4. `vue-tsc -b --noEmit` — 类型检查
5. `vite build` — 构建验证

## 数据库迁移

修改 ORM 模型后：

```bash
cd backend
alembic revision --autogenerate -m "描述变更"
alembic upgrade head
```

## 发布流程

1. 当前版本所有阶段 Issue 关闭
2. auto-dev 更新 VERSION + CHANGELOG + README
3. auto-dev 创建 release/v{X.Y.Z} 分支并推送
4. release.yml 自动打 tag + 构建 + 创建 GitHub Release
5. auto-dev 立即启动下一版本的第一个阶段规划

## 自动化定时任务

| 任务 | 频率 | 职责 |
|------|------|------|
| auto-dev | 每30分钟 | 版本规划 → Issue生成 → 开发 → 测试维护 → Release |
| health-check-morning | 每天 8:00 | Dependabot合并 + 过期Issue清理 |
| health-check-evening | 每天 20:00 | 滞留PR救援 + 补标签 |
| weekly-security-scan | 每周三 8:00 | 安全审计 + 密钥扫描 + CI加固 |
| friday-dev-digest | 每周五 17:00 | 开发周报 + 策略建议 |
