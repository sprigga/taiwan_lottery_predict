# Taiwan Lottery Crawler - Project Overview for Gemini

This document provides an overview of the `TaiwanLotteryCrawler` project, designed to assist the Gemini CLI agent in understanding its purpose, structure, and operational aspects.

## Project Overview

The `TaiwanLotteryCrawler` is a Python package that scrapes historical lottery drawing results from the official Taiwan Lottery website. It supports a variety of lottery games, including Super Lotto (威力彩), Lotto 6/49 (大樂透), Daily Cash (今彩539), Win-Win Lottery (雙贏彩), 3-Star Lottery (3星彩), 4-Star Lottery (4星彩), 38-Lotto (38樂合彩), 39-Lotto (39樂合彩), and 49-Lotto (49樂合彩).

A notable feature of this project is the `Lottery_predict.py` script, which leverages the `TaiwanLotteryCrawler` to fetch recent lottery data and then utilizes the Google Gemini 2.5 Pro model to analyze the data and provide lottery number recommendations based on "hot" and "cold" numbers.

**Key Technologies:**
*   **Python:** Core language.
*   **Requests:** For HTTP requests to the Taiwan Lottery website.
*   **Google Generative AI (Gemini 2.5 Pro):** Used in `Lottery_predict.py` for AI-driven lottery number prediction.
*   **Pytest:** For unit testing.
*   **Flake8:** For code linting.
*   **Pre-commit:** For managing Git pre-commit hooks.
*   **python-dotenv:** For loading environment variables (e.g., API keys).

## Building and Running

### Installation

The package can be installed via pip:

```bash
pip install taiwanlottery
```

### Running the Lottery Prediction Script

To run the AI-powered lottery prediction script (`Lottery_predict.py`), you need to:

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Set up Google AI API Key:**
    Create a `.env` file in the project root and add your Google AI API key:
    ```
    GOOGLE_AI_API_KEY='your_api_key_here'
    ```
3.  **Execute the script:**
    ```bash
    python Lottery_predict.py
    ```
    This script will fetch the latest 6 months of Lotto 6/49 data, analyze it, and print AI-recommended numbers. It will also save the raw data to `lotto649_six_months.json`.

### Running Tests

Tests are written using `pytest`. To run them and generate coverage reports:

```bash
pytest
```

### Linting

Code linting is performed using `flake8`. It's also integrated with `pre-commit` hooks.

```bash
flake8 .
```

## Development Conventions

*   **Code Style:** Adheres to `flake8` standards.
*   **Testing:** Uses `pytest` for unit and integration tests. Test files are located in the `tests/` directory and follow the `test_*.py` naming convention.
*   **Dependency Management:** `requirements.txt` lists direct dependencies. `setup.py` defines package metadata and installation requirements. `renovate.json` suggests automated dependency updates.
*   **Pre-commit Hooks:** Configured via `.pre-commit-config.yaml` to ensure code quality before commits.
*   **CI/CD:** GitHub Actions workflows (`.github/workflows/`) are in place for continuous integration (merge, pull request) and release processes.
*   **SonarCloud:** Integrated for code quality analysis, as indicated by `sonar-project.properties`.
