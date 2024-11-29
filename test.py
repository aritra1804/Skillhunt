import streamlit as st
import requests
import base64
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Udemy API credentials
CLIENT_ID = "JfHN7pmHzxTDZ4RGe9bqcpqwhxPVmwdLFX2npJ9S"
CLIENT_SECRET = "gCYnV43f2jsbkrCDyNywUPOk20bKFnIZcKAp0sSN3rtBgR9HjvY5IC69vETJIY4sWFNGmbJHTdWgYxZUsybKxrbcu6G1T67n9QD3Do1jRle2WE9dM3UCx1RVLCVGihlQ"

# Base URL for Udemy API
BASE_URL = "https://www.udemy.com/api-2.0/courses/"
COURSE_BASE_URL = "https://www.udemy.com"  # Base URL for constructing full course URLs

# Encode credentials for Basic Auth
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Headers for API requests
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Accept": "application/json"
}

# Function to fetch Udemy courses
def fetch_courses(search_term, max_pages=1):
    """
    Fetch courses from the Udemy API.

    Args:
    search_term (str): The search term for fetching courses.
    max_pages (int): The maximum number of pages to fetch.

    Returns:
    pd.DataFrame: A DataFrame containing the fetched courses.
    """
    all_courses = []
    for page in range(1, max_pages + 1):
        params = {
            "search": search_term,
            "page": page,
            "page_size": 100,
            "price": "price-paid",
            "language": "en"
        }
        response = requests.get(BASE_URL, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            courses = data.get("results", [])
            if not courses:
                break
            all_courses.extend(courses)
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            break
    # Create DataFrame
    courses_df = pd.DataFrame(all_courses)
    if not courses_df.empty and "url" in courses_df.columns:
        # Prepend the base URL to construct full URLs
        courses_df["url"] = COURSE_BASE_URL + courses_df["url"]
    return courses_df

# Streamlit App
st.title("Udemy Course Finder")
st.write("Search for Udemy courses, explore statistics, and visualize data interactively!")

# Sidebar inputs
st.sidebar.header("Search Parameters")
search_term = st.sidebar.text_input("Search Term", value="python")
max_pages = st.sidebar.slider("Number of Pages to Fetch", min_value=1, max_value=5, value=3)

# Fetch courses on button click
if st.sidebar.button("Fetch Courses"):
    st.write(f"Fetching courses for: {search_term} (up to {max_pages} pages)...")
    with st.spinner("Fetching data..."):
        courses_df = fetch_courses(search_term, max_pages)

    if not courses_df.empty:
        st.success(f"Found {len(courses_df)} courses!")

        # Clean and process the data
        if "price" in courses_df.columns:
            # Remove $ symbols and convert to numeric
            courses_df["price"] = pd.to_numeric(courses_df["price"].str.replace("$", ""), errors="coerce")

        # Key statistics
        st.write("### Descriptive Statistics")
        st.write(f"**Total Courses:** {len(courses_df)}")
        st.write(f"**Average Price:** ${courses_df['price'].mean():.2f}")
        st.write(f"**Most Expensive Course:** ${courses_df['price'].max():.2f}")
        st.write(f"**Cheapest Course:** ${courses_df['price'].min():.2f}")

        # Tabular visualization with URL
        st.write("### Top 10 Courses by Price")
        top_courses = courses_df.sort_values(by="price", ascending=False).head(10)
        
        # Display clickable links for each course
        st.write("### Clickable Links for Top 10 Courses")
        for _, row in top_courses.iterrows():
            st.markdown(
                f"- **[{row['title']}]({row['url']})** — ${row['price']:.2f}  \n  *{row['headline']}*"
            )

        # Full table display for top courses
        st.write("### Full Table View")
        st.dataframe(top_courses[["title", "price", "headline", "url"]])

        # Visualization
        st.write("### Price Distribution")
        fig, ax = plt.subplots()
        courses_df["price"].plot(kind="hist", bins=20, ax=ax, color="skyblue", edgecolor="black")
        ax.set_title("Course Price Distribution")
        ax.set_xlabel("Price ($)")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

        # Download button
        st.write("### Download Data")
        csv_data = courses_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="udemy_courses_with_urls.csv",
            mime="text/csv"
        )
    else:
        st.warning("No courses found for the given search term.")
