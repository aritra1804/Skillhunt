import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the We Work Remotely website
BASE_URL = "https://weworkremotely.com/remote-jobs"

# Function to fetch job data
def fetch_job_data():
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        print(f"Failed to fetch the page: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []
    
    # Find all job sections on the page
    job_sections = soup.find_all("section", {"class": "jobs"})
    for section in job_sections:
        listings = section.find_all("li", {"class": "feature"})
        for listing in listings:
            # Extract job details
            title = listing.find("span", {"class": "title"}).get_text(strip=True)
            company = listing.find("span", {"class": "company"}).get_text(strip=True)
            location = listing.find("span", {"class": "region"}).get_text(strip=True) if listing.find("span", {"class": "region"}) else "Remote"
            
            # Append the job to the list
            jobs.append({
                "Title": title,
                "Company": company,
                "Location": location
            })
    
    return jobs

# Function to save data to a CSV file
def save_to_csv(jobs, filename="weworkremotely_jobs.csv"):
    df = pd.DataFrame(jobs)
    df.to_csv(filename, index=False)
    print(f"Saved {len(jobs)} jobs to {filename}")

if __name__ == "__main__":
    print("Fetching job data from We Work Remotely...")
    job_data = fetch_job_data()
    if job_data:
        save_to_csv(job_data)
