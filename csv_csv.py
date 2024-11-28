import pandas as pd

# Attempt to load with a different encoding
try:
    df = pd.read_csv('/Users/aritra/CMU/Fall 24/DF Python/Project Code/kaggle_income.csv', encoding='latin1')
except UnicodeDecodeError:
    df = pd.read_csv('/Users/aritra/CMU/Fall 24/DF Python/Project Code/kaggle_income.csv', encoding='ISO-8859-1')

# Sample 500 random rows
random_sample = df.sample(n=500, random_state=1)  # Set random_state for reproducibility

# Save the random sample to a new CSV file
random_sample.to_csv('/Users/aritra/CMU/Fall 24/DF Python/Project Code/random_500_records.csv', index=False)

print("A random sample of 500 records has been saved to 'random_500_records.csv'.")
