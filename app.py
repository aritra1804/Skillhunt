import os
from dotenv import load_dotenv
import streamlit as st
import numpy as np
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
# Set custom page title
st.set_page_config(
    page_title="SkillHunt"
)
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
    
    # Separate search for jobs
    job_search_term = st.text_input("Enter a keyword for job search (e.g., Developer, Data Scientist):", value="developer")
    max_jobs = st.slider("Number of Results to Fetch (Jobs)", min_value=1, max_value=50, value=10)
    
    if st.button("Search Jobs"):
        with st.spinner("Fetching job listings..."):
            df, error = fetch_jobs(job_search_term)
            if error:
                st.error(error)
            elif not df.empty:
                # Limit results based on the slider value
                st.session_state.jobs_df = clean_jobs_data(df).head(max_jobs)

                # Add a numbering column
                st.session_state.jobs_df = st.session_state.jobs_df.reset_index(drop=True)
                st.session_state.jobs_df.insert(0, "S.No.", range(1, len(st.session_state.jobs_df) + 1))

                # Display without the default index
                st.dataframe(st.session_state.jobs_df.set_index("S.No."))
            else:
                st.warning("No job listings found for the entered keyword.")

# Google Trends Tab
with tab4:
    st.subheader("Google Trends")
    
    # Option to use backup data
    use_backup = st.checkbox("Use backup data if rate-limited")
    
    if st.button("Fetch Google Trends Data"):
        with st.spinner("Fetching Google Trends data..."):
            backup_file = "google_trends_backup.csv"  # Path to the backup file
            if use_backup:
                st.session_state.trends_df = fetch_google_trends(search_term, backup_file=backup_file)
            else:
                st.session_state.trends_df = fetch_google_trends(search_term)
        
        if st.session_state.trends_df is not None and not st.session_state.trends_df.empty:
            st.line_chart(st.session_state.trends_df.set_index("date")["Interest"])
        else:
            st.warning(f"No Google Trends data available for '{search_term}'.")


# Insights & Visualizations Tab
with tab5:
    st.subheader("Insights & Visualizations")
    if st.button("Generate Insights"):
        # Udemy Insights
        if st.session_state.udemy_df is not None and not st.session_state.udemy_df.empty:
            st.write("### Udemy Courses Price Analysis")
            if "price" in st.session_state.udemy_df.columns:
                st.session_state.udemy_df["price"] = (
                    st.session_state.udemy_df["price"]
                    .astype(str)  # Convert all values to string
                    .str.extract(r"(\d+\.?\d*)")  # Extract numeric part
                    .astype(float, errors="ignore")  # Convert to float
                )
                avg_price = np.mean(st.session_state.udemy_df["price"])
                st.write(f"**Average Udemy Course Price:** ${avg_price:.2f}")

                # Subplots for Udemy data
                fig, ax = plt.subplots(1, 2, figsize=(16, 6))

                # Price Distribution
                ax[0].hist(
                    st.session_state.udemy_df["price"], bins=10, color="skyblue", edgecolor="black"
                )
                ax[0].set_title("Udemy Course Price Distribution", fontsize=16)
                ax[0].set_xlabel("Price ($)", fontsize=12)
                ax[0].set_ylabel("Frequency", fontsize=12)

                # Price Boxplot
                ax[1].boxplot(st.session_state.udemy_df["price"], vert=False, patch_artist=True)
                ax[1].set_title("Udemy Course Price Boxplot", fontsize=16)
                ax[1].set_xlabel("Price ($)", fontsize=12)

                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("Price data is not available in Udemy courses.")
        else:
            st.warning("No Udemy data available. Please fetch Udemy courses first.")

        # Job Salary Insights
        if st.session_state.jobs_df is not None and not st.session_state.jobs_df.empty:
            st.write("### Job Listings Salary Analysis")
            job_salaries = [
                int(sal.split("-")[0].replace("$", "").replace(",", "")) 
                for sal in st.session_state.jobs_df["Estimated Salary"] 
                if sal != "Not Specified"
            ]
            if job_salaries:
                avg_salary = np.mean(job_salaries)
                st.write(f"**Average Estimated Job Salary:** ${avg_salary:,.2f}")

                # Subplots for Job Salaries
                fig, ax = plt.subplots(1, 2, figsize=(16, 6))

                # Salary Distribution
                ax[0].hist(job_salaries, bins=10, color="orange", edgecolor="black")
                ax[0].set_title("Job Salary Distribution", fontsize=16)
                ax[0].set_xlabel("Salary ($)", fontsize=12)
                ax[0].set_ylabel("Frequency", fontsize=12)

                # Salary Boxplot
                ax[1].boxplot(job_salaries, vert=False, patch_artist=True)
                ax[1].set_title("Job Salary Boxplot", fontsize=16)
                ax[1].set_xlabel("Salary ($)", fontsize=12)

                plt.tight_layout()
                st.pyplot(fig)

                # Heatmap Example (if relevant numerical data exists)
                if "title" in st.session_state.jobs_df.columns:
                    st.write("### Job Listings Heatmap (Dummy Example)")
                    salary_counts = pd.DataFrame({
                        "Job Titles": [title[:15] for title in st.session_state.jobs_df["title"]],
                        "Salaries": job_salaries
                    }).pivot_table(index="Job Titles", values="Salaries", aggfunc="mean")

                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.heatmap(
                        salary_counts, annot=True, cmap="YlGnBu", fmt=".2f", linewidths=.5, ax=ax
                    )
                    ax.set_title("Heatmap of Average Salaries by Job Title")
                    st.pyplot(fig)

            else:
                st.warning("No valid salary data available for visualization.")
        else:
            st.warning("No job data available. Please fetch job listings first.")

        # Google Trends Insights
        if st.session_state.trends_df is not None and not st.session_state.trends_df.empty:
            st.write("### Google Trends Interest Analysis")
            trends = st.session_state.trends_df["Interest"]
            avg_interest = np.mean(trends)
            max_interest = np.max(trends)
            min_interest = np.min(trends)

            st.write(f"**Average Interest:** {avg_interest:.2f}")
            st.write(f"**Peak Interest:** {max_interest}")
            st.write(f"**Lowest Interest:** {min_interest}")

            # Line Plot for Google Trends
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(st.session_state.trends_df["date"], trends, color="orange", marker="o", linestyle="-")
            ax.set_title("Google Trends Interest Over Time", fontsize=16)
            ax.set_xlabel("Date", fontsize=12)
            ax.set_ylabel("Interest", fontsize=12)
            plt.xticks(rotation=45, fontsize=10)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("No Google Trends data available. Please fetch Google Trends data first.")

        # Combined Insights
        if (
            st.session_state.udemy_df is not None and not st.session_state.udemy_df.empty and
            st.session_state.jobs_df is not None and not st.session_state.jobs_df.empty
        ):
            st.write("### Combined Insights")
            avg_salary = np.mean(job_salaries) if job_salaries else 0
            st.write(f"**Average Estimated Job Salary:** ${avg_salary:,.2f}")
            st.write(f"**Total Courses Found (Coursera):** {len(st.session_state.coursera_df)}")
        else:
            st.warning("No combined data available. Please ensure Udemy, Coursera, Jobs, and Google Trends data are loaded.")
