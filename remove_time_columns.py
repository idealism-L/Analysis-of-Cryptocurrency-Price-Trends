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

def remove_time_columns():
    """
    从fear_greed_index表中删除created_at和updated_at列
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
        
        print('开始从fear_greed_index表中删除时间列...')
        
        # 检查并删除created_at列
        cursor.execute("""
        SELECT COLUMN_NAME
        FROM information_schema.COLUMNS
        WHERE table_schema = DATABASE()
        AND table_name = 'fear_greed_index'
        AND column_name = 'created_at'
        """)
        
        if cursor.fetchone():
            cursor.execute("""
            ALTER TABLE fear_greed_index
            DROP COLUMN created_at
            """)
            print('成功从fear_greed_index表中删除created_at列')
        else:
            print('fear_greed_index表中不存在created_at列，无需删除')
        
        # 检查并删除updated_at列
        cursor.execute("""
        SELECT COLUMN_NAME
        FROM information_schema.COLUMNS
        WHERE table_schema = DATABASE()
        AND table_name = 'fear_greed_index'
        AND column_name = 'updated_at'
        """)
        
        if cursor.fetchone():
            cursor.execute("""
            ALTER TABLE fear_greed_index
            DROP COLUMN updated_at
            """)
            print('成功从fear_greed_index表中删除updated_at列')
        else:
            print('fear_greed_index表中不存在updated_at列，无需删除')
        
        # 提交修改
        conn.commit()
        
        # 验证操作结果
        cursor.execute("""
        DESCRIBE fear_greed_index
        """)
        
        print('\nfear_greed_index表当前结构:')
        for row in cursor.fetchall():
            print(f'{row[0]}: {row[1]}')
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        print('\n操作完成！')
        print('fear_greed_index表中的时间列已成功删除，表结构更加简洁。')
        
    except Exception as error:
        print('删除时间列失败:', str(error))
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    remove_time_columns()
