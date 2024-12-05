'''
This file is responsible for web scraping data from weworkremotely website and saving it as csv.
'''
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from utils import estimate_salary

def fetch_jobs(keyword):
    base_url = f"https://weworkremotely.com/remote-jobs/search?term={keyword}"
    response = requests.get(base_url)
    if response.status_code != 200:
        return pd.DataFrame(), f"Error fetching job data: {response.status_code}"

    soup = BeautifulSoup(response.content, "html.parser")
    jobs = []
    for job in soup.find_all("li", class_="feature"):
        title = job.find("span", class_="title").text if job.find("span", "title") else "N/A"
        company = job.find("span", "company").text if job.find("span", "company") else "N/A"
        link = "https://weworkremotely.com" + job.find("a")["href"] if job.find("a") else "N/A"
        salary = estimate_salary(title)
        jobs.append({"Title": title, "Company": company, "Link": link, "Estimated Salary": salary})
    return pd.DataFrame(jobs), None

def clean_jobs_data(df):
    df["Title"] = df["Title"].str.strip()
    df["Company"] = df["Company"].str.strip()
    return df

def visualize_jobs_data(df):
    if "Estimated Salary" in df.columns:
        df["Salary Range"] = df["Estimated Salary"].str.split("-").str[0].replace("Not Specified", None).dropna()
        df["Salary Range"] = df["Salary Range"].str.replace("$", "").str.replace(",", "").astype(int)
        df["Salary Range"].plot(kind="hist", bins=10, color="orange", edgecolor="black", title="Job Salary Distribution")
        plt.xlabel("Salary ($)")
        plt.ylabel("Frequency")
        plt.show()
