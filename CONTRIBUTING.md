# 贡献指南

感谢你对 stock-monitor 的关注！

## 开发环境搭建

1. Fork 本仓库
2. Clone 到本地: `git clone https://github.com/YOUR_USERNAME/stock-monitor.git`
3. 安装依赖: `make install`
4. 启动开发环境: 终端1: `make dev-backend` / 终端2: `make dev-frontend`

## 分支策略

- `master` — 稳定版本，直接合并需通过 PR 审查
- `feature/*` — 新功能开发分支
- `fix/*` — Bug 修复分支
- `release/*` — 发布准备分支

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式:

```
feat: 新增股票搜索自动补全
fix: 修复 K 线图时间轴显示错误
docs: 更新 API 文档
refactor: 重构评分引擎权重计算
test: 添加 RSI 指标单元测试
chore: 更新依赖版本
```

## 代码风格

- **Python**: 遵循 PEP 8，使用 type hints
- **TypeScript/Vue**: 使用项目 ESLint 配置，组件使用 Composition API
- 提交前运行: `cd backend && ruff check .` 和 `cd frontend && npx vue-tsc -b --noEmit`

## Pull Request 流程

1. 从 `master` 创建功能分支
2. 编写代码 + 测试
3. 确保 `make test` 通过
4. 提交 PR，填写 PR 模板中的所有内容
5. 等待 Code Review
6. CI 检查通过后合并

## 测试

```bash
# 后端单元测试
cd backend && pytest tests/unit/ -v

# 后端全部测试
cd backend && pytest tests/ -v
```

## 发布流程

1. 确保 `master` 分支所有测试通过
2. 更新 `CHANGELOG.md`
3. 创建版本标签: `git tag v0.2.0`
4. 推送标签: `git push --tags`
5. GitHub Actions 自动创建 Release
