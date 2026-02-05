# 导入必要的库
import pymysql
from datetime import datetime, timedelta

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'cryptocurrency_analysis',
    'charset': 'utf8mb4'
}

class InvestmentAnalyzer:
    """
    加密货币投资策略分析器
    基于贪婪恐惧指数进行投资决策
    """
    def __init__(self):
        """
        初始化投资分析器
        """
        self.initial_funds = 10000  # 初始资金
        self.current_funds = 10000  # 当前资金
        self.btc_holdings = 0  # 持有BTC数量
        self.eth_holdings = 0  # 持有ETH数量
        self.btc_average_price = 0  # BTC持有均价
        self.eth_average_price = 0  # ETH持有均价
        self.trade_records = []  # 交易记录
        self.last_buy_date = None  # 上次买入日期
        self.last_sell_date = None  # 上次卖出日期
        
        # 投资策略参数（集中管理，方便调整）
        self.investment_strategy = {
            'buy_thresholds': [
                {'fng': 10, 'btc': 500, 'eth': 300},
                {'fng': 15, 'btc': 200, 'eth': 100},
                {'fng': 20, 'btc': 100, 'eth': 50}
            ],
            'sell_thresholds': [
                {'fng': 90, 'btc': 0.03, 'eth': 0.05},
                {'fng': 85, 'btc': 0.01, 'eth': 0.02},
                {'fng': 80, 'btc': 0.005, 'eth': 0.01}
            ]
        }
        
        self.create_trade_table()  # 创建交易记录表
    
    def get_db_connection(self):
        """
        获取数据库连接
        """
        try:
            conn = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                charset=DB_CONFIG['charset']
            )
            return conn
        except Exception as error:
            print('数据库连接失败:', str(error))
            return None
    
    def fetch_and_store_price_data(self, symbol, start_date, end_date):
        """
        从外部API获取价格数据并存储到数据库
        注意：此函数为框架，实际数据获取由main.py中的fetch_historical_data函数处理
        """
        print(f"正在获取 {symbol} 价格数据...")
        # 实际数据获取由main.py中的fetch_historical_data函数处理
        # 这里只返回True作为占位符
        return True
    
    def fetch_and_store_fng_data(self, start_date, end_date):
        """
        从外部API获取贪婪恐惧指数数据并存储到数据库
        注意：此函数为框架，实际数据获取由main.py中的update_fng_data_2020_to_present函数处理
        """
        print("正在获取贪婪恐惧指数数据...")
        # 实际数据获取由main.py中的update_fng_data_2020_to_present函数处理
        # 这里只返回True作为占位符
        return True
    
    def update_data(self):
        """
        更新数据，从最新日期开始获取到当前日期的数据
        """
        print("正在更新数据...")
        
        # 获取最新时间戳
        latest_price_timestamp = self.get_latest_timestamp('price_data', 'timestamp')
        latest_fng_date = self.get_latest_timestamp('fear_greed_index', 'date')
        
        # 确定起始日期
        if latest_price_timestamp:
            price_start_date = latest_price_timestamp
        else:
            price_start_date = datetime(2020, 1, 1)
        
        if latest_fng_date:
            fng_start_date = latest_fng_date
        else:
            fng_start_date = datetime(2020, 1, 1)
        
        # 结束日期为当前日期
        end_date = datetime.now()
        
        # 获取价格数据
        self.fetch_and_store_price_data('BTC', price_start_date, end_date)
        self.fetch_and_store_price_data('ETH', price_start_date, end_date)
        
        # 获取贪婪恐惧指数数据
        self.fetch_and_store_fng_data(fng_start_date, end_date)
        
        print("数据更新完成")
        return True
    
    def create_trade_table(self):
        """
        创建交易记录表
        存在则删除再创建
        """
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # 删除已存在的表
            cursor.execute("DROP TABLE IF EXISTS trade_records")
            
            # 创建交易记录表
            create_table_sql = """
            CREATE TABLE trade_records (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '交易记录ID',
                trade_date DATE NOT NULL COMMENT '交易日期',
                trade_type VARCHAR(10) NOT NULL COMMENT '交易类型：buy或sell',
                btc_trade_amount DECIMAL(20, 8) NOT NULL COMMENT 'BTC交易数量',
                btc_trade_value DECIMAL(20, 2) NOT NULL COMMENT 'BTC交易金额',
                btc_trade_price DECIMAL(20, 2) NOT NULL COMMENT 'BTC交易时价格',
                eth_trade_amount DECIMAL(20, 8) NOT NULL COMMENT 'ETH交易数量',
                eth_trade_value DECIMAL(20, 2) NOT NULL COMMENT 'ETH交易金额',
                eth_trade_price DECIMAL(20, 2) NOT NULL COMMENT 'ETH交易时价格',
                total_trade_value DECIMAL(20, 2) NOT NULL COMMENT '交易总金额',
                btc_holdings DECIMAL(20, 8) NOT NULL COMMENT 'BTC持仓数量',
                eth_holdings DECIMAL(20, 8) NOT NULL COMMENT 'ETH持仓数量',
                btc_average_price DECIMAL(20, 2) NOT NULL COMMENT 'BTC持仓均价',
                eth_average_price DECIMAL(20, 2) NOT NULL COMMENT 'ETH持仓均价',
                remaining_usd DECIMAL(20, 2) NOT NULL COMMENT '剩余资金（USD）',
                account_total DECIMAL(20, 2) NOT NULL COMMENT '账户总价值',
                trade_note TEXT NOT NULL COMMENT '交易备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易记录表';
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
            print("交易记录表已重新创建")
            
            cursor.close()
            conn.close()
        except Exception as error:
            print('创建交易记录表失败:', str(error))
    
    def clear_trade_table(self):
        """
        清空交易记录表
        """
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # 清空表数据
            cursor.execute("TRUNCATE TABLE trade_records")
            conn.commit()
            print("交易记录表已清空")
            
            cursor.close()
            conn.close()
        except Exception as error:
            print('清空交易记录表失败:', str(error))
    
    def save_trade_to_database(self, trade_record):
        """
        将交易记录保存到数据库
        """
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # 插入交易记录
            insert_sql = """
            INSERT INTO trade_records (
                trade_date, trade_type, btc_trade_amount, btc_trade_value, btc_trade_price, 
                eth_trade_amount, eth_trade_value, eth_trade_price, total_trade_value, 
                btc_holdings, eth_holdings, btc_average_price, eth_average_price, 
                remaining_usd, account_total, trade_note
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                trade_record['trade_date'],
                trade_record['trade_type'],
                trade_record.get('btc_trade_amount', 0),
                trade_record.get('btc_trade_value', 0),
                trade_record.get('btc_trade_price', 0),
                trade_record.get('eth_trade_amount', 0),
                trade_record.get('eth_trade_value', 0),
                trade_record.get('eth_trade_price', 0),
                trade_record['total_trade_value'],
                trade_record['btc_holdings'],
                trade_record.get('eth_holdings', self.eth_holdings),
                trade_record.get('btc_average_price', 0),
                trade_record.get('eth_average_price', 0),
                trade_record['remaining_usd'],
                trade_record['account_total'],
                trade_record.get('trade_note', '')
            ))
            conn.commit()
            
            cursor.close()
            conn.close()
        except Exception as error:
            print('保存交易记录到数据库失败:', str(error))
    
    def get_latest_timestamp(self, table, date_column):
        """
        获取数据库中指定表的最新时间戳
        """
        try:
            conn = self.get_db_connection()
            if not conn:
                return None
            
            cursor = conn.cursor()
            
            query = f"SELECT MAX({date_column}) FROM {table}"
            cursor.execute(query)
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result and result[0]:
                return result[0]
            return None
        except Exception as error:
            print(f'获取最新时间戳失败: {str(error)}')
            return None
    
    def preload_data(self):
        """
        预加载所有需要的数据，减少数据库连接次数
        """
        print("正在预加载数据...")
        
        try:
            conn = self.get_db_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # 预加载BTC和ETH的日均价
            self.daily_prices = {'BTC': {}, 'ETH': {}}
            
            # 预加载BTC的日均价
            query = """
            SELECT DATE(timestamp) as date, AVG(price) as avg_price
            FROM price_data
            WHERE symbol = 'BTC' AND DATE(timestamp) >= '2020-01-01'
            GROUP BY DATE(timestamp)
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                # 确保日期是字符串格式
                date_str = row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])
                self.daily_prices['BTC'][date_str] = float(row[1])
            
            # 预加载ETH的日均价
            query = """
            SELECT DATE(timestamp) as date, AVG(price) as avg_price
            FROM price_data
            WHERE symbol = 'ETH' AND DATE(timestamp) >= '2020-01-01'
            GROUP BY DATE(timestamp)
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                # 确保日期是字符串格式
                date_str = row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])
                self.daily_prices['ETH'][date_str] = float(row[1])
            
            # 预加载贪婪恐惧指数
            self.daily_fng = {}
            query = """
            SELECT date, value as fear_greed_index
            FROM fear_greed_index
            WHERE date >= '2020-01-01'
            ORDER BY date
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                # 确保日期是字符串格式
                date_str = row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])
                self.daily_fng[date_str] = int(row[1])
            
            cursor.close()
            conn.close()
            
            # 打印一些样本数据用于调试
            print(f"预加载完成: {len(self.daily_prices)} 天价格数据, {len(self.daily_fng)} 天贪婪恐惧指数数据")
            
            # 打印前5天的数据样本
            print("\n数据样本:")
            sample_dates = list(self.daily_prices.keys())[:5]
            for date in sample_dates:
                fng = self.daily_fng.get(date, 'N/A')
                price = self.daily_prices.get(date, 'N/A')
                print(f"{date}: FNG={fng}, Price={price}")
            
            # 打印一些应该触发交易的日期
            print("\n潜在交易日期:")
            # 从配置中获取买入和卖出的阈值
            buy_thresholds = [t['fng'] for t in self.investment_strategy['buy_thresholds']]
            sell_thresholds = [t['fng'] for t in self.investment_strategy['sell_thresholds']]
            min_buy_threshold = min(buy_thresholds) if buy_thresholds else 30
            max_sell_threshold = max(sell_thresholds) if sell_thresholds else 65
            
            for date, fng in self.daily_fng.items():
                if fng < min_buy_threshold and date in self.daily_prices:
                    print(f"{date}: FNG={fng} (买入信号)")
                elif fng > max_sell_threshold and date in self.daily_prices:
                    print(f"{date}: FNG={fng} (卖出信号)")
            
            return True
        except Exception as error:
            print('预加载数据失败:', str(error))
            import traceback
            traceback.print_exc()
            return False
    
    def get_daily_average_price(self, symbol, date):
        """
        获取指定日期的日均价
        """
        if hasattr(self, 'daily_prices') and symbol in self.daily_prices:
            # 尝试直接匹配
            if date in self.daily_prices[symbol]:
                return self.daily_prices[symbol][date]
            # 尝试不同格式的日期匹配
            for stored_date in self.daily_prices[symbol]:
                if str(stored_date) == date:
                    return self.daily_prices[symbol][stored_date]
        return None
    
    def get_daily_fear_greed_index(self, date):
        """
        获取指定日期的贪婪恐惧指数
        """
        if hasattr(self, 'daily_fng'):
            # 尝试直接匹配
            if date in self.daily_fng:
                return self.daily_fng[date]
            # 尝试不同格式的日期匹配
            for stored_date in self.daily_fng:
                if str(stored_date) == date:
                    return self.daily_fng[stored_date]
        return None
    
    def calculate_investment_amount(self, fng):
        """
        根据贪婪恐惧指数计算投资金额
        返回(BTC投资金额, ETH投资金额)的元组
        """
        # 按贪婪恐惧指数从低到高排序
        sorted_buy_thresholds = sorted(self.investment_strategy['buy_thresholds'], key=lambda x: x['fng'])
        
        for threshold in sorted_buy_thresholds:
            if fng < threshold['fng']:
                return (threshold['btc'], threshold['eth'])
        
        return (0, 0)  # 所有阈值以上不买入
    
    def buy_btc(self, date, price, fng):
        """
        买入BTC
        """
        btc_investment, eth_investment = self.calculate_investment_amount(fng)
        
        # 检查资金是否足够购买BTC
        if self.current_funds < btc_investment:
            print(f"{date}: 资金不足，无法买入 {btc_investment} 美元的BTC")
            return False
        
        # 计算可购买的BTC数量
        btc_amount = btc_investment / price
        
        # 更新持仓和资金
        self.btc_holdings += btc_amount
        self.current_funds -= btc_investment
        
        # 更新BTC持有均价（使用正确的加权平均计算方法）
        if self.btc_holdings > 0:
            # 持仓均价 = （买入前的持仓均价 * 当前数量 + 此次买入价值）/ 买入后总数量
            new_btc_average_price = (self.btc_average_price * (self.btc_holdings - btc_amount) + btc_investment) / self.btc_holdings
            self.btc_average_price = new_btc_average_price
        else:
            self.btc_average_price = 0
        
        # 获取ETH价格
        eth_price = self.get_daily_average_price('ETH', date)
        if not eth_price:
            eth_price = price  # 如果没有ETH价格，使用BTC价格作为备选
        
        # 计算账户总额
        account_total = self.current_funds + (self.btc_holdings * price) + (self.eth_holdings * eth_price)
        
        # 生成交易备注
        note = f"交易类型: buy | 购买类型: BTC | 购买数量: {btc_amount:.6f} | 当前持仓: BTC={self.btc_holdings:.6f}, ETH={self.eth_holdings:.6f} | 总价值: ${account_total:.2f}"
        
        # 记录交易
        trade_record = {
            'date': date,
            'type': 'buy',
            'price': price,
            'amount': btc_amount,
            'total_usd': btc_investment,
            'btc_holdings': self.btc_holdings,
            'eth_holdings': self.eth_holdings,
            'btc_average_price': self.btc_average_price,
            'eth_average_price': self.eth_average_price,
            'remaining_usd': self.current_funds,
            'account_total': account_total,
            'note': note
        }
        self.trade_records.append(trade_record)
        
        # 保存到数据库
        self.save_trade_to_database(trade_record)
        
        print(f"{date}: 买入 {btc_amount:.6f} BTC, 价格: ${price:.2f}, 花费: ${btc_investment:.2f}")
        print(f"  当前持有: {self.btc_holdings:.6f} BTC, 剩余资金: ${self.current_funds:.2f}")
        print(f"  账户总额: ${account_total:.2f}")
        
        self.last_buy_date = date
        return True
    
    def buy_eth(self, date, price, fng):
        """
        买入ETH
        """
        btc_investment, eth_investment = self.calculate_investment_amount(fng)
        
        # 检查资金是否足够购买ETH
        if self.current_funds < eth_investment:
            print(f"{date}: 资金不足，无法买入 {eth_investment} 美元的ETH")
            return False
        
        # 计算可购买的ETH数量
        eth_amount = eth_investment / price
        
        # 更新持仓和资金
        self.eth_holdings += eth_amount
        self.current_funds -= eth_investment
        
        # 更新ETH持有均价（使用正确的加权平均计算方法）
        if self.eth_holdings > 0:
            # 持仓均价 = （买入前的持仓均价 * 当前数量 + 此次买入价值）/ 买入后总数量
            new_eth_average_price = (self.eth_average_price * (self.eth_holdings - eth_amount) + eth_investment) / self.eth_holdings
            self.eth_average_price = new_eth_average_price
        else:
            self.eth_average_price = 0
        
        # 获取BTC价格
        btc_price = self.get_daily_average_price('BTC', date)
        if not btc_price:
            btc_price = price  # 如果没有BTC价格，使用ETH价格作为备选
        
        # 计算账户总额
        account_total = self.current_funds + (self.btc_holdings * btc_price) + (self.eth_holdings * price)
        
        # 生成交易备注
        note = f"交易类型: buy | 购买类型: ETH | 购买数量: {eth_amount:.6f} | 当前持仓: BTC={self.btc_holdings:.6f}, ETH={self.eth_holdings:.6f} | 总价值: ${account_total:.2f}"
        
        # 记录交易
        trade_record = {
            'date': date,
            'type': 'buy',
            'price': price,
            'amount': eth_amount,
            'total_usd': eth_investment,
            'btc_holdings': self.btc_holdings,
            'eth_holdings': self.eth_holdings,
            'btc_average_price': self.btc_average_price,
            'eth_average_price': self.eth_average_price,
            'remaining_usd': self.current_funds,
            'account_total': account_total,
            'note': note
        }
        self.trade_records.append(trade_record)
        
        # 保存到数据库
        self.save_trade_to_database(trade_record)
        
        print(f"{date}: 买入 {eth_amount:.6f} ETH, 价格: ${price:.2f}, 花费: ${eth_investment:.2f}")
        print(f"  当前持有: {self.eth_holdings:.6f} ETH, 剩余资金: ${self.current_funds:.2f}")
        print(f"  账户总额: ${account_total:.2f}")
        
        return True
    
    def buy_crypto(self, date, btc_price, eth_price, fng):
        """
        合并买入BTC和ETH
        """
        btc_investment, eth_investment = self.calculate_investment_amount(fng)
        
        # 检查资金是否足够购买BTC
        if self.current_funds < btc_investment:
            print(f"{date}: 资金不足，无法买入 {btc_investment} 美元的BTC")
            return False
        
        # 计算可购买的BTC数量
        btc_amount = btc_investment / btc_price
        
        # 更新BTC持仓和资金
        self.btc_holdings += btc_amount
        self.current_funds -= btc_investment
        
        # 更新BTC持有均价（使用正确的加权平均计算方法）
        if self.btc_holdings > 0:
            # 持仓均价 = （买入前的持仓均价 * 当前数量 + 此次买入价值）/ 买入后总数量
            new_btc_average_price = (self.btc_average_price * (self.btc_holdings - btc_amount) + btc_investment) / self.btc_holdings
            self.btc_average_price = new_btc_average_price
        else:
            self.btc_average_price = 0
        
        # 检查资金是否足够购买ETH
        if self.current_funds < eth_investment:
            print(f"{date}: 资金不足，无法买入 {eth_investment} 美元的ETH")
            return False
        
        # 计算可购买的ETH数量
        eth_amount = eth_investment / eth_price
        
        # 更新ETH持仓和资金
        self.eth_holdings += eth_amount
        self.current_funds -= eth_investment
        
        # 更新ETH持有均价（使用正确的加权平均计算方法）
        if self.eth_holdings > 0:
            # 持仓均价 = （买入前的持仓均价 * 当前数量 + 此次买入价值）/ 买入后总数量
            new_eth_average_price = (self.eth_average_price * (self.eth_holdings - eth_amount) + eth_investment) / self.eth_holdings
            self.eth_average_price = new_eth_average_price
        else:
            self.eth_average_price = 0
        
        # 计算账户总额
        account_total = self.current_funds + (self.btc_holdings * btc_price) + (self.eth_holdings * eth_price)
        
        # 生成交易备注，包含贪恐指数
        trade_note = f"当日贪恐指数: {fng} - 交易类型: buy - 以${btc_price:.2f}价格买入{btc_amount:.6f}BTC - 以${eth_price:.2f}价格买入{eth_amount:.6f}ETH"
        
        # 记录交易
        trade_record = {
            'trade_date': date,
            'trade_type': 'buy',
            'btc_trade_amount': btc_amount,  # BTC购买数量
            'btc_trade_value': btc_investment,  # BTC交易金额
            'btc_trade_price': btc_price,  # BTC交易时价格
            'eth_trade_amount': eth_amount,  # ETH购买数量
            'eth_trade_value': eth_investment,  # ETH交易金额
            'eth_trade_price': eth_price,  # ETH交易时价格
            'total_trade_value': btc_investment + eth_investment,  # 总交易金额
            'btc_holdings': self.btc_holdings,
            'eth_holdings': self.eth_holdings,
            'btc_average_price': self.btc_average_price,
            'eth_average_price': self.eth_average_price,
            'remaining_usd': self.current_funds,
            'account_total': account_total,
            'trade_note': trade_note
        }
        self.trade_records.append(trade_record)
        
        # 保存到数据库
        self.save_trade_to_database(trade_record)
        
        buy_details = []
        if btc_amount > 0:
            buy_details.append(f"买入 {btc_amount:.6f} BTC, 花费: ${btc_investment:.2f}")
        if eth_amount > 0:
            buy_details.append(f"买入 {eth_amount:.6f} ETH, 花费: ${eth_investment:.2f}")
        print(f"{date}: {'; '.join(buy_details)}")
        print(f"  当前持有: BTC={self.btc_holdings:.6f}, ETH={self.eth_holdings:.6f}, 剩余资金: ${self.current_funds:.2f}")
        print(f"  账户总额: ${account_total:.2f}")
        
        self.last_buy_date = date
        return True
    
    def sell_btc(self, date, price, fng):
        """
        卖出BTC
        """
        if self.btc_holdings <= 0:
            print(f"{date}: 没有BTC可卖")
            return False
        
        # 根据贪婪恐惧指数确定卖出比例
        # 按贪婪恐惧指数从高到低排序
        sorted_sell_thresholds = sorted(self.investment_strategy['sell_thresholds'], key=lambda x: x['fng'], reverse=True)
        
        sell_percentage = None
        for threshold in sorted_sell_thresholds:
            if fng >= threshold['fng']:
                sell_percentage = threshold['btc']
                break
        
        if sell_percentage is None:
            return False  # 所有阈值以下不卖出
        
        # 计算卖出数量
        sell_amount = self.btc_holdings * sell_percentage
        sell_value = sell_amount * price
        
        # 更新持仓和资金
        self.btc_holdings -= sell_amount
        self.current_funds += sell_value
        
        # 卖出不影响总投资金额和均价，因为均价是基于买入成本计算的
        # 只需要更新持仓数量，总投资金额保持不变
        # 因此均价也保持不变，无需重新计算
        
        # 获取ETH价格
        eth_price = self.get_daily_average_price('ETH', date)
        if not eth_price:
            eth_price = price  # 如果没有ETH价格，使用BTC价格作为备选
        
        # 计算账户总额
        account_total = self.current_funds + (self.btc_holdings * price) + (self.eth_holdings * eth_price)
        
        # 生成交易备注
        note = f"交易类型: sell | 出售类型: BTC | 出售数量: {sell_amount:.6f} | 当前持仓: BTC={self.btc_holdings:.6f}, ETH={self.eth_holdings:.6f} | 总价值: ${account_total:.2f}"
        
        # 记录交易
        trade_record = {
            'date': date,
            'type': 'sell',
            'btc_price': price,
            'eth_price': eth_price,
            'btc_amount': sell_amount,  # BTC卖出数量
            'eth_amount': 0,  # ETH卖出数量
            'total_usd': sell_value,
            'btc_holdings': self.btc_holdings,
            'eth_holdings': self.eth_holdings,
            'btc_average_price': self.btc_average_price,
            'eth_average_price': self.eth_average_price,
            'remaining_usd': self.current_funds,
            'account_total': account_total,
            'note': note
        }
        self.trade_records.append(trade_record)
        
        # 保存到数据库
        self.save_trade_to_database(trade_record)
        
        print(f"{date}: 卖出 {sell_amount:.6f} BTC, 价格: ${price:.2f}, 获得: ${sell_value:.2f}")
        print(f"  当前持有: {self.btc_holdings:.6f} BTC, 剩余资金: ${self.current_funds:.2f}")
        print(f"  账户总额: ${account_total:.2f}")
        
        self.last_sell_date = date
        return True
    
    def sell_eth(self, date, price, fng):
        """
        卖出ETH
        """
        if self.eth_holdings <= 0:
            print(f"{date}: 没有ETH可卖")
            return False
        
        # 根据贪婪恐惧指数确定卖出比例
        # 按贪婪恐惧指数从高到低排序
        sorted_sell_thresholds = sorted(self.investment_strategy['sell_thresholds'], key=lambda x: x['fng'], reverse=True)
        
        sell_percentage = None
        for threshold in sorted_sell_thresholds:
            if fng >= threshold['fng']:
                sell_percentage = threshold['eth']
                break
        
        if sell_percentage is None:
            return False  # 所有阈值以下不卖出
        
        # 计算卖出数量
        sell_amount = self.eth_holdings * sell_percentage
        sell_value = sell_amount * price
        
        # 更新持仓和资金
        self.eth_holdings -= sell_amount
        self.current_funds += sell_value
        
        # 卖出不影响总投资金额和均价，因为均价是基于买入成本计算的
        # 只需要更新持仓数量，总投资金额保持不变
        # 因此均价也保持不变，无需重新计算
        
        # 获取BTC价格
        btc_price = self.get_daily_average_price('BTC', date)
        if not btc_price:
            btc_price = price  # 如果没有BTC价格，使用ETH价格作为备选
        
        # 计算账户总额
        account_total = self.current_funds + (self.btc_holdings * btc_price) + (self.eth_holdings * price)
        
        # 生成交易备注
        note = f"交易类型: sell | 出售类型: ETH | 出售数量: {sell_amount:.6f} | 当前持仓: BTC={self.btc_holdings:.6f}, ETH={self.eth_holdings:.6f} | 总价值: ${account_total:.2f}"
        
        # 记录交易
        trade_record = {
            'date': date,
            'type': 'sell',
            'btc_price': btc_price,
            'eth_price': price,
            'btc_amount': 0,  # BTC卖出数量
            'eth_amount': sell_amount,  # ETH卖出数量
            'total_usd': sell_value,
            'btc_holdings': self.btc_holdings,
            'eth_holdings': self.eth_holdings,
            'btc_average_price': self.btc_average_price,
            'eth_average_price': self.eth_average_price,
            'remaining_usd': self.current_funds,
            'account_total': account_total,
            'note': note
        }
        self.trade_records.append(trade_record)
        
        # 保存到数据库
        self.save_trade_to_database(trade_record)
        
        print(f"{date}: 卖出 {sell_amount:.6f} ETH, 价格: ${price:.2f}, 获得: ${sell_value:.2f}")
        print(f"  当前持有: {self.eth_holdings:.6f} ETH, 剩余资金: ${self.current_funds:.2f}")
        print(f"  账户总额: ${account_total:.2f}")
        
        return True
    
    def sell_crypto(self, date, btc_price, eth_price, fng):
        """
        合并卖出BTC和ETH
        """
        # 检查是否有BTC可卖
        if self.btc_holdings <= 0 and self.eth_holdings <= 0:
            print(f"{date}: 没有加密货币可卖")
            return False
        
        # 根据贪婪恐惧指数确定卖出比例
        # 按贪婪恐惧指数从高到低排序
        sorted_sell_thresholds = sorted(self.investment_strategy['sell_thresholds'], key=lambda x: x['fng'], reverse=True)
        
        btc_sell_percentage = None
        eth_sell_percentage = None
        
        for threshold in sorted_sell_thresholds:
            if fng >= threshold['fng']:
                btc_sell_percentage = threshold['btc']
                eth_sell_percentage = threshold['eth']
                break
        
        if btc_sell_percentage is None or eth_sell_percentage is None:
            return False  # 所有阈值以下不卖出
        
        # 计算BTC卖出数量和价值
        if self.btc_holdings > 0:
            btc_sell_amount = self.btc_holdings * btc_sell_percentage
            btc_sell_value = btc_sell_amount * btc_price
            
            # 更新BTC持仓和资金
            self.btc_holdings -= btc_sell_amount
            self.current_funds += btc_sell_value
        else:
            btc_sell_amount = 0
            btc_sell_value = 0
        
        # 计算ETH卖出数量和价值
        if self.eth_holdings > 0:
            eth_sell_amount = self.eth_holdings * eth_sell_percentage
            eth_sell_value = eth_sell_amount * eth_price
            
            # 更新ETH持仓和资金
            self.eth_holdings -= eth_sell_amount
            self.current_funds += eth_sell_value
        else:
            eth_sell_amount = 0
            eth_sell_value = 0
        
        # 计算总卖出价值
        total_sell_value = btc_sell_value + eth_sell_value
        
        # 计算账户总额
        account_total = self.current_funds + (self.btc_holdings * btc_price) + (self.eth_holdings * eth_price)
        
        # 生成交易备注
        trade_note = f"当日贪恐指数: {fng} - 交易类型: sell - 以${btc_price:.2f}价格卖出{btc_sell_amount:.6f}BTC - 以${eth_price:.2f}价格卖出{eth_sell_amount:.6f}ETH"
        
        # 记录交易
        trade_record = {
            'trade_date': date,
            'trade_type': 'sell',
            'btc_trade_amount': btc_sell_amount,  # BTC卖出数量
            'btc_trade_value': btc_sell_value,  # BTC交易金额
            'btc_trade_price': btc_price,  # BTC交易时价格
            'eth_trade_amount': eth_sell_amount,  # ETH卖出数量
            'eth_trade_value': eth_sell_value,  # ETH交易金额
            'eth_trade_price': eth_price,  # ETH交易时价格
            'total_trade_value': total_sell_value,  # 总交易金额
            'btc_holdings': self.btc_holdings,
            'eth_holdings': self.eth_holdings,
            'btc_average_price': self.btc_average_price,
            'eth_average_price': self.eth_average_price,
            'remaining_usd': self.current_funds,
            'account_total': account_total,
            'trade_note': trade_note
        }
        self.trade_records.append(trade_record)
        
        # 保存到数据库
        self.save_trade_to_database(trade_record)
        
        # 打印交易信息
        if btc_sell_amount > 0 or eth_sell_amount > 0:
            sell_details = []
            if btc_sell_amount > 0:
                sell_details.append(f"卖出 {btc_sell_amount:.6f} BTC, 获得: ${btc_sell_value:.2f}")
            if eth_sell_amount > 0:
                sell_details.append(f"卖出 {eth_sell_amount:.6f} ETH, 获得: ${eth_sell_value:.2f}")
            print(f"{date}: {'; '.join(sell_details)}")
            print(f"  当前持有: BTC={self.btc_holdings:.6f}, ETH={self.eth_holdings:.6f}, 剩余资金: ${self.current_funds:.2f}")
            print(f"  账户总额: ${account_total:.2f}")
        
        self.last_sell_date = date
        return True
    
    def analyze_investment(self):
        """
        分析投资策略
        """
        print("\n" + "=" * 90)
        print("        加密货币投资策略分析")
        print("=" * 90)
        print(f"初始资金: ${self.initial_funds:.2f}")
        
        # 动态生成投资策略描述
        buy_strategy_lines = []
        for threshold in sorted(self.investment_strategy['buy_thresholds'], key=lambda x: x['fng']):
            buy_strategy_lines.append(f"{threshold['fng']}以下买入{threshold['btc']}u BTC和{threshold['eth']}u ETH")
        buy_strategy = "，".join(buy_strategy_lines)
        print(f"投资策略: 贪婪恐惧指数{buy_strategy}")
        
        # 动态生成卖出策略描述
        sell_strategy_lines = []
        for threshold in sorted(self.investment_strategy['sell_thresholds'], key=lambda x: x['fng']):
            btc_percent = threshold['btc'] * 100
            eth_percent = threshold['eth'] * 100
            sell_strategy_lines.append(f"{threshold['fng']}以上卖出BTC {btc_percent:.0f}%和ETH {eth_percent:.0f}%")
        sell_strategy = "，".join(sell_strategy_lines)
        print(f"卖出策略: 贪婪恐惧指数{sell_strategy}")
        
        # 强制从2020年开始分析，以获取完整的历史数据
        start_date = datetime(2020, 1, 1)
        print(f"从初始日期开始: {start_date.strftime('%Y年%m月%d日')}")
        
        end_date = datetime.now()
        print(f"时间范围: {start_date.strftime('%Y年%m月%d日')} - {end_date.strftime('%Y年%m月%d日')}")
        print("=" * 90)
        
        # 更新数据
        if not self.update_data():
            print("数据更新失败，无法继续分析")
            return
        
        # 预加载数据
        if not self.preload_data():
            print("数据预加载失败，无法继续分析")
            return
        
        # 遍历从起始日期到现在的每一天
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # 获取当日的贪婪恐惧指数
            fng = self.get_daily_fear_greed_index(date_str)
            if fng is None:
                current_date += timedelta(days=1)
                continue
            
            # 获取当日BTC均价
            btc_price = self.get_daily_average_price('BTC', date_str)
            if btc_price is None:
                current_date += timedelta(days=1)
                continue
            
            # 获取当日ETH均价
            eth_price = self.get_daily_average_price('ETH', date_str)
            if eth_price is None:
                current_date += timedelta(days=1)
                continue
            
            # 检查是否需要操作
            if fng is not None and btc_price is not None and eth_price is not None:
                # 从配置中获取最大的买入阈值和最小的卖出阈值
                buy_thresholds = [t['fng'] for t in self.investment_strategy['buy_thresholds']]
                sell_thresholds = [t['fng'] for t in self.investment_strategy['sell_thresholds']]
                max_buy_threshold = max(buy_thresholds) if buy_thresholds else 20
                min_sell_threshold = min(sell_thresholds) if sell_thresholds else 80
                
                if fng < max_buy_threshold:
                    # 贪婪恐惧指数低于最大买入阈值，买入
                    if self.last_buy_date != date_str:
                        print(f"\n{date_str}: 贪婪恐惧指数={fng}, BTC均价=${btc_price:.2f}, ETH均价=${eth_price:.2f}")
                        # 合并买入BTC和ETH
                        self.buy_crypto(date_str, btc_price, eth_price, fng)
                elif fng >= min_sell_threshold:
                    # 贪婪恐惧指数高于最小卖出阈值，根据不同区间卖出不同比例
                    if self.last_sell_date != date_str:
                        print(f"\n{date_str}: 贪婪恐惧指数={fng}, BTC均价=${btc_price:.2f}, ETH均价=${eth_price:.2f}")
                        # 合并卖出BTC和ETH
                        self.sell_crypto(date_str, btc_price, eth_price, fng)
                # 其他区间，不操作，不输出
            else:
                # 调试：检查数据缺失情况
                if fng is None:
                    print(f"{date_str}: 无贪婪恐惧指数数据")
                if btc_price is None:
                    print(f"{date_str}: 无BTC价格数据")
                if eth_price is None:
                    print(f"{date_str}: 无ETH价格数据")
            
            current_date += timedelta(days=1)
        
        # 分析结束，输出结果
        self.print_summary()
    

    
    def print_summary(self):
        """
        输出投资总结
        """
        print("\n" + "=" * 90)
        print("        投资策略分析总结")
        print("=" * 90)
        
        # 计算最终价值（以当前价格估算）
        latest_date = datetime.now().strftime('%Y-%m-%d')
        btc_final_price = self.get_daily_average_price('BTC', latest_date)
        eth_final_price = self.get_daily_average_price('ETH', latest_date)
        
        if not btc_final_price:
            # 如果没有当天价格，尝试获取最近的价格
            if self.trade_records:
                latest_trade = self.trade_records[-1]
                btc_final_price = latest_trade.get('btc_trade_price', 0)
                print(f"使用最近交易价格作为BTC最终价格: ${btc_final_price:.2f}")
        
        if not eth_final_price:
            # 如果没有当天价格，尝试获取最近的ETH价格
            if self.trade_records:
                # 找到最近的ETH交易
                for trade in reversed(self.trade_records):
                    if 'ETH' in trade.get('trade_note', ''):
                        eth_final_price = trade.get('eth_trade_price', 0)
                        print(f"使用最近交易价格作为ETH最终价格: ${eth_final_price:.2f}")
                        break
        
        if btc_final_price and eth_final_price:
            btc_value = self.btc_holdings * btc_final_price
            eth_value = self.eth_holdings * eth_final_price
            total_value = self.current_funds + btc_value + eth_value
            
            print(f"初始资金: ${self.initial_funds:.2f}")
            print(f"最终资金: ${self.current_funds:.2f}")
            print(f"最终持有BTC: {self.btc_holdings:.6f}")
            print(f"最终持有ETH: {self.eth_holdings:.6f}")
            print(f"BTC最终价格: ${btc_final_price:.2f}")
            print(f"ETH最终价格: ${eth_final_price:.2f}")
            print(f"BTC持仓均价: ${self.btc_average_price:.2f}")
            print(f"ETH持仓均价: ${self.eth_average_price:.2f}")
            print(f"BTC价值: ${btc_value:.2f}")
            print(f"ETH价值: ${eth_value:.2f}")
            print(f"总价值 (BTC+ETH+U): ${total_value:.2f}")
            print(f"收益率: {(total_value / self.initial_funds - 1) * 100:.2f}%")
        elif btc_final_price:
            btc_value = self.btc_holdings * btc_final_price
            total_value = self.current_funds + btc_value
            
            print(f"初始资金: ${self.initial_funds:.2f}")
            print(f"最终资金: ${self.current_funds:.2f}")
            print(f"最终持有BTC: {self.btc_holdings:.6f}")
            print(f"最终持有ETH: {self.eth_holdings:.6f}")
            print(f"BTC最终价格: ${btc_final_price:.2f}")
            print(f"BTC持仓均价: ${self.btc_average_price:.2f}")
            print(f"ETH持仓均价: ${self.eth_average_price:.2f}")
            print(f"BTC价值: ${btc_value:.2f}")
            print(f"总价值 (BTC+U): ${total_value:.2f}")
            print(f"收益率: {(total_value / self.initial_funds - 1) * 100:.2f}%")
        else:
            print(f"初始资金: ${self.initial_funds:.2f}")
            print(f"最终资金: ${self.current_funds:.2f}")
            print(f"最终持有BTC: {self.btc_holdings:.6f}")
            print(f"最终持有ETH: {self.eth_holdings:.6f}")
            print(f"BTC持仓均价: ${self.btc_average_price:.2f}")
            print(f"ETH持仓均价: ${self.eth_average_price:.2f}")
            print("无法计算总价值（缺少价格数据）")
        
        print(f"\n交易统计:")
        print(f"- 交易次数: {len(self.trade_records)}")
        print(f"- 买入次数: {sum(1 for r in self.trade_records if r['trade_type'] == 'buy')}")
        print(f"- 卖出次数: {sum(1 for r in self.trade_records if r['trade_type'] == 'sell')}")
        
        print("=" * 90)


if __name__ == '__main__':
    """
    主函数，执行投资策略分析
    """
    print("启动加密货币投资策略分析...")
    analyzer = InvestmentAnalyzer()
    analyzer.analyze_investment()