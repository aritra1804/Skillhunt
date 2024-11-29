import streamlit as st
import requests
import base64
import pandas as pd
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import time

# Udemy API Credentials
CLIENT_ID = "JfHN7pmHzxTDZ4RGe9bqcpqwhxPVmwdLFX2npJ9S"
CLIENT_SECRET = "gCYnV43f2jsbkrCDyNywUPOk20bKFnIZcKAp0sSN3rtBgR9HjvY5IC69vETJIY4sWFNGmbJHTdWgYxZUsybKxrbcu6G1T67n9QD3Do1jRle2WE9dM3UCx1RVLCVGihlQ"
UDEMY_BASE_URL = "https://www.udemy.com/api-2.0/courses/"
UDEMY_COURSE_BASE_URL = "https://www.udemy.com"

# Headers for Udemy API
encoded_credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
headers = {"Authorization": f"Basic {encoded_credentials}", "Accept": "application/json"}

# edX API URL
EDX_API_URL = "https://www.edx.org/api/v1/catalog/search"


# Udemy Courses Function
def fetch_udemy_courses(search_term, max_pages=1):
    all_courses = []
    for page in range(1, max_pages + 1):
        params = {"search": search_term, "page": page, "page_size": 10, "price": "price-paid", "language": "en"}
        response = requests.get(UDEMY_BASE_URL, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            courses = data.get("results", [])
            if not courses:
                break
            all_courses.extend(courses)
        else:
            st.error(f"Error fetching Udemy courses: {response.status_code}")
            break
        time.sleep(0.5)  # Respect API rate limits
    courses_df = pd.DataFrame(all_courses)
    if not courses_df.empty and "url" in courses_df.columns:
        courses_df["url"] = UDEMY_COURSE_BASE_URL + courses_df["url"]
    return courses_df


# Coursera Courses Function
def fetch_coursera_courses(search_term):
    COURSERA_API_URL = "https://api.coursera.org/api/courses.v1"
    params = {"q": "search", "query": search_term}
    response = requests.get(COURSERA_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        courses = data.get("elements", [])
        return pd.DataFrame([{"Title": course.get("name"), "Link": f"https://www.coursera.org/learn/{course.get('slug', '')}"} for course in courses])
    else:
        st.error(f"Error fetching Coursera courses: {response.status_code}")
        return pd.DataFrame()


# edX Courses Function
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


# We Work Remotely Jobs Function
def fetch_jobs(keyword):
    base_url = f"https://weworkremotely.com/remote-jobs/search?term={keyword}"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")
    jobs = []
    for job in soup.find_all("li", class_="feature"):
        title = job.find("span", class_="title").text if job.find("span", class_="title") else "N/A"
        company = job.find("span", class_="company").text if job.find("span", class_="company") else "N/A"
        link = "https://weworkremotely.com" + job.find("a")["href"] if job.find("a") else "N/A"
        jobs.append({"Title": title, "Company": company, "Link": link})
    return pd.DataFrame(jobs)


# Google Trends Function
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
st.sidebar.header("Search Parameters")
search_term = st.sidebar.text_input("Enter a keyword (e.g., Python, Data Science, Remote):", value="python")
max_pages = st.sidebar.slider("Number of Pages to Fetch (Udemy)", min_value=1, max_value=5, value=2)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Udemy Courses", "Coursera Courses", "Jobs", "edX Courses", "Google Trends"])

# Udemy Courses Tab
with tab1:
    st.subheader("Udemy Courses")
    if st.button("Fetch Udemy Courses"):
        with st.spinner("Fetching Udemy courses..."):
            udemy_df = fetch_udemy_courses(search_term, max_pages)
        if not udemy_df.empty:
            st.dataframe(udemy_df[["title", "url", "price"]].head(10))
            csv_data = udemy_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Udemy Courses CSV", csv_data, "udemy_courses.csv", "text/csv")
        else:
            st.warning("No Udemy courses found.")

# Coursera Courses Tab
with tab2:
    st.subheader("Coursera Courses")
    if st.button("Fetch Coursera Courses"):
        with st.spinner("Fetching Coursera courses..."):
            coursera_df = fetch_coursera_courses(search_term)
        if not coursera_df.empty:
            st.dataframe(coursera_df)
            csv_data = coursera_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Coursera Courses CSV", csv_data, "coursera_courses.csv", "text/csv")
        else:
            st.warning("No Coursera courses found.")

# Jobs Tab
with tab3:
    st.subheader("Job Listings from We Work Remotely")
    if st.button("Fetch Jobs"):
        with st.spinner("Fetching jobs..."):
            jobs_df = fetch_jobs(search_term)
        if not jobs_df.empty:
            st.dataframe(jobs_df.head(10))
            csv_data = jobs_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Job Listings CSV", csv_data, "wework_jobs.csv", "text/csv")
        else:
            st.warning("No job listings found.")

# edX Courses Tab
with tab4:
    st.subheader("edX Courses")
    if st.button("Fetch edX Courses"):
        with st.spinner("Fetching edX courses..."):
            edx_df = fetch_edx_courses(search_term)
        if not edx_df.empty:
            st.dataframe(edx_df)
            csv_data = edx_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download edX Courses CSV", csv_data, "edx_courses.csv", "text/csv")
        else:
            st.warning("No edX courses found.")

# Google Trends Tab
with tab5:
    st.subheader("Google Trends")
    if st.button("Fetch Trends"):
        with st.spinner("Fetching Google Trends..."):
            trends_df = fetch_google_trends(search_term)
        if not trends_df.empty:
            st.line_chart(trends_df.set_index("date")[[search_term]])
            st.write(trends_df)
        else:
            st.warning("No trends data found.")
