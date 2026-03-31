# -*- coding: utf-8 -*-
from Lottery_predict import compute_frequency_analysis


def test_compute_frequency_analysis_basic():
    lottery_data = [
        {'期別': 1, '開獎日期': '2024-01-01', '獎號': [1, 2, 3, 4, 5, 6], '特別號': 7},
        {'期別': 2, '開獎日期': '2024-01-05', '獎號': [1, 2, 3, 10, 11, 12], '特別號': 7},
    ]
    result = compute_frequency_analysis(lottery_data)
    assert result['number_frequency'][1] == 2
    assert result['number_frequency'][4] == 1
    assert result['special_frequency'][7] == 2
    assert 1 in [n for n, _ in result['hot_numbers']]
    assert isinstance(result['cold_numbers'], list)


def test_compute_frequency_analysis_empty():
    result = compute_frequency_analysis([])
    assert result['number_frequency'] == {}
    assert result['special_frequency'] == {}
    assert result['hot_numbers'] == []
    assert result['cold_numbers'] == []
