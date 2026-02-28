import logging
import requests
import schedule
import time
from datetime import datetime, timedelta

from config import (
    get_db_connection, DB_NAME, SYMBOLS, MAX_RETRIES,
    REQUEST_LIMIT, BATCH_SIZE
)

logger = logging.getLogger(__name__)


def init_database():
    try:
        with get_db_connection(use_database=False) as conn:
            if not conn:
                return
            cursor = conn.cursor()
            
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            logger.info(f"数据库 {DB_NAME} 已创建或已存在")
            
            cursor.execute(f"USE {DB_NAME}")
            
            create_currency_table_sql = """
            CREATE TABLE IF NOT EXISTS currencies (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(10) NOT NULL UNIQUE,
                name VARCHAR(50) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_currency_table_sql)
            logger.info("表 currencies 已创建或已存在")
            
            create_price_table_sql = """
            CREATE TABLE IF NOT EXISTS price_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                currency_id INT NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                price DECIMAL(20, 2) NULL,
                timestamp DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (currency_id) REFERENCES currencies(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_price_table_sql)
            logger.info("表 price_data 已创建或已存在")
            
            create_fng_table_sql = """
            CREATE TABLE IF NOT EXISTS fear_greed_index (
                date DATE NOT NULL PRIMARY KEY,
                value INT NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_fng_table_sql)
            logger.info("表 fear_greed_index 已创建或已存在")
            
            _ensure_indexes(cursor)
            
            insert_currency_sql = """
            INSERT IGNORE INTO currencies (symbol, name)
            VALUES (%s, %s)
            """
            currencies = [('BTC', 'Bitcoin'), ('ETH', 'Ethereum')]
            cursor.executemany(insert_currency_sql, currencies)
            conn.commit()
            logger.info("默认币种数据已插入")
            
            logger.info("数据库初始化完成")
    except Exception as error:
        logger.error(f'数据库初始化失败: {error}')


def _ensure_indexes(cursor):
    indexes = [
        ('idx_price_data_timestamp', 'price_data', 'timestamp'),
        ('idx_price_data_symbol', 'price_data', 'symbol')
    ]
    for index_name, table_name, column in indexes:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.STATISTICS 
            WHERE table_schema = DATABASE() 
            AND table_name = %s 
            AND index_name = %s
        """, (table_name, index_name))
        if cursor.fetchone()[0] == 0:
            cursor.execute(f"CREATE INDEX {index_name} ON {table_name}({column})")
            logger.info(f"创建索引 {index_name} 成功")
        else:
            logger.debug(f"索引 {index_name} 已存在")
    logger.debug("索引检查完成")


def fetch_price(symbol):
    for retry in range(MAX_RETRIES):
        try:
            response = requests.get(
                f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT',
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return {
                'symbol': symbol,
                'price': float(data['price']),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as error:
            logger.warning(f'获取{symbol}价格失败: {error}')
            if retry < MAX_RETRIES - 1:
                logger.info(f'等待10秒后重新尝试...({retry + 1}/{MAX_RETRIES})')
                time.sleep(10)
    
    logger.error(f'已尝试{MAX_RETRIES}次，获取{symbol}价格失败')
    return {
        'symbol': symbol,
        'price': None,
        'timestamp': datetime.now().isoformat()
    }


def fetch_historical_data(symbol, start_time, end_time):
    start_ts = int(start_time.timestamp() * 1000)
    end_ts = int(end_time.timestamp() * 1000)
    interval = '5m'
    request_count = 0
    total_processed = 0
    current_start = start_ts
    
    while current_start < end_ts:
        current_end = min(current_start + (REQUEST_LIMIT * 5 * 60 * 1000), end_ts)
        
        logger.debug(f'请求 {symbol} 数据: {datetime.fromtimestamp(current_start/1000)} 到 {datetime.fromtimestamp(current_end/1000)}')
        
        sleep_time = 1.0 + (hash(current_start) % 10) / 5
        logger.debug(f'等待 {sleep_time:.2f} 秒后请求...')
        time.sleep(sleep_time)
        
        klines = _fetch_klines_with_retry(symbol, interval, current_start, current_end)
        
        if not klines:
            logger.info('没有更多数据，停止爬取')
            break
        
        batch_data = []
        for kline in klines:
            timestamp = datetime.fromtimestamp(kline[0] / 1000)
            open_price = float(kline[1])
            close_price = float(kline[4])
            avg_price = (open_price + close_price) / 2
            
            batch_data.append({
                'symbol': symbol,
                'price': avg_price,
                'timestamp': timestamp.isoformat()
            })
        
        if batch_data:
            logger.debug(f'保存 {len(batch_data)} 条 {symbol} 数据...')
            save_to_database(batch_data)
            total_processed += len(batch_data)
        
        current_start = current_end
        request_count += 1
        
        if request_count % 3 == 0:
            logger.debug(f'已请求 {request_count} 次，长时间休息...')
            time.sleep(3)
        else:
            time.sleep(1)
    
    logger.info(f'成功获取并保存 {symbol} 的 {total_processed} 条历史数据')


def _fetch_klines_with_retry(symbol, interval, start_ts, end_ts):
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': f'{symbol}USDT',
        'interval': interval,
        'startTime': start_ts,
        'endTime': end_ts,
        'limit': REQUEST_LIMIT
    }
    
    for retry in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as error:
            if retry < MAX_RETRIES - 1:
                logger.warning(f'请求失败，10秒后重新尝试...({retry + 1}/{MAX_RETRIES})')
                time.sleep(10)
            else:
                logger.error(f'已尝试{MAX_RETRIES}次，请求仍然失败: {error}')
    return []


def fetch_prices():
    logger.info('正在获取价格...')
    data = [fetch_price(symbol) for symbol in SYMBOLS]
    logger.debug(f'已获取价格: {data}')
    save_to_database(data)


def get_latest_fng_date():
    with get_db_connection() as conn:
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(date) FROM fear_greed_index")
        result = cursor.fetchone()
        return result[0] if result and result[0] else None


def fetch_fng_history(start_date=None):
    if start_date:
        logger.info(f'获取从 {start_date} 开始的贪婪恐惧指数数据...')
        current_date = datetime.now().date()
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        date_diff = (current_date - start_date).days
        required_limit = date_diff + 10
        logger.debug(f'计算需要获取 {required_limit} 条数据...')
    else:
        logger.info('获取完整的贪婪恐惧指数历史数据...')
        required_limit = 3000
    
    url = f'https://api.alternative.me/fng/?limit={required_limit}'
    logger.debug(f'API请求URL: {url}')
    
    time.sleep(3)
    
    data = {'data': []}
    for retry in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            break
        except Exception as error:
            if retry < MAX_RETRIES - 1:
                logger.warning(f'请求失败，10秒后重新尝试...({retry + 1}/{MAX_RETRIES})')
                time.sleep(10)
            else:
                logger.error(f'已尝试{MAX_RETRIES}次，请求仍然失败: {error}')
    
    if not data.get('data'):
        return {}
    
    history_dict = {}
    for item in data['data']:
        item_date = datetime.fromtimestamp(int(item['timestamp'])).strftime('%Y-%m-%d')
        
        if start_date:
            if item_date > start_date.strftime('%Y-%m-%d'):
                history_dict[item_date] = int(item['value'])
        else:
            history_dict[item_date] = int(item['value'])
    
    if history_dict:
        logger.info(f'成功获取 {len(history_dict)} 条贪婪恐惧指数数据')
        logger.debug(f'数据时间范围: 最早 {min(history_dict.keys())}, 最晚 {max(history_dict.keys())}')
    else:
        logger.info('没有找到符合条件的贪婪恐惧指数数据')
    
    return history_dict


def save_to_database(data):
    with get_db_connection() as conn:
        if not conn:
            return
        cursor = conn.cursor()
        insert_data = []
        total_processed = 0
        duplicate_count = 0
        
        for i, item in enumerate(data):
            timestamp = datetime.fromisoformat(item['timestamp'])
            
            cursor.execute("SELECT id FROM currencies WHERE symbol = %s", (item['symbol'],))
            currency_result = cursor.fetchone()
            if not currency_result:
                logger.warning(f"币种 {item['symbol']} 不存在，跳过保存")
                continue
            
            currency_id = currency_result[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM price_data
                WHERE symbol = %s AND timestamp = %s
            """, (item['symbol'], timestamp))
            exists = cursor.fetchone()[0]
            
            if exists > 0:
                duplicate_count += 1
                if duplicate_count % 100 == 0:
                    logger.debug(f"跳过 {duplicate_count} 条重复数据")
                continue
            
            if (i + 1) % 100 == 0:
                logger.debug(f"处理进度: {i + 1}/{len(data)}")
            
            insert_data.append((currency_id, item['symbol'], item['price'], timestamp))
            total_processed += 1
            
            if len(insert_data) >= BATCH_SIZE:
                cursor.executemany("""
                    INSERT INTO price_data (currency_id, symbol, price, timestamp)
                    VALUES (%s, %s, %s, %s)
                """, insert_data)
                conn.commit()
                logger.debug(f"已保存 {len(insert_data)} 条数据")
                insert_data = []
        
        if insert_data:
            cursor.executemany("""
                INSERT INTO price_data (currency_id, symbol, price, timestamp)
                VALUES (%s, %s, %s, %s)
            """, insert_data)
            conn.commit()
            logger.debug(f"已保存 {len(insert_data)} 条数据")
        
        if duplicate_count > 0:
            logger.debug(f"跳过 {duplicate_count} 条重复数据")
        logger.info(f"成功保存 {total_processed} 条价格数据到数据库")


def setup_scheduler():
    logger.info('正在设置定时任务...')
    init_database()
    fetch_prices()
    schedule.every(5).minutes.do(fetch_prices)
    logger.info('定时任务已启动。每5分钟获取一次价格。')
    logger.info('按Ctrl+C停止脚本。')
    
    while True:
        schedule.run_pending()
        time.sleep(1)


def get_latest_timestamp(symbol):
    with get_db_connection() as conn:
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(timestamp) as latest_time
            FROM price_data
            WHERE symbol = %s
        """, (symbol,))
        result = cursor.fetchone()
        return result[0] if result and result[0] else None


def _adjust_to_next_5min(dt):
    minutes = dt.minute
    remainder = minutes % 5
    if remainder != 0:
        next_minute = minutes - remainder + 5
    else:
        next_minute = minutes + 5
    
    if next_minute >= 60:
        new_hour = (dt.hour + 1) % 24
        dt = dt.replace(minute=0, hour=new_hour)
        if new_hour == 0:
            dt += timedelta(days=1)
    else:
        dt = dt.replace(minute=next_minute)
    
    return dt


def fetch_data_2020_to_present():
    logger.info('开始获取2020年至今的历史数据...')
    
    for symbol in SYMBOLS:
        logger.info(f'获取 {symbol} 2020年至今数据')
        
        latest_timestamp = get_latest_timestamp(symbol)
        
        if latest_timestamp:
            start_time = _adjust_to_next_5min(latest_timestamp)
        else:
            start_time = datetime(2020, 1, 1, 0, 0, 0)
        
        end_time = datetime.now()
        
        if start_time < end_time:
            logger.info(f'时间范围: {start_time} 到 {end_time}')
            fetch_historical_data(symbol, start_time, end_time)
        else:
            logger.info(f'{symbol} 数据已是最新，无需更新')
    
    logger.info('2020年至今历史数据获取完成！')


def update_fng_data_2020_to_present():
    logger.info('开始更新2020年至今的恐惧贪婪指数数据...')
    
    latest_fng_date = get_latest_fng_date()
    
    if latest_fng_date:
        logger.info(f'本地最新贪婪恐惧指数日期: {latest_fng_date}')
        logger.info('将只获取该日期之后的数据...')
    else:
        logger.info('本地没有贪婪恐惧指数数据，将获取完整的历史数据...')
    
    history_data = fetch_fng_history(latest_fng_date)
    
    if not history_data:
        logger.info('无法获取贪婪恐惧指数历史数据或数据已是最新')
        return
    
    logger.info(f'找到 {len(history_data)} 条恐惧贪婪指数数据')
    
    with get_db_connection() as conn:
        if not conn:
            return
        cursor = conn.cursor()
        insert_count = 0
        
        for date_str, value in sorted(history_data.items()):
            try:
                year = int(date_str.split('-')[0])
                if year >= 2020:
                    cursor.execute("""
                        INSERT IGNORE INTO fear_greed_index (date, value)
                        VALUES (%s, %s)
                    """, (date_str, value))
                    insert_count += 1
            except Exception as e:
                logger.error(f'保存 {date_str} 数据失败: {e}')
        
        conn.commit()
        logger.info(f'成功保存 {insert_count} 条2020年至今的恐惧贪婪指数数据')
    
    logger.info('2020年至今恐惧贪婪指数数据更新完成！')


def main():
    logger.info('启动加密货币价格分析工具...')
    logger.info('项目: Analysis of Cryptocurrency Price Trends')
    logger.info('仓库: https://github.com/idealism-L')
    logger.info('目标: 获取2020年至今的完整加密货币数据')
    logger.info('执行顺序: 1. 获取贪婪恐惧指数数据 2. 获取BTC/ETH价格数据')
    
    init_database()
    
    logger.info('=== 步骤1: 获取完整的贪婪恐惧指数数据 ===')
    update_fng_data_2020_to_present()
    
    logger.info('=== 步骤2: 获取BTC和ETH价格数据 ===')
    fetch_data_2020_to_present()
    
    logger.info('2020年至今数据获取和更新任务完成！')


if __name__ == '__main__':
    main()
