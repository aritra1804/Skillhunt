import requests
import base64
import time
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

# Function to fetch a specific number of pages
def fetch_courses_fixed_pages(max_pages=5, output_file="udemy_courses.csv"):
    page = 1
    page_size = 100
    all_courses = []

    while page <= max_pages:
        print(f"Fetching page {page}...")
        params = {
            "search": "python",  # Use a specific term or keep it empty
            "page": page,
            "page_size": page_size,
            "price": "price-paid",  # Fetch paid courses
            "language": "en"       # Fetch English courses
        }
        response = requests.get(BASE_URL, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            courses = data.get("results", [])
            
            # Debugging: Print the first course to inspect available fields
            if courses:
                print("First course in response:")
                print(courses[0])  # Inspect fields of the first course

            # Add courses to the list
            all_courses.extend(courses)

            # Stop if no results are returned
            if not courses:
                print("No more courses found.")
                break

            page += 1
            time.sleep(1)  # Add a delay to respect rate limits
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break

    print(f"Total courses fetched: {len(all_courses)}")

    # Save to CSV
    if all_courses:
        df = pd.DataFrame(all_courses)

        # Print available columns for debugging
        print("Available columns:", df.columns.tolist())

        # Select relevant columns (adjust based on API response)
        columns_to_save = [col for col in ["id", "title", "url", "price", "rating", "num_subscribers"] if col in df.columns]
        if columns_to_save:
            df = df[columns_to_save]
            df.to_csv(output_file, index=False)
            print(f"Data saved to '{output_file}'")
        else:
            print("No relevant columns to save.")
    else:
        print("No courses fetched. CSV not created.")

# Fetch and save the data
fetch_courses_fixed_pages(max_pages=5, output_file="udemy_courses.csv")
