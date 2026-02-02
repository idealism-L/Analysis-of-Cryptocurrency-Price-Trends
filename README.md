# 加密货币价格趋势分析系统

## 项目简介

本项目是一个加密货币价格趋势分析系统，主要功能包括：
- 从Binance API获取BTC和ETH的价格数据
- 从Alternative.me API获取比特币贪婪恐惧指数数据
- 将数据存储到MySQL数据库中
- 基于贪婪恐惧指数的投资策略分析
- 每日数据完整性检查和修复
- 价格计算使用开盘价和收盘价的均价

## 功能特性

- **数据获取**：从Binance API获取5分钟间隔的K线数据，从Alternative.me API获取每日贪婪恐惧指数
- **错误重试**：API请求失败时自动重试，提高数据获取成功率
- **数据存储**：将数据存储到MySQL数据库，支持增量更新
- **投资分析**：基于贪婪恐惧指数的投资策略分析，生成交易记录
- **数据完整性**：检查每日数据完整性（288条/天），自动修复缺失数据
- **价格计算**：使用开盘价和收盘价的均价作为价格
- **项目结构**：清晰的模块化设计，易于维护和扩展

## 项目结构

```
Analysis of Cryptocurrency Price Trends/
├── main.py              # 核心功能模块，数据获取和数据库操作
├── investment_analysis.py  # 投资策略分析模块
├── daily_data_checker.py    # 每日数据完整性检查模块
├── README.md            # 项目说明文档
└── requirements.txt     # 项目依赖
```

## 安装和依赖

### 依赖项

- Python 3.7+
- MySQL 5.7+
- 所需Python库：
  - requests
  - schedule
  - pymysql

### 安装方法

1. 克隆项目到本地
2. 安装所需依赖：
   ```bash
   pip install requests schedule pymysql
   ```
3. 确保MySQL服务已启动
4. 修改数据库配置（在各文件中）：
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': '123456',
       'charset': 'utf8mb4'
   }
   ```

## 使用方法

### 1. 初始化数据库和获取数据

运行主脚本，初始化数据库并获取2020年至今的完整数据：

```bash
python main.py
```

### 2. 运行投资策略分析

分析基于贪婪恐惧指数的投资策略：

```bash
python investment_analysis.py
```

### 3. 检查数据完整性

检查并修复每日数据完整性：

```bash
python daily_data_checker.py
```

## 数据库结构

### 1. currencies表

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| id | INT | 自增主键 |
| symbol | VARCHAR(10) | 加密货币符号（如BTC、ETH） |
| name | VARCHAR(50) | 加密货币名称（如Bitcoin、Ethereum） |
| is_active | BOOLEAN | 是否活跃 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 2. price_data表

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| id | INT | 自增主键 |
| currency_id | INT | 关联currencies表的外键 |
| symbol | VARCHAR(10) | 加密货币符号（冗余字段） |
| price | DECIMAL(20, 2) | 价格（开盘价和收盘价的均价） |
| timestamp | DATETIME | 时间戳 |
| created_at | TIMESTAMP | 创建时间 |

### 3. fear_greed_index表

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| date | DATE | 日期（主键） |
| value | INT | 贪婪恐惧指数值（0-100） |

### 4. trade_records表

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| id | INT | 自增主键 |
| date | DATE | 交易日期 |
| type | VARCHAR(10) | 交易类型（buy/sell） |
| amount | DECIMAL(20, 8) | 交易数量 |
| price | DECIMAL(20, 2) | 交易价格 |
| total_usd | DECIMAL(20, 2) | 交易总金额 |
| btc_holdings | DECIMAL(20, 8) | 持有BTC数量 |
| remaining_usd | DECIMAL(20, 2) | 剩余资金 |
| account_total | DECIMAL(20, 2) | 账户总价值 |
| created_at | TIMESTAMP | 创建时间 |

## 投资策略说明

### 买入策略

基于贪婪恐惧指数的买入策略：
- 贪婪恐惧指数 < 20：买入300美元
- 贪婪恐惧指数 < 25：买入200美元
- 贪婪恐惧指数 < 30：买入100美元

### 卖出策略

基于贪婪恐惧指数的卖出策略：
- 贪婪恐惧指数 >= 80：卖出5%的持仓
- 贪婪恐惧指数 >= 75：卖出3%的持仓
- 贪婪恐惧指数 >= 70：卖出2%的持仓

### 初始资金

- 初始资金：10,000美元
- 只投资BTC

## 数据完整性检查

### 检查逻辑

- 每天应包含288条数据（5分钟间隔）
- 检查从2020年至今的所有数据
- 日期范围不超过当前日期

### 修复方法

- 当发现数据不足时，从Binance API重新获取数据
- 使用开盘价和收盘价的均价作为价格
- 数据直接存储到price_data表中

## 价格计算方法

本项目使用开盘价和收盘价的均价作为价格：

```python
open_price = float(kline[1])  # 开盘价
close_price = float(kline[4])  # 收盘价
avg_price = (open_price + close_price) / 2  # 均价
```

## 注意事项

1. **API限制**：Binance API有请求频率限制，项目已添加延迟机制避免触发限制
2. **数据存储**：首次运行时会创建数据库和表结构，确保MySQL服务已启动
3. **投资风险**：本项目的投资策略仅供参考，不构成投资建议
4. **数据完整性**：数据检查可能需要较长时间，特别是首次运行时
5. **网络连接**：确保网络连接稳定，避免数据获取中断

## 扩展建议

1. **支持更多币种**：修改代码以支持更多加密货币
2. **增加技术指标**：添加更多技术指标到投资分析中
3. **可视化界面**：添加数据可视化界面，更直观地展示分析结果
4. **自动化交易**：集成交易API，实现自动化交易
5. **性能优化**：优化数据获取和存储性能，支持更大规模的数据

## 联系方式

如有问题或建议，欢迎联系项目维护者。

---

*项目版本：1.0.0*
*最后更新：2026-02-01*
