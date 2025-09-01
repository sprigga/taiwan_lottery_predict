# 台灣彩券 AI 選號系統

## 專案概述

這個專案結合了 **FastAPI** 後端和 **Vue.js** 前端，為台灣彩券提供 AI 智能選號服務。系統使用 Google Gemini AI 分析半年歷史資料，提供大樂透號碼推薦和選號理由。

## 🏗️ 系統架構

```
TaiwanLotteryCrawler/
├── backend/                 # FastAPI 後端
│   └── main.py             # 主要 API 服務
├── frontend/               # Vue.js 前端
│   ├── src/
│   │   ├── views/          # 頁面元件
│   │   │   ├── Home.vue    # 首頁
│   │   │   ├── Lotto649.vue # 大樂透 AI 選號
│   │   │   ├── SuperLotto.vue # 威力彩查詢
│   │   │   └── History.vue  # 歷史資料查詢
│   │   ├── App.vue         # 主應用元件
│   │   └── main.js         # 應用入口
│   ├── package.json        # Node.js 依賴
│   └── vite.config.js      # Vite 設定
├── TaiwanLottery/          # 原始爬蟲模組
├── Lottery_predict.py      # AI 預測邏輯
├── requirements.txt        # Python 依賴
└── start_dev.sh           # 開發環境啟動腳本
```

## 🚀 快速開始

### 1. 環境需求

- **Python 3.8+**
- **Node.js 16+** 和 **npm**
- **Google AI API Key** (用於 Gemini AI)

### 2. 設定環境變數

建立 `.env` 檔案：
```bash
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
```

### 3. 一鍵啟動

使用提供的啟動腳本：
```bash
./start_dev.sh
```

或者手動啟動：

#### 後端 (FastAPI)
```bash
# 安裝 Python 依賴
pip install -r requirements.txt

# 啟動後端服務
cd backend
python main.py
```

#### 前端 (Vue.js)
```bash
# 安裝 Node.js 依賴
cd frontend
npm install

# 啟動前端開發服務器
npm run dev
```

### 4. 訪問應用

- **前端應用**: http://localhost:3000
- **後端 API**: http://localhost:8000
- **API 文件**: http://localhost:8000/docs

## 🎯 功能特色

### 1. AI 智能選號
- 使用 Google Gemini 2.5 Pro 分析半年歷史資料
- 提供冷門號碼組合和熱門號碼組合
- 詳細的選號理由說明

### 2. 號碼頻率分析
- 熱門號碼統計 (前10名)
- 冷門號碼統計 (後10名)
- 完整的號碼出現頻率報告

### 3. 多彩種支援
- **大樂透** (6/49+1) - AI 選號功能
- **威力彩** (6/38+1) - 歷史資料查詢
- **今彩539** (5/39) - 歷史資料查詢

### 4. 響應式 UI
- 基於 Element Plus 的現代化界面
- 手機、平板、電腦完美適配
- 直觀的資料視覺化

## 📊 API 端點

### 大樂透相關
- `GET /api/lotto649` - 獲取大樂透歷史資料
- `GET /api/lotto649/predict` - AI 預測大樂透號碼

### 其他彩種
- `GET /api/super_lotto` - 威力彩歷史資料
- `GET /api/daily_cash` - 今彩539歷史資料

### 查詢參數
- `year` - 年份 (字串格式，如 "2024")
- `month` - 月份 (字串格式，如 "03")

## 🛠️ 技術棧

### 後端
- **FastAPI** - 現代化的 Python Web 框架
- **Pydantic** - 資料驗證和序列化
- **Uvicorn** - ASGI 伺服器
- **Google Generative AI** - AI 分析引擎

### 前端
- **Vue 3** - 漸進式 JavaScript 框架
- **Vue Router** - 路由管理
- **Element Plus** - UI 元件庫
- **Axios** - HTTP 客戶端
- **Vite** - 快速建構工具

### 資料來源
- **台灣彩券官方 API** - `https://api.taiwanlottery.com`

## 🔧 開發指令

### 後端開發
```bash
# 執行測試
pytest

# 程式碼格式檢查
flake8

# 安裝為開發模式
pip install -e .
```

### 前端開發
```bash
# 開發模式
npm run dev

# 建構生產版本
npm run build

# 預覽生產版本
npm run preview
```

## 📝 使用說明

### 1. 首頁
- 系統功能介紹
- 快速導航到各功能頁面

### 2. 大樂透 AI 選號
- 點擊「獲取推薦」按鈕
- AI 將分析半年歷史資料
- 提供兩組推薦號碼和詳細理由
- 顯示號碼頻率統計

### 3. 威力彩查詢
- 選擇查詢的年月
- 查看該月份的所有開獎記錄
- 支援分頁瀏覽

### 4. 歷史資料查詢
- 支援多種彩券類型
- 靈活的年月查詢
- 詳細的統計資訊

## ⚠️ 注意事項

1. **AI 功能需要 Google AI API Key**
2. **本系統僅供娛樂參考，不保證中獎**
3. **請理性投注，量力而為**
4. **建議在良好的網路環境下使用**

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request 來改善這個專案！

## 📄 授權條款

本專案採用原有的授權條款。