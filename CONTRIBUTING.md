# 贡献指南 (Contributing Guide)

> 欢迎为翠花量化系统贡献代码！

---

## 🚀 快速开始

### 1. Fork 仓库
在 GitHub 上 Fork 本仓库。

### 2. 克隆到本地
```bash
git clone https://github.com/你的用户名/cuihua-quant.git
cd cuihua-quant
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 4. 创建分支
```bash
git checkout -b feature/你的功能名
```

---

## 📝 开发规范

### 代码风格
- 遵循 PEP 8 规范
- 使用 Black 格式化
- 添加类型注解 (Type Hints)
- 所有公共 API 必须有文档字符串

### 提交信息
使用语义化提交信息：

```
<type>(<scope>): <description>

[optional body]
```

**Type 类型**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

**示例**:
```
feat(strategy): 添加动量策略
fix(data): 修复 Futu 数据同步问题
docs(api): 更新 API 文档
```

### 测试要求
- 新功能必须包含单元测试
- 测试覆盖率目标 >80%
- 运行 `pytest tests/ -v` 确保所有测试通过

---

## 🔧 开发流程

### 1. 运行测试
```bash
pytest tests/ -v --cov=src/
```

### 2. 代码检查
```bash
flake8 src/ tests/
mypy src/
black src/ tests/
```

### 3. 提交 Pull Request
- 描述清楚你的改动
- 关联相关 Issue
- 确保 CI 通过

---

## 📋 代码审查清单

提交 PR 前请检查：
- [ ] 代码通过所有测试
- [ ] 添加了必要的单元测试
- [ ] 更新了相关文档
- [ ] 提交信息符合规范
- [ ] 代码已格式化 (Black)
- [ ] 无 lint 错误

---

## 🤝 如何贡献

### 报告 Bug
1. 查看现有 Issue 是否已报告
2. 创建新 Issue，包含：
   - 问题描述
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息 (Python 版本、操作系统等)

### 提出新功能
1. 创建 Issue 讨论想法
2. 说明功能用途和实现方案
3. 等待维护者反馈

### 提交代码
1. Fork 仓库
2. 创建功能分支
3. 编写代码和测试
4. 提交 PR

---

## 📞 联系方式

- GitHub Issues: <https://github.com/xuefeng19988/cuihua-quant/issues>
- Email: cuihua@openclaw.ai

---

感谢你的贡献！🎉
