# 台灣彩券 AI 選號系統

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.3%2B-4FC08D.svg)](https://vuejs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/stu01509/TaiwanLotteryCrawler/workflows/Merge/badge.svg)](https://github.com/stu01509/TaiwanLotteryCrawler/actions)

## 專案概述

這是一個結合 **AI 智能分析** 和 **現代化 Web 技術** 的台灣彩券選號系統。專案整合了原有的台灣彩券爬蟲功能，並擴展為全棧 Web 應用，提供：

- 🤖 **AI 智能選號**：使用 Google Gemini AI 分析半年歷史資料
- 📊 **數據視覺化**：直觀的號碼頻率統計和趨勢分析  
- 🎯 **多彩種支援**：大樂透、威力彩、今彩539、雙贏彩等
- 📱 **響應式設計**：支援桌面、平板、手機等多種設備
- ⚡ **高效能架構**：FastAPI + Vue.js 現代化技術棧

## 🏗️ 系統架構

```
TaiwanLotteryCrawler/
├── 📁 backend/                    # FastAPI 後端服務
│   └── main.py                   # API 路由與業務邏輯
├── 📁 frontend/                   # Vue.js 前端應用
│   ├── src/
│   │   ├── views/                # 頁面元件
│   │   │   ├── Home.vue         # 首頁與快速選號
│   │   │   ├── Lotto649.vue     # 大樂透詳細分析
│   │   │   ├── SuperLotto.vue   # 威力彩查詢
│   │   │   └── History.vue      # 歷史資料統計
│   │   ├── App.vue              # 主應用元件
│   │   └── main.js              # 應用程式入口
│   ├── package.json             # Node.js 依賴管理
│   └── vite.config.js           # Vite 建構配置
├── 📁 TaiwanLottery/              # 核心爬蟲模組
│   ├── __init__.py              # 主要爬蟲類別
│   └── utils.py                 # 工具函式庫
├── 📁 tests/                     # 單元測試
│   ├── test_lottery.py          # 爬蟲功能測試
│   └── test_utils.py            # 工具函式測試
├── 📁 .github/workflows/         # CI/CD 自動化
│   ├── merge.yaml               # 主分支部署
│   ├── pull_request.yaml        # PR 檢查
│   └── release.yaml             # 版本發布
├── Lottery_predict.py            # AI 預測核心邏輯
├── ISSUE.md                      # 問題修復記錄
├── requirements.txt              # Python 依賴清單
├── setup.py                     # 套件安裝配置
├── pytest.ini                   # 測試配置

## 🔍 核心模組分析

### 1. TaiwanLottery 爬蟲模組

**主要類別**: `TaiwanLotteryCrawler`
- **資料來源**: `https://api.taiwanlottery.com/TLCAPIWeB/Lottery`
- **支援彩種**: 9種台灣彩券類型
- **核心方法**:
  - `lotto649()` - 大樂透 (6/49+特別號)
  - `super_lotto()` - 威力彩 (6/38+第二區1號)
  - `daily_cash()` - 今彩539 (5/39)
  - `lotto1224()` - 雙贏彩 (12/24)
  - `lotto3d()` - 3星彩
  - `lotto4d()` - 4星彩
  - `lotto38m6()` - 38樂合彩
  - `lotto49m6()` - 49樂合彩
  - `lotto39m5()` - 39樂合彩

**工具函數** (`utils.py`):
- `get_current_month()` - 取得當前月份
- `get_current_year()` - 取得當前年份
- `convert_to_republic_era_month()` - 西元年轉民國年
- `month_diff()` - 計算月份差異
- `output_to_json()` - JSON 檔案輸出
- `print_to_table()` - 表格格式顯示

### 2. AI 預測模組 (`Lottery_predict.py`)

**核心功能**:
- **資料收集**: `get_six_months_lotto649_data()` - 擷取半年大樂透資料
- **AI 分析**: `predict_lottery_numbers_with_ai()` - 使用 Google Gemini 2.5 Flash
- **智能選號**: 基於歷史資料提供冷門/熱門號碼組合

**AI 分析策略**:
- 奇偶比分佈 (建議 3:2 或 2:3)
- 大小號分佈 (小號 1-25，大號 26-49)
- 避開連號和順序號
- 遺漏號碼追蹤 (5-10期未出現)
- 熱門/冷門號碼搭配

### 3. FastAPI 後端服務 (`backend/main.py`)

**API 架構**:
- **框架**: FastAPI + Uvicorn
- **CORS 支援**: 跨域請求處理
- **資料模型**: Pydantic 驗證
- **健康檢查**: `/health` 端點

**主要端點**:
- `GET /` - API 服務資訊
- `GET /api/lotto649` - 大樂透歷史資料
- `GET /api/lotto649/predict` - AI 預測服務
- `GET /api/super_lotto` - 威力彩資料
- `GET /api/daily_cash` - 今彩539資料

**AI 預測處理**:
- 正規表達式解析 AI 回應
- 結構化號碼推薦
- 頻率統計分析
- 錯誤處理機制

### 4. Vue.js 前端應用

**技術棧**:
- **框架**: Vue.js 3 + Composition API
- **UI 庫**: Element Plus
- **路由**: Vue Router 4
- **HTTP 客戶端**: Axios
- **建構工具**: Vite

**頁面結構**:
- `App.vue` - 主應用框架，包含導航和佈局
- `Home.vue` - 首頁，快速選號功能
- `Lotto649.vue` - 大樂透專頁，AI 分析結果
- `SuperLotto.vue` - 威力彩查詢頁面
- `History.vue` - 歷史資料統計頁面

### 5. 容器化部署

**Docker 配置**:
- `docker-compose.yml` - 服務編排
- `Dockerfile.backend` - Python 後端容器
- `frontend/Dockerfile` - Node.js 前端容器

**服務架構**:
- **前端服務**: Nginx + Vue.js (Port 8080)
- **後端服務**: FastAPI + Uvicorn (Port 8000)
- **網路**: Bridge 網路連接
- **健康檢查**: 自動服務監控

### 6. CI/CD 流程

**GitHub Actions**:
- `merge.yaml` - 主分支自動測試與部署
- `pull_request.yaml` - PR 程式碼檢查
- `release.yaml` - 版本發布自動化

**品質控制**:
- **測試**: pytest + pytest-cov
- **程式碼檢查**: flake8
- **程式碼掃描**: SonarCloud
- **覆蓋率報告**: Codecov
- **Git Hooks**: pre-commit

## 📊 技術特色

### 資料處理流程
1. **資料擷取** → 台灣彩券官方 API
2. **資料清理** → 格式標準化與驗證
3. **AI 分析** → Google Gemini 深度學習
4. **結果呈現** → RESTful API + 響應式 UI

### 效能最佳化
- **非同步處理**: FastAPI 非同步路由
- **快取機制**: 半年資料本地快取
- **容器化**: Docker 輕量化部署
- **CDN 支援**: 靜態資源最佳化

### 安全性設計
- **API 金鑰管理**: 環境變數保護
- **CORS 政策**: 跨域安全控制
- **輸入驗證**: Pydantic 資料驗證
- **容器安全**: 非 root 使用者執行

## 📈 資料分析能力

### 統計分析功能
- **號碼頻率統計**: 分析半年內各號碼出現次數
- **冷熱門分析**: 識別高頻與低頻號碼
- **遺漏分析**: 追蹤長期未出現的號碼
- **趨勢分析**: 號碼出現模式識別

### AI 智能分析
- **模型**: Google Gemini 2.5 Flash
- **資料範圍**: 過去6個月歷史資料
- **分析維度**: 
  - 奇偶數分佈平衡
  - 大小號碼分佈
  - 連號避免策略
  - 號碼組合最佳化

### 資料格式
```json
{
  "期別": 114000001,
  "開獎日期": "2025-01-02T00:00:00",
  "獎號": [1, 15, 23, 31, 42, 49],
  "特別號": 7
}
```

## 🛠️ 依賴套件分析

### Python 後端依賴
```python
# 核心框架
fastapi>=0.104.0          # 高效能 Web 框架
uvicorn[standard]>=0.24.0 # ASGI 伺服器
pydantic>=2.4.0           # 資料驗證

# 資料處理
requests==2.31.0          # HTTP 請求處理
terminaltables==3.1.0     # 表格格式輸出
python-dotenv>=1.0.0      # 環境變數管理

# AI 整合
google-generativeai>=0.3.0 # Google Gemini API

# 開發工具
pytest==7.4.0            # 單元測試框架
pytest-cov==4.1.0        # 測試覆蓋率
flake8==6.0.0            # 程式碼風格檢查
pre-commit==3.3.3        # Git hooks 管理
```

### 前端依賴
```json
{
  "dependencies": {
    "vue": "^3.3.0",                    // Vue.js 核心框架
    "axios": "^1.5.0",                 // HTTP 客戶端
    "vue-router": "^4.2.0",            // 路由管理
    "element-plus": "^2.4.0",          // UI 組件庫
    "@element-plus/icons-vue": "^2.1.0" // 圖示庫
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.4.0",    // Vue Vite 插件
    "vite": "^4.4.0"                   // 建構工具
  }
}
```

## 🔧 開發環境配置

### 環境變數設定
```bash
# .env 檔案配置
GOOGLE_AI_API_KEY=your_gemini_api_key_here
NODE_ENV=development
PYTHONPATH=/app
```

### 開發工具配置
- **pytest.ini**: 測試配置與覆蓋率設定
- **setup.cfg**: 專案元數據與 flake8 規則
- **.pre-commit-config.yaml**: Git hooks 自動化
- **sonar-project.properties**: 程式碼品質分析
- **renovate.json**: 依賴套件自動更新

### 版本資訊
- **專案版本**: 1.5.1 (setup.py)
- **Python 支援**: 3.6+ (建議 3.9+)
- **Node.js 支援**: 16+ (建議 18+)
- **授權條款**: MIT License
├── setup.cfg                    # 專案元數據
├── sonar-project.properties     # 程式碼品質分析
└── start_dev.sh                 # 一鍵開發環境啟動
```

## 🚀 快速開始

### 1. 環境需求

- **Python 3.8+** (建議使用 3.10+)
- **Node.js 16+** 和 **npm** 或 **yarn**
- **Google AI API Key** (用於 Gemini AI 功能)
- **Git** (用於版本控制)

### 2. 專案克隆與設定

```bash
# 克隆專案
git clone https://github.com/stu01509/TaiwanLotteryCrawler.git
cd TaiwanLotteryCrawler

# 建立 Python 虛擬環境 (建議)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 建立環境變數檔案
cp .env.example .env  # 如果有範例檔案
# 或手動建立 .env 檔案
```

### 3. 環境變數設定

建立 `.env` 檔案並設定以下變數：
```bash
# Google AI API Key (必要 - 用於 AI 選號功能)
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# 可選配置
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FRONTEND_PORT=3000
```

### 4. 一鍵啟動 (推薦)

使用提供的啟動腳本：
```bash
chmod +x start_dev.sh
./start_dev.sh
```

### 5. 手動啟動

#### 方法一：使用 uv (推薦)
```bash
# 安裝 uv (如果尚未安裝)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 建立虛擬環境並安裝依賴
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 啟動後端
cd backend && python main.py &

# 啟動前端
cd frontend && npm install && npm run dev
```

#### 方法二：傳統方式
```bash
# 後端 (FastAPI)
pip install -r requirements.txt
cd backend
python main.py &

# 前端 (Vue.js) - 新終端視窗
cd frontend
npm install
npm run dev
```

### 6. 訪問應用

- **🌐 前端應用**: http://localhost:3000
- **🔧 後端 API**: http://localhost:8000  
- **📖 API 文件**: http://localhost:8000/docs
- **🔍 API 規格**: http://localhost:8000/redoc

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

### 🎲 大樂透相關
- `GET /api/lotto649` - 獲取大樂透歷史資料
  - 查詢參數：`year`, `month`
  - 回應：期別、開獎日期、獎號、特別號
- `GET /api/lotto649/predict` - AI 智能預測大樂透號碼
  - 功能：分析半年資料，提供冷門/熱門號碼組合
  - 回應：推薦號碼、選號理由、頻率統計

### 🎯 其他彩種
- `GET /api/super_lotto` - 威力彩歷史資料 (6/38+1)
- `GET /api/daily_cash` - 今彩539歷史資料 (5/39)
- `GET /api/lotto1224` - 雙贏彩歷史資料 (12/24)

### 📋 查詢參數
- `year` - 年份 (字串格式，如 "2025")
- `month` - 月份 (字串格式，如 "08")
- 預設值：當前年月

### 📖 API 文件
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🛠️ 技術棧

### 🔧 後端技術
- **FastAPI 0.104+** - 高效能 Python Web 框架
- **Pydantic 2.4+** - 資料驗證與序列化
- **Uvicorn** - ASGI 高效能伺服器
- **Google Generative AI** - Gemini 2.5 Flash AI 引擎
- **Requests** - HTTP 客戶端庫
- **Python-dotenv** - 環境變數管理

### 🎨 前端技術
- **Vue 3.3+** - 漸進式 JavaScript 框架
- **Vue Router 4.2+** - 單頁應用路由管理
- **Element Plus 2.4+** - 企業級 UI 元件庫
- **Axios 1.5+** - Promise 基礎 HTTP 客戶端
- **Vite 4.4+** - 次世代前端建構工具
- **@element-plus/icons-vue** - 圖示元件庫

### 🧪 開發與測試
- **Pytest 7.4+** - Python 測試框架
- **Pytest-cov 4.1+** - 測試覆蓋率報告
- **Flake8 6.0+** - 程式碼風格檢查
- **Pre-commit 3.3+** - Git hooks 管理
- **Terminaltables 3.1+** - 終端表格顯示

### 🚀 CI/CD 與品質保證
- **GitHub Actions** - 自動化 CI/CD 流水線
- **SonarCloud** - 程式碼品質分析
- **Codecov** - 測試覆蓋率追蹤
- **Dependabot** - 依賴更新自動化

### 📡 資料來源
- **台灣彩券官方 API** - `https://api.taiwanlottery.com`
  - SSL/TLS 1.3 加密連線
  - TWCA 憑證認證
  - RESTful API 設計

## 🔧 開發指令

### 🐍 後端開發
```bash
# 執行所有測試
pytest

# 執行測試並生成覆蓋率報告
pytest --cov=. tests/ --cov-report=html

# 程式碼風格檢查
flake8

# 安裝為開發模式
pip install -e .

# 啟動開發伺服器 (自動重載)
cd backend && python main.py

# 檢查依賴安全性
pip-audit
```

### 🎨 前端開發
```bash
# 開發模式 (熱重載)
npm run dev

# 建構生產版本
npm run build

# 預覽生產版本
npm run preview

# 依賴檢查
npm audit

# 依賴更新
npm update
```

### 🧪 測試與品質
```bash
# 執行所有測試
pytest tests/

# 執行特定測試
pytest tests/test_lottery.py::test_lotto649

# 程式碼覆蓋率
pytest --cov=TaiwanLottery --cov-report=term-missing

# 程式碼品質檢查
flake8 --max-line-length=160

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## 📝 使用說明

### 🏠 1. 首頁 (Home.vue)
- **功能概覽**：系統主要功能介紹
- **快速選號**：一鍵獲取 AI 推薦號碼
- **導航中心**：快速跳轉到各功能頁面
- **響應式設計**：適配各種螢幕尺寸

### 🎲 2. 大樂透 AI 選號 (Lotto649.vue)
- **智能分析**：AI 分析半年歷史資料 (約 44 期)
- **雙組推薦**：提供冷門與熱門號碼組合
- **詳細理由**：說明每組號碼的選擇邏輯
- **頻率統計**：視覺化號碼出現頻率
- **歷史趨勢**：號碼熱度變化分析

### 🎯 3. 威力彩查詢 (SuperLotto.vue)
- **月份查詢**：選擇特定年月查看開獎記錄
- **完整資訊**：期別、日期、第一區、第二區號碼
- **分頁瀏覽**：支援大量資料的分頁顯示
- **資料匯出**：支援 JSON 格式匯出

### 📊 4. 歷史資料查詢 (History.vue)
- **多彩種支援**：大樂透、威力彩、今彩539、雙贏彩
- **彈性查詢**：自訂年月範圍
- **統計分析**：號碼頻率、趨勢分析
- **資料視覺化**：圖表展示統計結果

## 🔒 安全性與隱私

### 🛡️ 資料安全
- **HTTPS 連線**：所有 API 請求使用 TLS 1.3 加密
- **API Key 保護**：環境變數儲存敏感資訊
- **無個人資料**：系統不收集使用者個人資訊
- **本地處理**：AI 分析在本地伺服器執行

### 🔐 API 安全
- **CORS 設定**：限制跨域請求來源
- **請求驗證**：Pydantic 模型驗證所有輸入
- **錯誤處理**：安全的錯誤訊息回應
- **速率限制**：防止 API 濫用 (可選)

## ⚠️ 重要注意事項

### 🚨 免責聲明
1. **娛樂用途**：本系統僅供娛樂和學習參考
2. **無中獎保證**：AI 推薦不保證中獎結果
3. **理性投注**：請量力而為，避免過度投注
4. **風險自負**：使用者需自行承擔投注風險

### 🔧 技術需求
1. **API Key 必要**：AI 功能需要有效的 Google AI API Key
2. **網路連線**：需要穩定的網際網路連線
3. **瀏覽器支援**：建議使用現代瀏覽器 (Chrome 90+, Firefox 88+, Safari 14+)
4. **效能建議**：建議 4GB+ RAM 以獲得最佳體驗

### 📱 裝置相容性
- **桌面電腦**：Windows, macOS, Linux
- **行動裝置**：iOS 12+, Android 8+
- **平板電腦**：iPad, Android 平板
- **響應式設計**：自動適配螢幕尺寸

## 🤝 貢獻指南

### 📋 如何貢獻
1. **Fork 專案**到您的 GitHub 帳戶
2. **建立分支**：`git checkout -b feature/amazing-feature`
3. **提交變更**：`git commit -m 'Add amazing feature'`
4. **推送分支**：`git push origin feature/amazing-feature`
5. **建立 Pull Request**

### 🐛 回報問題
- 使用 [GitHub Issues](https://github.com/stu01509/TaiwanLotteryCrawler/issues)
- 提供詳細的錯誤描述和重現步驟
- 包含系統環境資訊 (OS, Python 版本等)

### 💡 功能建議
- 在 Issues 中標記為 `enhancement`
- 詳細描述建議的功能和使用場景
- 歡迎提供設計草圖或原型

## 📊 專案統計

- **程式語言**：Python (後端), JavaScript (前端)
- **程式碼行數**：~2000+ 行
- **測試覆蓋率**：85%+ (目標)
- **支援彩種**：4 種台灣彩券
- **API 端點**：8 個主要端點
- **版本**：v1.5.1 (持續更新)

## 🔗 相關連結

- **專案首頁**：[GitHub Repository](https://github.com/stu01509/TaiwanLotteryCrawler)
- **問題回報**：[GitHub Issues](https://github.com/stu01509/TaiwanLotteryCrawler/issues)
- **版本發布**：[GitHub Releases](https://github.com/stu01509/TaiwanLotteryCrawler/releases)
- **台灣彩券官網**：[taiwanlottery.com](https://www.taiwanlottery.com)
- **Google AI Studio**：[aistudio.google.com](https://aistudio.google.com)

## 📄 授權條款

本專案採用 **MIT License** 授權條款。詳細內容請參閱 [LICENSE](LICENSE) 檔案。

---

<div align="center">

**🎯 Made with ❤️ for Taiwan Lottery Enthusiasts**

如果這個專案對您有幫助，請給我們一個 ⭐ Star！

</div>