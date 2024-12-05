'''
This file is responsible for fetching udemy data through the API. It also cleans and visualizes the data.

'''
import requests
import pandas as pd
import time
import matplotlib.pyplot as plt

# Constants for Udemy API
UDEMY_BASE_URL = "https://www.udemy.com/api-2.0/courses/"
UDEMY_COURSE_BASE_URL = "https://www.udemy.com"

def fetch_udemy_courses(search_term, max_pages, headers):
    """
    Fetch courses from Udemy API.

    Args:
        search_term (str): Keyword to search for courses.
        max_pages (int): Maximum number of pages to fetch.
        headers (dict): API headers for authorization.

    Returns:
        pd.DataFrame: DataFrame containing fetched course data.
        str: Error message, if any.
    """
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
            return pd.DataFrame(), f"Error fetching Udemy courses: {response.status_code}"
        time.sleep(0.5)  # Respect API rate limits

    courses_df = pd.DataFrame(all_courses)
    if not courses_df.empty and "url" in courses_df.columns:
        courses_df["url"] = UDEMY_COURSE_BASE_URL + courses_df["url"]
    return courses_df, None

def clean_udemy_data(df):
    """
    Clean and preprocess Udemy course data.

    Args:
        df (pd.DataFrame): Raw DataFrame of Udemy courses.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    if "price" in df.columns:
        # Convert all values to strings and handle missing data
        df["price"] = df["price"].fillna("").astype(str)
        
        # Extract numeric part using regex
        df["price"] = df["price"].str.extract(r"(\d+\.?\d*)", expand=False)
        
        # Convert valid numeric strings to float; invalid entries become NaN
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
    
    return df







def save_udemy_data(df, file_name="udemy_courses.csv"):
    """
    Save cleaned Udemy data to a CSV file.

    Args:
        df (pd.DataFrame): Cleaned DataFrame of Udemy courses.
        file_name (str): File name to save the data.
    """
    if not df.empty:
        df.to_csv(file_name, index=False)
        print(f"Data saved to {file_name}")
    else:
        print("No data available to save.")

def visualize_udemy_data(df):
    """
    Visualize Udemy course data.

    Args:
        df (pd.DataFrame): Cleaned DataFrame of Udemy courses.
    """
    if "price" in df.columns:
        avg_price = df["price"].mean()
        print(f"Average Price: ${avg_price:.2f}")

        # Plot Price Distribution
        plt.figure(figsize=(8, 6))
        df["price"].plot(kind="hist", bins=10, color="skyblue", edgecolor="black", title="Price Distribution")
        plt.xlabel("Price ($)")
        plt.ylabel("Frequency")
        plt.title("Udemy Course Price Distribution")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.show()

# Example usage (to be called in the main app or during testing)
if __name__ == "__main__":
    # Replace with actual API headers
    headers = {"Authorization": "Bearer <YOUR_API_KEY>", "Accept": "application/json"}
    search_term = "python"
    max_pages = 2

    # Fetch courses
    courses_df, error = fetch_udemy_courses(search_term, max_pages, headers)
    if error:
        print(error)
    else:
        # Clean and visualize data
        cleaned_df = clean_udemy_data(courses_df)
        save_udemy_data(cleaned_df)
        visualize_udemy_data(cleaned_df)
