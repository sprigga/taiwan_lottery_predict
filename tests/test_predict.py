# -*- coding: utf-8 -*-
from Lottery_predict import compute_frequency_analysis


def test_compute_frequency_analysis_basic():
    # 製造 20 筆資料，涵蓋足夠多種號碼以驗證熱門/冷門分離
    lottery_data = []
    # 號碼 1, 2, 3 各出現 10 次（熱門）；號碼 40-49 各只出現 1 次（冷門）
    for _ in range(10):
        lottery_data.append({'期別': len(lottery_data) + 1, '開獎日期': '2024-01-01',
                             '獎號': [1, 2, 3, 20, 21, 22], '特別號': 7})
    for i in range(10):
        lottery_data.append({'期別': len(lottery_data) + 1, '開獎日期': '2024-01-02',
                             '獎號': [40 + i, 30, 31, 32, 33, 34], '特別號': 8})

    result = compute_frequency_analysis(lottery_data)

    # 基本驗證
    assert result['number_frequency'][1] == 10
    assert result['number_frequency'][40] == 1
    assert result['special_frequency'][7] == 10
    assert result['special_frequency'][8] == 10

    # 驗證熱門與冷門不重疊
    hot_nums = {n for n, _ in result['hot_numbers']}
    cold_nums = {n for n, _ in result['cold_numbers']}
    assert len(hot_nums & cold_nums) == 0, "熱門與冷門號碼不應有重疊"

    # 驗證熱門號碼確實包含高頻率號碼
    assert 1 in hot_nums or 2 in hot_nums or 3 in hot_nums

    assert isinstance(result['cold_numbers'], list)


def test_compute_frequency_analysis_empty():
    result = compute_frequency_analysis([])
    assert result['number_frequency'] == {}
    assert result['special_frequency'] == {}
    assert result['hot_numbers'] == []
    assert result['cold_numbers'] == []


from backend.main import parse_ai_prediction


def test_parse_ai_prediction_valid_json():
    ai_text = '''```json
[
  {"type": "冷門號碼組合", "regular_numbers": [3, 17, 22, 31, 40, 45], "special_number": 12, "reason": "冷門測試"},
  {"type": "熱門號碼組合", "regular_numbers": [1, 5, 10, 20, 35, 48], "special_number": 7, "reason": "熱門測試"},
  {"type": "熱門 + 冷門 混合號碼組合", "regular_numbers": [2, 9, 18, 27, 36, 44], "special_number": 3, "reason": "混合測試"},
  {"type": "均衡組合", "regular_numbers": [4, 13, 23, 32, 41, 47], "special_number": 6, "reason": "均衡測試"}
]
```'''
    result = parse_ai_prediction(ai_text)
    assert result is not None
    assert len(result) == 4
    assert result[0]['type'] == '冷門號碼組合'
    assert result[0]['regular_numbers'] == [3, 17, 22, 31, 40, 45]
    assert result[0]['special_number'] == 12


def test_parse_ai_prediction_plain_json():
    ai_text = ('[{"type":"均衡組合","regular_numbers":[1,2,3,4,5,6],"special_number":7,"reason":"test"},'
               '{"type":"熱門號碼組合","regular_numbers":[8,9,10,11,12,13],"special_number":14,"reason":"test"},'
               '{"type":"冷門號碼組合","regular_numbers":[15,16,17,18,19,20],"special_number":21,"reason":"test"},'
               '{"type":"混合","regular_numbers":[22,23,24,25,26,27],"special_number":28,"reason":"test"}]')
    result = parse_ai_prediction(ai_text)
    assert result is not None
    assert len(result) == 4


def test_parse_ai_prediction_invalid_returns_none():
    result = parse_ai_prediction("這是無效的輸出，沒有任何JSON")
    assert result is None


def test_parse_ai_prediction_empty_returns_none():
    result = parse_ai_prediction("")
    assert result is None
