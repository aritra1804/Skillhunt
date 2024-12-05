from pytrends.request import TrendReq
import pandas as pd
import time
import matplotlib.pyplot as plt
from pytrends.exceptions import TooManyRequestsError
import streamlit as st

def fetch_google_trends(search_term, retries=3, delay=5, backup_file="google_trends_backup.csv"):
    """
    Fetch Google Trends data for a search term. Uses a backup file if rate-limited.
    
    Args:
        search_term (str): Keyword to search on Google Trends.
        retries (int): Number of retry attempts if rate-limited.
        delay (int): Delay (seconds) between retries.
        backup_file (str): Path to backup file for fallback data.

    Returns:
        pd.DataFrame: Google Trends data.
    """
    pytrends = TrendReq()
    
    try:
        pytrends.build_payload([search_term], cat=0, timeframe="today 12-m", geo="", gprop="")
        trends = pytrends.interest_over_time()
        
        if not trends.empty:
            # Save data locally for future use
            trends.reset_index(inplace=True)
            trends["date"] = trends["date"].dt.strftime("%Y-%m-%d")
            trends.rename(columns={search_term: "Interest"}, inplace=True)
            trends.drop(columns=["isPartial"], inplace=True)
            trends.to_csv(backup_file, index=False)  # Save backup
            return trends
        else:
            return pd.DataFrame()  # Return empty DataFrame if no data
    except TooManyRequestsError:
        if retries > 0:
            time.sleep(delay)
            return fetch_google_trends(search_term, retries - 1, delay, backup_file)
        else:
            st.warning(f"Rate limit reached. Using backup data from {backup_file}.")
            try:
                return pd.read_csv(backup_file)
            except FileNotFoundError:
                st.error(f"No backup data available in {backup_file}.")
                return pd.DataFrame()

def clean_trends_data(df):
    """
    Clean and preprocess Google Trends data.

    Args:
        df (pd.DataFrame): Raw trends data.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    if "Interest" in df.columns:
        df["Interest"] = df["Interest"].astype(float)
    return df

def visualize_trends_data(df):
    """
    Visualize Google Trends data.

    Args:
        df (pd.DataFrame): Cleaned trends data.

    """
    print("Interest Over Time (Google Trends)")
    df.plot(x="date", y="Interest", kind="line", title="Google Trends Interest Over Time", legend=False)
    plt.xlabel("Date")
    plt.ylabel("Interest")
    plt.xticks(rotation=45)
    plt.show()
