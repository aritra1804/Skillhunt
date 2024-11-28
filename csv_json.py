import pandas as pd

# Read the CSV file and load only the first 1,000 rows
df = pd.read_csv('kaggle_income.csv', nrows=500)

# Convert to JSON
json_data = df.to_json(orient='records')

# Save to a JSON file
with open('your_file_1000_records.json', 'w') as json_file:
    json_file.write(json_data)

print("First 1,000 records have been successfully converted to JSON.")
