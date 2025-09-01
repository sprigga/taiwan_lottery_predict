# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Commands
- `pip install -r requirements.txt` - Install all dependencies
- `pytest` - Run unit tests with coverage (configured in pytest.ini)
- `flake8` - Run linting (max line length: 160 characters)
- `pip install -e .` - Install package in development mode

### Package Management
- `python setup.py sdist bdist_wheel` - Build distribution packages
- `pip install taiwanlottery` - Install from PyPI

### Testing
- `pytest tests/` - Run all tests in tests directory
- `pytest tests/test_lottery.py::test_super_lotto` - Run specific test
- `pytest --cov=. tests/ --cov-report=html` - Generate HTML coverage report

## Architecture

### Core Structure
The project is a Python package for crawling Taiwan lottery results from the official Taiwan Lottery API.

**Main Module**: `TaiwanLottery/`
- `__init__.py` - Contains the main `TaiwanLotteryCrawler` class
- `utils.py` - Utility functions for date handling, data conversion, and output formatting

**API Integration**:
- Base URL: `https://api.taiwanlottery.com/TLCAPIWeB/Lottery`
- All lottery methods follow the pattern: `/{LotteryType}Result?period&month={year}-{month}&pageSize=31`
- Returns JSON responses that are processed into standardized dictionaries

**Supported Lottery Games**:
1. `super_lotto()` - 威力彩 (Super Lotto 6/38+1)
2. `lotto649()` - 大樂透 (Lotto 6/49+1)
3. `daily_cash()` - 今彩539 (Daily Cash 5/39)
4. `lotto1224()` - 雙贏彩 (Double Win 12/24)
5. `lotto3d()` - 3星彩 (3D Lottery)
6. `lotto4d()` - 4星彩 (4D Lottery)
7. `lotto38m6()` - 38樂合彩 (38M6)
8. `lotto39m5()` - 39樂合彩 (39M5)  
9. `lotto49m6()` - 49樂合彩 (49M6)

**Data Structure**:
Each lottery method returns a list of dictionaries with keys:
- `期別` (Period number)
- `開獎日期` (Draw date in ISO format)
- Game-specific number fields (varies by lottery type)

**Utility Functions** (`utils.py`):
- Date/time utilities for current year/month
- Republic era calendar conversion (Taiwan uses Minguo calendar)
- JSON file output functionality
- ASCII table formatting for console display

**Testing Strategy**:
- Unit tests in `tests/` directory test specific date ranges with expected results
- Tests verify exact lottery results for known historical draws
- Coverage reporting configured via pytest.ini

**CI/CD Pipeline**:
- GitHub Actions workflows for merge, pull requests, and releases
- Automated testing with pytest
- Code quality checks with flake8
- SonarCloud analysis for code quality
- Codecov integration for coverage reporting
- Automated PyPI releases

## Development Notes

- Python 3.6+ required
- Uses `requests` for HTTP API calls
- `terminaltables` for formatted console output
- All lottery methods accept optional `back_time` parameter as `[year, month]` list
- Default behavior fetches current month's results
- Error handling includes logging for "no data" scenarios
- Package distributed on PyPI as `taiwanlottery`