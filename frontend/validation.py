import re


TICKER_PATTERN = re.compile(r"^[A-Z][A-Z0-9.-]{0,9}$")


def normalize_ticker(value: str) -> str:
    """Normalize and validate a US equity ticker entered by the user."""
    ticker = value.strip().upper()
    if not TICKER_PATTERN.fullmatch(ticker):
        raise ValueError("Enter a ticker such as AAPL, SPY, or NVDA.")
    return ticker
