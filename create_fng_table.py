# 导入必要的库
import pymysql
from datetime import datetime

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'cryptocurrency_analysis',
    'charset': 'utf8mb4'
}

def create_fng_table():
    """
    创建贪婪恐惧指数表并迁移数据
    """
    try:
        # 连接到MySQL数据库
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset']
        )
        cursor = conn.cursor()
        
        print('开始创建贪婪恐惧指数表...')
        
        # 创建fear_greed_index表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fear_greed_index (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            date DATE NOT NULL UNIQUE COMMENT '日期',
            value INT NOT NULL COMMENT '贪婪恐惧指数值',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '贪婪恐惧指数表 - 存储每日贪婪恐惧指数数据';
        """)
        print('贪婪恐惧指数表创建成功')
        
        # 从price_data表中提取贪婪恐惧指数数据并去重
        print('开始迁移数据...')
        cursor.execute("""
        INSERT IGNORE INTO fear_greed_index (date, value)
        SELECT DISTINCT DATE(timestamp) as date, fear_greed_index as value
        FROM price_data
        WHERE fear_greed_index IS NOT NULL
        ORDER BY date;
        """)
        
        inserted_count = cursor.rowcount
        print(f'成功迁移 {inserted_count} 条贪婪恐惧指数数据')
        
        # 提交修改
        conn.commit()
        
        # 验证数据迁移结果
        cursor.execute("""
        SELECT COUNT(*) FROM fear_greed_index;
        """)
        total_count = cursor.fetchone()[0]
        print(f'贪婪恐惧指数表中共有 {total_count} 条数据')
        
        # 查看最新的几条数据
        cursor.execute("""
        SELECT date, value
        FROM fear_greed_index
        ORDER BY date DESC
        LIMIT 5;
        """)
        print('\n最新的5条贪婪恐惧指数数据:')
        for row in cursor.fetchall():
            print(f'{row[0]}: {row[1]}')
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        print('\n贪婪恐惧指数表创建和数据迁移完成！')
        print('\n下一步需要修改代码以使用新表：')
        print('1. 修改main.py中的数据获取和存储逻辑')
        print('2. 修改investment_analysis.py中的数据查询逻辑')
        
    except Exception as error:
        print('创建贪婪恐惧指数表失败:', str(error))
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_fng_table()
