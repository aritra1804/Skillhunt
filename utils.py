'''
This file contains salary list and helps in estimating salary based on job roles scraped from weworkremotely website.
'''
SALARY_ESTIMATES = {
    "Senior": (100000, 150000),
    "Mid-Level": (70000, 100000),
    "Junior": (50000, 70000),
    "Intern": (30000, 50000),
    "Developer": (60000, 120000),
    "Designer": (50000, 100000),
    "Manager": (80000, 150000),
    "Engineer": (75000, 140000),
    "Data Scientist": (90000, 160000),
    "Analyst": (60000, 90000),
}

def estimate_salary(title):
    for keyword, (low, high) in SALARY_ESTIMATES.items():
        if keyword.lower() in title.lower():
            return f"${low:,} - ${high:,}"
    return "Not Specified"
