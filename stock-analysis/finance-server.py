from typing import Dict, Any
from dataclasses import dataclass
import pandas as pd
import os
from datetime import datetime
import requests


# API Key
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

@dataclass
class MarketData:
    symbol: str
    interval: str
    data: pd.DataFrame
    last_updated: datetime

class AlphaVantageAPI:
    @staticmethod
    def get_intraday_data(symbol: str, interval: str="1min", outputsize: str="compact") -> pd.DataFrame:
        """Fetch intraday data from AlphaVantage API"""
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={ALPHAVANTAGE_API_KEY}"
        
        response = requests.get(url)
        data = response.json()

        # Check for error responses
        if "Error Message" in data:
            raise ValueError(f"API Error: {data['Error Message']}")
        if "Note" in data:
            print(f"API Note: {data['Note']}")

        # Extract time series data
        time_series_key = f"Time Series ({interval})"
        if time_series_key not in data:
            raise ValueError(f"No time series data found for {symbol} with interval {interval}.")
        
        time_series = data[time_series_key]

        # Convert to Dataframe
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # Rename columns and convert to numeric
        df.columns = [col.split(". ")[1] for col in df.columns]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])

        return df



# Technical Analysis Tools
def calculate_moving_averages(symbol: str, short_period: int=20, long_period: int=50) -> Dict[str, Any]:
    """
    Calculate short and long term moving averages for a symbol
    
    Args:
        symbol: The ticker symbol to analyze
        short_period: Short moving average period in minutes
        long_period: Long moving average period in minutes
        
    Returns:
        Dictionary with moving average data and analysis
    """
    cache_key = f"{symbol}_1min"

    if cache_key not in market