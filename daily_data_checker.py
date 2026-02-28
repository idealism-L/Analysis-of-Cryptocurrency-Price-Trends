import logging
from datetime import datetime, timedelta
import requests
import time

from config import get_db_connection, SYMBOLS

logger = logging.getLogger(__name__)


class DailyDataChecker:
    def __init__(self):
        pass
    
    def count_daily_records(self, symbol, date):
        try:
            with get_db_connection() as conn:
                if not conn:
                    return 0
                
                cursor = conn.cursor()
                
                start_time = datetime(date.year, date.month, date.day, 0, 0, 0)
                end_time = datetime(date.year, date.month, date.day, 23, 59, 59)
                
                query = """
                SELECT COUNT(*) 
                FROM price_data 
                WHERE symbol = %s AND timestamp BETWEEN %s AND %s
                """
                cursor.execute(query, (symbol, start_time, end_time))
                result = cursor.fetchone()
                
                return result[0] if result else 0
        except Exception as error:
            logger.error(f'计算每日记录数失败: {error}')
            return 0
    
    def fetch_and_store_daily_data(self, symbol, date):
        try:
            start_time = datetime(date.year, date.month, date.day, 0, 0, 0)
            end_time = datetime(date.year, date.month, date.day, 23, 59, 59)
            
            start_ts = int(start_time.timestamp() * 1000)
            end_ts = int(end_time.timestamp() * 1000)
            limit = 1000
            
            url = 'https://api.binance.com/api/v3/klines'
            params = {
                'symbol': f'{symbol}USDT',
                'interval': '5m',
                'startTime': start_ts,
                'endTime': end_ts,
                'limit': limit
            }
            
            time.sleep(1)
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            klines = response.json()
            if not klines:
                logger.warning("API返回空数据")
                return 0
            
            logger.debug(f"API返回 {len(klines)} 条数据")
            
            with get_db_connection() as conn:
                if not conn:
                    return 0
                
                cursor = conn.cursor()
                
                cursor.execute("SELECT id FROM currencies WHERE symbol = %s", (symbol,))
                currency_result = cursor.fetchone()
                if not currency_result:
                    return 0
                
                currency_id = currency_result[0]
                
                insert_count = 0
                for kline in klines:
                    timestamp = datetime.fromtimestamp(kline[0] / 1000)
                    open_price = float(kline[1])
                    close_price = float(kline[4])
                    avg_price = (open_price + close_price) / 2
                    
                    insert_sql = """
                    INSERT IGNORE INTO price_data (currency_id, symbol, price, timestamp)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql, (currency_id, symbol, avg_price, timestamp))
                    insert_count += 1
                
                conn.commit()
                
                return insert_count
        except Exception as error:
            logger.error(f'请求和存储数据失败: {error}')
            return 0
    
    def check_yearly_data(self, symbol='BTC', year=2020):
        logger.info(f"检查 {year} 年 {symbol} 数据完整性")
        
        try:
            days_in_year = 366 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 365
            
            start_date = datetime(year, 1, 1)
            total_checked = 0
            total_fixed = 0
            
            current_date_now = datetime.now()
            
            for day in range(days_in_year):
                current_date = start_date + timedelta(days=day)
                
                if current_date > current_date_now:
                    logger.debug(f"日期 {current_date.strftime('%Y-%m-%d')} 超过当前日期，停止检查")
                    break
                
                record_count = self.count_daily_records(symbol, current_date)
                total_checked += 1
                
                if record_count >= 288:
                    logger.debug(f"{current_date.strftime('%Y-%m-%d')}: 数据完整 ({record_count}/288)")
                else:
                    logger.warning(f"{current_date.strftime('%Y-%m-%d')}: 数据不足 ({record_count}/288)，重新获取...")
                    logger.debug("添加延迟，避免API限制...")
                    time.sleep(1)
                    fetched_count = self.fetch_and_store_daily_data(symbol, current_date)
                    if fetched_count > 0:
                        total_fixed += 1
                        logger.debug(f"已获取 {fetched_count} 条数据")
                        new_count = self.count_daily_records(symbol, current_date)
                        logger.debug(f"更新后数据条数: {new_count}/288")
                    if total_fixed > 0 and total_fixed % 10 == 0:
                        logger.debug("添加较长延迟，避免API限制...")
                        time.sleep(3)
            
            logger.info(f"检查了 {total_checked} 天的数据")
            logger.info(f"修复了 {total_fixed} 天的数据")
            return True
        except Exception as error:
            logger.error(f'检查年度数据失败: {error}')
            return False


def main():
    checker = DailyDataChecker()
    
    logger.info("检查BTC数据...")
    for year in range(2020, 2027):
        checker.check_yearly_data(symbol='BTC', year=year)
    
    logger.info("检查ETH数据...")
    for year in range(2020, 2027):
        checker.check_yearly_data(symbol='ETH', year=year)


if __name__ == '__main__':
    main()
