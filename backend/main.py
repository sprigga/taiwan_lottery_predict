# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
# import json
import json
import os
import sys
import re
from datetime import datetime

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from TaiwanLottery import TaiwanLotteryCrawler
from Lottery_predict import get_six_months_lotto649_data, predict_lottery_numbers_with_ai, compute_frequency_analysis

app = FastAPI(
    title="台灣彩券 API",
    description="提供台灣彩券歷史資料與 AI 選號推薦服務",
    version="1.0.0"
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vue.js 開發伺服器、前端容器和 Docker 服務名稱
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

def _resolve_back_time(year: Optional[str], month: Optional[str]) -> list:
    """解析年月參數，若未提供則使用目前年月"""
    if year and month:
        return [year, month]
    from TaiwanLottery.utils import get_current_year, get_current_month
    return [str(get_current_year()), str(get_current_month()).zfill(2)]

def _parse_numbers(numbers_str):
    """從號碼字符串解析出整數列表，處理各種分隔符"""
    numbers_str = re.sub(r'[^\d,，、\s]', '', numbers_str)
    result = []
    for num_str in re.split(r'[,，、\s]+', numbers_str):
        if num_str.strip().isdigit():
            result.append(int(num_str.strip()))
    return result


_SET_TYPES = ["冷門號碼組合", "熱門號碼組合", "熱門 + 冷門 混合號碼組合", "均衡組合"]


def _build_set(set_type, numbers_str, special_number_str):
    """解析一組號碼並構建推薦字典，失敗返回 None"""
    regular_numbers = _parse_numbers(numbers_str)
    if len(regular_numbers) != 6:
        return None
    return {
        "type": set_type,
        "regular_numbers": regular_numbers,
        "special_number": int(special_number_str),
        "reason": f"基於歷史資料分析的{set_type}"
    }


def _build_sets_from_matches(matches, has_type=False):
    """從匹配結果構建推薦號碼列表"""
    sets = []
    for i, match in enumerate(matches[:4]):
        if has_type and len(match) == 3:
            set_type, numbers_str, special_number_str = match
        elif len(match) == 2:
            set_type = _SET_TYPES[i] if i < len(_SET_TYPES) else f"第{i+1}組"
            numbers_str, special_number_str = match
        else:
            continue
        s = _build_set(set_type, numbers_str, special_number_str)
        if s:
            sets.append(s)
    return sets


# [原始] 以下 parse_ai_prediction 已重構為 JSON 解析，原始 regex 多格式匹配保留如下：
# def parse_ai_prediction(ai_prediction_text):
#     if not ai_prediction_text:
#         return None
#     pattern = r'\*{0,2}第[一二三四]組\(([^)]+)\):\*{0,2}\s*\[([^\]]+)\]\s*\+\s*特別號:\s*(\d+)'
#     matches = re.findall(pattern, ai_prediction_text)
#     if matches:
#         return _build_sets_from_matches(matches, has_type=True)
#     markdown_pattern = r'\*\*彩券號碼:\*\*\s*\[([^\]]+)\]\s*\+\s*\*\*特別號:\*\*\s*(\d+)'
#     markdown_matches = re.findall(markdown_pattern, ai_prediction_text)
#     if len(markdown_matches) >= 4:
#         return _build_sets_from_matches(markdown_matches)
#     pattern1 = r'\*\*獎號\*\*:\s*\[([^\]]+)\]\s*\*\*特別號\*\*:\s*(\d+)'
#     matches1 = re.findall(pattern1, ai_prediction_text)
#     if matches1:
#         return _build_sets_from_matches(matches1)
#     pattern2 = r'\*\*第[一二三四]組\(([^)]+)\):\*\*\s*\[([^\]]+)\]\s*\+\s*特別號:\s*(\d+)'
#     matches2 = re.findall(pattern2, ai_prediction_text)
#     if matches2:
#         return _build_sets_from_matches(matches2, has_type=True)
#     simple_pattern = r'\[([^\]]+)\]\s*\+\s*(?:\*\*)?特別號(?:\*\*)?:\s*(\d+)'
#     simple_matches = re.findall(simple_pattern, ai_prediction_text)
#     if len(simple_matches) >= 4:
#         return _build_sets_from_matches(simple_matches)
#     return None
def parse_ai_prediction(ai_prediction_text):
    """
    解析 AI 預測文字。要求 AI 輸出 JSON 陣列，直接用 json.loads() 解析。
    相容 ```json ... ``` markdown 包裝格式。
    """
    if not ai_prediction_text:
        return None

    # 移除可能的 markdown ```json ... ``` 包裝
    text = ai_prediction_text.strip()
    json_block = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', text)
    if json_block:
        text = json_block.group(1).strip()

    try:
        data = json.loads(text)
        if not isinstance(data, list):
            return None
        sets = []
        for item in data[:4]:
            if not isinstance(item, dict):
                continue
            regular = item.get('regular_numbers', [])
            special = item.get('special_number')
            set_type = item.get('type', '')
            reason = item.get('reason', f"基於歷史資料分析的{set_type}")
            if len(regular) != 6 or special is None:
                continue
            sets.append({
                "type": set_type,
                "regular_numbers": [int(n) for n in regular],
                "special_number": int(special),
                "reason": reason
            })
        return sets if sets else None
    except (json.JSONDecodeError, ValueError, TypeError):
        return None

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

# [原始] get_lotto649 原先內聯解析年月參數，已改用 _resolve_back_time() 共用函數
# @app.get("/api/lotto649", response_model=List[LotteryData])
# async def get_lotto649(year: Optional[str] = None, month: Optional[str] = None):
#     """取得大樂透歷史資料"""
#     try:
#         if year and month:
#             back_time = [year, month]
#         else:
#             from TaiwanLottery.utils import get_current_year, get_current_month
#             back_time = [str(get_current_year()), str(get_current_month()).zfill(2)]
#         result = lottery_crawler.lotto649(back_time)
#         if not result:
#             raise HTTPException(status_code=404, detail="查無資料")
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"資料擷取失敗: {str(e)}")

@app.get("/api/lotto649", response_model=List[LotteryData])
async def get_lotto649(year: Optional[str] = None, month: Optional[str] = None):
    """取得大樂透歷史資料"""
    try:
        back_time = _resolve_back_time(year, month)
        result = lottery_crawler.lotto649(back_time)
        if not result:
            raise HTTPException(status_code=404, detail="查無資料")
        return result
    except HTTPException:
        raise
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
        
        # [原始] 以下頻率計算已移至 compute_frequency_analysis() 共用函數，避免與 Lottery_predict.py 重複
        # number_frequency = {}
        # special_frequency = {}
        # for data in lotto649_data:
        #     for num in data['獎號']:
        #         number_frequency[num] = number_frequency.get(num, 0) + 1
        #     special_frequency[data['特別號']] = special_frequency.get(data['特別號'], 0) + 1
        # sorted_numbers = sorted(number_frequency.items(), key=lambda x: x[1], reverse=True)
        # hot_numbers = sorted_numbers[:10]
        # cold_numbers = sorted_numbers[-10:] if len(sorted_numbers) >= 10 else sorted_numbers

        # 計算號碼頻率統計（使用共用函數，避免與 Lottery_predict.py 重複計算）
        freq = compute_frequency_analysis(lotto649_data)
        statistics["frequency_analysis"] = {
            "hot_numbers": freq["hot_numbers"],
            "cold_numbers": freq["cold_numbers"],
            "number_frequency": dict(freq["sorted_numbers"]),
            "special_frequency": dict(sorted(freq["special_frequency"].items(), key=lambda x: x[1], reverse=True))
        }
        
        # 解析 AI 預測文字，提取結構化的推薦號碼
        recommended_sets = parse_ai_prediction(ai_prediction) if ai_prediction else None

        response_data = {
            "status": "success",
            "data": statistics,
            "ai_prediction": ai_prediction if ai_prediction else "AI 預測服務暫時無法使用"
        }
        
        # 如果成功解析出推薦號碼，加入回應中
        if recommended_sets:
            response_data["recommended_sets"] = recommended_sets

        return response_data
        
    except Exception as e:
        return PredictionResponse(
            status="error",
            error=f"預測過程發生錯誤: {str(e)}"
        )

# [原始] get_super_lotto 原先內聯解析年月參數，已改用 _resolve_back_time() 共用函數
# @app.get("/api/super_lotto")
# async def get_super_lotto(year: Optional[str] = None, month: Optional[str] = None):
#     """取得威力彩歷史資料"""
#     try:
#         if year and month:
#             back_time = [year, month]
#         else:
#             from TaiwanLottery.utils import get_current_year, get_current_month
#             back_time = [str(get_current_year()), str(get_current_month()).zfill(2)]
#         result = lottery_crawler.super_lotto(back_time)
#         if not result:
#             raise HTTPException(status_code=404, detail="查無資料")
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"資料擷取失敗: {str(e)}")

@app.get("/api/super_lotto")
async def get_super_lotto(year: Optional[str] = None, month: Optional[str] = None):
    """取得威力彩歷史資料"""
    try:
        back_time = _resolve_back_time(year, month)
        result = lottery_crawler.super_lotto(back_time)
        if not result:
            raise HTTPException(status_code=404, detail="查無資料")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"資料擷取失敗: {str(e)}")

# [原始] get_daily_cash 原先內聯解析年月參數，已改用 _resolve_back_time() 共用函數
# @app.get("/api/daily_cash")
# async def get_daily_cash(year: Optional[str] = None, month: Optional[str] = None):
#     """取得今彩539歷史資料"""
#     try:
#         if year and month:
#             back_time = [year, month]
#         else:
#             from TaiwanLottery.utils import get_current_year, get_current_month
#             back_time = [str(get_current_year()), str(get_current_month()).zfill(2)]
#         result = lottery_crawler.daily_cash(back_time)
#         if not result:
#             raise HTTPException(status_code=404, detail="查無資料")
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"資料擷取失敗: {str(e)}")

@app.get("/api/daily_cash")
async def get_daily_cash(year: Optional[str] = None, month: Optional[str] = None):
    """取得今彩539歷史資料"""
    try:
        back_time = _resolve_back_time(year, month)
        result = lottery_crawler.daily_cash(back_time)
        if not result:
            raise HTTPException(status_code=404, detail="查無資料")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"資料擷取失敗: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)