# 加密货币价格趋势分析工具

一个用于获取、存储和分析加密货币价格数据的Python工具，支持BTC和ETH的历史数据获取、贪婪恐惧指数追踪以及基于情绪指标的投资策略分析。

## 功能特性

- 数据获取：从Binance API获取BTC和ETH的5分钟K线数据
- 情绪追踪：从Alternative.me获取贪婪恐惧指数数据
- 数据存储：使用MySQL数据库存储所有历史数据
- 投资分析：基于贪婪恐惧指数的自动交易策略回测
- 日志系统：支持多级别日志输出，便于调试和监控
- 配置管理：通过环境变量管理所有配置项

## 项目结构

```
Analysis of Cryptocurrency Price Trends/
├── config.py              # 统一配置模块
├── main.py                # 主程序：数据获取和数据库初始化
├── daily_data_checker.py   # 数据完整性检查工具
├── investment_analysis.py   # 投资策略分析工具
├── requirements.txt        # Python依赖包
├── .env                  # 环境变量配置（本地）
├── .env.example          # 环境变量配置模板
└── .gitignore           # Git忽略文件
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

复制`.env.example`为`.env`并修改配置：

```env
# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_CHARSET=utf8mb4
DB_NAME=cryptocurrency_analysis

# 初始资金
INITIAL_FUNDS=10000

# 买入策略（贪婪恐惧指数低于阈值时买入）
BUY_THRESHOLDS=[{"fng": 10, "btc": 500, "eth": 300}, {"fng": 15, "btc": 200, "eth": 100}, {"fng": 20, "btc": 100, "eth": 50}]

# 卖出策略（贪婪恐惧指数高于阈值时卖出）
SELL_THRESHOLDS=[{"fng": 90, "btc": 0.03, "eth": 0.05}, {"fng": 85, "btc": 0.01, "eth": 0.02}, {"fng": 80, "btc": 0.005, "eth": 0.01}]

# 日志级别（DEBUG/INFO/WARNING/ERROR）
LOG_LEVEL=INFO
```

## 使用方法

### 1. 获取历史数据

运行主程序获取2020年至今的完整数据：

```bash
python main.py
```

程序将自动：
- 初始化数据库和表结构
- 获取贪婪恐惧指数历史数据
- 获取BTC和ETH的价格数据
- 保存所有数据到MySQL数据库

### 2. 检查数据完整性

检查并修复缺失的数据：

```bash
python daily_data_checker.py
```

### 3. 投资策略分析

基于贪婪恐惧指数进行投资策略回测：

```bash
python investment_analysis.py
```

## 投资策略说明

### 买入策略

当贪婪恐惧指数低于以下阈值时，分别买入BTC和ETH：

| 指数 | BTC投资额 | ETH投资额 |
|------|-----------|-----------|
| < 10 | $500 | $300 |
| < 15 | $200 | $100 |
| < 20 | $100 | $50 |

### 卖出策略

当贪婪恐惧指数高于以下阈值时，卖出对应比例的持仓：

| 指数 | BTC卖出比例 | ETH卖出比例 |
|------|------------|------------|
| > 90 | 3% | 5% |
| > 85 | 1% | 2% |
| > 80 | 0.5% | 1% |

## 数据库表结构

### currencies
- id: 币种ID
- symbol: 币种符号（BTC/ETH）
- name: 币种名称
- is_active: 是否活跃
- created_at/updated_at: 创建/更新时间

### price_data
- id: 记录ID
- currency_id: 币种ID
- symbol: 币种符号
- price: 价格
- timestamp: 时间戳
- created_at: 创建时间

### fear_greed_index
- date: 日期
- value: 贪婪恐惧指数值（0-100）

### trade_records
- id: 交易记录ID
- trade_date: 交易日期
- trade_type: 交易类型（buy/sell）
- btc_trade_amount/value/price: BTC交易信息
- eth_trade_amount/value/price: ETH交易信息
- total_trade_value: 交易总金额
- btc_holdings/eth_holdings: 持仓数量
- btc_average_price/eth_average_price: 持仓均价
- remaining_usd: 剩余资金
- account_total: 账户总价值
- trade_note: 交易备注
- created_at: 创建时间

## API说明

### Binance API
- 获取实时价格：`/api/v3/ticker/price`
- 获取K线数据：`/api/v3/klines`
- 请求限制：每IP 1200次/分钟

### Alternative.me API
- 获取贪婪恐惧指数：`/fng/`
- 数据范围：最多返回3000条历史数据

## 日志级别

- **DEBUG**: 详细的调试信息，包括所有请求和响应
- **INFO**: 一般信息，包括程序启动、完成、数据统计
- **WARNING**: 警告信息，包括资源不足、数据缺失
- **ERROR**: 错误信息，包括连接失败、请求失败

通过修改`.env`文件中的`LOG_LEVEL`来控制日志输出详细程度。

## 技术栈

- Python 3.x
- MySQL
- Binance API
- Alternative.me API
- python-dotenv（环境变量管理）
- requests（HTTP请求）
- schedule（定时任务）
- pymysql（MySQL连接）

## 注意事项

1. 首次运行前确保MySQL服务已启动
2. 修改`.env`文件中的数据库密码
3. API请求有速率限制，程序已内置重试机制
4. 数据获取可能需要较长时间，请耐心等待
5. 定期运行`daily_data_checker.py`检查数据完整性

## 许可证

MIT License

## 作者

idealism-L

## 项目链接

GitHub: https://github.com/idealism-L
