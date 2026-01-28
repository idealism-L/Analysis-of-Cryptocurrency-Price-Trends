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

def add_table_comments():
    """
    给数据库中的表格添加注释
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
        
        print('开始给表格添加注释...')
        
        # 给currencies表添加注释
        cursor.execute("""
        ALTER TABLE currencies
        COMMENT '币种主表 - 存储加密货币基本信息'
        """)
        print('已给currencies表添加注释')
        
        # 给price_data表添加注释
        cursor.execute("""
        ALTER TABLE price_data
        COMMENT '价格子表 - 存储加密货币价格和贪婪恐惧指数数据'
        """)
        print('已给price_data表添加注释')
        
        # 给trade_records表添加注释
        cursor.execute("""
        ALTER TABLE trade_records
        COMMENT '交易记录表 - 存储投资策略的交易记录'
        """)
        print('已给trade_records表添加注释')
        
        # 提交修改
        conn.commit()
        print('所有表格注释添加成功！')
        
        # 验证注释是否添加成功
        cursor.execute("""
        SELECT table_name, table_comment
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
        AND table_name IN ('currencies', 'price_data', 'trade_records')
        """)
        
        print('\n表格注释验证:')
        for row in cursor.fetchall():
            print(f'{row[0]}: {row[1]}')
        
        # 关闭连接
        cursor.close()
        conn.close()
        
    except Exception as error:
        print('添加表格注释失败:', str(error))
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_table_comments()
