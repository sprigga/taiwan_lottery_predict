# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import sys
import re
from datetime import datetime

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from TaiwanLottery import TaiwanLotteryCrawler
from Lottery_predict import get_six_months_lotto649_data, predict_lottery_numbers_with_ai

app = FastAPI(
    title="台灣彩券 API",
    description="提供台灣彩券歷史資料與 AI 選號推薦服務",
    version="1.0.0"
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:8000", 
        "http://127.0.0.1:8000",
        "http://frontend:80",
        "http://taiwan-lottery-frontend:80"
    ],  # Vue.js 開發伺服器、前端容器和 Docker 服務名稱
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 模型
class LotteryData(BaseModel):
    期別: int  # 修改為 int 類型，因為實際數據是整數
    開獎日期: str
    獎號: List[int]
    特別號: int

class PredictionResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    ai_prediction: Optional[str] = None
    recommended_sets: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class BackTimeRequest(BaseModel):
    year: Optional[str] = None
    month: Optional[str] = None

# 初始化彩券爬蟲
lottery_crawler = TaiwanLotteryCrawler()

def parse_ai_prediction(ai_prediction_text):
    """
    解析 AI 預測文字，提取出兩組號碼
    """
    if not ai_prediction_text:
        return None
    
    recommended_sets = []
    
    # 根據 Lottery_predict.py 中的提示詞格式，匹配以下格式：
    # 第一組(冷門號碼組合): [號碼1, 號碼2, 號碼3, 號碼4, 號碼5, 號碼6] + 特別號: 號碼
    # 第二組(熱門號碼組合): [號碼1, 號碼2, 號碼3, 號碼4, 號碼5, 號碼6] + 特別號: 號碼
    
    # 主要匹配模式：第X組(類型): [數字列表] + 特別號: 數字
    pattern = r'第[一二]組\(([^)]+)\):\s*\[([^\]]+)\]\s*\+\s*特別號:\s*(\d+)'
    matches = re.findall(pattern, ai_prediction_text)
    
    # 如果沒匹配到，嘗試更寬鬆的格式（可能有額外的符號或格式）
    if not matches:
        # 匹配帶有星號或其他格式的版本
        pattern = r'\*?\*?第[一二]組\(([^)]+)\):\*?\*?\s*\[([^\]]+)\]\s*\+\s*特別號:\s*(\d+)'
        matches = re.findall(pattern, ai_prediction_text)
    
    # 如果還是沒匹配到，嘗試 Markdown 格式：**彩券號碼:** [數字列表] + **特別號:** 數字
    if not matches:
        # 匹配 Markdown 格式的彩券號碼
        markdown_pattern = r'\*\*彩券號碼:\*\*\s*\[([^\]]+)\]\s*\+\s*\*\*特別號:\*\*\s*(\d+)'
        markdown_matches = re.findall(markdown_pattern, ai_prediction_text)
        
        if len(markdown_matches) >= 2:
            # 確定第一組是冷門，第二組是熱門（根據文本中的順序）
            for i, match in enumerate(markdown_matches[:2]):
                numbers_str, special_number_str = match
                # 解析號碼字符串，處理各種可能的分隔符
                numbers_str = re.sub(r'[^\d,，、\s]', '', numbers_str)  # 移除非數字、逗號、空格的字符
                regular_numbers = []
                for num_str in re.split(r'[,，、\s]+', numbers_str):
                    if num_str.strip().isdigit():
                        regular_numbers.append(int(num_str.strip()))
                
                if len(regular_numbers) == 6:  # 確保有6個號碼
                    special_number = int(special_number_str)
                    # 根據文本中的順序判斷類型
                    set_type = "冷門號碼組合" if i == 0 else "熱門號碼組合"
                    reason = f"基於歷史資料分析的{set_type}"
                    
                    recommended_sets.append({
                        "type": set_type,
                        "regular_numbers": regular_numbers,
                        "special_number": special_number,
                        "reason": reason
                    })
    
    # 如果還是沒匹配到，嘗試最簡單的格式（直接匹配數字組合）
    if not matches and not recommended_sets:
        pattern = r'\[([^\]]+)\]\s*\+\s*(?:\*\*)?特別號(?:\*\*)?:\s*(\d+)'
        simple_matches = re.findall(pattern, ai_prediction_text)
        if len(simple_matches) >= 2:
            for i, match in enumerate(simple_matches[:2]):
                numbers_str, special_number_str = match
                # 解析號碼字符串，處理各種可能的分隔符
                numbers_str = re.sub(r'[^\d,，、\s]', '', numbers_str)  # 移除非數字、逗號、空格的字符
                regular_numbers = []
                for num_str in re.split(r'[,，、\s]+', numbers_str):
                    if num_str.strip().isdigit():
                        regular_numbers.append(int(num_str.strip()))
                
                if len(regular_numbers) == 6:  # 確保有6個號碼
                    special_number = int(special_number_str)
                    set_type = "冷門號碼組合" if i == 0 else "熱門號碼組合"
                    reason = f"基於歷史資料分析的{set_type}"
                    
                    recommended_sets.append({
                        "type": set_type,
                        "regular_numbers": regular_numbers,
                        "special_number": special_number,
                        "reason": reason
                    })
    else:
        # 處理帶類型的匹配結果
        for match in matches[:2]:
            if len(match) == 3:  # 帶類型的格式
                set_type, numbers_str, special_number_str = match
                # 解析號碼字符串，處理各種可能的分隔符和格式
                numbers_str = re.sub(r'[^\d,，、\s]', '', numbers_str)  # 移除非數字、逗號、空格的字符
                regular_numbers = []
                for num_str in re.split(r'[,，、\s]+', numbers_str):
                    if num_str.strip().isdigit():
                        regular_numbers.append(int(num_str.strip()))
                
                if len(regular_numbers) == 6:  # 確保有6個號碼
                    special_number = int(special_number_str)
                    reason = f"基於歷史資料分析的{set_type}"
                    
                    recommended_sets.append({
                        "type": set_type,
                        "regular_numbers": regular_numbers,
                        "special_number": special_number,
                        "reason": reason
                    })
    
    return recommended_sets if recommended_sets else None

@app.get("/")
async def root():
    return {
        "message": "台灣彩券 API 服務",
        "version": "1.0.0",
        "endpoints": {
            "lotto649": "/api/lotto649",
            "lotto649_predict": "/api/lotto649/predict",
            "super_lotto": "/api/super_lotto",
            "daily_cash": "/api/daily_cash"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Backend service is running"}

@app.get("/api/lotto649", response_model=List[LotteryData])
async def get_lotto649(year: Optional[str] = None, month: Optional[str] = None):
    """取得大樂透歷史資料"""
    try:
        if year and month:
            back_time = [year, month]
        else:
            # 使用目前年月
            from TaiwanLottery.utils import get_current_year, get_current_month
            back_time = [str(get_current_year()), str(get_current_month()).zfill(2)]
        
        result = lottery_crawler.lotto649(back_time)
        if not result:
            raise HTTPException(status_code=404, detail="查無資料")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"資料擷取失敗: {str(e)}")

@app.get("/api/lotto649/predict", response_model=PredictionResponse)
async def predict_lotto649():
    """使用 AI 預測大樂透號碼"""
    try:
        # 取得半年的大樂透資料
        lotto649_data = get_six_months_lotto649_data()
        
        if not lotto649_data:
            return PredictionResponse(
                status="error",
                error="無法取得大樂透歷史資料"
            )
        
        # 使用 AI 進行預測
        ai_prediction = predict_lottery_numbers_with_ai(lotto649_data)
        
        # 統計資訊
        statistics = {
            "total_periods": len(lotto649_data),
            "date_range": {
                "start": lotto649_data[-1]['開獎日期'][:10],
                "end": lotto649_data[0]['開獎日期'][:10]
            },
            "latest_period": lotto649_data[0]['期別'],
            "oldest_period": lotto649_data[-1]['期別']
        }
        
        # 計算號碼頻率統計
        number_frequency = {}
        special_frequency = {}
        
        for data in lotto649_data:
            for num in data['獎號']:
                number_frequency[num] = number_frequency.get(num, 0) + 1
            special_frequency[data['特別號']] = special_frequency.get(data['特別號'], 0) + 1
        
        # 找出熱門和冷門號碼
        sorted_numbers = sorted(number_frequency.items(), key=lambda x: x[1], reverse=True)
        hot_numbers = sorted_numbers[:10]  # 前10個熱門號碼
        cold_numbers = sorted_numbers[-10:] if len(sorted_numbers) >= 10 else sorted_numbers  # 後10個冷門號碼
        
        statistics["frequency_analysis"] = {
            "hot_numbers": hot_numbers,
            "cold_numbers": cold_numbers,
            "number_frequency": dict(sorted_numbers),
            "special_frequency": dict(sorted(special_frequency.items(), key=lambda x: x[1], reverse=True))
        }
        
        # 解析 AI 預測文字，提取結構化的推薦號碼
        recommended_sets = parse_ai_prediction(ai_prediction) if ai_prediction else None
        
        # 調試信息
        print(f"AI prediction length: {len(ai_prediction) if ai_prediction else 0}")
        print(f"Recommended sets: {recommended_sets}")
        
        response_data = {
            "status": "success",
            "data": statistics,
            "ai_prediction": ai_prediction if ai_prediction else "AI 預測服務暫時無法使用"
        }
        
        # 如果成功解析出推薦號碼，加入回應中
        if recommended_sets:
            response_data["recommended_sets"] = recommended_sets
            print("Added recommended_sets to response")
        
        return response_data
        
    except Exception as e:
        return PredictionResponse(
            status="error",
            error=f"預測過程發生錯誤: {str(e)}"
        )

@app.get("/api/super_lotto")
async def get_super_lotto(year: Optional[str] = None, month: Optional[str] = None):
    """取得威力彩歷史資料"""
    try:
        if year and month:
            back_time = [year, month]
        else:
            from TaiwanLottery.utils import get_current_year, get_current_month
            back_time = [str(get_current_year()), str(get_current_month()).zfill(2)]
        
        result = lottery_crawler.super_lotto(back_time)
        if not result:
            raise HTTPException(status_code=404, detail="查無資料")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"資料擷取失敗: {str(e)}")

@app.get("/api/daily_cash")
async def get_daily_cash(year: Optional[str] = None, month: Optional[str] = None):
    """取得今彩539歷史資料"""
    try:
        if year and month:
            back_time = [year, month]
        else:
            from TaiwanLottery.utils import get_current_year, get_current_month
            back_time = [str(get_current_year()), str(get_current_month()).zfill(2)]
        
        result = lottery_crawler.daily_cash(back_time)
        if not result:
            raise HTTPException(status_code=404, detail="查無資料")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"資料擷取失敗: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)