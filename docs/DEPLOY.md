# Cuihua Quant System - 部署指南

> 版本: v0.5.0  
> 日期: 2026-04-17

---

## 🚀 快速部署

### 方式 1: Docker (推荐)

```bash
# 克隆仓库
git clone https://github.com/xuefeng19988/cuihua-quant.git
cd cuihua-quant

# 配置环境变量
cp .env.example .env
# 编辑 .env 填写你的 API 密钥

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f cuihua-quant
```

### 方式 2: 手动部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env

# 3. 同步数据
python cli_v2.py sync --pool watchlist --days 60

# 4. 启动 Web 看板
python src/web/dashboard.py
```

---

## ⚙️ 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `FUTU_HOST` | Futu OpenD 地址 | `127.0.0.1` |
| `FUTU_PORT` | Futu OpenD 端口 | `11112` |
| `WECOM_WEBHOOK` | 企业微信 Webhook | - |
| `DB_PATH` | 数据库路径 | `data/cuihua_quant.db` |
| `ALPHA_VANTAGE_KEY` | 美股 API Key | `demo` |

### 配置文件

所有配置都在 `config/` 目录下:
- `app.yaml` - 应用设置
- `stocks.yaml` - 股票池
- `strategies.yaml` - 策略参数
- `risk.yaml` - 风控参数

---

## 📊 监控

### Web 看板

访问 `http://localhost:5000` 查看实时监控看板。

### API 状态

```bash
curl http://localhost:5000/api/status
```

### 日志

日志文件位于 `data/logs/` 目录。

---

## 🔧 维护

### 数据备份

```bash
# 备份数据库
cp data/cuihua_quant.db backups/cuihua_quant_$(date +%Y%m%d).db
```

### 数据库优化

```bash
# 清理碎片
python -c "import sqlite3; sqlite3.connect('data/cuihua_quant.db').execute('VACUUM')"
```

### 更新系统

```bash
git pull
pip install -r requirements.txt
python cli_v2.py sync
```

---

## 🐛 故障排除

### Futu 连接失败

```bash
# 检查 Futu OpenD 状态
ss -tlnp | grep 11112

# 重启 Futu OpenD
# (通过 GUI 或命令行)
```

### 数据库错误

```bash
# 检查数据库文件
ls -lh data/cuihua_quant.db

# 重新创建数据库
rm data/cuihua_quant.db
python cli_v2.py sync
```

---

## 📞 支持

- GitHub Issues: <https://github.com/xuefeng19988/cuihua-quant/issues>
- 文档: <https://github.com/xuefeng19988/cuihua-quant/docs>
