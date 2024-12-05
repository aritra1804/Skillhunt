import os
from dotenv import load_dotenv
import streamlit as st
from udemy import fetch_udemy_courses, clean_udemy_data, visualize_udemy_data
from coursera import fetch_coursera_courses, clean_coursera_data, visualize_coursera_data
from trends import fetch_google_trends, clean_trends_data, visualize_trends_data
from jobs import fetch_jobs, clean_jobs_data, visualize_jobs_data
import matplotlib.pyplot as plt

# Load environment variables from .env file
load_dotenv()

# Get Udemy credentials from environment variables
UDEMY_CLIENT_ID = os.getenv("UDEMY_CLIENT_ID")
UDEMY_CLIENT_SECRET = os.getenv("UDEMY_CLIENT_SECRET")

# Encode credentials for Udemy API
import base64
encoded_credentials = base64.b64encode(f"{UDEMY_CLIENT_ID}:{UDEMY_CLIENT_SECRET}".encode()).decode()
headers = {"Authorization": f"Basic {encoded_credentials}", "Accept": "application/json"}

# Initialize Session State
if "udemy_df" not in st.session_state:
    st.session_state.udemy_df = None

if "coursera_df" not in st.session_state:
    st.session_state.coursera_df = None

if "jobs_df" not in st.session_state:
    st.session_state.jobs_df = None

if "trends_df" not in st.session_state:
    st.session_state.trends_df = None

# Streamlit App
st.title("SkillHunt - Enhanced Learning and Job Finder with Insights")

# Sidebar Inputs
st.sidebar.header("Search Parameters")
search_term = st.sidebar.text_input("Enter a keyword (e.g., Python, Data Science):", value="python")
max_pages = st.sidebar.slider("Number of Pages to Fetch (Udemy)", min_value=1, max_value=5, value=2)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Udemy Courses",
    "Coursera Courses",
    "Jobs with Salaries",
    "Google Trends",
    "Insights & Visualizations"
])

# Udemy Tab
with tab1:
    st.subheader("Udemy Courses")
    if st.button("Fetch Udemy Courses"):
        with st.spinner("Fetching Udemy courses..."):
            df, error = fetch_udemy_courses(search_term, max_pages, headers)  # Pass headers here
            if error:
                st.error(error)
            elif not df.empty:
                # Clean the data
                st.session_state.udemy_df = clean_udemy_data(df)

                # Add a numbering column and reset index
                st.session_state.udemy_df = st.session_state.udemy_df.reset_index(drop=True)
                st.session_state.udemy_df.insert(0, "S.No.", range(1, len(st.session_state.udemy_df) + 1))

                # Display without the default index
                st.dataframe(st.session_state.udemy_df.set_index("S.No.")[["title", "url", "price"]])
            else:
                st.warning("No Udemy courses found.")



# Coursera Tab
with tab2:
    st.subheader("Coursera Courses")
    max_results = st.sidebar.slider("Number of Results to Fetch (Coursera)", min_value=1, max_value=50, value=10)

    if st.button("Fetch Coursera Courses"):
        with st.spinner("Fetching Coursera courses..."):
            df, error = fetch_coursera_courses(search_term)
            if error:
                st.error(error)
            elif not df.empty:
                # Clean the data
                st.session_state.coursera_df = clean_coursera_data(df)

                # Limit results to the slider value
                st.session_state.coursera_df = st.session_state.coursera_df.head(max_results)

                # Add a numbering column
                st.session_state.coursera_df = st.session_state.coursera_df.reset_index(drop=True)
                st.session_state.coursera_df.insert(0, "S.No.", range(1, len(st.session_state.coursera_df) + 1))

                # Display without the default index
                st.dataframe(st.session_state.coursera_df.set_index("S.No."))
            else:
                st.warning("No Coursera courses found.")


# Jobs Tab
with tab3:
    st.subheader("Job Listings with Estimated Salaries")
    if st.button("Fetch Jobs"):
        with st.spinner("Fetching job listings..."):
            df, error = fetch_jobs(search_term)
            if error:
                st.error(error)
            elif not df.empty:
                st.session_state.jobs_df = clean_jobs_data(df)
                st.dataframe(st.session_state.jobs_df)
            else:
                st.warning("No job listings found.")

# Google Trends Tab
with tab4:
    st.subheader("Google Trends")
    if st.button("Fetch Google Trends Data"):
        with st.spinner("Fetching Google Trends data..."):
            st.session_state.trends_df = fetch_google_trends(search_term)
        if not st.session_state.trends_df.empty:
            st.line_chart(st.session_state.trends_df.set_index("date")["Interest"])
        else:
            st.warning(f"No Google Trends data found for '{search_term}'.")

# Insights & Visualizations Tab
with tab5:
    st.subheader("Insights & Visualizations")
    if st.button("Generate Insights"):
        # Udemy Insights
        if not st.session_state.udemy_df.empty:
            if "price" in st.session_state.udemy_df.columns:
                # Clean and process the price column
                if "price" in st.session_state.udemy_df.columns:
                    st.session_state.udemy_df["price"] = (
                        st.session_state.udemy_df["price"]
                        .astype(str)  # Convert all values to string
                        .str.extract(r"(\d+\.?\d*)")  # Extract numeric part
                        .astype(float, errors="ignore")  # Convert to float
                    )
                else:
                    st.warning("The 'price' column is missing in the dataset.")
                st.write("### Udemy Courses Price Analysis")
                st.bar_chart(st.session_state.udemy_df["price"])
                avg_price = st.session_state.udemy_df["price"].mean()
                st.write(f"**Average Udemy Course Price:** ${avg_price:.2f}")
            else:
                st.warning("Price data is not available in Udemy courses.")
        else:
            st.warning("No Udemy data available. Please fetch Udemy courses first.")

        # Google Trends Insights
        if not st.session_state.trends_df.empty:
            st.write("### Google Trends Interest Over Time")
            st.line_chart(st.session_state.trends_df.set_index("date")["Interest"])
        else:
            st.warning("No Google Trends data available. Please fetch Google Trends data first.")

        # Job Salary Insights
        if not st.session_state.jobs_df.empty:
            st.write("### Job Listings Estimated Salary Distribution")
            job_salaries = [
                int(sal.split("-")[0].replace("$", "").replace(",", "")) 
                for sal in st.session_state.jobs_df["Estimated Salary"] 
                if sal != "Not Specified"
            ]
            if job_salaries:
                fig, ax = plt.subplots()
                ax.hist(job_salaries, bins=10, color="skyblue", edgecolor="black")
                ax.set_title("Estimated Salary Distribution")
                ax.set_xlabel("Salary ($)")
                ax.set_ylabel("Frequency")
                st.pyplot(fig)
            else:
                st.warning("No valid salary data available for visualization.")
        else:
            st.warning("No job data available. Please fetch job listings first.")

        # Combined Insights
        if not st.session_state.udemy_df.empty and not st.session_state.jobs_df.empty:
            st.write("### Combined Insights")
            avg_salary = sum(job_salaries) / len(job_salaries) if job_salaries else 0
            st.write(f"**Average Estimated Job Salary:** ${avg_salary:,.2f}")
        if not st.session_state.coursera_df.empty:
            st.write("### Coursera Courses Summary")
            st.write(f"**Total Courses Found:** {len(st.session_state.coursera_df)}")
        else:
            st.warning("No Coursera data available. Please fetch Coursera courses first.")
