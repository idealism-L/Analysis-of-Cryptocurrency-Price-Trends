# Analysis of Cryptocurrency Price Trends

## 项目介绍

这是一个加密货币价格分析项目，通过币安API抓取BTC和ETH的价格数据，结合Alternative.me的恐惧贪婪指数，实现基于市场情绪的投资策略分析。

项目主要功能包括：
- 实时价格数据抓取（每5分钟一次）
- 历史价格数据获取（2023年至今）
- 恐惧贪婪指数数据集成
- 基于市场情绪的投资策略分析
- 交易记录存储和分析
- 数据库优化和管理

## 技术栈

- **编程语言**：Python 3.8+
- **数据库**：MySQL
- **核心库**：
  - `requests` - API调用
  - `schedule` - 定时任务
  - `pymysql` - 数据库操作
- **API**：
  - Binance API - 加密货币价格数据
  - Alternative.me API - 恐惧贪婪指数数据

## 项目结构

```
Analysis of Cryptocurrency Price Trends/
├── main.py                 # 核心功能模块
├── investment_analysis.py  # 投资策略分析模块
├── check_fng_data.py       # 恐惧贪婪指数数据检查工具
├── requirements.txt        # Python依赖配置
├── .gitignore              # Git忽略文件配置
└── README.md               # 项目说明文档
```

## 安装和运行

### 前置条件

- Python 3.8 或更高版本
- MySQL 数据库
- Git（可选，用于版本控制）

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/idealism-L/Analysis-of-Cryptocurrency-Price-Trends.git
cd Analysis-of-Cryptocurrency-Price-Trends
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **配置数据库**

确保MySQL数据库已启动，创建一个数据库（如`cryptocurrency`），并使用以下命令配置用户权限：

```sql
CREATE DATABASE cryptocurrency;
CREATE USER 'root'@'localhost' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON cryptocurrency.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

4. **运行项目**

运行主脚本开始获取数据：

```bash
python main.py
```

运行投资分析脚本：

```bash
python investment_analysis.py
```

## 数据库结构

项目使用了优化的数据库结构，包含以下表：

### 1. currencies 表

存储加密货币基本信息

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| id | INT | 自增主键 |
| symbol | VARCHAR(10) | 货币符号（如BTC, ETH） |
| name | VARCHAR(50) | 货币名称 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 2. price_data 表

存储加密货币价格数据

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| id | INT | 自增主键 |
| currency_id | INT | 外键，关联currencies表 |
| price | DECIMAL(18,6) | 价格 |
| timestamp | TIMESTAMP | 时间戳 |
| created_at | TIMESTAMP | 创建时间 |

### 3. fear_greed_index 表

存储恐惧贪婪指数数据

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| id | INT | 自增主键 |
| date | DATE | 日期 |
| value | INT | 恐惧贪婪指数值（0-100） |

### 4. trade_records 表

存储交易记录

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| id | INT | 自增主键 |
| date | DATE | 交易日期 |
| type | ENUM('buy', 'sell') | 交易类型 |
| price | DECIMAL(18,6) | 交易价格 |
| amount | DECIMAL(18,8) | 交易数量 |
| total_usd | DECIMAL(18,2) | 交易金额（USD） |
| btc_holdings | DECIMAL(18,8) | 持有BTC数量 |
| remaining_usd | DECIMAL(18,2) | 剩余USD金额 |
| account_total | DECIMAL(18,2) | 账户总价值（USD） |
| created_at | TIMESTAMP | 创建时间 |

## 投资策略

项目实现了基于恐惧贪婪指数的渐进式投资策略：

### 买入策略

- 当恐惧贪婪指数 **≤ 30** 时：买入 100 USD
- 当恐惧贪婪指数 **≤ 25** 时：买入 200 USD
- 当恐惧贪婪指数 **≤ 20** 时：买入 300 USD

### 卖出策略

- 当恐惧贪婪指数 **≥ 70** 时：卖出持有BTC的 2%
- 当恐惧贪婪指数 **≥ 75** 时：卖出持有BTC的 3%
- 当恐惧贪婪指数 **≥ 80** 时：卖出持有BTC的 5%

### 投资档位

- 初始投资金额：10,000 USD
- 每10,000 USD为一个投资档位
- 当账户金额翻倍（20,000 USD）时，买入金额改为200 USD
- 当账户金额达到30,000 USD时，买入金额改为300 USD

## API使用说明

### Binance API

用于获取加密货币价格数据：
- 实时价格：`https://api.binance.com/api/v3/ticker/price`
- 历史K线数据：`https://api.binance.com/api/v3/klines`

### Alternative.me API

用于获取比特币恐惧贪婪指数：
- 历史数据：`https://api.alternative.me/fng/`

## 注意事项

1. **API限制**：
   - 项目已实现API调用限制和防封禁措施
   - 历史数据获取时会自动添加随机延迟
   - 恐惧贪婪指数数据已实现缓存机制

2. **数据库配置**：
   - 默认数据库连接配置为 `root:123456@localhost:3306/cryptocurrency`
   - 如需修改，请在代码中相应位置更新

3. **性能优化**：
   - 数据批量处理减少数据库操作
   - 恐惧贪婪指数数据缓存减少API调用
   - 定时任务合理安排避免资源占用过高

4. **数据完整性**：
   - 项目会自动从最新数据时间戳开始抓取历史数据
   - 确保数据的连续性和完整性

## 运行示例

### 启动数据抓取

```bash
python main.py
```

输出示例：

```
启动加密货币价格分析工具...
连接数据库成功！
创建必要的数据库表...
数据库表检查完成！
开始获取历史数据...
从 2023-01-01 开始获取 BTC 历史数据...
获取历史数据完成！
开始获取 ETH 历史数据...
获取历史数据完成！
定时任务已启动。每5分钟获取一次价格。
按Ctrl+C停止脚本。

正在获取价格...
已获取价格: BTC: 42000.50, ETH: 2100.75
价格已保存到数据库
```

### 运行投资分析

```bash
python investment_analysis.py
```

输出示例：

```
连接数据库成功！
开始分析投资策略...
交易记录已保存到数据库
分析完成！

交易记录:
+------------+------+-------------+-------------+-------------+-------------+-------------+-------------+
|    日期    | 类型 |    数量     |    价格     |    金额     |  持有BTC    |   剩余U     |   总额U     |
+------------+------+-------------+-------------+-------------+-------------+-------------+-------------+
| 2023-01-01 | buy  | 0.00238095  | 42000.00    | 100.00      | 0.00238095  | 9900.00     | 10000.00    |
| 2023-01-15 | sell | 0.00004762  | 43000.00    | 2.05        | 0.00233333  | 9902.05     | 10005.00    |
+------------+------+-------------+-------------+-------------+-------------+-------------+-------------+

最终账户状态:
- 持有BTC: 0.50000000
- 剩余U: 15000.00
- 总额U: 35000.00
```

## 项目优化

项目在开发过程中进行了多次优化：

1. **数据库结构优化**：
   - 初始使用单表存储所有数据
   - 优化为多表结构，分离货币信息、价格数据和交易记录
   - 进一步优化，将恐惧贪婪指数数据移至独立表

2. **性能优化**：
   - 实现API调用防封禁措施
   - 添加数据缓存机制
   - 优化数据库查询

3. **功能扩展**：
   - 添加交易记录存储
   - 实现渐进式投资策略
   - 添加账户价值计算

## 贡献指南

欢迎贡献代码和提出建议！请按照以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- GitHub: [idealism-L](https://github.com/idealism-L)
- 项目地址: [Analysis of Cryptocurrency Price Trends](https://github.com/idealism-L/Analysis-of-Cryptocurrency-Price-Trends)

---

**注意**：本项目仅供学习和研究使用，不构成投资建议。加密货币投资存在高风险，请谨慎决策。