# SKILL HUNT

## Overview
Skill Hunt is an Enhanced Learning and Job Finder application built with Python and Streamlit. It integrates multiple data sources to help users:

1. **Discover Courses**: Search for courses on **Udemy** and **Coursera** based on a specific keyword.
2. **Job Insights**: Explore remote job listings from **We Work Remotely** with estimated salaries.
3. **Google Trends Analysis**: Analyze Google Trends data to visualize the popularity of specific keywords over time.
4. **Data Visualization**: Generate insights such as course price distributions, salary ranges, and combined data trends.

This project demonstrates the use of APIs, web scraping, data cleaning, and visualization techniques to provide actionable insights for professionals and learners.

---

## Features
- **Course Search**: Search for paid courses on Udemy and Coursera by keyword.
- **Job Listings**: Fetch remote job listings along with estimated salary ranges.
- **Google Trends**: Visualize interest trends for keywords over time.
- **Insights**: Interactive visualizations, including price distributions, salary histograms, and combined trends.

---

## Requirements

### Python Environment
Ensure you have Python installed. We recommend **Python 3.8 or higher**.

### Dependencies
Install the following Python packages:
- `streamlit`
- `requests`
- `pandas`
- `matplotlib`
- `beautifulsoup4`
- `pytrends`
- `python-dotenv`

Run the command below to install all required packages:
```bash
pip install -r requirements.txt 
```
## Installation Instructions

1. Download the project as a zip file.
2. Locate the downloaded zip file on your computer.
3. Extract it to a folder of your choice.
4. Navigate to the extracted folder in your terminal or command prompt:
```bash
cd path/to/extracted/folder
```
5. Install the required packages:
```bash
pip install -r requirements.txt 
```

## Running the Application 

1. Run the Streamlit app:
```bash
streamlit run app.py
```
2. Open the URL provided by Streamlit (usually http://localhost:8502) in your browser.

## How to Use
### Search Paramters
1. Enter a Keyword: For example, "Python" or "Java".
2. Adjust the Number of Pages: This controls how many pages of Udemy courses to fetch.


