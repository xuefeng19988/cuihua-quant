# Performance Optimization Guide

## 📊 Caching Layer

The system includes a multi-level caching layer for performance optimization.

### Memory Cache (Default)
```python
from src.data.cache import CacheManager

cache = CacheManager()
cache.set('stock_data:AAPL', data, ttl_seconds=300)
result = cache.get('stock_data:AAPL')
```

### Redis Cache (Production)
```python
cache = CacheManager(use_redis=True, redis_url='redis://localhost:6379/0')
```

### Cache Decorator
```python
@cache.cache_query('features', ttl=600)
def get_features(code):
    # Expensive operation
    return features
```

## 🚀 Query Optimization

### Batch Queries
```python
# Instead of multiple queries
codes = ['SH.600519', 'SZ.002594', ...]
codes_str = ','.join([f"'{c}'" for c in codes])
df = pd.read_sql(f"SELECT * FROM stock_daily WHERE code IN ({codes_str})", engine)
```

### Index Usage
```sql
-- Add indexes for common queries
CREATE INDEX idx_stock_date ON stock_daily(date);
CREATE INDEX idx_stock_code ON stock_daily(code);
```

## 📈 Database Optimization

### VACUUM
```python
import sqlite3
conn = sqlite3.connect('data/cuihua_quant.db')
conn.execute('VACUUM')
conn.close()
```

### Connection Pooling
For production, use SQLAlchemy connection pooling:
```python
from sqlalchemy import create_engine
engine = create_engine('sqlite:///data/cuihua_quant.db', pool_size=5, max_overflow=10)
```

## 🌐 US Stock Data

```python
from src.data.us_stocks import USStockFetcher

fetcher = USStockFetcher(api_key='your_key')
df = fetcher.fetch_daily('AAPL')
fetcher.save_to_db('AAPL', df)
```

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f cuihua-quant

# Scale (if needed)
docker-compose up -d --scale cuihua-quant=2
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FUTU_HOST` | Futu OpenD host | `127.0.0.1` |
| `FUTU_PORT` | Futu OpenD port | `11112` |
| `DB_PATH` | Database path | `data/cuihua_quant.db` |
| `LOG_LEVEL` | Log level | `INFO` |
| `REDIS_URL` | Redis connection | - |
