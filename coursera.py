import requests
import pandas as pd
import matplotlib.pyplot as plt

def fetch_coursera_courses(search_term):
    COURSERA_API_URL = "https://api.coursera.org/api/courses.v1"
    params = {"q": "search", "query": search_term}
    response = requests.get(COURSERA_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        courses = data.get("elements", [])
        df = pd.DataFrame([{"Title": course.get("name"), "Link": f"https://www.coursera.org/learn/{course.get('slug', '')}"} for course in courses])
        return df, None
    else:
        return pd.DataFrame(), f"Error fetching Coursera courses: {response.status_code}"

def clean_coursera_data(df):
    df["Title"] = df["Title"].str.strip()
    return df

def visualize_coursera_data(df):
    print(f"Total Coursera Courses: {len(df)}")
    df["Title Length"] = df["Title"].apply(len)
    df["Title Length"].plot(kind="hist", bins=10, color="green", title="Title Length Distribution")
    plt.xlabel("Title Length")
    plt.ylabel("Frequency")
    plt.show()
