import streamlit as st
import requests
import base64
import pandas as pd

# Udemy API credentials
CLIENT_ID = "JfHN7pmHzxTDZ4RGe9bqcpqwhxPVmwdLFX2npJ9S"
CLIENT_SECRET = "gCYnV43f2jsbkrCDyNywUPOk20bKFnIZcKAp0sSN3rtBgR9HjvY5IC69vETJIY4sWFNGmbJHTdWgYxZUsybKxrbcu6G1T67n9QD3Do1jRle2WE9dM3UCx1RVLCVGihlQ"

# Base URL
BASE_URL = "https://www.udemy.com/api-2.0/courses/"

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

    return pd.DataFrame(all_courses) if all_courses else pd.DataFrame()

# Streamlit App
st.title("Udemy Course Finder with Filters")
st.write("Search for Udemy courses, filter results, and fetch details interactively!")

# Sidebar inputs
st.sidebar.header("Search Parameters")
search_term = st.sidebar.text_input("Search Term", value="python")
max_pages = st.sidebar.slider("Number of Pages to Fetch", min_value=1, max_value=5, value=3)

# Fetch courses on button click
if st.sidebar.button("Fetch Courses"):
    st.write(f"Fetching courses for: {search_term} (up to {max_pages} pages)...")
    with st.spinner("Fetching data..."):
        courses_df = fetch_courses(search_term, max_pages)

    # Display results
    if not courses_df.empty:
        st.success(f"Found {len(courses_df)} courses!")

        # Debugging: Print available columns
        st.write("Available columns in the dataset:")
        st.write(courses_df.columns.tolist())

        # Dynamically select columns to display
        available_columns = ["id", "title", "price", "headline", "url"]  # Updated for your dataset
        columns_to_display = [col for col in available_columns if col in courses_df.columns]

        # Filter options
        st.sidebar.header("Filter Options")

        # Filter by price range
        if "price" in courses_df.columns:
            courses_df["price"] = courses_df["price"].str.replace("$", "").astype(float, errors="ignore")
        min_price, max_price = st.sidebar.slider(
            "Price Range ($)", 
            min_value=0, 
            max_value=200, 
            value=(0, 50)
        )
        filtered_df = courses_df.copy()
        if "price" in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df["price"] >= min_price) & (filtered_df["price"] <= max_price)
            ]

        # Display filtered results
        if not filtered_df.empty:
            st.write("### Filtered Course Results")
            st.dataframe(filtered_df[columns_to_display].head(10))

            # Download button
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Filtered CSV",
                data=csv_data,
                file_name="filtered_udemy_courses.csv",
                mime="text/csv"
            )
        else:
            st.warning("No courses match the selected filters.")
    else:
        st.warning("No courses found for the given search term.")
