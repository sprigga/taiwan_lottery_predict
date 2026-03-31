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
