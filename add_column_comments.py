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

def add_column_comments():
    """
    给数据库表格中的字段添加注释
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
        
        print('开始给表格字段添加注释...')
        
        # 给currencies表的字段添加注释
        print('\n处理currencies表字段...')
        cursor.execute("""
        ALTER TABLE currencies
        MODIFY COLUMN id INT AUTO_INCREMENT COMMENT '自增主键',
        MODIFY COLUMN symbol VARCHAR(10) NOT NULL UNIQUE COMMENT '币种符号（如BTC、ETH）',
        MODIFY COLUMN name VARCHAR(50) NOT NULL COMMENT '币种名称（如Bitcoin、Ethereum）',
        MODIFY COLUMN is_active BOOLEAN DEFAULT TRUE COMMENT '是否活跃',
        MODIFY COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        MODIFY COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
        """)
        print('currencies表字段注释添加成功')
        
        # 给price_data表的字段添加注释
        print('\n处理price_data表字段...')
        cursor.execute("""
        ALTER TABLE price_data
        MODIFY COLUMN id INT AUTO_INCREMENT COMMENT '自增主键',
        MODIFY COLUMN currency_id INT NOT NULL COMMENT '币种ID（外键）',
        MODIFY COLUMN symbol VARCHAR(10) NOT NULL COMMENT '币种符号（冗余字段）',
        MODIFY COLUMN price DECIMAL(20, 2) NULL COMMENT '价格',
        MODIFY COLUMN fear_greed_index INT NULL COMMENT '贪婪恐惧指数',
        MODIFY COLUMN timestamp DATETIME NOT NULL COMMENT '数据时间戳',
        MODIFY COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
        """)
        print('price_data表字段注释添加成功')
        
        # 给trade_records表的字段添加注释
        print('\n处理trade_records表字段...')
        cursor.execute("""
        ALTER TABLE trade_records
        MODIFY COLUMN id INT AUTO_INCREMENT COMMENT '自增主键',
        MODIFY COLUMN date DATE NOT NULL COMMENT '交易日期',
        MODIFY COLUMN type VARCHAR(10) NOT NULL COMMENT '交易类型（buy/sell）',
        MODIFY COLUMN amount DECIMAL(20, 8) NOT NULL COMMENT '交易数量（BTC）',
        MODIFY COLUMN price DECIMAL(20, 2) NOT NULL COMMENT '交易价格（USD）',
        MODIFY COLUMN total_usd DECIMAL(20, 2) NOT NULL COMMENT '交易总金额（USD）',
        MODIFY COLUMN btc_holdings DECIMAL(20, 8) NOT NULL COMMENT '持有BTC数量',
        MODIFY COLUMN remaining_usd DECIMAL(20, 2) NOT NULL COMMENT '剩余USD金额',
        MODIFY COLUMN account_total DECIMAL(20, 2) NOT NULL COMMENT '账户总价值（USD）',
        MODIFY COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
        """)
        print('trade_records表字段注释添加成功')
        
        # 提交修改
        conn.commit()
        print('\n所有表格字段注释添加成功！')
        
        # 验证注释是否添加成功（可选）
        print('\n验证字段注释（部分字段）:')
        cursor.execute("""
        SELECT column_name, column_comment
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
        AND table_name = 'currencies'
        LIMIT 3
        """)
        print('currencies表前3个字段:')
        for row in cursor.fetchall():
            print(f'{row[0]}: {row[1]}')
        
        cursor.execute("""
        SELECT column_name, column_comment
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
        AND table_name = 'price_data'
        LIMIT 3
        """)
        print('\nprice_data表前3个字段:')
        for row in cursor.fetchall():
            print(f'{row[0]}: {row[1]}')
        
        cursor.execute("""
        SELECT column_name, column_comment
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
        AND table_name = 'trade_records'
        LIMIT 3
        """)
        print('\ntrade_records表前3个字段:')
        for row in cursor.fetchall():
            print(f'{row[0]}: {row[1]}')
        
        # 关闭连接
        cursor.close()
        conn.close()
        
    except Exception as error:
        print('添加字段注释失败:', str(error))
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_column_comments()
