import os
import json
import logging
import pymysql
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4')
}

DB_NAME = os.getenv('DB_NAME', 'cryptocurrency_analysis')

SYMBOLS = ['BTC', 'ETH']

MAX_RETRIES = 3
REQUEST_LIMIT = 500
BATCH_SIZE = 1000

INITIAL_FUNDS = float(os.getenv('INITIAL_FUNDS', '10000'))

BUY_THRESHOLDS = json.loads(os.getenv('BUY_THRESHOLDS', '[{"fng": 10, "btc": 500, "eth": 300}, {"fng": 15, "btc": 200, "eth": 100}, {"fng": 20, "btc": 100, "eth": 50}]'))

SELL_THRESHOLDS = json.loads(os.getenv('SELL_THRESHOLDS', '[{"fng": 90, "btc": 0.03, "eth": 0.05}, {"fng": 85, "btc": 0.01, "eth": 0.02}, {"fng": 80, "btc": 0.005, "eth": 0.01}]'))

INVESTMENT_STRATEGY = {
    'buy_thresholds': BUY_THRESHOLDS,
    'sell_thresholds': SELL_THRESHOLDS
}


@contextmanager
def get_db_connection(use_database=True):
    conn = None
    try:
        config = DB_CONFIG.copy()
        if use_database:
            config['database'] = DB_NAME
        conn = pymysql.connect(**config)
        yield conn
    except Exception as error:
        logger.error(f'数据库连接失败: {error}')
        yield None
    finally:
        if conn:
            conn.close()
