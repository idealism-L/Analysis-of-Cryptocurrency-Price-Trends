# 检查贪婪恐惧指数数据范围
import pymysql

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'cryptocurrency_analysis',
    'charset': 'utf8mb4'
}

def get_db_connection():
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

def check_fng_range():
    print("检查贪婪恐惧指数数据范围...")
    
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 查询贪婪恐惧指数的最小值、最大值和分布
    query = """
    SELECT 
        MIN(fear_greed_index) as min_fng,
        MAX(fear_greed_index) as max_fng,
        AVG(fear_greed_index) as avg_fng
    FROM price_data
    WHERE fear_greed_index IS NOT NULL
    """
    cursor.execute(query)
    stats = cursor.fetchone()
    
    print(f"贪婪恐惧指数统计:")
    print(f"最小值: {stats[0]}")
    print(f"最大值: {stats[1]}")
    print(f"平均值: {stats[2]:.2f}")
    
    # 查询不同区间的天数
    ranges = [(0, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 65), (65, 70), (70, 80), (80, 100)]
    print("\n不同区间的天数分布:")
    
    for min_val, max_val in ranges:
        query = """
        SELECT COUNT(DISTINCT DATE(timestamp)) as day_count
        FROM price_data
        WHERE fear_greed_index IS NOT NULL
        AND fear_greed_index >= %s AND fear_greed_index < %s
        """
        cursor.execute(query, (min_val, max_val))
        count = cursor.fetchone()[0]
        print(f"{min_val}-{max_val}: {count} 天")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_fng_range()
