import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Udemy API Credentials
CLIENT_ID = "JfHN7pmHzxTDZ4RGe9bqcpqwhxPVmwdLFX2npJ9S"
CLIENT_SECRET = "gCYnV43f2jsbkrCDyNywUPOk20bKFnIZcKAp0sSN3rtBgR9HjvY5IC69vETJIY4sWFNGmbJHTdWgYxZUsybKxrbcu6G1T67n9QD3Do1jRle2WE9dM3UCx1RVLCVGihlQ"
UDEMY_BASE_URL = "https://www.udemy.com/api-2.0/courses/"
UDEMY_COURSE_BASE_URL = "https://www.udemy.com"

# Coursera API URL
COURSERA_API_URL = "https://api.coursera.org/api/courses.v1"

# Headers for Udemy API
encoded_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}".encode("ascii").hex()
headers = {"Authorization": f"Basic {encoded_credentials}", "Accept": "application/json"}

# Function to fetch Udemy courses
def fetch_udemy_courses(search_term, max_pages=1):
    """
    Fetch courses from Udemy API based on a search term.
    """
    all_courses = []
    for page in range(1, max_pages + 1):
        params = {"search": search_term, "page": page, "page_size": 10, "price": "price-paid", "language": "en"}
        response = requests.get(UDEMY_BASE_URL, headers=headers, params=params)

        # Debugging: Print response status and content
        print(f"Fetching page {page} for '{search_term}'")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("Response Data:", data)  # Debugging: Print response JSON

            courses = data.get("results", [])
            if not courses:
                break  # Exit loop if no results
            all_courses.extend(courses)
        else:
            st.error(f"Error fetching Udemy courses: {response.status_code}")
            print("Error Response:", response.text)  # Debugging: Print error details
            break

    courses_df = pd.DataFrame(all_courses)
    if not courses_df.empty and "url" in courses_df.columns:
        courses_df["url"] = UDEMY_COURSE_BASE_URL + courses_df["url"]
    return courses_df

# Function to fetch Coursera courses
def fetch_coursera_courses(search_term):
    """
    Fetch courses from the Coursera API based on a search term.
    """
    params = {"q": "search", "query": search_term}
    response = requests.get(COURSERA_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        courses = data.get("elements", [])
        if not courses:
            return pd.DataFrame()
        courses_list = []
        for course in courses:
            courses_list.append({
                "Title": course.get("name", "N/A"),
                "Course ID": course.get("id", "N/A"),
                "Slug": course.get("slug", "N/A"),
                "Link": f"https://www.coursera.org/learn/{course.get('slug', '')}",
            })
        return pd.DataFrame(courses_list)
    else:
        st.error(f"Error fetching Coursera courses: {response.status_code}")
        return pd.DataFrame()

# Function to scrape We Work Remotely jobs
def scrape_jobs(keyword):
    """
    Scrape job listings from We Work Remotely based on a keyword.
    """
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
st.write("Search for courses and jobs based on your interests!")

# Input: Search Keyword
search_term = st.text_input("Enter a keyword (e.g., Python, Data Science, Remote):", value="python")

# Search Courses Section
if st.button("Search Courses"):
    st.subheader(f"Top Courses for: {search_term}")
    with st.spinner("Fetching Udemy courses..."):
        udemy_df = fetch_udemy_courses(search_term, max_pages=2)
    with st.spinner("Fetching Coursera courses..."):
        coursera_df = fetch_coursera_courses(search_term)

    # Display Udemy Results
    if not udemy_df.empty:
        st.write("### Udemy Courses")
        for _, row in udemy_df.head(10).iterrows():
            st.markdown(f"- **[{row['title']}]({row['url']})** — ${row['price']}  \n  *{row['headline']}*")
        if len(udemy_df) > 10:
            st.write(f"View all {len(udemy_df)} Udemy courses by downloading below.")
        csv_data = udemy_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Udemy Courses CSV", csv_data, "udemy_courses.csv", "text/csv")
    else:
        st.warning("No Udemy courses found.")

    # Display Coursera Results
    if not coursera_df.empty:
        st.write("### Coursera Courses")
        for _, row in coursera_df.head(10).iterrows():
            st.markdown(f"- **[{row['Title']}]({row['Link']})**  \n  *(Course ID: {row['Course ID']})*")
        if len(coursera_df) > 10:
            st.write(f"View all {len(coursera_df)} Coursera courses by downloading below.")
        csv_data = coursera_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Coursera Courses CSV", csv_data, "coursera_courses.csv", "text/csv")
    else:
        st.warning("No Coursera courses found.")

# Search Jobs Section
if st.button("Search Jobs"):
    st.subheader(f"Jobs Matching: {search_term}")
    with st.spinner("Fetching job listings..."):
        jobs_df = scrape_jobs(search_term)

    if not jobs_df.empty:
        for _, row in jobs_df.iterrows():
            st.markdown(f"- **[{row['Title']}]({row['Link']})**  \n  *{row['Company']}*")
        csv_data = jobs_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Job Listings CSV", csv_data, "wework_jobs.csv", "text/csv")
    else:
        st.warning("No jobs found for the given keyword.")
