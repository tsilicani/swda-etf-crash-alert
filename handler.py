from statistics import mean, stdev
from typing import List, Dict, Union, Tuple, Optional
from urllib import request, parse
import json
import time


def send_telegram_message(message):
    url = "https://api.telegram.org/bot7820652349:AAHZTGk4f85a7BKoF18kEVhJsu3NCAFDNHU/sendMessage"
    chat_id = "185850234"
    text = parse.quote(
        message
    )  # Remove the encode("UTF-8") as parse.quote handles encoding
    uri = f"{url}?chat_id={chat_id}&text={text}"
    print(f"Sending request to: {uri}")  # Debug print
    req = request.Request(uri)
    request.urlopen(req)


def get_current_data() -> Tuple[float, List[Optional[float]], List[int]]:
    """
    Fetch current and historical data for SWDA.MI ETF from Yahoo Finance.

    Returns:
        Tuple containing:
        - current_price: Current market price
        - close_prices: List of historical closing prices
        - timestamps: List of corresponding timestamps
    """
    current_timestamp = int(time.time())
    base_url = "https://query2.finance.yahoo.com/v8/finance/chart/SWDA.MI"

    params = {
        "period1": "1253862000",
        "period2": str(current_timestamp),
        "interval": "1d",
        "includePrePost": "true",
    }

    # Construct URL with parameters
    url = f"{base_url}?{parse.urlencode(params)}"

    # Create request with headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"  # noqa
    }
    req = request.Request(url, headers=headers)

    # Make request and parse response
    with request.urlopen(req) as response:
        data = json.loads(response.read().decode())

    result = data["chart"]["result"][0]
    current_price = result["meta"]["regularMarketPrice"]
    close_prices = result["indicators"]["quote"][0]["close"]
    timestamps = result["timestamp"]

    return current_price, close_prices, timestamps


def calculate_bbands(
    prices: List[float], timestamps: List[int], period: int = 20, num_std: float = 2.0
) -> Dict[str, Union[float, int]]:
    """
    Calculate Bollinger Bands for a given list of prices.

    Args:
        prices: List of closing prices
        timestamps: List of timestamps corresponding to prices
        period: Period for moving average (default: 20)
        num_std: Number of standard deviations for bands (default: 2.0)

    Returns:
        Dictionary containing middle, upper, lower bands and timestamp
    """
    if len(prices) < period:
        raise ValueError(f"Not enough prices. Need at least {period} prices")
    if len(prices) != len(timestamps):
        raise ValueError("Length of prices and timestamps must match")

    # Calculate middle band (SMA)
    sma = mean(prices[-period:])

    # Calculate standard deviation
    std = stdev(prices[-period:])

    # Calculate upper and lower bands
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)

    return {
        "middle": sma,
        "upper": upper_band,
        "lower": lower_band,
        "timestamp": timestamps[-1],  # Use the latest timestamp
        "price": prices[-1],
    }


def calculate_bbands_series(
    prices: List[float], timestamps: List[int], period: int = 20, num_std: float = 2.0
) -> List[Dict[str, Union[float, int, None]]]:
    """
    Calculate Bollinger Bands for entire price series.

    Args:
        prices: List of closing prices
        timestamps: List of timestamps corresponding to prices
        period: Period for moving average (default: 20)
        num_std: Number of standard deviations for bands (default: 2.0)

    Returns:
        List of dictionaries containing bands and timestamps for each point
    """
    if len(prices) != len(timestamps):
        raise ValueError("Length of prices and timestamps must match")

    results = []

    # Add None for the first period-1 points where we can't calculate bands
    for i in range(period - 1):
        results.append(
            {
                "middle": None,
                "upper": None,
                "lower": None,
                "timestamp": timestamps[i],
                "price": prices[i],
            }
        )

    # Calculate bands for the rest of the points
    for i in range(period - 1, len(prices)):
        window_prices = prices[i - period + 1 : i + 1]
        window_timestamps = timestamps[i - period + 1 : i + 1]
        bands = calculate_bbands(window_prices, window_timestamps, period, num_std)
        results.append(bands)

    return results


def handler(event, context):
    current_price, close_prices, timestamps = get_current_data()
    bands = calculate_bbands_series(close_prices, timestamps)
    latest_band = bands[-1]
    lower = latest_band["lower"]
    interesting_value = current_price - lower
    message = (
        "Current: {:.2f} €\n"
        "Lower Band: {:.2f} €\n"
        "Distance to Lower Band: {:.2f} €".format(
            current_price, latest_band["lower"], interesting_value
        )
    )
    send_telegram_message(message)


if __name__ == "__main__":
    handler(None, None)
