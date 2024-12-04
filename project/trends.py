from pytrends.request import TrendReq
import pandas as pd
import time
import matplotlib.pyplot as plt
from pytrends.exceptions import TooManyRequestsError
import streamlit as st

def fetch_google_trends(search_term):
    pytrends = TrendReq()
    pytrends.build_payload([search_term], cat=0, timeframe="today 12-m", geo="", gprop="")
    trends = pytrends.interest_over_time()
    if not trends.empty:
        trends.reset_index(inplace=True)
        trends["date"] = trends["date"].dt.strftime("%Y-%m-%d")
        trends.rename(columns={search_term: "Interest"}, inplace=True)
        trends.drop(columns=["isPartial"], inplace=True)
        return trends
    else:
        st.warning(f"No Google Trends data found for '{search_term}'")
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
