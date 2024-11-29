import streamlit as st
import requests
import base64
import pandas as pd
from bs4 import BeautifulSoup
import time

# Udemy API Credentials
CLIENT_ID = "your_client_id"  # Replace with your Udemy API Client ID
CLIENT_SECRET = "your_client_secret"  # Replace with your Udemy API Client Secret
UDEMY_BASE_URL = "https://www.udemy.com/api-2.0/courses/"
UDEMY_COURSE_BASE_URL = "https://www.udemy.com"

# Coursera API URL
COURSERA_API_URL = "https://api.coursera.org/api/courses.v1"

# Headers for Udemy API
encoded_credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
headers = {"Authorization": f"Basic {encoded_credentials}", "Accept": "application/json"}


# Function to fetch Udemy courses
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
        time.sleep(0.5)  # Respect Udemy API rate limits
    courses_df = pd.DataFrame(all_courses)
    if not courses_df.empty and "url" in courses_df.columns:
        courses_df["url"] = UDEMY_COURSE_BASE_URL + courses_df["url"]
    return courses_df


# Function to fetch Coursera courses
def fetch_coursera_courses(search_term):
    params = {"q": "search", "query": search_term}
    response = requests.get(COURSERA_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        courses = data.get("elements", [])
        courses_list = [
            {
                "Title": course.get("name", "N/A"),
                "Link": f"https://www.coursera.org/learn/{course.get('slug', '')}"
            }
            for course in courses
        ]
        return pd.DataFrame(courses_list)
    else:
        st.error(f"Error fetching Coursera courses: {response.status_code}")
        return pd.DataFrame()


# Function to scrape jobs from We Work Remotely
def fetch_jobs(keyword):
    base_url = f"https://weworkremotely.com/remote-jobs/search?term={keyword}"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")
    jobs = []
    job_listings = soup.find_all("li", class_="feature")
    for job in job_listings:
        title = job.find("span", class_="title").text if job.find("span", class_="title") else "N/A"
        company = job.find("span", class_="company").text if job.find("span", class_="company") else "N/A"
        link = "https://weworkremotely.com" + job.find("a")["href"] if job.find("a") else "N/A"
        jobs.append({"Title": title, "Company": company, "Link": link})
    return pd.DataFrame(jobs)


# Streamlit App
st.title("Unified Learning and Job Finder")
st.sidebar.header("Search Parameters")
search_term = st.sidebar.text_input("Search Term", value="python")
max_pages = st.sidebar.slider("Number of Pages to Fetch (Udemy)", min_value=1, max_value=5, value=2)

tab1, tab2, tab3 = st.tabs(["Udemy Courses", "Coursera Courses", "Jobs"])

# Udemy Courses Tab
with tab1:
    st.subheader("Udemy Courses")
    if st.button("Fetch Udemy Courses"):
        st.write(f"Fetching courses for: {search_term} (up to {max_pages} pages)...")
        with st.spinner("Fetching Udemy courses..."):
            udemy_df = fetch_udemy_courses(search_term, max_pages)
        if not udemy_df.empty:
            st.success(f"Found {len(udemy_df)} courses!")
            for _, row in udemy_df.head(10).iterrows():
                st.markdown(f"- **[{row['title']}]({row['url']})** — ${row['price']}  \n  *{row['headline']}*")
            csv_data = udemy_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Udemy Courses CSV", csv_data, "udemy_courses.csv", "text/csv")
        else:
            st.warning("No Udemy courses found.")

# Coursera Courses Tab
with tab2:
    st.subheader("Coursera Courses")
    if st.button("Fetch Coursera Courses"):
        st.write(f"Fetching courses for: {search_term}")
        with st.spinner("Fetching Coursera courses..."):
            coursera_df = fetch_coursera_courses(search_term)
        if not coursera_df.empty:
            st.success(f"Found {len(coursera_df)} courses!")
            for _, row in coursera_df.iterrows():
                st.markdown(f"- **[{row['Title']}]({row['Link']})**")
            csv_data = coursera_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Coursera Courses CSV", csv_data, "coursera_courses.csv", "text/csv")
        else:
            st.warning("No Coursera courses found.")

# Jobs Tab
with tab3:
    st.subheader("Jobs from We Work Remotely")
    if st.button("Fetch Jobs"):
        st.write(f"Fetching jobs for: {search_term}")
        with st.spinner("Fetching job listings..."):
            jobs_df = fetch_jobs(search_term)
        if not jobs_df.empty:
            st.success(f"Found {len(jobs_df)} jobs!")
            for _, row in jobs_df.iterrows():
                st.markdown(f"- **[{row['Title']}]({row['Link']})**  \n  *{row['Company']}*")
            csv_data = jobs_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Job Listings CSV", csv_data, "wework_jobs.csv", "text/csv")
        else:
            st.warning("No jobs found.")
