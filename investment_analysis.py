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
        self.trade_records = []  # 交易记录
        self.last_buy_date = None  # 上次买入日期
        self.last_sell_date = None  # 上次卖出日期
        self.create_trade_table()  # 创建交易记录表
        self.clear_trade_table()  # 清空交易记录表
    
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
        """
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # 创建交易记录表
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS trade_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                type VARCHAR(10) NOT NULL,
                amount DECIMAL(20, 8) NOT NULL,
                price DECIMAL(20, 2) NOT NULL,
                total_usd DECIMAL(20, 2) NOT NULL,
                btc_holdings DECIMAL(20, 8) NOT NULL,
                remaining_usd DECIMAL(20, 2) NOT NULL,
                account_total DECIMAL(20, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_table_sql)
            conn.commit()
            print("交易记录表已创建或已存在")
            
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
                date, type, amount, price, total_usd, btc_holdings, remaining_usd, account_total
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                trade_record['date'],
                trade_record['type'],
                trade_record['amount'],
                trade_record['price'],
                trade_record['total_usd'],
                trade_record['btc_holdings'],
                trade_record['remaining_usd'],
                trade_record['account_total']
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
            
            # 预加载BTC的日均价
            self.daily_prices = {}
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
                self.daily_prices[date_str] = float(row[1])
            
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
            for date, fng in self.daily_fng.items():
                if fng < 30 and date in self.daily_prices:
                    print(f"{date}: FNG={fng} (买入信号)")
                elif fng > 65 and date in self.daily_prices:
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
        if hasattr(self, 'daily_prices'):
            # 尝试直接匹配
            if date in self.daily_prices:
                return self.daily_prices[date]
            # 尝试不同格式的日期匹配
            for stored_date in self.daily_prices:
                if str(stored_date) == date:
                    return self.daily_prices[stored_date]
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
        """
        if fng < 20:
            return 300  # 20以下买入300u
        elif fng < 25:
            return 200  # 25以下买入200u
        elif fng < 30:
            return 100  # 30以下买入100u
        else:
            return 0  # 30以上不买入
    
    def buy_btc(self, date, price, fng):
        """
        买入BTC
        """
        investment_amount = self.calculate_investment_amount(fng)
        
        # 检查资金是否足够
        if self.current_funds < investment_amount:
            print(f"{date}: 资金不足，无法买入 {investment_amount} 美元的BTC")
            return False
        
        # 计算可购买的BTC数量
        btc_amount = investment_amount / price
        
        # 更新持仓和资金
        self.btc_holdings += btc_amount
        self.current_funds -= investment_amount
        
        # 计算账户总额
        account_total = self.current_funds + (self.btc_holdings * price)
        
        # 记录交易
        trade_record = {
            'date': date,
            'type': 'buy',
            'price': price,
            'amount': btc_amount,
            'total_usd': investment_amount,
            'btc_holdings': self.btc_holdings,
            'remaining_usd': self.current_funds,
            'account_total': account_total
        }
        self.trade_records.append(trade_record)
        
        # 保存到数据库
        self.save_trade_to_database(trade_record)
        
        print(f"{date}: 买入 {btc_amount:.6f} BTC, 价格: ${price:.2f}, 花费: ${investment_amount:.2f}")
        print(f"  当前持有: {self.btc_holdings:.6f} BTC, 剩余资金: ${self.current_funds:.2f}")
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
        if fng >= 80:
            sell_percentage = 0.05  # 80以上卖出5%
        elif fng >= 75:
            sell_percentage = 0.03  # 75以上卖出3%
        elif fng >= 70:
            sell_percentage = 0.02  # 70以上卖出2%
        else:
            return False  # 70以下不卖出
        
        # 计算卖出数量
        sell_amount = self.btc_holdings * sell_percentage
        sell_value = sell_amount * price
        
        # 更新持仓和资金
        self.btc_holdings -= sell_amount
        self.current_funds += sell_value
        
        # 计算账户总额
        account_total = self.current_funds + (self.btc_holdings * price)
        
        # 记录交易
        trade_record = {
            'date': date,
            'type': 'sell',
            'price': price,
            'amount': sell_amount,
            'total_usd': sell_value,
            'btc_holdings': self.btc_holdings,
            'remaining_usd': self.current_funds,
            'account_total': account_total
        }
        self.trade_records.append(trade_record)
        
        # 保存到数据库
        self.save_trade_to_database(trade_record)
        
        print(f"{date}: 卖出 {sell_amount:.6f} BTC, 价格: ${price:.2f}, 获得: ${sell_value:.2f}")
        print(f"  当前持有: {self.btc_holdings:.6f} BTC, 剩余资金: ${self.current_funds:.2f}")
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
        print("投资策略: 贪婪恐惧指数30以下买入100u，25以下买入200u，20以下买入300u")
        print("卖出策略: 70以上卖出2%，75以上卖出3%，80以上卖出5%")
        
        # 获取最新时间戳，决定起始日期
        latest_price_timestamp = self.get_latest_timestamp('price_data', 'timestamp')
        latest_fng_date = self.get_latest_timestamp('fear_greed_index', 'date')
        
        # 确定起始日期
        if latest_price_timestamp:
            start_date = latest_price_timestamp
            print(f"从最新数据日期开始: {start_date.strftime('%Y年%m月%d日')}")
        else:
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
            
            # 获取当日均价
            avg_price = self.get_daily_average_price('BTC', date_str)
            if avg_price is None:
                current_date += timedelta(days=1)
                continue
            
            # 检查是否需要操作
            if fng is not None and avg_price is not None:
                if fng < 30:
                    # 贪婪恐惧指数30以下，买入
                    if self.last_buy_date != date_str:
                        print(f"\n{date_str}: 贪婪恐惧指数={fng}, 均价=${avg_price:.2f}")
                        self.buy_btc(date_str, avg_price, fng)
                elif fng >= 70:
                    # 贪婪恐惧指数70以上，根据不同区间卖出不同比例
                    if self.last_sell_date != date_str:
                        print(f"\n{date_str}: 贪婪恐惧指数={fng}, 均价=${avg_price:.2f}")
                        self.sell_btc(date_str, avg_price, fng)
                # 30-70区间，不操作，不输出
            else:
                # 调试：检查数据缺失情况
                if fng is None:
                    print(f"{date_str}: 无贪婪恐惧指数数据")
                if avg_price is None:
                    print(f"{date_str}: 无价格数据")
            
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
        final_price = self.get_daily_average_price('BTC', latest_date)
        if not final_price:
            # 如果没有当天价格，尝试获取最近的价格
            if self.trade_records:
                latest_trade = self.trade_records[-1]
                final_price = latest_trade['price']
                print(f"使用最近交易价格作为最终价格: ${final_price:.2f}")
        
        if final_price:
            btc_value = self.btc_holdings * final_price
            total_value = self.current_funds + btc_value
            
            print(f"初始资金: ${self.initial_funds:.2f}")
            print(f"最终资金: ${self.current_funds:.2f}")
            print(f"最终持有BTC: {self.btc_holdings:.6f}")
            print(f"BTC最终价格: ${final_price:.2f}")
            print(f"BTC价值: ${btc_value:.2f}")
            print(f"总价值 (BTC+U): ${total_value:.2f}")
            print(f"收益率: {(total_value / self.initial_funds - 1) * 100:.2f}%")
        else:
            print(f"初始资金: ${self.initial_funds:.2f}")
            print(f"最终资金: ${self.current_funds:.2f}")
            print(f"最终持有BTC: {self.btc_holdings:.6f}")
            print("无法计算总价值（缺少价格数据）")
        
        print(f"\n交易统计:")
        print(f"- 交易次数: {len(self.trade_records)}")
        print(f"- 买入次数: {sum(1 for r in self.trade_records if r['type'] == 'buy')}")
        print(f"- 卖出次数: {sum(1 for r in self.trade_records if r['type'] == 'sell')}")
        
        # 输出交易记录（美化格式）
        if self.trade_records:
            print("\n交易记录:")
            # 使用固定宽度的格式字符串，确保精确对齐
            format_str = "{:<12} {:<8} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}"
            
            # 打印表头
            print(format_str.format('日期', '类型', '数量', '价格', '金额', '持有BTC', '剩余U', '总额U'))
            print('=' * 95)  # 精确计算的分隔线长度
            
            # 打印数据行
            for record in self.trade_records:
                account_total = record.get('account_total', self.current_funds + (self.btc_holdings * record['price']))
                print(format_str.format(
                    record['date'],
                    record['type'].upper(),
                    f"{record['amount']:.6f}",
                    f"${record['price']:.2f}",
                    f"${record['total_usd']:.2f}",
                    f"{record['btc_holdings']:.6f}",
                    f"${record['remaining_usd']:.2f}",
                    f"${account_total:.2f}"
                ))
            
            # 打印底部分隔线
            print('=' * 95)
        
        print("=" * 90)

def main():
    """
    主函数
    """
    analyzer = InvestmentAnalyzer()
    
    # 分析投资策略
    print("分析投资策略...")
    analyzer.analyze_investment()

if __name__ == '__main__':
    main()
