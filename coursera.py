import streamlit as st
import requests
import pandas as pd

# Base URL for Coursera API
COURSERA_API_URL = "https://api.coursera.org/api/courses.v1"

# Function to fetch Coursera courses
def fetch_coursera_courses(search_term):
    """
    Fetch courses from the Coursera API based on a search term.

    Args:
        search_term (str): The keyword to search courses for.

    Returns:
        pd.DataFrame: A DataFrame containing course details.
    """
    params = {"q": "search", "query": search_term}
    response = requests.get(COURSERA_API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        courses = data.get("elements", [])
        if not courses:
            return pd.DataFrame()

        # Extract relevant information from API response
        courses_list = []
        for course in courses:
            course_data = {
                "Title": course.get("name", "N/A"),
                "Course ID": course.get("id", "N/A"),
                "Slug": course.get("slug", "N/A"),
                "Link": f"https://www.coursera.org/learn/{course.get('slug', '')}",
            }
            courses_list.append(course_data)

        return pd.DataFrame(courses_list)
    else:
        st.error(f"Error fetching Coursera courses: {response.status_code}")
        return pd.DataFrame()

# Streamlit App Integration
st.header("Coursera Course Finder")

# Input: Search Term
search_term = st.text_input("Enter Keyword (e.g., Python, Data Science):", value="python")

# Fetch courses on button click
if st.button("Search Coursera Courses"):
    st.write(f"Fetching courses for: {search_term}")
    with st.spinner("Fetching data..."):
        coursera_courses_df = fetch_coursera_courses(search_term)

    # Display results
    if not coursera_courses_df.empty:
        st.success(f"Found {len(coursera_courses_df)} courses on Coursera!")
        
        # Clickable links for each course
        st.write("### Coursera Courses")
        for _, row in coursera_courses_df.iterrows():
            st.markdown(f"- **[{row['Title']}]({row['Link']})**  \n  *(Course ID: {row['Course ID']})*")
        
        # CSV Download
        csv_data = coursera_courses_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Coursera Courses CSV",
            data=csv_data,
            file_name="coursera_courses.csv",
            mime="text/csv",
        )
    else:
        st.warning("No courses found on Coursera for the given keyword.")
