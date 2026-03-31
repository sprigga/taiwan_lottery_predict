# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta
from TaiwanLottery import TaiwanLotteryCrawler
import google.generativeai as genai
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()


def get_six_months_lotto649_data():
    """
    擷取大樂透過去半年(6個月)的中獎號碼
    Returns: 包含所有中獎資料的 JSON 格式變數
    """
    lottery = TaiwanLotteryCrawler()
    all_data = []
    
    # 計算過去6個月的年月組合
    current_date = datetime.now()
    months_data = []
    
    for i in range(6):
        # 計算要擷取的月份
        target_date = current_date - timedelta(days=30 * i)
        year = str(target_date.year)
        month = str(target_date.month).zfill(2)
        months_data.append([year, month])
    
    print("開始擷取大樂透過去半年的中獎號碼...")
    
    for year, month in months_data:
        print(f"正在擷取 {year}-{month} 的大樂透資料...")
        try:
            monthly_result = lottery.lotto649([year, month])
            if monthly_result:
                all_data.extend(monthly_result)
                print(f"成功擷取 {year}-{month} 共 {len(monthly_result)} 筆資料")
            else:
                print(f"{year}-{month} 無資料")
        except Exception as e:
            print(f"擷取 {year}-{month} 資料時發生錯誤: {e}")
    
    # 按期別降序排序 (最新的在前面)
    all_data.sort(key=lambda x: x['期別'], reverse=True)
    
    print(f"總共擷取到 {len(all_data)} 筆大樂透中獎資料")
    return all_data


def predict_lottery_numbers_with_ai(lottery_data):
    """
    使用 Google Gemini 2.5 Pro 模型分析大樂透資料並推薦號碼
    Args:
        lottery_data: 半年的大樂透中獎資料
    Returns:
        AI 推薦的兩組彩券號碼
    """
    # 設定 Google AI API Key (需要設定環境變數 GOOGLE_AI_API_KEY)
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("警告: 請設定環境變數 GOOGLE_AI_API_KEY")
        print("範例: export GOOGLE_AI_API_KEY='your_api_key_here'")
        return None
    
    try:
        # 配置 Google AI
        genai.configure(api_key=api_key)
        
        # 建立模型
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 準備資料摘要給 AI 分析
        data_summary = "大樂透半年中獎資料分析:\n\n"
        data_summary += f"總期數: {len(lottery_data)}\n"
        data_summary += f"日期範圍: {lottery_data[-1]['開獎日期'][:10]} 至 {lottery_data[0]['開獎日期'][:10]}\n\n"
        # print(f"data_summary_日期範圍: {data_summary}")
        
        # 加入所有期數的詳細資料
        data_summary += f"所有{len(lottery_data)}期中獎號碼:\n"
        for i, data in enumerate(lottery_data):
            data_summary += f"第{data['期別']}期 ({data['開獎日期'][:10]}): 獎號 {data['獎號']} | 特別號 {data['特別號']}\n"
            # print(f"data_summary_期別: {data_summary}")
            
        # 統計所有號碼出現頻率
        number_frequency = {}
        special_frequency = {}
        
        for data in lottery_data:
            # 統計獎號頻率
            for num in data['獎號']:
                number_frequency[num] = number_frequency.get(num, 0) + 1
            # 統計特別號頻率
            special_frequency[data['特別號']] = special_frequency.get(data['特別號'], 0) + 1
        
        # 加入完整號碼頻率統計
        data_summary += "\n完整獎號出現頻率統計 (1-49號碼):\n"
        sorted_numbers = sorted(number_frequency.items(), key=lambda x: x[1], reverse=True)
        for num, freq in sorted_numbers:
            data_summary += f"號碼 {num}: {freq} 次\n"
        
        # 找出從未出現的號碼
        all_possible_numbers = set(range(1, 50))
        appeared_numbers = set(number_frequency.keys())
        never_appeared = all_possible_numbers - appeared_numbers
        if never_appeared:
            data_summary += f"\n半年內從未出現的獎號: {sorted(never_appeared)}\n"
        
        data_summary += "\n完整特別號出現頻率統計:\n"
        sorted_special = sorted(special_frequency.items(), key=lambda x: x[1], reverse=True)
        for num, freq in sorted_special:
            data_summary += f"特別號 {num}: {freq} 次\n"
        
        # 找出從未出現的特別號
        appeared_special = set(special_frequency.keys())
        never_appeared_special = all_possible_numbers - appeared_special
        if never_appeared_special:
            data_summary += f"\n半年內從未出現的特別號: {sorted(never_appeared_special)}\n"
        
        # 建構提示詞
        prompt = f"""{data_summary}


基於數學原理與數據分析，以下為具體選號策略，旨在增加與短期趨勢的吻合度，同時保持隨機性：

均衡分佈：
- 選擇3:3或2:4的單雙比組合。
- 選擇和值在120–160之間的號碼組合。
- 確保首尾差在30–40之間，避免過於集中或分散的號碼。

包含同尾號與連號：
- 至少包含1–2組同尾號，優先選擇3尾、5尾或7尾（如03, 13或05, 15）。
- 包含1組2連號（如15, 16或36, 37），優先在1–20或30–49區間。

分區選號：
- 將1–49分為三區：1–16（低）、17–33（中）、34–49（高）。
- 選擇2個低區、2個中區、2個高區的號碼，確保分佈均衡。例如：04, 15, 25, 33, 41, 46。

熱門號碼與冷門號碼結合：
- 選擇2–3個熱門號碼與3–4個其他號碼結合，避免全選熱門號碼。
- 可考慮冷門號碼作為補充，因其可能在未來「回歸均值」。

大樂透玩法以及號碼選取技巧:
- 大樂透獎號為6個號碼，範圍是1-49
- 特別號為1個號碼，範圍是1-49，且不能與獎號重複
- 請以清楚的格式回答，並簡單說明選號理由
- 奇偶比分佈: 大樂透玩法中，奇、偶數號碼各5個。建議選擇奇偶比例接近 3:2 或 2:3 的組合，例如 3 個奇數 + 2 個偶數或 2 個奇數 + 3 個偶數，避免選擇 5 個奇數或 5 個偶數的極端組合。
- 大小比分佈: 大樂透玩法的號碼分為小號碼和大小號碼，各 5 個。建議選擇介於 10~39 的小號碼 2~3 個，大號碼 40~49 2~3 個。避免選擇全部小號碼或全部大號碼的組合。
- 避開連號和順序號: 建議避免選擇 3 個以上的連號，例如 1、2、3 或 4、5、6 等。此外，順序號，例如 1、11、21 等，中獎機率也不高，建議減少選擇此類組合。
— 考慮遺漏號碼： 大樂透玩法中，每期開獎號碼皆不相同。追蹤遺漏號碼可以幫助玩家找出較久未開出的號碼。當號碼遺漏超過 5~10 期時，可以考慮將其納入選號組合，增加中獎機會。
— 熱門號碼與冷門號碼搭配： 熱門號通常是指近期頻繁出現的號碼，冷門號是指較少出現的號碼。建議在選號時，適當地搭配熱門和冷門號碼，既能提高命中率，又能降低與其他彩民重複中獎的機率。

根據大樂透半年的中獎資料，請試著分析並且參照[選號策略]和［大樂透玩法以及號碼選取技巧］推薦出四組彩券號碼(包含特別號):

請務必按照以下格式及pattern回答, 不要添加任何額外說明或文字，僅回覆符合格式的內容:
# 主要匹配模式：第X組(類型): [數字列表] + 特別號: 數字
pattern = r'第[X]組\(([^)]+)\):\s*\[([^\]]+)\]\s*\+\s*特別號:\s*(\d+)'

根據以下主題，[冷門號碼組合、熱門號碼組合熱門 + 冷門 混合號碼組合、均衡組合]產生四組號碼組合，並說明選號理由:
第[X]組([主題]): [號碼1, 號碼2, 號碼3, 號碼4, 號碼5, 號碼6] + 特別號: 號碼
選號理由: ...

"""

        
        print("\n正在使用 Google Gemini 2.5 分析資料並推薦號碼...")
        print("這可能需要幾秒鐘的時間...\n")
        
        # 發送請求給 AI 模型
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        print(f"AI 預測過程中發生錯誤: {e}")
        return None


def main():
    """主程式執行函數"""
    # 擷取半年的大樂透資料
    lotto649_six_months_data = get_six_months_lotto649_data()
    
    # 將資料轉換為JSON格式並儲存到變數
    lotto649_json_data = json.dumps(lotto649_six_months_data, ensure_ascii=False, indent=2)
    
    # 顯示統計資訊
    if lotto649_six_months_data:
        print("\n=== 大樂透半年資料統計 ===")
        print(f"資料筆數: {len(lotto649_six_months_data)}")
        print(f"最新期別: {lotto649_six_months_data[0]['期別']}")
        print(f"最舊期別: {lotto649_six_months_data[-1]['期別']}")
        print(f"日期範圍: {lotto649_six_months_data[-1]['開獎日期'][:10]} 至 {lotto649_six_months_data[0]['開獎日期'][:10]}")
        
        # 顯示最近5期的中獎號碼
        # print("\n=== 最近5期中獎號碼 ===")
        # for i in range(min(5, len(lotto649_six_months_data))):
        #     data = lotto649_six_months_data[i]
        #     print(f"第{data['期別']}期 ({data['開獎日期'][:10]}): 獎號 {data['獎號']} | 特別號 {data['特別號']}")
        
        # 使用 AI 進行號碼推薦
        print("\n=== AI 大樂透號碼推薦 ===")
        ai_prediction = predict_lottery_numbers_with_ai(lotto649_six_months_data)
        
        if ai_prediction:
            print(ai_prediction)
        else:
            print("AI 預測功能暫時無法使用，請檢查 API Key 設定")
    
    # 將JSON資料寫入檔案以供參考
    with open('lotto649_six_months.json', 'w', encoding='utf-8') as f:
        f.write(lotto649_json_data)
    
    print(f"\nJSON資料已儲存至 'lotto649_six_months.json' 檔案")
    print("程式執行完成！")
    
    # 回傳JSON格式的變數供其他程式使用
    return lotto649_json_data


if __name__ == "__main__":
    # 執行主程式並取得JSON格式的中獎資料
    lottery_json_variable = main()