import requests
import time
import json
from datetime import datetime
import os

class FNGUpdateChecker:
    def __init__(self):
        self.api_url = "https://api.binance.com/api/v3/ticker/price"
        self.fng_symbol = "BTCUSDT"  # 使用BTC价格作为参考
        self.data_file = "fng_update_records.json"
        self.update_records = self.load_records()
    
    def load_records(self):
        """加载已有的更新记录"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_records(self):
        """保存更新记录到文件"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.update_records, f, indent=2, ensure_ascii=False)
    
    def get_current_price(self):
        """获取当前BTC价格"""
        try:
            response = requests.get(self.api_url, params={"symbol": self.fng_symbol}, timeout=10)
            data = response.json()
            return float(data["price"])
        except Exception as e:
            print(f"获取价格失败: {e}")
            return None
    
    def check_update(self):
        """检查是否有更新"""
        current_price = self.get_current_price()
        if current_price is None:
            return False
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 检查是否有更新记录
        if not self.update_records:
            # 首次记录
            self.update_records.append({
                "time": current_time,
                "price": current_price,
                "change": 0
            })
            self.save_records()
            print(f"首次记录: {current_time}, 价格: ${current_price:.2f}")
            return True
        
        # 检查与上次记录的差异
        last_record = self.update_records[-1]
        price_diff = abs(current_price - last_record["price"])
        percent_diff = (price_diff / last_record["price"]) * 100
        
        # 如果价格变化超过0.1%，视为更新
        if percent_diff > 0.1:
            self.update_records.append({
                "time": current_time,
                "price": current_price,
                "change": percent_diff
            })
            self.save_records()
            print(f"检测到更新: {current_time}, 价格: ${current_price:.2f}, 变化: {percent_diff:.2f}%")
            return True
        
        return False
    
    def analyze_update_frequency(self):
        """分析更新频率"""
        if len(self.update_records) < 2:
            print("记录不足，无法分析更新频率")
            return
        
        time_diffs = []
        for i in range(1, len(self.update_records)):
            time1 = datetime.strptime(self.update_records[i-1]["time"], "%Y-%m-%d %H:%M:%S")
            time2 = datetime.strptime(self.update_records[i]["time"], "%Y-%m-%d %H:%M:%S")
            diff_seconds = (time2 - time1).total_seconds()
            time_diffs.append(diff_seconds)
        
        if time_diffs:
            avg_seconds = sum(time_diffs) / len(time_diffs)
            min_seconds = min(time_diffs)
            max_seconds = max(time_diffs)
            
            print(f"\n更新频率分析:")
            print(f"平均更新间隔: {avg_seconds:.2f} 秒 ({avg_seconds/60:.2f} 分钟)")
            print(f"最短更新间隔: {min_seconds:.2f} 秒")
            print(f"最长更新间隔: {max_seconds:.2f} 秒")
            print(f"总记录数: {len(self.update_records)}")
    
    def run_monitoring(self, duration_minutes=60):
        """运行监控"""
        print(f"开始监控币安贪婪恐惧指数更新频率...")
        print(f"监控时长: {duration_minutes} 分钟")
        print("按 Ctrl+C 停止监控\n")
        
        end_time = time.time() + duration_minutes * 60
        check_interval = 5  # 每5秒检查一次
        
        try:
            while time.time() < end_time:
                self.check_update()
                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("\n监控已手动停止")
        finally:
            self.analyze_update_frequency()

if __name__ == "__main__":
    checker = FNGUpdateChecker()
    checker.run_monitoring()
