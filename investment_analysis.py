import logging
from datetime import datetime, timedelta

from config import (
    get_db_connection, INITIAL_FUNDS, INVESTMENT_STRATEGY
)

logger = logging.getLogger(__name__)


class InvestmentAnalyzer:
    def __init__(self, initial_funds=None, investment_strategy=None):
        self.initial_funds = initial_funds if initial_funds is not None else INITIAL_FUNDS
        self.current_funds = self.initial_funds
        self.btc_holdings = 0
        self.eth_holdings = 0
        self.btc_average_price = 0
        self.eth_average_price = 0
        self.trade_records = []
        self.last_buy_date = None
        self.last_sell_date = None
        
        self.investment_strategy = investment_strategy if investment_strategy is not None else INVESTMENT_STRATEGY
        
        self.create_trade_table()
    
    def get_latest_timestamp(self, table, date_column):
        with get_db_connection() as conn:
            if not conn:
                return None
            cursor = conn.cursor()
            query = f"SELECT MAX({date_column}) FROM {table}"
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result and result[0] else None
    
    def create_trade_table(self):
        try:
            with get_db_connection() as conn:
                if not conn:
                    return
                
                cursor = conn.cursor()
                
                cursor.execute("DROP TABLE IF EXISTS trade_records")
                
                create_table_sql = """
                CREATE TABLE trade_records (
                    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '交易记录ID',
                    trade_date DATE NOT NULL COMMENT '交易日期',
                    trade_type VARCHAR(10) NOT NULL COMMENT '交易类型：buy或sell',
                    btc_trade_amount DECIMAL(20, 8) NOT NULL COMMENT 'BTC交易数量',
                    btc_trade_value DECIMAL(20, 2) NOT NULL COMMENT 'BTC交易金额',
                    btc_trade_price DECIMAL(20, 2) NOT NULL COMMENT 'BTC交易时价格',
                    eth_trade_amount DECIMAL(20, 8) NOT NULL COMMENT 'ETH交易数量',
                    eth_trade_value DECIMAL(20, 2) NOT NULL COMMENT 'ETH交易金额',
                    eth_trade_price DECIMAL(20, 2) NOT NULL COMMENT 'ETH交易时价格',
                    total_trade_value DECIMAL(20, 2) NOT NULL COMMENT '交易总金额',
                    btc_holdings DECIMAL(20, 8) NOT NULL COMMENT 'BTC持仓数量',
                    eth_holdings DECIMAL(20, 8) NOT NULL COMMENT 'ETH持仓数量',
                    btc_average_price DECIMAL(20, 2) NOT NULL COMMENT 'BTC持仓均价',
                    eth_average_price DECIMAL(20, 2) NOT NULL COMMENT 'ETH持仓均价',
                    remaining_usd DECIMAL(20, 2) NOT NULL COMMENT '剩余资金（USD）',
                    account_total DECIMAL(20, 2) NOT NULL COMMENT '账户总价值',
                    trade_note TEXT NOT NULL COMMENT '交易备注',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易记录表';
                """
                
                cursor.execute(create_table_sql)
                conn.commit()
                logger.info("交易记录表已重新创建")
        except Exception as error:
            logger.error(f'创建交易记录表失败: {error}')
    
    def save_trade_to_database(self, trade_record):
        try:
            with get_db_connection() as conn:
                if not conn:
                    return
                
                cursor = conn.cursor()
                
                insert_sql = """
                INSERT INTO trade_records (
                    trade_date, trade_type, btc_trade_amount, btc_trade_value, btc_trade_price, 
                    eth_trade_amount, eth_trade_value, eth_trade_price, total_trade_value, 
                    btc_holdings, eth_holdings, btc_average_price, eth_average_price, 
                    remaining_usd, account_total, trade_note
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (
                    trade_record['trade_date'],
                    trade_record['trade_type'],
                    trade_record.get('btc_trade_amount', 0),
                    trade_record.get('btc_trade_value', 0),
                    trade_record.get('btc_trade_price', 0),
                    trade_record.get('eth_trade_amount', 0),
                    trade_record.get('eth_trade_value', 0),
                    trade_record.get('eth_trade_price', 0),
                    trade_record['total_trade_value'],
                    trade_record['btc_holdings'],
                    trade_record.get('eth_holdings', self.eth_holdings),
                    trade_record.get('btc_average_price', 0),
                    trade_record.get('eth_average_price', 0),
                    trade_record['remaining_usd'],
                    trade_record['account_total'],
                    trade_record.get('trade_note', '')
                ))
                conn.commit()
        except Exception as error:
            logger.error(f'保存交易记录到数据库失败: {error}')
    
    def preload_data(self):
        logger.info("正在预加载数据...")
        
        try:
            with get_db_connection() as conn:
                if not conn:
                    return False
                
                cursor = conn.cursor()
                
                self.daily_prices = {'BTC': {}, 'ETH': {}}
                
                query = """
                SELECT DATE(timestamp) as date, AVG(price) as avg_price
                FROM price_data
                WHERE symbol = 'BTC' AND DATE(timestamp) >= '2020-01-01'
                GROUP BY DATE(timestamp)
                """
                cursor.execute(query)
                for row in cursor.fetchall():
                    date_str = row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])
                    self.daily_prices['BTC'][date_str] = float(row[1])
                
                query = """
                SELECT DATE(timestamp) as date, AVG(price) as avg_price
                FROM price_data
                WHERE symbol = 'ETH' AND DATE(timestamp) >= '2020-01-01'
                GROUP BY DATE(timestamp)
                """
                cursor.execute(query)
                for row in cursor.fetchall():
                    date_str = row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])
                    self.daily_prices['ETH'][date_str] = float(row[1])
                
                self.daily_fng = {}
                query = """
                SELECT date, value as fear_greed_index
                FROM fear_greed_index
                WHERE date >= '2020-01-01'
                ORDER BY date
                """
                cursor.execute(query)
                for row in cursor.fetchall():
                    date_str = row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])
                    self.daily_fng[date_str] = int(row[1])
                
                logger.info(f"预加载完成: {len(self.daily_prices)} 天价格数据, {len(self.daily_fng)} 天贪婪恐惧指数数据")
                
                buy_thresholds = [t['fng'] for t in self.investment_strategy['buy_thresholds']]
                sell_thresholds = [t['fng'] for t in self.investment_strategy['sell_thresholds']]
                min_buy_threshold = min(buy_thresholds) if buy_thresholds else 30
                max_sell_threshold = max(sell_thresholds) if sell_thresholds else 65
                
                logger.debug("潜在交易日期:")
                for date, fng in self.daily_fng.items():
                    if fng < min_buy_threshold and date in self.daily_prices:
                        logger.debug(f"{date}: FNG={fng} (买入信号)")
                    elif fng > max_sell_threshold and date in self.daily_prices:
                        logger.debug(f"{date}: FNG={fng} (卖出信号)")
                
                return True
        except Exception as error:
            logger.error(f'预加载数据失败: {error}')
            return False
    
    def get_daily_average_price(self, symbol, date):
        if hasattr(self, 'daily_prices') and symbol in self.daily_prices:
            if date in self.daily_prices[symbol]:
                return self.daily_prices[symbol][date]
            for stored_date in self.daily_prices[symbol]:
                if str(stored_date) == date:
                    return self.daily_prices[symbol][stored_date]
        return None
    
    def get_daily_fear_greed_index(self, date):
        if hasattr(self, 'daily_fng'):
            if date in self.daily_fng:
                return self.daily_fng[date]
            for stored_date in self.daily_fng:
                if str(stored_date) == date:
                    return self.daily_fng[stored_date]
        return None
    
    def calculate_investment_amount(self, fng):
        sorted_buy_thresholds = sorted(self.investment_strategy['buy_thresholds'], key=lambda x: x['fng'])
        
        for threshold in sorted_buy_thresholds:
            if fng < threshold['fng']:
                return (threshold['btc'], threshold['eth'])
        
        return (0, 0)
    
    def buy_crypto(self, date, btc_price, eth_price, fng):
        btc_investment, eth_investment = self.calculate_investment_amount(fng)
        
        if self.current_funds < btc_investment:
            logger.warning(f"{date}: 资金不足，无法买入 {btc_investment} 美元的BTC")
            return False
        
        btc_amount = btc_investment / btc_price
        
        self.btc_holdings += btc_amount
        self.current_funds -= btc_investment
        
        if self.btc_holdings > 0:
            new_btc_average_price = (self.btc_average_price * (self.btc_holdings - btc_amount) + btc_investment) / self.btc_holdings
            self.btc_average_price = new_btc_average_price
        else:
            self.btc_average_price = 0
        
        if self.current_funds < eth_investment:
            logger.warning(f"{date}: 资金不足，无法买入 {eth_investment} 美元的ETH")
            return False
        
        eth_amount = eth_investment / eth_price
        
        self.eth_holdings += eth_amount
        self.current_funds -= eth_investment
        
        if self.eth_holdings > 0:
            new_eth_average_price = (self.eth_average_price * (self.eth_holdings - eth_amount) + eth_investment) / self.eth_holdings
            self.eth_average_price = new_eth_average_price
        else:
            self.eth_average_price = 0
        
        account_total = self.current_funds + (self.btc_holdings * btc_price) + (self.eth_holdings * eth_price)
        
        trade_note = f"当日贪恐指数: {fng} - 交易类型: buy - 以${btc_price:.2f}价格买入{btc_amount:.6f}BTC - 以${eth_price:.2f}价格买入{eth_amount:.6f}ETH"
        
        trade_record = {
            'trade_date': date,
            'trade_type': 'buy',
            'btc_trade_amount': btc_amount,
            'btc_trade_value': btc_investment,
            'btc_trade_price': btc_price,
            'eth_trade_amount': eth_amount,
            'eth_trade_value': eth_investment,
            'eth_trade_price': eth_price,
            'total_trade_value': btc_investment + eth_investment,
            'btc_holdings': self.btc_holdings,
            'eth_holdings': self.eth_holdings,
            'btc_average_price': self.btc_average_price,
            'eth_average_price': self.eth_average_price,
            'remaining_usd': self.current_funds,
            'account_total': account_total,
            'trade_note': trade_note
        }
        self.trade_records.append(trade_record)
        
        self.save_trade_to_database(trade_record)
        
        buy_details = []
        if btc_amount > 0:
            buy_details.append(f"买入 {btc_amount:.6f} BTC, 花费: ${btc_investment:.2f}")
        if eth_amount > 0:
            buy_details.append(f"买入 {eth_amount:.6f} ETH, 花费: ${eth_investment:.2f}")
        logger.info(f"{date}: {'; '.join(buy_details)}")
        logger.debug(f"  当前持有: BTC={self.btc_holdings:.6f}, ETH={self.eth_holdings:.6f}, 剩余资金: ${self.current_funds:.2f}")
        logger.debug(f"  账户总额: ${account_total:.2f}")
        
        self.last_buy_date = date
        return True
    
    def sell_crypto(self, date, btc_price, eth_price, fng):
        if self.btc_holdings <= 0 and self.eth_holdings <= 0:
            logger.warning(f"{date}: 没有加密货币可卖")
            return False
        
        sorted_sell_thresholds = sorted(self.investment_strategy['sell_thresholds'], key=lambda x: x['fng'], reverse=True)
        
        btc_sell_percentage = None
        eth_sell_percentage = None
        
        for threshold in sorted_sell_thresholds:
            if fng >= threshold['fng']:
                btc_sell_percentage = threshold['btc']
                eth_sell_percentage = threshold['eth']
                break
        
        if btc_sell_percentage is None or eth_sell_percentage is None:
            return False
        
        if self.btc_holdings > 0:
            btc_sell_amount = self.btc_holdings * btc_sell_percentage
            btc_sell_value = btc_sell_amount * btc_price
            
            self.btc_holdings -= btc_sell_amount
            self.current_funds += btc_sell_value
        else:
            btc_sell_amount = 0
            btc_sell_value = 0
        
        if self.eth_holdings > 0:
            eth_sell_amount = self.eth_holdings * eth_sell_percentage
            eth_sell_value = eth_sell_amount * eth_price
            
            self.eth_holdings -= eth_sell_amount
            self.current_funds += eth_sell_value
        else:
            eth_sell_amount = 0
            eth_sell_value = 0
        
        total_sell_value = btc_sell_value + eth_sell_value
        
        account_total = self.current_funds + (self.btc_holdings * btc_price) + (self.eth_holdings * eth_price)
        
        trade_note = f"当日贪恐指数: {fng} - 交易类型: sell - 以${btc_price:.2f}价格卖出{btc_sell_amount:.6f}BTC - 以${eth_price:.2f}价格卖出{eth_sell_amount:.6f}ETH"
        
        trade_record = {
            'trade_date': date,
            'trade_type': 'sell',
            'btc_trade_amount': btc_sell_amount,
            'btc_trade_value': btc_sell_value,
            'btc_trade_price': btc_price,
            'eth_trade_amount': eth_sell_amount,
            'eth_trade_value': eth_sell_value,
            'eth_trade_price': eth_price,
            'total_trade_value': total_sell_value,
            'btc_holdings': self.btc_holdings,
            'eth_holdings': self.eth_holdings,
            'btc_average_price': self.btc_average_price,
            'eth_average_price': self.eth_average_price,
            'remaining_usd': self.current_funds,
            'account_total': account_total,
            'trade_note': trade_note
        }
        self.trade_records.append(trade_record)
        
        self.save_trade_to_database(trade_record)
        
        if btc_sell_amount > 0 or eth_sell_amount > 0:
            sell_details = []
            if btc_sell_amount > 0:
                sell_details.append(f"卖出 {btc_sell_amount:.6f} BTC, 获得: ${btc_sell_value:.2f}")
            if eth_sell_amount > 0:
                sell_details.append(f"卖出 {eth_sell_amount:.6f} ETH, 获得: ${eth_sell_value:.2f}")
            logger.info(f"{date}: {'; '.join(sell_details)}")
            logger.debug(f"  当前持有: BTC={self.btc_holdings:.6f}, ETH={self.eth_holdings:.6f}, 剩余资金: ${self.current_funds:.2f}")
            logger.debug(f"  账户总额: ${account_total:.2f}")
        
        self.last_sell_date = date
        return True
    
    def analyze_investment(self, start_date=None, end_date=None):
        logger.info("加密货币投资策略分析")
        logger.info(f"初始资金: ${self.initial_funds:.2f}")
        
        buy_strategy_lines = []
        for threshold in sorted(self.investment_strategy['buy_thresholds'], key=lambda x: x['fng']):
            buy_strategy_lines.append(f"{threshold['fng']}以下买入{threshold['btc']}u BTC和{threshold['eth']}u ETH")
        buy_strategy = "，".join(buy_strategy_lines)
        logger.info(f"投资策略: 贪婪恐惧指数{buy_strategy}")
        
        sell_strategy_lines = []
        for threshold in sorted(self.investment_strategy['sell_thresholds'], key=lambda x: x['fng']):
            btc_percent = threshold['btc'] * 100
            eth_percent = threshold['eth'] * 100
            sell_strategy_lines.append(f"{threshold['fng']}以上卖出BTC {btc_percent:.0f}%和ETH {eth_percent:.0f}%")
        sell_strategy = "，".join(sell_strategy_lines)
        logger.info(f"卖出策略: 贪婪恐惧指数{sell_strategy}")
        
        if not start_date:
            start_date = datetime(2020, 1, 1)
        if not end_date:
            end_date = datetime.now()
        
        logger.info(f"投资开始时间: {start_date.strftime('%Y年%m月%d日')}")
        logger.info(f"投资结束时间: {end_date.strftime('%Y年%m月%d日')}")
        
        if not self.preload_data():
            logger.error("数据预加载失败，无法继续分析")
            return
        
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            fng = self.get_daily_fear_greed_index(date_str)
            if fng is None:
                current_date += timedelta(days=1)
                continue
            
            btc_price = self.get_daily_average_price('BTC', date_str)
            if btc_price is None:
                current_date += timedelta(days=1)
                continue
            
            eth_price = self.get_daily_average_price('ETH', date_str)
            if eth_price is None:
                current_date += timedelta(days=1)
                continue
            
            if fng is not None and btc_price is not None and eth_price is not None:
                buy_thresholds = [t['fng'] for t in self.investment_strategy['buy_thresholds']]
                sell_thresholds = [t['fng'] for t in self.investment_strategy['sell_thresholds']]
                max_buy_threshold = max(buy_thresholds) if buy_thresholds else 20
                min_sell_threshold = min(sell_thresholds) if sell_thresholds else 80
                
                if fng < max_buy_threshold:
                    if self.last_buy_date != date_str:
                        logger.debug(f"{date_str}: 贪婪恐惧指数={fng}, BTC均价=${btc_price:.2f}, ETH均价=${eth_price:.2f}")
                        self.buy_crypto(date_str, btc_price, eth_price, fng)
                elif fng >= min_sell_threshold:
                    if self.last_sell_date != date_str:
                        logger.debug(f"{date_str}: 贪婪恐惧指数={fng}, BTC均价=${btc_price:.2f}, ETH均价=${eth_price:.2f}")
                        self.sell_crypto(date_str, btc_price, eth_price, fng)
            
            current_date += timedelta(days=1)
        
        self.print_summary(end_date)
    
    def print_summary(self, end_date):
        logger.info("投资策略分析总结")
        
        latest_date = end_date.strftime('%Y-%m-%d')
        btc_final_price = self.get_daily_average_price('BTC', latest_date)
        eth_final_price = self.get_daily_average_price('ETH', latest_date)
        
        if not btc_final_price:
            if self.trade_records:
                latest_trade = self.trade_records[-1]
                btc_final_price = latest_trade.get('btc_trade_price', 0)
                logger.debug(f"使用最近交易价格作为BTC最终价格: ${btc_final_price:.2f}")
        
        if not eth_final_price:
            if self.trade_records:
                for trade in reversed(self.trade_records):
                    if 'ETH' in trade.get('trade_note', ''):
                        eth_final_price = trade.get('eth_trade_price', 0)
                        logger.debug(f"使用最近交易价格作为ETH最终价格: ${eth_final_price:.2f}")
                        break
        
        if btc_final_price and eth_final_price:
            btc_value = self.btc_holdings * btc_final_price
            eth_value = self.eth_holdings * eth_final_price
            total_value = self.current_funds + btc_value + eth_value
            
            logger.info(f"初始资金: ${self.initial_funds:.2f}")
            logger.info(f"最终资金: ${self.current_funds:.2f}")
            logger.info(f"最终持有BTC: {self.btc_holdings:.6f}")
            logger.info(f"最终持有ETH: {self.eth_holdings:.6f}")
            logger.info(f"BTC最终价格: ${btc_final_price:.2f}")
            logger.info(f"ETH最终价格: ${eth_final_price:.2f}")
            logger.info(f"BTC持仓均价: ${self.btc_average_price:.2f}")
            logger.info(f"ETH持仓均价: ${self.eth_average_price:.2f}")
            logger.info(f"BTC价值: ${btc_value:.2f}")
            logger.info(f"ETH价值: ${eth_value:.2f}")
            logger.info(f"总价值 (BTC+ETH+U): ${total_value:.2f}")
            logger.info(f"收益率: {(total_value / self.initial_funds - 1) * 100:.2f}%")
        else:
            logger.info(f"初始资金: ${self.initial_funds:.2f}")
            logger.info(f"最终资金: ${self.current_funds:.2f}")
            logger.info(f"最终持有BTC: {self.btc_holdings:.6f}")
            logger.info(f"最终持有ETH: {self.eth_holdings:.6f}")
            logger.info(f"BTC持仓均价: ${self.btc_average_price:.2f}")
            logger.info(f"ETH持仓均价: ${self.eth_average_price:.2f}")
            logger.warning("无法计算总价值（缺少价格数据）")
        
        logger.info(f"交易次数: {len(self.trade_records)}")
        logger.info(f"买入次数: {sum(1 for r in self.trade_records if r['trade_type'] == 'buy')}")
        logger.info(f"卖出次数: {sum(1 for r in self.trade_records if r['trade_type'] == 'sell')}")


if __name__ == '__main__':
    logger.info("启动加密货币投资策略分析...")
    
    analyzer = InvestmentAnalyzer()
    
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2020, 12, 31)
    
    if start_date >= end_date:
        logger.warning("错误: 开始时间必须早于结束时间")
        start_date = datetime(2020, 1, 1)
        end_date = datetime.now()
        logger.info(f"使用默认时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    
    analyzer.analyze_investment(start_date, end_date)
