# 导入必要的库
import requests  # 用于发送HTTP请求
import schedule  # 用于设置定时任务
import time  # 用于时间控制
from datetime import datetime  # 用于获取当前时间
import pymysql  # 用于MySQL数据库操作

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'charset': 'utf8mb4'
}

# 数据库和表名
DB_NAME = 'cryptocurrency_analysis'
TABLE_NAME = 'price_data'


def init_database():
    """
    初始化数据库，创建数据库和表
    """
    try:
        # 连接到MySQL服务器
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"数据库 {DB_NAME} 已创建或已存在")
        
        # 选择数据库
        cursor.execute(f"USE {DB_NAME}")
        
        # 创建币种主表
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
        print("表 currencies 已创建或已存在")
        
        # 删除旧的price_data表（如果存在）
        cursor.execute("DROP TABLE IF EXISTS price_data")
        print("旧的 price_data 表已删除")
        
        # 创建价格子表（字段冗余）
        create_price_table_sql = """
        CREATE TABLE IF NOT EXISTS price_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            currency_id INT NOT NULL,
            symbol VARCHAR(10) NOT NULL,
            price DECIMAL(20, 2) NULL,
            fear_greed_index INT NULL,
            timestamp DATETIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (currency_id) REFERENCES currencies(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(create_price_table_sql)
        print("新的 price_data 表已创建")
        
        # 为timestamp字段创建索引，提高查询性能
        cursor.execute("CREATE INDEX idx_price_data_timestamp ON price_data(timestamp)")
        cursor.execute("CREATE INDEX idx_price_data_symbol ON price_data(symbol)")
        print("已创建索引，提高查询性能")
        
        # 插入默认币种数据
        insert_currency_sql = """
        INSERT IGNORE INTO currencies (symbol, name)
        VALUES (%s, %s)
        """
        currencies = [
            ('BTC', 'Bitcoin'),
            ('ETH', 'Ethereum')
        ]
        cursor.executemany(insert_currency_sql, currencies)
        conn.commit()
        print("默认币种数据已插入")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        print("数据库初始化完成")
    except Exception as error:
        print('数据库初始化失败:', str(error))


def get_db_connection():
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
            database=DB_NAME,
            charset=DB_CONFIG['charset']
        )
        return conn
    except Exception as error:
        print('数据库连接失败:', str(error))
        return None


def fetch_price(symbol):
    """
    获取指定加密货币的实时价格
    
    参数:
        symbol (str): 加密货币的符号，如'BTC'、'ETH'
    
    返回:
        dict: 包含货币符号、价格和时间戳的字典
    """
    try:
        # 发送GET请求到币安API获取价格
        response = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT')
        # 检查请求是否成功
        response.raise_for_status()
        # 解析JSON响应
        data = response.json()
        # 返回价格信息
        return {
            'symbol': symbol,
            'price': float(data['price']),  # 将价格转换为浮点数
            'timestamp': datetime.now().isoformat()  # 获取当前时间戳
        }
    except Exception as error:
        # 处理异常情况
        print(f'获取{symbol}价格失败:', str(error))
        # 异常时返回空价格
        return {
            'symbol': symbol,
            'price': None,
            'timestamp': datetime.now().isoformat()
        }


def fetch_historical_data(symbol, start_time, end_time):
    """
    获取指定加密货币的历史K线数据
    
    参数:
        symbol (str): 加密货币的符号，如'BTC'、'ETH'
        start_time (datetime): 开始时间
        end_time (datetime): 结束时间
    
    返回:
        list: 包含历史价格信息的字典列表
    """
    try:
        # 转换时间为毫秒时间戳
        start_ts = int(start_time.timestamp() * 1000)
        end_ts = int(end_time.timestamp() * 1000)
        
        # 每次请求最多获取500条数据，减少单次请求量
        limit = 500
        interval = '5m'  # 5分钟K线
        request_count = 0
        total_processed = 0
        
        while True:
            # 获取最新时间戳，确保每次都从数据库最新位置开始
            latest_time = get_latest_timestamp(symbol)
            if latest_time:
                current_start = int(latest_time.timestamp() * 1000) + 1
            else:
                current_start = start_ts
            
            if current_start >= end_ts:
                print(f'{symbol} 数据已是最新，无需更新')
                break
            
            # 计算本次请求的结束时间
            current_end = min(current_start + (limit * 5 * 60 * 1000), end_ts)
            
            print(f'请求 {symbol} 数据: {datetime.fromtimestamp(current_start/1000)} 到 {datetime.fromtimestamp(current_end/1000)}')
            
            # 发送GET请求到币安API获取K线数据
            url = f'https://api.binance.com/api/v3/klines'
            params = {
                'symbol': f'{symbol}USDT',
                'interval': interval,
                'startTime': current_start,
                'endTime': current_end,
                'limit': limit
            }
            
            # 添加更长的随机延迟避免API限制
            sleep_time = 1.0 + (hash(current_start) % 10) / 5
            print(f'等待 {sleep_time:.2f} 秒后请求...')
            time.sleep(sleep_time)
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # 解析JSON响应
            klines = response.json()
            
            if not klines:
                print('没有更多数据，停止爬取')
                break
            
            # 处理K线数据
            batch_data = []
            for kline in klines:
                timestamp = datetime.fromtimestamp(kline[0] / 1000)
                close_price = float(kline[4])  # 收盘价
                
                batch_data.append({
                    'symbol': symbol,
                    'price': close_price,
                    'timestamp': timestamp.isoformat()
                })
            
            # 每次请求后立即保存数据
            if batch_data:
                print(f'保存 {len(batch_data)} 条 {symbol} 数据...')
                save_to_database(batch_data)
                total_processed += len(batch_data)
            
            # 每3次请求增加更长的延迟
            request_count += 1
            if request_count % 3 == 0:
                print(f'已请求 {request_count} 次，长时间休息...')
                time.sleep(3)
            else:
                # 每次请求后都有短暂休息
                time.sleep(1)
        
        print(f'成功获取并保存 {symbol} 的 {total_processed} 条历史数据')
        return []
    except Exception as error:
        # 处理异常情况
        print(f'获取{symbol}历史数据失败:', str(error))
        return []


def fetch_prices():
    """
    获取BTC和ETH的价格并保存到Excel
    """
    print('正在获取价格...')
    # 获取BTC价格
    btc_price = fetch_price('BTC')
    # 获取ETH价格
    eth_price = fetch_price('ETH')
    
    # 组合价格数据
    data = [btc_price, eth_price]
    print('已获取价格:', data)
    
    # 保存价格数据到数据库
    save_to_database(data)


# 贪婪恐惧指数缓存
fear_greed_cache = {}


def fetch_fear_greed_index(timestamp=None):
    """
    获取比特币贪婪恐惧指数
    
    参数:
        timestamp (str, optional): 时间戳，格式为ISO 8601
    
    返回:
        int: 贪婪恐惧指数 (0-100)
    """
    try:
        if timestamp:
            # 解析时间戳获取日期
            date = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d')
            
            # 检查缓存
            if date in fear_greed_cache:
                return fear_greed_cache[date]
            
            # 使用Alternative.me的API获取指定日期的贪婪恐惧指数
            url = f'https://api.alternative.me/fng/?date={date}'
        else:
            # 获取当前贪婪恐惧指数
            url = 'https://api.alternative.me/fng/?limit=1'
        
        # 添加随机延迟避免API限制
        time.sleep(0.5 + (hash(timestamp) % 10) / 10)
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data['data'] and len(data['data']) > 0:
            index_value = int(data['data'][0]['value'])
            # 缓存结果
            if timestamp:
                fear_greed_cache[date] = index_value
            return index_value
        return None
    except Exception as error:
        # 处理异常情况
        if timestamp:
            date = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d')
            print(f'获取{date}贪婪恐惧指数失败:', str(error))
        else:
            print('获取当前贪婪恐惧指数失败:', str(error))
        return None


def save_to_database(data):
    """
    将价格数据保存到MySQL数据库
    
    参数:
        data (list): 包含价格信息的字典列表
    """
    try:
        # 获取数据库连接
        conn = get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # 准备插入数据
        insert_data = []
        batch_size = 100  # 每批次处理的记录数
        total_processed = 0
        
        for i, item in enumerate(data):
            # 解析时间戳
            timestamp = datetime.fromisoformat(item['timestamp'])
            
            # 查询币种ID
            cursor.execute("SELECT id FROM currencies WHERE symbol = %s", (item['symbol'],))
            currency_result = cursor.fetchone()
            if not currency_result:
                print(f"币种 {item['symbol']} 不存在，跳过保存")
                continue
            
            currency_id = currency_result[0]
            
            # 获取该时间点的贪婪恐惧指数
            fear_greed_index = fetch_fear_greed_index(item['timestamp'])
            
            # 每100条打印一次进度
            if (i + 1) % batch_size == 0:
                print(f"处理进度: {i + 1}/{len(data)}")
            
            insert_data.append((
                currency_id,
                item['symbol'],
                item['price'],
                fear_greed_index,
                timestamp
            ))
            
            total_processed += 1
            
            # 每1000条数据执行一次批量插入
            if len(insert_data) >= 1000:
                # 执行批量插入
                insert_sql = """
                INSERT INTO price_data (currency_id, symbol, price, fear_greed_index, timestamp)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.executemany(insert_sql, insert_data)
                conn.commit()
                
                print(f"已保存 {len(insert_data)} 条数据")
                insert_data = []
        
        # 处理剩余数据
        if insert_data:
            insert_sql = """
            INSERT INTO price_data (currency_id, symbol, price, fear_greed_index, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_sql, insert_data)
            conn.commit()
            print(f"已保存 {len(insert_data)} 条数据")
        
        print(f"成功保存 {total_processed} 条价格数据到数据库")
        
        # 关闭连接
        cursor.close()
        conn.close()
    except Exception as error:
        # 处理保存失败的情况
        print('保存到数据库失败:', str(error))
        # 回滚事务
        if 'conn' in locals() and conn:
            try:
                conn.rollback()
            except:
                pass
        # 关闭连接
        if 'cursor' in locals() and cursor:
            try:
                cursor.close()
            except:
                pass
        if 'conn' in locals() and conn:
            try:
                conn.close()
            except:
                pass


def setup_scheduler():
    """
    设置定时任务，每5分钟获取一次价格
    """
    print('正在设置定时任务...')
    
    # 初始化数据库
    init_database()
    
    # 立即执行一次价格获取
    fetch_prices()
    
    # 设置每5分钟执行一次fetch_prices函数
    schedule.every(5).minutes.do(fetch_prices)
    
    print('定时任务已启动。每5分钟获取一次价格。')
    print('按Ctrl+C停止脚本。')
    
    # 持续运行定时任务
    while True:
        schedule.run_pending()  # 运行待执行的任务
        time.sleep(1)  # 暂停1秒，避免CPU占用过高


def get_latest_timestamp(symbol):
    """
    获取数据库中指定币种的最新数据时间戳
    
    参数:
        symbol (str): 加密货币的符号
    
    返回:
        datetime: 最新数据的时间戳，如果没有数据则返回None
    """
    try:
        conn = get_db_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        # 查询最新的时间戳
        query = """
        SELECT MAX(timestamp) as latest_time
        FROM price_data
        WHERE symbol = %s
        """
        cursor.execute(query, (symbol,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result and result[0]:
            return result[0]
        return None
    except Exception as error:
        print(f'获取{symbol}最新时间戳失败:', str(error))
        return None


def fetch_historical_data_from_latest():
    """
    从数据库中最新数据的时间开始爬取历史数据
    """
    print('开始爬取历史数据...')
    
    # 计算时间范围
    end_time = datetime.now()
    
    # 定义要爬取的币种
    symbols = ['BTC', 'ETH']
    
    for symbol in symbols:
        print(f'\n===== 爬取 {symbol} 数据 =====')
        
        # 获取最新数据时间戳
        latest_timestamp = get_latest_timestamp(symbol)
        
        if latest_timestamp:
            # 如果有数据，从最新时间的下一个5分钟开始
            start_time = latest_timestamp
            # 调整到下一个5分钟整点
            minutes = start_time.minute
            remainder = minutes % 5
            if remainder != 0:
                start_time = start_time.replace(minute=minutes - remainder + 5)
            else:
                start_time = start_time.replace(minute=minutes + 5)
            
            # 确保开始时间不超过结束时间
            if start_time >= end_time:
                print(f'{symbol} 数据已是最新，无需更新')
                continue
            
            print(f'从 {start_time} 开始爬取 {symbol} 数据')
        else:
            # 如果没有数据，从2023年1月1日开始
            start_time = datetime(2023, 1, 1, 0, 0, 0)
            print(f'首次爬取 {symbol} 数据，从2023年1月1日开始')
        
        # 爬取数据（现在函数内部会自动保存）
        fetch_historical_data(symbol, start_time, end_time)
    
    print('\n历史数据爬取完成！')


def main():
    """
    主函数，启动加密货币价格分析工具
    """
    print('启动加密货币价格分析工具...')
    print('项目: Analysis of Cryptocurrency Price Trends')
    print('仓库: https://github.com/idealism-L')
    print('=============================================')
    
    # 初始化数据库
    init_database()
    
    # 从最新数据时间开始爬取历史数据
    fetch_historical_data_from_latest()
    
    # 启动定时任务（每5分钟获取一次价格）
    print('\n启动定时任务...')
    setup_scheduler()


if __name__ == '__main__':
    # 当脚本直接运行时执行主函数
    main()