from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Path to your ChromeDriver
driver_path = '/Users/aritra/Downloads/chromedriver-mac-x64/chromedriver'  # Update this path

# Set up Selenium WebDriver
service = Service(driver_path)
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode
driver = webdriver.Chrome(service=service, options=options)

# URL of the "New Business Courses" page
url = 'https://www.coursera.org/collections/popular-new-business-courses'

# Open the page
driver.get(url)

# Allow time for the page to load
time.sleep(5)

# Scroll to the bottom to load all courses
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(5)  # Wait for additional content to load

# Extract course elements
courses = driver.find_elements(By.CLASS_NAME, 'css-1d7t1l5')

course_data = []

for course in courses:
    try:
        title_element = course.find_element(By.CLASS_NAME, 'css-14f7bde')
        title = title_element.text
        link = title_element.get_attribute('href')
        intro_element = course.find_element(By.CLASS_NAME, 'css-1c66n4l')
        intro = intro_element.text
        category = 'Business'  # Since we're in the Business category
        course_data.append({
            'Title': title,
            'URL': link,
            'Short Introduction': intro,
            'Category': category
        })
    except Exception as e:
        print(f"Error extracting data for a course: {e}")

# Close the driver
driver.quit()

# Save data to a DataFrame
df = pd.DataFrame(course_data)

# Save DataFrame to CSV
df.to_csv('new_business_courses.csv', index=False)
print("Data saved to 'new_business_courses.csv'.")
