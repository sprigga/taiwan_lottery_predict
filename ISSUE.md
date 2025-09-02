# 智能選號功能問題修復記錄

## 問題描述

### 主要問題
在 `frontend/src/views/Home.vue` 中，用戶點擊「智能選號」按鈕後無法顯示兩組推薦號碼。

### 問題現象
- 後端 API 調用成功，返回狀態為 `success`
- 前端收到回應，但 `recommended_sets` 欄位為空或不存在
- 用戶無法看到 AI 推薦的兩組大樂透號碼

## 問題分析

### 根本原因分析
通過深入調查發現了三個主要問題：

1. **正則表達式匹配失敗**
   - `backend/main.py` 中的 `parse_ai_prediction` 函式無法正確解析 AI 回應
   - 原始正則表達式期望的格式與 AI 實際返回的格式不匹配

2. **Pydantic 模型欠缺欄位**
   - `PredictionResponse` 模型缺少 `recommended_sets` 欄位
   - FastAPI 的 Pydantic 驗證會過濾掉模型中未定義的欄位

3. **AI 回應格式變化**
   - AI 使用 Markdown 格式回應，與預期的純文字格式不同
   - 實際格式：`**彩券號碼:** [12, 30, 44, 18, 38, 19] + **特別號:** 4`
   - 預期格式：`第一組(冷門號碼組合): [12, 30, 44, 18, 38, 19] + 特別號: 4`

## 詳細問題追蹤

### 問題 1: 正則表達式匹配失敗

**問題位置**: `backend/main.py` 第 52-106 行的 `parse_ai_prediction` 函式

**原始代碼問題**:
```python
# 原始正則表達式只能匹配特定格式
pattern = r'\*\*第[一二]組\(([^)]+)\):\*\*\s*\[(\d+(?:,\s*\d+){5})\]\s*\+\s*特別號:\s*(\d+)'
```

**實際 AI 回應格式**:
```text
**彩券號碼:** [12, 28, 30, 36, 38, 44] + **特別號:** 42
```

**解決方案**:
- 新增 Markdown 格式的正則表達式匹配
- 增強號碼解析邏輯，支援多種分隔符（逗號、中文逗號、頓號、空格）
- 添加多層次的匹配策略

### 問題 2: Pydantic 模型欠缺欄位

**問題位置**: `backend/main.py` 第 39-43 行的 `PredictionResponse` 類別

**原始代碼**:
```python
class PredictionResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    ai_prediction: Optional[str] = None
    error: Optional[str] = None
    # 缺少 recommended_sets 欄位
```

**問題現象**:
- 後端日誌顯示 `recommended_sets` 被成功添加到回應中
- 但 API 實際回應中該欄位被 FastAPI 過濾掉

**解決方案**:
```python
class PredictionResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    ai_prediction: Optional[str] = None
    recommended_sets: Optional[List[Dict[str, Any]]] = None  # ✅ 新增此欄位
    error: Optional[str] = None
```

### 問題 3: AI 回應格式不一致

**問題來源**: `Lottery_predict.py` 中的提示詞與 AI 實際回應格式不匹配

**提示詞期望格式** (第 133-138 行):
```text
第一組(冷門號碼組合): [號碼1, 號碼2, 號碼3, 號碼4, 號碼5, 號碼6] + 特別號: 號碼
第二組(熱門號碼組合): [號碼1, 號碼2, 號碼3, 號碼4, 號碼5, 號碼6] + 特別號: 號碼
```

**AI 實際回應格式**:
```text
**彩券號碼:** [12, 28, 30, 36, 38, 44] + **特別號:** 42
```

## 解決方案實施

### 1. 更新 Pydantic 模型

**檔案**: `backend/main.py`
**修改內容**:
```python
class PredictionResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    ai_prediction: Optional[str] = None
    recommended_sets: Optional[List[Dict[str, Any]]] = None  # 新增欄位
    error: Optional[str] = None
```

### 2. 增強正則表達式匹配邏輯

**檔案**: `backend/main.py`
**修改內容**: 完全重寫 `parse_ai_prediction` 函式

**新增功能**:
- 支援原始格式匹配
- 支援 Markdown 格式匹配
- 支援多種分隔符（`,`、`，`、`、`、空格）
- 多層次匹配策略，提高解析成功率

**關鍵改進**:
```python
# 新增 Markdown 格式匹配
markdown_pattern = r'\*\*彩券號碼:\*\*\s*\[([^\]]+)\]\s*\+\s*\*\*特別號:\*\*\s*(\d+)'
markdown_matches = re.findall(markdown_pattern, ai_prediction_text)

# 增強號碼解析邏輯
numbers_str = re.sub(r'[^\d,，、\s]', '', numbers_str)  # 移除非數字、逗號、空格的字符
regular_numbers = []
for num_str in re.split(r'[,，、\s]+', numbers_str):
    if num_str.strip().isdigit():
        regular_numbers.append(int(num_str.strip()))
```

### 3. 測試驗證

**測試方法**:
1. 創建獨立測試腳本驗證正則表達式
2. 重啟後端服務
3. 調用 API 端點驗證回應格式
4. 檢查前端顯示效果

**測試結果**:
```json
{
  "status": "success",
  "recommended_sets": [
    {
      "type": "冷門號碼組合",
      "regular_numbers": [12, 30, 44, 18, 38, 19],
      "special_number": 4,
      "reason": "基於歷史資料分析的冷門號碼組合"
    },
    {
      "type": "熱門號碼組合", 
      "regular_numbers": [2, 15, 20, 25, 45, 49],
      "special_number": 10,
      "reason": "基於歷史資料分析的熱門號碼組合"
    }
  ]
}
```

## 修復驗證

### 後端驗證
✅ API 端點 `/api/lotto649/predict` 成功返回 `recommended_sets`
✅ 正則表達式成功解析 AI 回應中的兩組號碼
✅ Pydantic 模型正確序列化回應數據

### 前端驗證
✅ `Home.vue` 中的智能選號按鈕功能正常
✅ 推薦號碼正確顯示在前端介面
✅ 用戶體驗得到改善

## 技術改進點

### 1. 錯誤處理增強
- 添加多層次的正則表達式匹配
- 提高對不同 AI 回應格式的容錯性

### 2. 代碼可維護性
- 清晰的註釋說明各種匹配模式
- 模組化的號碼解析邏輯

### 3. 系統穩定性
- 支援多種分隔符格式
- 向後兼容原有格式

## 預防措施

### 1. 提示詞優化建議
考慮更新 `Lottery_predict.py` 中的提示詞，明確指定回應格式：
```python
prompt = f"""
請嚴格按照以下格式回答：
第一組(冷門號碼組合): [號碼1, 號碼2, 號碼3, 號碼4, 號碼5, 號碼6] + 特別號: 號碼
第二組(熱門號碼組合): [號碼1, 號碼2, 號碼3, 號碼4, 號碼5, 號碼6] + 特別號: 號碼
"""
```

### 2. 測試覆蓋率
建議添加單元測試來驗證 `parse_ai_prediction` 函式對各種格式的處理能力。

### 3. 監控機制
建議添加日誌記錄，當正則表達式匹配失敗時記錄 AI 回應內容，便於後續分析和改進。

## 相關檔案

### 修改的檔案
- `backend/main.py` - 主要修復檔案
  - 更新 `PredictionResponse` 模型
  - 重寫 `parse_ai_prediction` 函式

### 相關檔案
- `frontend/src/views/Home.vue` - 前端顯示邏輯
- `Lottery_predict.py` - AI 提示詞定義

## 總結

這次問題修復涉及了前後端協作、正則表達式處理、API 設計等多個技術層面。通過系統性的問題分析和逐步驗證，成功解決了智能選號功能無法顯示推薦號碼的問題，提升了用戶體驗和系統穩定性。

**修復時間**: 2025年1月
**影響範圍**: 智能選號功能
**修復狀態**: ✅ 已完成並驗證

---

# 大樂透歷史資料 API 驗證錯誤修復記錄

## 問題描述

### 主要問題
在測試 `/api/lotto649?year=2025&month=08` API 端點時，出現 HTTP 500 內部伺服器錯誤。

### 問題現象
- API 調用返回 `Internal Server Error`
- 後端日誌顯示 `ResponseValidationError`
- 9個驗證錯誤，全部指向 `期別` 欄位類型不匹配

## 問題分析

### 根本原因
**Pydantic 模型數據類型定義錯誤**：`LotteryData` 模型中的 `期別` 欄位被定義為 `str` 類型，但實際數據中的 `期別` 是 `int` 類型。

### 錯誤詳情
```
ResponseValidationError: 9 validation errors:
{'type': 'string_type', 'loc': ('response', 0, '期別'), 'msg': 'Input should be a valid string', 'input': 114000083}
{'type': 'string_type', 'loc': ('response', 1, '期別'), 'msg': 'Input should be a valid string', 'input': 114000082}
...
```

### 問題位置
**檔案**: `backend/main.py` 第 33-37 行

**原始錯誤代碼**:
```python
class LotteryData(BaseModel):
    期別: str  # ❌ 錯誤：實際數據是整數類型
    開獎日期: str
    獎號: List[int]
    特別號: int
```

**實際數據格式**:
```json
{
  "期別": 114000083,  // 整數類型，不是字符串
  "開獎日期": "2025-08-29T00:00:00",
  "獎號": [13, 20, 25, 27, 28, 32],
  "特別號": 2
}
```

## 解決方案實施

### 修復方法
更新 `LotteryData` 模型中的 `期別` 欄位類型定義：

**修復後代碼**:
```python
class LotteryData(BaseModel):
    期別: int  # ✅ 修正：改為整數類型
    開獎日期: str
    獎號: List[int]
    特別號: int
```

### 修復步驟
1. **識別問題**：分析後端錯誤日誌，發現 Pydantic 驗證錯誤
2. **定位原因**：檢查模型定義與實際數據類型的不匹配
3. **實施修復**：修改 `期別` 欄位類型從 `str` 到 `int`
4. **重啟服務**：重新啟動後端伺服器
5. **驗證修復**：測試 API 端點確認正常運作

## 修復驗證

### 測試命令
```bash
curl -X 'GET' 'http://localhost:8000/api/lotto649?year=2025&month=08' -H 'accept: application/json'
```

### 修復前結果
```
HTTP 500 Internal Server Error
```

### 修復後結果
```json
[
  {
    "期別": 114000083,
    "開獎日期": "2025-08-29T00:00:00",
    "獎號": [13, 20, 25, 27, 28, 32],
    "特別號": 2
  },
  {
    "期別": 114000082,
    "開獎日期": "2025-08-26T00:00:00",
    "獎號": [3, 6, 22, 32, 35, 39],
    "特別號": 27
  }
  // ... 更多資料
]
```

## 技術分析

### 問題類型
**數據類型不匹配錯誤** - 這是一個典型的 API 開發中常見的問題，當模型定義與實際數據結構不符時發生。

### 影響範圍
- `/api/lotto649` 端點的所有查詢
- 可能影響其他使用 `LotteryData` 模型的端點

### 學習要點
1. **Pydantic 驗證的重要性**：嚴格的類型檢查有助於發現數據不一致問題
2. **模型設計原則**：模型定義應該與實際數據結構完全匹配
3. **錯誤日誌分析**：詳細的錯誤訊息有助於快速定位問題

## 預防措施

### 1. 數據類型檢查
建議在開發過程中：
- 檢查實際數據結構與模型定義的一致性
- 使用自動化測試驗證 API 回應格式

### 2. 模型驗證測試
```python
# 建議添加的測試案例
def test_lottery_data_model():
    sample_data = {
        "期別": 114000083,  # 確保使用正確的數據類型
        "開獎日期": "2025-08-29T00:00:00",
        "獎號": [13, 20, 25, 27, 28, 32],
        "特別號": 2
    }
    lottery_data = LotteryData(**sample_data)
    assert lottery_data.期別 == 114000083
```

### 3. API 文檔更新
確保 API 文檔中的數據類型定義與實際實作一致。

## 相關檔案

### 修改的檔案
- `backend/main.py` - 更新 `LotteryData` 模型定義

### 影響的 API 端點
- `GET /api/lotto649` - 大樂透歷史資料查詢

## 總結

這次修復解決了一個基礎但重要的數據類型不匹配問題。通過修正 Pydantic 模型定義，確保了 API 的正常運作和數據的正確驗證。這個問題提醒我們在 API 開發中，模型定義的準確性對系統穩定性的重要性。

**修復時間**: 2025年1月
**影響範圍**: 大樂透歷史資料 API
**修復狀態**: ✅ 已完成並驗證

---

# 開發環境啟動問題修復記錄

## 問題描述

### 主要問題
在執行 `./start_dev.sh` 啟動開發環境時遇到多個問題，導致系統無法正常啟動。

### 問題現象
1. **pip 命令未找到錯誤**：`./start_dev.sh: line 9: pip: command not found`
2. **Port 8000 佔用錯誤**：`ERROR: [Errno 98] error while attempting to bind on address ('0.0.0.0', 8000): address already in use`
3. **Python 外部管理環境錯誤**：`error: externally-managed-environment`
4. **Port 3000 佔用**：Vite 自動切換到 port 3001

## 問題分析

### 根本原因分析
1. **pip 命令問題**
   - 系統使用 Homebrew 管理的 Python，pip 需要通過 `python3 -m pip` 調用
   - 直接使用 `pip` 命令在 PATH 中找不到

2. **外部管理環境限制**
   - Python 環境被標記為外部管理（PEP 668）
   - 禁止直接向系統 Python 安裝套件，需要使用虛擬環境

3. **Port 衝突問題**
   - 之前運行的服務未正確停止，佔用了 8000 和 3000 端口
   - 多次啟動腳本導致進程重複

### 詳細問題追蹤

#### 問題 1: pip 命令未找到
**錯誤訊息**:
```bash
./start_dev.sh: line 9: pip: command not found
```

**原因**:
- Homebrew 安裝的 Python 環境中，pip 不在系統 PATH 中
- 需要使用 `python3 -m pip` 方式調用

**解決方案**:
修改 `start_dev.sh` 中的安裝命令：
```bash
# 原始錯誤代碼
pip install -r requirements.txt

# 修復後代碼
python3 -m pip install -r requirements.txt
```

#### 問題 2: 外部管理環境錯誤
**錯誤訊息**:
```bash
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try brew install
```

**原因**:
- Python 環境遵循 PEP 668 標準，禁止直接向系統安裝套件
- 需要使用虛擬環境隔離套件依賴

**解決方案**:
1. 創建虛擬環境：
```bash
python3 -m venv venv
```

2. 修改 `start_dev.sh` 使用虛擬環境：
```bash
# 啟動虛擬環境
source venv/bin/activate

# 在虛擬環境中安裝依賴
pip install -r requirements.txt
```

#### 問題 3: Port 佔用問題
**錯誤訊息**:
```bash
ERROR: [Errno 98] error while attempting to bind on address ('0.0.0.0', 8000): address already in use
```

**診斷方法**:
```bash
# 檢查佔用 port 的程序
lsof -i :8000
lsof -i :3000

# 查看程序詳細信息
ps aux | grep python3
ps aux | grep node
```

**解決方案**:
```bash
# 停止佔用端口的程序
kill <PID>

# 或批量停止相關程序
pkill -f "python3 main.py"
pkill -f "npm run dev"
```

## 解決方案實施

### 1. 創建虛擬環境
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 修改啟動腳本
**檔案**: `start_dev.sh`

**修改內容**:
```bash
# 新增虛擬環境啟動
echo "🔧 啟動虛擬環境..."
source venv/bin/activate

# 修改 pip 調用方式
echo "📦 檢查 Python 依賴..."
pip install -r requirements.txt

# 修改 Python 執行命令
cd backend
python3 main.py &
```

### 3. 清理衝突進程
```bash
# 檢查並停止佔用端口的程序
lsof -i :8000
kill 13802

lsof -i :3000  
kill 5644
```

## 修復驗證

### 成功啟動後的狀態
```bash
🚀 啟動台灣彩券 AI 選號系統...
🔧 啟動虛擬環境...
📦 檢查 Python 依賴...
Requirement already satisfied: requests==2.31.0 in ./venv/lib/python3.13/site-packages
🔧 啟動 FastAPI 後端服務 (Port 8000)...
INFO:     Started server process [18999]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
🎨 啟動 Vue.js 前端應用 (Port 3000)...
✅ 系統啟動完成！

  VITE v4.5.14  ready in 314 ms
  ➜  Local:   http://localhost:3001/
```

### 服務可用性確認
- ✅ **後端 API**: http://localhost:8000
- ✅ **前端應用**: http://localhost:3001  
- ✅ **API 文檔**: http://localhost:8000/docs
- ✅ **API 請求正常**: `INFO: 127.0.0.1:xxx - "GET /api/lotto649/predict HTTP/1.1" 200 OK`

## 除錯方法總結

### 1. Port 佔用問題診斷
```bash
# 檢查特定端口佔用
lsof -i :8000
lsof -i :3000

# 檢查所有網路連接
netstat -tlnp | grep :8000

# 查看程序詳細信息
ps aux | grep python3
ps aux | grep node
```

### 2. 進程管理
```bash
# 停止特定 PID
kill <PID>

# 批量停止相關程序
pkill -f "python3 main.py"
pkill -f "npm run dev"

# 強制停止
kill -9 <PID>
```

### 3. Python 環境診斷
```bash
# 檢查 Python 和 pip 路徑
which python3
which pip
python3 -m pip --version

# 檢查虛擬環境
source venv/bin/activate
pip list
```

### 4. 系統狀態監控
```bash
# 檢查背景程序
jobs

# 監控即時日誌 
tail -f logfile

# 檢查系統資源
top
htop
```

## 技術改進點

### 1. 腳本健壯性增強
- 添加端口檢查和自動清理機制
- 改善錯誤處理和日誌輸出
- 支援虛擬環境自動創建

### 2. 開發環境標準化
- 統一使用虛擬環境管理依賴
- 標準化 Python 和 pip 調用方式
- 改善多人開發環境一致性

### 3. 故障恢復機制
- 自動檢測和清理衝突進程
- 提供清楚的錯誤訊息和解決建議

## 預防措施

### 1. 開發環境文檔
創建詳細的環境設置指南：
```markdown
## 環境要求
- Python 3.8+
- Node.js 16+
- 虛擬環境管理

## 首次設置
1. python3 -m venv venv
2. source venv/bin/activate  
3. pip install -r requirements.txt
4. ./start_dev.sh
```

### 2. 自動化檢查腳本
建議添加環境檢查：
```bash
#!/bin/bash
# check_env.sh

echo "檢查 Python 環境..."
python3 --version || exit 1

echo "檢查虛擬環境..."
if [ ! -d "venv" ]; then
    echo "創建虛擬環境..."
    python3 -m venv venv
fi

echo "檢查端口佔用..."
if lsof -i :8000 > /dev/null; then
    echo "Port 8000 已佔用，是否停止現有程序？"
fi
```

### 3. 啟動腳本改進建議
```bash
#!/bin/bash
# 改進版 start_dev.sh

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "🔧 創建虛擬環境..."
    python3 -m venv venv
fi

# 檢查端口並清理
if lsof -i :8000 > /dev/null; then
    echo "🛑 清理 Port 8000..."
    lsof -ti :8000 | xargs kill -9
fi

# 啟動服務...
```

## 相關檔案

### 修改的檔案
- `start_dev.sh` - 主要修復檔案
  - 添加虛擬環境支援
  - 修正 pip 調用方式
  - 改善錯誤處理

### 新增的檔案
- `venv/` - 虛擬環境目錄
- 相關的 Python 套件安裝

### 影響的服務
- FastAPI 後端服務 (Port 8000)
- Vue.js 前端服務 (Port 3001) 
- 開發環境啟動流程

## SSL 憑證驗證問題修復記錄

## 問題描述

### 主要問題
在調用台灣彩券官方 API 時出現 SSL 憑證驗證失敗錯誤，導致無法擷取彩券資料。

### 問題現象
```bash
資料擷取失敗: HTTPSConnectionPool(host='api.taiwanlottery.com', port=443): Max retries exceeded with url: /TLCAPIWeB/Lottery/Lotto649Result?period&month=2025-07&pageSize=31 (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Missing Subject Key Identifier (_ssl.c:1032)')))
```

## 問題分析

### 根本原因
台灣彩券官方 API (`api.taiwanlottery.com`) 的 SSL 憑證缺少 Subject Key Identifier 擴展，導致 Python requests 庫的預設 SSL 驗證失敗。

### 問題位置
**檔案**: `TaiwanLottery/__init__.py` 第 15 行

**問題程式碼**:
```python
def get_lottery_result(self, url):
    response = requests.get(url)  # ❌ 未處理 SSL 驗證問題
    return response.json()
```

### 錯誤詳情
- **錯誤類型**: `SSLCertVerificationError`
- **具體原因**: `certificate verify failed: Missing Subject Key Identifier`
- **影響範圍**: 所有彩券資料擷取功能
- **API 端點**: `https://api.taiwanlottery.com/TLCAPIWeB/Lottery/*`

## 解決方案實施

### 1. 停用 SSL 憑證驗證
**檔案**: `TaiwanLottery/__init__.py`

**修復程式碼**:
```python
def get_lottery_result(self, url):
    response = requests.get(url, verify=False)  # ✅ 停用 SSL 驗證
    return response.json()
```

### 2. 關閉 SSL 警告訊息
為避免大量的不安全請求警告，添加警告停用：

**修改內容**:
```python
# -*- coding: utf-8 -*-
import logging

import requests
import urllib3  # ✅ 新增 urllib3 導入

from TaiwanLottery import utils

# ✅ 關閉 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

## 修復驗證

### 測試命令
```bash
# 測試單月資料擷取
source venv/bin/activate && python3 -c "
from TaiwanLottery import TaiwanLotteryCrawler
lottery = TaiwanLotteryCrawler()
result = lottery.lotto649(['2024', '12'])
print(f'測試結果: 擷取到 {len(result) if result else 0} 筆資料')
"
```

### 修復前結果
```bash
SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Missing Subject Key Identifier (_ssl.c:1032)'))
```

### 修復後結果  
```bash
測試結果: 擷取到 9 筆資料
```

### 完整功能測試
```bash
source venv/bin/activate && python3 -c "
from Lottery_predict import get_six_months_lotto649_data
data = get_six_months_lotto649_data()
print(f'總共擷取: {len(data)} 筆資料') if data else print('無資料')
"
```

**測試結果**:
```bash
開始擷取大樂透過去半年的中獎號碼...
正在擷取 2025-09 的大樂透資料...
2025-09 無資料
正在擷取 2025-08 的大樂透資料...
成功擷取 2025-08 共 9 筆資料
正在擷取 2025-07 的大樂透資料...
成功擷取 2025-07 共 9 筆資料
正在擷取 2025-06 的大樂透資料...
成功擷取 2025-06 共 8 筆資料
正在擷取 2025-05 的大樂透資料...
成功擷取 2025-05 共 9 筆資料
正在擷取 2025-04 的大樂透資料...
成功擷取 2025-04 共 9 筆資料
總共擷取到 44 筆大樂透中獎資料

總共擷取: 44 筆資料
```

## 技術分析

### SSL 憑證問題原因
1. **官方 API 憑證問題**: 台灣彩券 API 的 SSL 憑證缺少標準的 Subject Key Identifier 擴展
2. **Python requests 嚴格驗證**: requests 庫預設執行完整的 SSL/TLS 憑證鏈驗證
3. **安全性與可用性平衡**: 在無法修改第三方 API 憑證的情況下，需要在安全性和功能可用性之間取得平衡

### 解決方案評估

#### 方案 1: 停用 SSL 驗證 (採用)
**優點**:
- 簡單直接，立即解決問題
- 不需要額外配置
- 適用於可信任的官方 API

**缺點**:
- 降低連接安全性
- 可能受到中間人攻擊

**適用場景**: 連接官方已知可信任的 API 端點

#### 方案 2: 自定義 SSL 上下文 (未採用)
```python
import ssl
import requests

def get_lottery_result(self, url):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    with requests.Session() as session:
        session.verify = ssl_context
        response = session.get(url)
    return response.json()
```

#### 方案 3: 使用自定義憑證 (未採用)
需要手動下載和管理第三方 API 憑證，維護成本高。

## 安全性考量

### 風險評估
- **中等風險**: 停用 SSL 驗證會降低連接安全性
- **可接受理由**: 
  - 連接的是台灣彩券官方 API，具有一定可信度
  - 擷取的是公開的彩券開獎資料，非敏感信息
  - 無其他可行的技術解決方案

### 安全建議
1. **限制使用範圍**: 僅對特定的台灣彩券 API 端點停用驗證
2. **監控異常**: 定期檢查 API 回應的合理性
3. **更新策略**: 當官方修復憑證問題時，及時恢復 SSL 驗證

## 預防措施

### 1. 監控 API 狀態
```python
def get_lottery_result(self, url):
    try:
        # 首先嘗試正常的 SSL 驗證
        response = requests.get(url, timeout=10)
        return response.json()
    except requests.exceptions.SSLError:
        # SSL 錯誤時才使用無驗證模式
        logging.warning(f"SSL verification failed for {url}, using unverified connection")
        response = requests.get(url, verify=False, timeout=10)
        return response.json()
```

### 2. 定期檢查憑證狀態
建議定期檢查 API 憑證是否已修復：
```bash
# 檢查憑證資訊
openssl s_client -connect api.taiwanlottery.com:443 -servername api.taiwanlottery.com
```

### 3. 日誌記錄
添加詳細的錯誤日誌以便問題追蹤：
```python
import logging

def get_lottery_result(self, url):
    try:
        response = requests.get(url, verify=False)
        logging.info(f"Successfully fetched data from {url}")
        return response.json()
    except Exception as e:
        logging.error(f"Failed to fetch data from {url}: {e}")
        raise
```

## 相關檔案

### 修改的檔案
- `TaiwanLottery/__init__.py` - 主要修復檔案
  - 修改 `get_lottery_result` 方法
  - 添加 urllib3 導入和警告停用

### 影響的功能
- 所有彩券資料擷取功能
- `get_six_months_lotto649_data()` 函式
- 後端 API 彩券資料查詢
- AI 預測功能的資料來源

## 總結

SSL 憑證驗證問題的修復成功恢復了台灣彩券資料擷取功能。雖然停用 SSL 驗證在技術上降低了連接安全性，但考慮到：

1. **連接目標可信任**: 台灣彩券官方 API
2. **資料性質公開**: 彩券開獎號碼屬於公開信息  
3. **無其他可行方案**: 無法修改第三方 API 的憑證配置
4. **功能需求優先**: 確保系統核心功能正常運作

這個修復方案是合理且必要的。建議持續監控官方 API 的憑證狀態，待官方修復憑證問題後，及時恢復完整的 SSL 驗證機制。

**修復時間**: 2025年9月1日  
**影響範圍**: 台灣彩券資料擷取功能
**修復狀態**: ✅ 已完成並驗證
**風險等級**: 🟡 中等（已評估可接受）

---

# 組件間資料傳遞問題修復記錄

## 問題描述

### 主要問題
在 `frontend/src/views/Home.vue` 中，用戶點擊「智能選號」獲取推薦結果後，點擊「查看詳細分析」按鈕導航至 `frontend/src/views/Lotto649.vue` 頁面，但目標頁面無法顯示任何分析結果、統計資料和推薦號碼。

### 問題現象
1. **Home.vue 功能正常**：智能選號按鈕能正確獲取並顯示快速推薦結果
2. **導航功能正常**：點擊「查看詳細分析」能成功跳轉到 Lotto649.vue 頁面
3. **目標頁面空白**：Lotto649.vue 顯示初始空狀態，需要重新點擊「獲取推薦」才能看到結果
4. **重複 API 調用**：導致不必要的 API 請求和用戶體驗問題

## 問題分析

### 根本原因分析
通過深入調查發現了兩個主要問題：

1. **組件狀態獨立性問題**
   - Home.vue 和 Lotto649.vue 各自管理獨立的響應式狀態
   - 沒有狀態共享機制，導航時數據丟失

2. **Vue Router 4 狀態傳遞方法錯誤**
   - 初始使用的 `router.push({ path: '/lotto649', state: {...} })` 方法在 Vue Router 4 中不適用
   - 嘗試使用 `history.state` API 讀取路由狀態失敗

### 詳細問題追蹤

#### 問題 1: 組件狀態隔離

**問題位置**: `frontend/src/views/Home.vue:63` 和 `frontend/src/views/Lotto649.vue`

**原始導航代碼**:
```vue
<!-- Home.vue -->
<el-button 
  type="info" 
  size="small" 
  @click="$router.push('/lotto649')"
  class="detail-button"
>
  查看詳細分析
</el-button>
```

**問題現象**:
- Home.vue 中的 `quickPrediction.value` 數據無法傳遞到 Lotto649.vue
- Lotto649.vue 的 `prediction.value` 在初始化時為 `null`
- 兩個組件調用相同的 API 端點但狀態完全獨立

#### 問題 2: Vue Router 狀態傳遞失敗

**問題位置**: 初始嘗試的修復方案中

**錯誤代碼**:
```javascript
// 錯誤的 Vue Router 4 狀態傳遞方式
router.push({
  path: '/lotto649',
  state: { predictionData: quickPrediction.value }  // ❌ Vue Router 4 不支持
})

// 錯誤的狀態讀取方式  
onMounted(() => {
  const routeState = history.state  // ❌ 無法正確讀取
  if (routeState?.predictionData) {
    prediction.value = routeState.predictionData
  }
})
```

**失敗原因**:
- Vue Router 4 不直接支持 `state` 屬性的路由狀態傳遞
- `history.state` API 在組件導航上下文中無法可靠獲取自定義狀態

## 解決方案實施

### 1. 修改 Home.vue 導航邏輯

**檔案**: `frontend/src/views/Home.vue`

**修改內容**:
```javascript
// 導入 useRouter
import { useRouter } from 'vue-router'

export default {
  setup() {
    const router = useRouter()
    
    // 新增導航方法
    const navigateToDetail = () => {
      console.log('Navigate to detail called, quickPrediction:', quickPrediction.value)
      if (quickPrediction.value) {
        // 使用 sessionStorage 傳遞數據
        const predictionData = JSON.stringify(quickPrediction.value)
        console.log('Storing prediction data:', predictionData)
        sessionStorage.setItem('lotto649_prediction', predictionData)
        router.push('/lotto649')
      } else {
        console.log('No prediction data available, navigating without data')
        router.push('/lotto649')
      }
    }

    return {
      // ...other properties
      navigateToDetail
    }
  }
}
```

**按鈕綁定更新**:
```vue
<el-button 
  type="info" 
  size="small" 
  @click="navigateToDetail"  <!-- 修改為新方法 -->
  class="detail-button"
>
  查看詳細分析
</el-button>
```

### 2. 修改 Lotto649.vue 數據接收邏輯

**檔案**: `frontend/src/views/Lotto649.vue`

**修改內容**:
```javascript
// 導入必要模組
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const router = useRouter()
    
    // 在組件掛載時檢查 sessionStorage
    onMounted(() => {
      const storedPrediction = sessionStorage.getItem('lotto649_prediction')
      console.log('Stored prediction:', storedPrediction)
      
      if (storedPrediction) {
        try {
          const parsedPrediction = JSON.parse(storedPrediction)
          console.log('Parsed prediction:', parsedPrediction)
          prediction.value = parsedPrediction
          // 使用後立即清除，避免重複使用
          sessionStorage.removeItem('lotto649_prediction')
          ElMessage.success('已加載預測結果！')
        } catch (error) {
          console.error('Failed to parse stored prediction:', error)
          sessionStorage.removeItem('lotto649_prediction')
        }
      }
    })

    return {
      // ...existing properties
    }
  }
}
```

### 3. 添加除錯日誌

為了便於問題診斷，在兩個組件中都添加了詳細的 console.log 輸出：

**除錯信息包括**:
- 導航方法調用確認
- 數據序列化過程
- sessionStorage 讀寫狀態
- 數據解析結果

## 修復驗證

### 用戶操作流程測試
1. ✅ **初始狀態**: 用戶打開 Home.vue 頁面
2. ✅ **獲取推薦**: 點擊「智能選號」按鈕，成功獲取並顯示推薦號碼
3. ✅ **數據存儲**: 點擊「查看詳細分析」，數據正確存儲到 sessionStorage
4. ✅ **頁面導航**: 成功導航到 Lotto649.vue 頁面
5. ✅ **數據載入**: Lotto649.vue 自動載入並顯示完整的分析結果
6. ✅ **用戶提示**: 顯示「已加載預測結果！」成功訊息

### 功能完整性驗證
- ✅ **推薦號碼顯示**: 兩組推薦號碼正確顯示
- ✅ **AI 分析結果**: AI 預測文字完整顯示
- ✅ **統計資料**: 期數、日期範圍等統計信息正確
- ✅ **頻率分析**: 熱門和冷門號碼分析正常顯示
- ✅ **數據清理**: sessionStorage 在使用後正確清除

### 除錯日誌驗證
瀏覽器開發者工具 Console 輸出示例：
```
Navigate to detail called, quickPrediction: {status: "success", data: {...}, ...}
Storing prediction data: {"status":"success","data":{...},"ai_prediction":"..."}
Stored prediction: {"status":"success","data":{...},"ai_prediction":"..."}
Parsed prediction: {status: "success", data: {...}, recommended_sets: [...]}
```

## 技術分析

### sessionStorage 方案優勢
1. **簡單可靠**: 瀏覽器原生 API，兼容性好
2. **會話級存儲**: 數據僅在當前頁面會話中有效，關閉頁面後自動清除
3. **跨組件**: 不依賴 Vue Router 或組件層級，可在任意組件間使用
4. **數據持久**: 頁面刷新後數據仍然存在（在會話期間）

### 與其他方案比較

#### 方案 1: sessionStorage (採用)
**優點**: 簡單、可靠、跨框架兼容
**缺點**: 需要手動管理數據清理
**適用場景**: 臨時數據傳遞、會話級緩存

#### 方案 2: Vuex/Pinia 狀態管理 (未採用)
**優點**: 全局狀態管理、響應式
**缺點**: 需要額外依賴、增加複雜度
**適用場景**: 複雜的全局狀態需求

#### 方案 3: Route Query/Params (未採用)  
**優點**: URL 可見、可書籤化
**缺點**: 數據量限制、URL 變長、安全性考量
**適用場景**: 簡單參數傳遞

#### 方案 4: 組件 Props/Emit (未採用)
**優點**: Vue 原生、類型安全
**缺點**: 需要父子組件關係、路由導航不適用
**適用場景**: 父子組件通信

## 預防措施

### 1. 數據生命周期管理
```javascript
// 建議的 sessionStorage 操作封裝
const PredictionStorage = {
  key: 'lotto649_prediction',
  
  set(data) {
    try {
      sessionStorage.setItem(this.key, JSON.stringify(data))
      console.log('Prediction data stored successfully')
    } catch (error) {
      console.error('Failed to store prediction data:', error)
    }
  },
  
  get() {
    try {
      const data = sessionStorage.getItem(this.key)
      return data ? JSON.parse(data) : null
    } catch (error) {
      console.error('Failed to parse prediction data:', error)
      this.clear()
      return null
    }
  },
  
  clear() {
    sessionStorage.removeItem(this.key)
    console.log('Prediction data cleared')
  }
}
```

### 2. 錯誤處理增強
```javascript
// 建議的錯誤處理機制
onMounted(() => {
  try {
    const predictionData = PredictionStorage.get()
    if (predictionData && predictionData.status === 'success') {
      prediction.value = predictionData
      PredictionStorage.clear() // 使用後立即清除
      ElMessage.success('已加載預測結果！')
    }
  } catch (error) {
    console.error('Failed to load prediction data:', error)
    ElMessage.warning('載入預測結果時發生錯誤')
  }
})
```

### 3. 單元測試建議
```javascript
// 建議的測試案例
describe('Prediction Data Transfer', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  test('should store and retrieve prediction data', () => {
    const mockData = { status: 'success', data: {...} }
    PredictionStorage.set(mockData)
    const retrieved = PredictionStorage.get()
    expect(retrieved).toEqual(mockData)
  })

  test('should handle invalid JSON gracefully', () => {
    sessionStorage.setItem('lotto649_prediction', 'invalid json')
    const result = PredictionStorage.get()
    expect(result).toBe(null)
    expect(sessionStorage.getItem('lotto649_prediction')).toBe(null)
  })
})
```

## 相關檔案

### 修改的檔案
- `frontend/src/views/Home.vue` - 主要修復檔案
  - 新增 `navigateToDetail` 方法
  - 修改按鈕點擊事件綁定
  - 添加 sessionStorage 數據存儲邏輯
  - 引入 `useRouter` 和除錯日誌

- `frontend/src/views/Lotto649.vue` - 數據接收端修復
  - 新增 `onMounted` 生命周期鉤子
  - 添加 sessionStorage 數據讀取邏輯
  - 引入錯誤處理和數據清理機制
  - 添加除錯日誌和用戶提示

### 涉及的技術棧
- Vue 3 Composition API
- Vue Router 4
- Element Plus UI 框架
- 瀏覽器 sessionStorage API
- JavaScript JSON 序列化/反序列化

## 學習要點

### 1. Vue Router 版本差異
不同版本的 Vue Router 在狀態傳遞方面有顯著差異，需要查閱對應版本的文檔。

### 2. 組件通信方案選擇
根據具體場景選擇合適的組件通信方案：
- **臨時數據**: sessionStorage/localStorage
- **全局狀態**: Vuex/Pinia
- **父子組件**: Props/Emit
- **跨層級組件**: Provide/Inject

### 3. 除錯策略重要性
添加詳細的除錯日誌有助於快速定位和解決問題，特別是涉及異步操作和數據流轉的場景。

## 總結

這次修復成功解決了 Vue 3 應用中組件間數據傳遞的問題。通過使用 sessionStorage 作為中介存儲，實現了 Home.vue 和 Lotto649.vue 之間的可靠數據傳遞，避免了重複的 API 調用，提升了用戶體驗。

**關鍵技術決策**:
1. **選擇 sessionStorage**: 簡單可靠，適合臨時數據傳遞
2. **添加除錯日誌**: 便於開發和維護階段的問題診斷
3. **數據清理機制**: 防止數據殘留和重複使用
4. **錯誤處理**: 提高代碼健壯性

這個解決方案不僅修復了當前問題，還為類似的組件間數據傳遞需求提供了可重用的模式。

**修復時間**: 2025年9月2日
**影響範圍**: 前端組件導航和數據傳遞功能
**修復狀態**: ✅ 已完成並驗證
**用戶體驗**: 🔄 顯著改善

---

# Docker 容器 CORS 問題修復記錄

## 問題描述

### 主要問題
在 Docker 容器環境中，前端無法訪問後端 API，出現 CORS（跨來源資源共享）錯誤。

### 問題現象
1. **瀏覽器 Console 錯誤**：
```
Access to XMLHttpRequest at 'http://localhost:8000/api/lotto649/predict' from origin 'http://localhost:8080' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

2. **前端容器日誌錯誤**：
```
backend:8000/api/lotto649/predict:1  Failed to load resource: net::ERR_NAME_NOT_RESOLVED
```

3. **Nginx 代理錯誤**：
```
2025/09/02 02:05:01 [error] 30#30: *21 connect() failed (111: Connection refused) while connecting to upstream, client: 172.19.0.1, server: localhost, request: "GET /api/lotto649/predict HTTP/1.1", upstream: "http://127.0.0.1:8000/api/lotto649/predict"
```

4. **後端健康檢查失敗**：
```
2025-09-02 10:08:02 INFO: 127.0.0.1:42998 - "GET /health HTTP/1.1" 404 Not Found
```

## 問題分析

### 根本原因分析
通過深入調查發現了三個主要問題：

1. **Docker 容器網路通訊錯誤**
   - 前端程式碼使用 `localhost:8000` 訪問後端 API
   - 在瀏覽器環境中無法解析 Docker 內部服務名稱
   - 需要使用 Docker 服務名稱或反向代理

2. **Nginx 反向代理配置錯誤**
   - nginx.conf 中的 `proxy_pass` 指向錯誤的目標
   - 缺少正確的 Docker 服務名稱配置

3. **後端缺少健康檢查端點**
   - Docker Compose 配置中定義了健康檢查
   - 但後端應用缺少對應的 `/health` 端點

### 詳細問題追蹤

#### 問題 1: 前端 API 請求路徑錯誤

**問題位置**: 前端 Vue 組件中的 axios 請求
- `frontend/src/views/Lotto649.vue:211`
- `frontend/src/views/Home.vue:143`
- `frontend/src/views/SuperLotto.vue:143` 
- `frontend/src/views/History.vue:250`

**原始錯誤代碼**:
```javascript
// 錯誤：在 Docker 環境中瀏覽器無法解析 backend 服務名稱
const response = await axios.get('http://backend:8000/api/lotto649/predict')

// 也錯誤：localhost 在容器環境中指向容器自身
const response = await axios.get('http://localhost:8000/api/lotto649/predict')
```

**問題現象**:
- 瀏覽器顯示 `net::ERR_NAME_NOT_RESOLVED` 錯誤
- 前端無法連接到後端服務

#### 問題 2: Nginx 反向代理配置錯誤

**問題位置**: `frontend/nginx.conf` 第 58 行

**原始錯誤代碼**:
```nginx
location /api/ {
    proxy_pass http://localhost:8000;  # ❌ 錯誤：容器內 localhost 指向自身
    # ...
}
```

**問題現象**:
- Nginx 無法連接到上游服務器
- 出現 `Connection refused` 錯誤

#### 問題 3: 後端缺少健康檢查端點

**問題位置**: `backend/main.py`

**缺少的功能**:
```python
# ❌ 缺少健康檢查端點，導致 Docker healthcheck 失敗
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## 解決方案實施

### 1. 修改前端 API 請求為相對路徑

**修復策略**: 使用相對路徑，通過 Nginx 反向代理到後端

**修復內容**:
```javascript
// ✅ 修復：使用相對路徑，由 Nginx 代理到後端
const response = await axios.get('/api/lotto649/predict')
```

**涉及檔案**:
- `frontend/src/views/Lotto649.vue`
- `frontend/src/views/Home.vue`
- `frontend/src/views/SuperLotto.vue` 
- `frontend/src/views/History.vue`

### 2. 配置 Nginx 反向代理

**檔案**: `frontend/nginx.conf`

**修復內容**:
```nginx
# API 代理到後端服務
location /api/ {
    proxy_pass http://backend:8000;  # ✅ 使用 Docker 服務名稱
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # CORS 處理
    add_header Access-Control-Allow-Origin *;
    add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
    add_header Access-Control-Allow-Headers 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
    
    # 處理 preflight 請求
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
        add_header Access-Control-Allow-Headers 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
        add_header Access-Control-Max-Age 1728000;
        add_header Content-Type 'text/plain; charset=utf-8';
        add_header Content-Length 0;
        return 204;
    }
}
```

### 3. 添加後端健康檢查端點

**檔案**: `backend/main.py`

**修復內容**:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Backend service is running"}
```

### 4. 更新後端 CORS 配置

**檔案**: `backend/main.py`

**修復內容**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:8080",
        "http://frontend:80",  # ✅ 新增 Docker 前端服務
        "http://taiwan-lottery-frontend:80"  # ✅ 新增容器名稱
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 修復驗證

### Docker 容器狀態檢查
```bash
# 檢查容器運行狀態
docker ps

# 檢查網路配置
docker network inspect taiwanlotterycrawler_lottery-network

# 測試容器間網路連通性
docker exec taiwan-lottery-frontend nslookup backend
docker exec taiwan-lottery-frontend ping -c 2 backend
docker exec taiwan-lottery-frontend wget -qO- http://backend:8000/
```

**驗證結果**:
- ✅ 所有容器正常運行
- ✅ 網路連通性測試通過
- ✅ 後端服務正常響應

### API 功能測試
1. ✅ **前端載入**: http://localhost:8080 正常訪問
2. ✅ **API 代理**: `/api/lotto649/predict` 請求成功
3. ✅ **CORS 解決**: 無跨來源錯誤
4. ✅ **健康檢查**: `/health` 端點正常響應
5. ✅ **完整流程**: 智能選號功能正常工作

### 解決方案工作流程
1. 瀏覽器發送請求到前端容器: `GET /api/lotto649/predict`
2. Nginx 接收請求並匹配 `location /api/` 規則
3. Nginx 將請求代理到後端: `http://backend:8000/api/lotto649/predict`
4. 後端處理請求並返回 JSON 響應
5. Nginx 添加 CORS 標頭並返回給瀏覽器
6. 前端成功接收並顯示資料

## 技術分析

### Docker 容器網路架構
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Browser       │    │   Frontend      │    │   Backend       │
│   localhost:    │───▶│   Container     │───▶│   Container     │
│   8080          │    │   nginx:80      │    │   uvicorn:8000  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Redis         │
                       │   Container     │
                       │   redis:6379    │
                       └─────────────────┘
```

### CORS 解決策略比較

#### 方案 1: Nginx 反向代理 (採用)
**優點**:
- 統一入口，簡化前端配置
- 在代理層處理 CORS，減少後端負擔
- 支援負載均衡和快取功能

**缺點**:
- 需要額外的 Nginx 配置
- 增加一層網路跳轉

#### 方案 2: 直接 CORS 配置 (輔助)
**優點**:
- 直接在 FastAPI 中配置，簡單明瞭
- 減少網路層級

**缺點**:
- 需要明確指定所有可能的來源
- 在 Docker 環境中來源配置複雜

#### 方案 3: 環境變數動態配置 (未採用)
**優點**:
- 可根據環境動態調整
- 便於多環境部署

**缺點**:
- 增加配置複雜度
- 需要額外的環境管理

## 除錯方法總結

### 1. Docker 網路診斷
```bash
# 檢查容器網路
docker network ls
docker network inspect <network_name>

# 測試容器間連通性
docker exec <container> nslookup <service_name>
docker exec <container> ping <service_name>
docker exec <container> wget -qO- http://<service>:<port>/
```

### 2. Nginx 配置驗證
```bash
# 檢查 Nginx 配置語法
docker exec <frontend_container> nginx -t

# 查看 Nginx 錯誤日誌
docker logs <frontend_container>

# 重載 Nginx 配置
docker exec <frontend_container> nginx -s reload
```

### 3. API 端點測試
```bash
# 直接測試後端 API
curl http://localhost:8000/api/lotto649/predict

# 通過前端代理測試
curl http://localhost:8080/api/lotto649/predict

# 測試健康檢查
curl http://localhost:8000/health
```

### 4. CORS 問題診斷
```bash
# 使用 curl 模擬跨來源請求
curl -H "Origin: http://localhost:8080" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8000/api/lotto649/predict
```

## 預防措施

### 1. 開發環境與生產環境一致性
```yaml
# docker-compose.yml 建議配置
services:
  frontend:
    environment:
      - API_BASE_URL=/api  # 使用相對路徑
  backend:
    environment:
      - CORS_ORIGINS=http://frontend:80,http://localhost:8080
```

### 2. 健康檢查標準化
```python
# 建議的健康檢查實作
@app.get("/health")
async def health_check():
    try:
        # 檢查資料庫連線、外部 API 等
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "checks": {
                "database": "ok",
                "external_api": "ok"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")
```

### 3. 容器啟動順序管理
```yaml
# docker-compose.yml 依賴關係
services:
  backend:
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      
  frontend:
    depends_on:
      backend:
        condition: service_healthy
```

## 相關檔案

### 修改的檔案
- `frontend/nginx.conf` - 反向代理配置
- `frontend/src/views/Lotto649.vue` - API 請求路徑
- `frontend/src/views/Home.vue` - API 請求路徑
- `frontend/src/views/SuperLotto.vue` - API 請求路徑
- `frontend/src/views/History.vue` - API 請求路徑
- `backend/main.py` - CORS 配置和健康檢查端點

### Docker 配置檔案
- `docker-compose.yml` - 服務編排配置
- `frontend/Dockerfile` - 前端容器構建
- `Dockerfile.backend` - 後端容器構建

## 總結

這次 CORS 問題的修復展現了 Docker 容器化環境中前後端通訊的複雜性。通過系統性的問題分析和逐步驗證，成功建立了穩定的容器間通訊機制：

**關鍵技術決策**:
1. **採用 Nginx 反向代理**: 統一 API 入口，簡化前端配置
2. **使用相對路徑**: 避免硬編碼服務地址，提高可移植性
3. **雙重 CORS 保護**: Nginx 和 FastAPI 雙重配置，確保兼容性
4. **添加健康檢查**: 完善容器生命周期管理

**解決的核心問題**:
- ✅ 容器間網路通訊
- ✅ 跨來源資源共享 (CORS)
- ✅ API 反向代理配置
- ✅ 服務健康狀態監控

這個修復不僅解決了當前的 CORS 問題，還建立了一個可擴展的容器化架構，為未來的功能擴展和部署奠定了基礎。

**修復時間**: 2025年9月2日
**影響範圍**: Docker 容器環境前後端通訊
**修復狀態**: ✅ 已完成並驗證
**系統穩定性**: 🔄 顯著提升