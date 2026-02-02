# 导入必要的库
import pymysql
from datetime import datetime, timedelta
import requests
import time

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'cryptocurrency_analysis',
    'charset': 'utf8mb4'
}

class DailyDataChecker:
    """
    每日数据完整性检查器
    用于验证加密货币价格数据的完整性（每天288条数据）
    并在数据缺失时从Binance API重新获取
    """
    def __init__(self):
        """
        初始化数据检查器
        """
        pass
    
    def get_db_connection(self):
        """
        获取数据库连接
        
        返回:
            pymysql.connections.Connection: 数据库连接对象
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
    
    def count_daily_records(self, symbol, date):
        """
        计算指定日期的实际数据条数
        
        参数:
            symbol (str): 加密货币的符号
            date (datetime): 要检查的日期
            
        返回:
            int: 实际数据条数
        """
        try:
            conn = self.get_db_connection()
            if not conn:
                return 0
            
            cursor = conn.cursor()
            
            # 构建日期的开始和结束时间
            start_time = datetime(date.year, date.month, date.day, 0, 0, 0)
            end_time = datetime(date.year, date.month, date.day, 23, 59, 59)
            
            # 查询数据条数
            query = """
            SELECT COUNT(*) 
            FROM price_data 
            WHERE symbol = %s AND timestamp BETWEEN %s AND %s
            """
            cursor.execute(query, (symbol, start_time, end_time))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return result[0] if result else 0
        except Exception as error:
            print('计算每日记录数失败:', str(error))
            return 0
    
    def fetch_and_store_daily_data(self, symbol, date):
        """
        获取指定日期的数据并存储到price_data表中
        使用开盘价和收盘价的均价作为价格
        
        参数:
            symbol (str): 加密货币的符号
            date (datetime): 要获取的日期
            
        返回:
            int: 成功存储的数据条数
        """
        try:
            # 构建日期的开始和结束时间
            start_time = datetime(date.year, date.month, date.day, 0, 0, 0)
            end_time = datetime(date.year, date.month, date.day, 23, 59, 59)
            
            # 计算需要的参数
            start_ts = int(start_time.timestamp() * 1000)
            end_ts = int(end_time.timestamp() * 1000)
            limit = 1000  # 每次请求最多1000条
            
            # 构建请求URL
            url = f'https://api.binance.com/api/v3/klines'
            params = {
                'symbol': f'{symbol}USDT',
                'interval': '5m',
                'startTime': start_ts,
                'endTime': end_ts,
                'limit': limit
            }
            
            # 添加延迟避免API限制
            time.sleep(1)
            
            # 发送请求
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # 解析响应
            klines = response.json()
            if not klines:
                print("API返回空数据")
                return 0
            
            # 打印API返回的数据信息
            print(f"API返回 {len(klines)} 条数据")
            # 准备存储数据
            conn = self.get_db_connection()
            if not conn:
                return 0
            
            cursor = conn.cursor()
            
            # 获取币种ID
            cursor.execute("SELECT id FROM currencies WHERE symbol = %s", (symbol,))
            currency_result = cursor.fetchone()
            if not currency_result:
                cursor.close()
                conn.close()
                return 0
            
            currency_id = currency_result[0]
            
            # 存储数据（使用INSERT IGNORE避免重复）
            insert_count = 0
            for kline in klines:
                timestamp = datetime.fromtimestamp(kline[0] / 1000)
                open_price = float(kline[1])  # 开盘价
                close_price = float(kline[4])  # 收盘价
                avg_price = (open_price + close_price) / 2  # 开盘价和收盘价的均价
                
                # 插入或更新数据
                insert_sql = """
                INSERT IGNORE INTO price_data (currency_id, symbol, price, timestamp)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (currency_id, symbol, avg_price, timestamp))
                insert_count += 1
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return insert_count
        except Exception as error:
            print('请求和存储数据失败:', str(error))
            return 0
    
    def check_yearly_data(self, symbol='BTC', year=2020):
        """
        检查指定年份的数据完整性，每天必须有288条数据
        
        参数:
            symbol (str): 加密货币的符号，默认为'BTC'
            year (int): 要检查的年份，默认为2020
            
        返回:
            bool: 检查是否成功完成
        """
        print(f"\n" + "=" * 90)
        print(f"        检查 {year} 年 {symbol} 数据完整性")
        print("=" * 90)
        
        try:
            # 计算年份的天数
            days_in_year = 366 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 365
            
            # 遍历每一天
            start_date = datetime(year, 1, 1)
            total_checked = 0
            total_fixed = 0
            
            # 获取当前日期
            current_date_now = datetime.now()
            
            for day in range(days_in_year):
                current_date = start_date + timedelta(days=day)
                
                # 如果日期超过当前日期，停止检查
                if current_date > current_date_now:
                    print(f"日期 {current_date.strftime('%Y-%m-%d')} 超过当前日期，停止检查")
                    break
                
                # 检查当天的数据条数
                record_count = self.count_daily_records(symbol, current_date)
                total_checked += 1
                
                if record_count >= 288:
                    print(f"{current_date.strftime('%Y-%m-%d')}: 数据完整 ({record_count}/288)")
                else:
                    print(f"{current_date.strftime('%Y-%m-%d')}: 数据不足 ({record_count}/288)，重新获取...")
                    # 添加延迟，避免API限制
                    print("添加延迟，避免API限制...")
                    time.sleep(1)
                    # 重新获取数据
                    fetched_count = self.fetch_and_store_daily_data(symbol, current_date)
                    if fetched_count > 0:
                        total_fixed += 1
                        print(f"  已获取 {fetched_count} 条数据")
                        # 再次检查数据条数
                        new_count = self.count_daily_records(symbol, current_date)
                        print(f"  更新后数据条数: {new_count}/288")
                    # 每修复10天后添加一个较长的延迟
                    if (total_fixed > 0 and total_fixed % 10 == 0):
                        print("\n添加较长延迟，避免API限制...")
                        time.sleep(3)
            
            print(f"\n" + "=" * 90)
            print(f"        检查完成")
            print(f"检查了 {total_checked} 天的数据")
            print(f"修复了 {total_fixed} 天的数据")
            print("=" * 90)
            return True
        except Exception as error:
            print('检查年度数据失败:', str(error))
            import traceback
            traceback.print_exc()
            return False

def main():
    """
    主函数
    """
    checker = DailyDataChecker()
    
    # 检查BTC数据
    print("检查BTC数据...")
    for year in range(2020, 2027):
        checker.check_yearly_data(symbol='BTC', year=year)
    
    # 检查ETH数据
    print("\n检查ETH数据...")
    for year in range(2020, 2027):
        checker.check_yearly_data(symbol='ETH', year=year)

if __name__ == '__main__':
    main()
