import streamlit as st
import requests
import base64
import pandas as pd
from bs4 import BeautifulSoup
from pytrends.request import TrendReq  # For Google Trends

# Udemy API Credentials
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
UDEMY_BASE_URL = "https://www.udemy.com/api-2.0/courses/"
UDEMY_COURSE_BASE_URL = "https://www.udemy.com"

# Headers for Udemy API
encoded_credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
headers = {"Authorization": f"Basic {encoded_credentials}", "Accept": "application/json"}

# edX API URL
EDX_API_URL = "https://www.edx.org/api/v1/catalog/search"

# Function to fetch edX courses
def fetch_edx_courses(search_term):
    params = {"q": search_term}
    response = requests.get(EDX_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        courses = data.get("objects", [])
        return pd.DataFrame([{"Title": course.get("title"), "Link": course.get("marketing_url")} for course in courses])
    else:
        st.error(f"Error fetching edX courses: {response.status_code}")
        return pd.DataFrame()

# Function to fetch Google Trends data
def fetch_google_trends(search_term):
    pytrends = TrendReq()
    pytrends.build_payload([search_term], cat=0, timeframe="today 12-m", geo="", gprop="")
    trends = pytrends.interest_over_time()
    if not trends.empty:
        trends.reset_index(inplace=True)
        return trends
    else:
        st.warning(f"No Google Trends data found for '{search_term}'")
        return pd.DataFrame()

# Streamlit App
st.title("Enhanced Learning and Job Finder")
search_term = st.sidebar.text_input("Enter a keyword (e.g., Python, Data Science, Remote):", value="python")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Udemy Courses", "Coursera Courses", "Jobs", "edX Courses", "Google Trends"]
)

# Udemy Courses Tab
with tab1:
    st.subheader("Udemy Courses")
    if st.button("Fetch Udemy Courses"):
        with st.spinner("Fetching Udemy courses..."):
            udemy_df = fetch_udemy_courses(search_term)
        if not udemy_df.empty:
            st.dataframe(udemy_df[["title", "url", "price"]].head(10))
        else:
            st.warning("No Udemy courses found.")

# Coursera Courses Tab
with tab2:
    st.subheader("Coursera Courses")
    if st.button("Fetch Coursera Courses"):
        with st.spinner("Fetching Coursera courses..."):
            coursera_df = fetch_coursera_courses(search_term)
        if not coursera_df.empty:
            st.dataframe(coursera_df.head(10))
        else:
            st.warning("No Coursera courses found.")

# Jobs Tab
with tab3:
    st.subheader("Job Listings")
    if st.button("Fetch Jobs"):
        with st.spinner("Fetching job listings..."):
            jobs_df = fetch_jobs(search_term)
        if not jobs_df.empty:
            st.dataframe(jobs_df.head(10))
        else:
            st.warning("No job listings found.")

# edX Courses Tab
with tab4:
    st.subheader("edX Courses")
    if st.button("Fetch edX Courses"):
        with st.spinner("Fetching edX courses..."):
            edx_df = fetch_edx_courses(search_term)
        if not edx_df.empty:
            st.dataframe(edx_df.head(10))
        else:
            st.warning("No edX courses found.")

# Google Trends Tab
with tab5:
    st.subheader("Google Trends")
    if st.button("Fetch Trends"):
        with st.spinner("Fetching Google Trends..."):
            trends_df = fetch_google_trends(search_term)
        if not trends_df.empty:
            st.line_chart(trends_df.set_index("date")["python"])  # Replace "python" with your search term
        else:
            st.warning("No trends data found.")
