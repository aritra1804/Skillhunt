import pandas as pd

# Load the scraped data
file_path = "weworkremotely_jobs.csv"

def clean_data(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    print(f"Original data shape: {df.shape}")
    
    # Drop duplicate rows
    df.drop_duplicates(inplace=True)
    print(f"After removing duplicates: {df.shape}")
    
    # Handle missing values (e.g., fill with 'Unknown' or drop rows with missing data)
    df.fillna("Unknown", inplace=True)
    
    # Standardize case for titles and companies
    df["Title"] = df["Title"].str.title()
    df["Company"] = df["Company"].str.title()
    
    # Trim whitespace
    df["Title"] = df["Title"].str.strip()
    df["Company"] = df["Company"].str.strip()
    df["Location"] = df["Location"].str.strip()
    
    # Validate and standardize location (e.g., capitalize first letter)
    df["Location"] = df["Location"].str.title()
    
    # Remove rows where all fields are "Unknown" (if applicable)
    df = df[(df != "Unknown").any(axis=1)]
    
    print(f"After cleaning: {df.shape}")
    
    # Save the cleaned data to a new CSV file
    cleaned_file_path = "cleaned_weworkremotely_jobs.csv"
    df.to_csv(cleaned_file_path, index=False)
    print(f"Cleaned data saved to {cleaned_file_path}")
    
    return df

if __name__ == "__main__":
    print("Cleaning data...")
    cleaned_data = clean_data(file_path)
    print("Preview of cleaned data:")
    print(cleaned_data.head())
