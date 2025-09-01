#!/bin/bash

# 台灣彩券 AI 選號系統 開發環境啟動腳本

echo "🚀 啟動台灣彩券 AI 選號系統..."

# 啟動虛擬環境
echo "🔧 啟動虛擬環境..."
source venv/bin/activate

# 檢查 Python 依賴
echo "📦 檢查 Python 依賴..."
pip install -r requirements.txt

# 啟動 FastAPI 後端 (背景執行)
echo "🔧 啟動 FastAPI 後端服務 (Port 8000)..."
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..

# 等待後端啟動
echo "⏳ 等待後端服務啟動..."
sleep 3

# 檢查前端依賴並啟動
echo "🎨 準備前端應用..."
cd frontend

# 檢查是否已安裝 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安裝 Node.js 依賴..."
    npm install
fi

# 啟動 Vue.js 前端
echo "🎨 啟動 Vue.js 前端應用 (Port 3000)..."
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ 系統啟動完成！"
echo ""
# echo "🌐 前端應用: http://localhost:3000"
# echo "🔧 後端 API: http://localhost:8000"
# echo "📖 API 文件: http://localhost:8000/docs"
# echo ""
echo "按 Ctrl+C 停止所有服務"

# 等待用戶中斷
wait

# 清理程序
echo "🛑 停止服務..."
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null
echo "✅ 所有服務已停止"