const axios = require('axios');
const xlsx = require('xlsx');
const schedule = require('node-schedule');
const fs = require('fs');

const EXCEL_FILE_PATH = './cryptocurrency_prices.xlsx';

async function fetchPrice(symbol) {
  try {
    const response = await axios.get(`https://api.binance.com/api/v3/ticker/price?symbol=${symbol}USDT`);
    return {
      symbol: symbol,
      price: parseFloat(response.data.price),
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error(`获取${symbol}价格失败:`, error.message);
    return {
      symbol: symbol,
      price: null,
      timestamp: new Date().toISOString()
    };
  }
}

async function fetchPrices() {
  console.log('正在获取价格...');
  const btcPrice = await fetchPrice('BTC');
  const ethPrice = await fetchPrice('ETH');
  
  const data = [btcPrice, ethPrice];
  console.log('已获取价格:', data);
  
  saveToExcel(data);
}

function saveToExcel(data) {
  try {
    let workbook;
    let worksheet;
    let existingData = [];
    
    if (fs.existsSync(EXCEL_FILE_PATH)) {
      workbook = xlsx.readFile(EXCEL_FILE_PATH);
      worksheet = workbook.Sheets['Prices'];
      if (worksheet) {
        existingData = xlsx.utils.sheet_to_json(worksheet);
      }
    } else {
      workbook = xlsx.utils.book_new();
    }
    
    const newRows = data.map(item => ({
      Timestamp: item.timestamp,
      Symbol: item.symbol,
      Price: item.price
    }));
    
    const updatedData = [...existingData, ...newRows];
    
    worksheet = xlsx.utils.json_to_sheet(updatedData);
    xlsx.utils.book_append_sheet(workbook, worksheet, 'Prices');
    
    xlsx.writeFile(workbook, EXCEL_FILE_PATH);
    console.log('价格已保存到Excel文件:', EXCEL_FILE_PATH);
  } catch (error) {
    console.error('保存到Excel失败:', error.message);
  }
}

function setupScheduler() {
  console.log('正在设置定时任务...');
  
  fetchPrices();
  
  const job = schedule.scheduleJob('*/5 * * * *', () => {
    fetchPrices();
  });
  
  console.log('定时任务已启动。每5分钟获取一次价格。');
  console.log('按Ctrl+C停止脚本。');
}

function main() {
  console.log('启动加密货币价格分析工具...');
  console.log('项目: Analysis of Cryptocurrency Price Trends');
  console.log('仓库: https://github.com/idealism-L');
  console.log('=============================================');
  
  setupScheduler();
}

if (require.main === module) {
  main();
}

module.exports = {
  fetchPrice,
  fetchPrices,
  saveToExcel,
  setupScheduler
};