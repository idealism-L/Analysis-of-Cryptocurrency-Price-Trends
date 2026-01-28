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


def fetch_fear_greed_index():
    """
    获取比特币贪婪恐惧指数
    
    返回:
        int: 贪婪恐惧指数 (0-100)
    """
    try:
        # 使用Alternative.me的API获取贪婪恐惧指数
        response = requests.get('https://api.alternative.me/fng/?limit=1')
        response.raise_for_status()
        data = response.json()
        if data['data'] and len(data['data']) > 0:
            return int(data['data'][0]['value'])
        return None
    except Exception as error:
        print('获取贪婪恐惧指数失败:', str(error))
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
        
        # 获取贪婪恐惧指数
        fear_greed_index = fetch_fear_greed_index()
        print(f"当前贪婪恐惧指数: {fear_greed_index}")
        
        # 准备插入数据
        insert_data = []
        for item in data:
            # 解析时间戳
            timestamp = datetime.fromisoformat(item['timestamp'])
            
            # 查询币种ID
            cursor.execute("SELECT id FROM currencies WHERE symbol = %s", (item['symbol'],))
            currency_result = cursor.fetchone()
            if not currency_result:
                print(f"币种 {item['symbol']} 不存在，跳过保存")
                continue
            
            currency_id = currency_result[0]
            
            insert_data.append((
                currency_id,
                item['symbol'],
                item['price'],
                fear_greed_index,
                timestamp
            ))
        
        if not insert_data:
            print("没有数据可保存")
            cursor.close()
            conn.close()
            return
        
        # 执行批量插入
        insert_sql = """
        INSERT INTO price_data (currency_id, symbol, price, fear_greed_index, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_sql, insert_data)
        
        # 提交事务
        conn.commit()
        
        print(f"成功保存 {len(insert_data)} 条价格数据到数据库")
        
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


def main():
    """
    主函数，启动加密货币价格分析工具
    """
    print('启动加密货币价格分析工具...')
    print('项目: Analysis of Cryptocurrency Price Trends')
    print('仓库: https://github.com/idealism-L')
    print('=============================================')
    
    # 设置并启动定时任务
    setup_scheduler()


if __name__ == '__main__':
    # 当脚本直接运行时执行主函数
    main()