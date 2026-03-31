# -*- coding: utf-8 -*-
from unittest.mock import patch, MagicMock
from TaiwanLottery import TaiwanLotteryCrawler


def _make_mock_response(content_key, items):
    """建立 mock API 回應"""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        'content': {
            'totalSize': len(items),
            content_key: items
        }
    }
    return mock_resp


def test_fetch_lottery_lotto649():
    """確認 lotto649 仍能正確回傳資料（透過 _fetch_lottery）"""
    items = [
        {'period': 112000001, 'lotteryDate': '2023-01-01T00:00:00', 'drawNumberSize': [1, 2, 3, 4, 5, 6, 7]}
    ]
    mock_resp = _make_mock_response('lotto649Res', items)

    with patch('requests.get', return_value=mock_resp):
        crawler = TaiwanLotteryCrawler()
        result = crawler.lotto649(['2023', '01'])

    assert len(result) == 1
    assert result[0]['期別'] == 112000001
    assert result[0]['獎號'] == [1, 2, 3, 4, 5, 6]
    assert result[0]['特別號'] == 7


def test_fetch_lottery_super_lotto():
    """確認 super_lotto 仍能正確回傳資料（透過 _fetch_lottery）"""
    items = [
        {'period': 112000001, 'lotteryDate': '2023-01-01T00:00:00', 'drawNumberSize': [1, 2, 3, 4, 5, 6, 3]}
    ]
    mock_resp = _make_mock_response('superLotto638Res', items)

    with patch('requests.get', return_value=mock_resp):
        crawler = TaiwanLotteryCrawler()
        result = crawler.super_lotto(['2023', '01'])

    assert len(result) == 1
    assert result[0]['第一區'] == [1, 2, 3, 4, 5, 6]
    assert result[0]['第二區'] == 3


def test_fetch_lottery_empty_returns_empty_list():
    """確認無資料時回傳空列表"""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        'content': {'totalSize': 0, 'lotto649Res': []}
    }

    with patch('requests.get', return_value=mock_resp):
        crawler = TaiwanLotteryCrawler()
        result = crawler.lotto649(['2023', '01'])

    assert result == []
