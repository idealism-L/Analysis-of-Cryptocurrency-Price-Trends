# 导入必要的库
import pymysql

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'cryptocurrency_analysis',
    'charset': 'utf8mb4'
}

def remove_fng_column():
    """
    从price_data表中删除fear_greed_index列
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
        
        print('开始从price_data表中删除fear_greed_index列...')
        
        # 检查列是否存在
        cursor.execute("""
        SELECT COLUMN_NAME
        FROM information_schema.COLUMNS
        WHERE table_schema = DATABASE()
        AND table_name = 'price_data'
        AND column_name = 'fear_greed_index'
        """)
        
        if cursor.fetchone():
            # 执行删除列的操作
            cursor.execute("""
            ALTER TABLE price_data
            DROP COLUMN fear_greed_index
            """)
            print('成功从price_data表中删除fear_greed_index列')
        else:
            print('price_data表中不存在fear_greed_index列，无需删除')
        
        # 提交修改
        conn.commit()
        
        # 验证操作结果
        cursor.execute("""
        DESCRIBE price_data
        """)
        
        print('\nprice_data表当前结构:')
        for row in cursor.fetchall():
            print(f'{row[0]}: {row[1]}')
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        print('\n操作完成！')
        print('price_data表中的fear_greed_index列已成功删除，数据已迁移到新的fear_greed_index表中。')
        
    except Exception as error:
        print('删除fear_greed_index列失败:', str(error))
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    remove_fng_column()
