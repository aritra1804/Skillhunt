import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import base64
import pandas as pd
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Udemy API Credentials
CLIENT_ID = "JfHN7pmHzxTDZ4RGe9bqcpqwhxPVmwdLFX2npJ9S"
CLIENT_SECRET = "gCYnV43f2jsbkrCDyNywUPOk20bKFnIZcKAp0sSN3rtBgR9HjvY5IC69vETJIY4sWFNGmbJHTdWgYxZUsybKxrbcu6G1T67n9QD3Do1jRle2WE9dM3UCx1RVLCVGihlQ"
UDEMY_BASE_URL = "https://www.udemy.com/api-2.0/courses/"
UDEMY_COURSE_BASE_URL = "https://www.udemy.com"

# Headers for Udemy API
encoded_credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
headers = {"Authorization": f"Basic {encoded_credentials}", "Accept": "application/json"}

# Function to fetch Udemy courses
def fetch_udemy_courses(search_term, max_pages=1):
    all_courses = []
    for page in range(1, max_pages + 1):
        params = {"search": search_term, "page": page, "page_size": 10, "price": "price-paid", "language": "en"}
        response = requests.get(UDEMY_BASE_URL, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            courses = data.get("results", [])
            if not courses:
                break
            all_courses.extend(courses)
        else:
            messagebox.showerror("Error", f"Error fetching Udemy courses: {response.status_code}")
            break
    courses_df = pd.DataFrame(all_courses)
    if not courses_df.empty and "url" in courses_df.columns:
        courses_df["url"] = UDEMY_COURSE_BASE_URL + courses_df["url"]
    return courses_df

# Function to fetch Coursera courses
def fetch_coursera_courses(search_term):
    COURSERA_API_URL = "https://api.coursera.org/api/courses.v1"
    params = {"q": "search", "query": search_term}
    response = requests.get(COURSERA_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        courses = data.get("elements", [])
        return pd.DataFrame([{"Title": course.get("name"), "Link": f"https://www.coursera.org/learn/{course.get('slug', '')}"} for course in courses])
    else:
        messagebox.showerror("Error", f"Error fetching Coursera courses: {response.status_code}")
        return pd.DataFrame()

# Function to scrape jobs from We Work Remotely
def fetch_jobs(keyword):
    base_url = f"https://weworkremotely.com/remote-jobs/search?term={keyword}"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")
    jobs = []
    for job in soup.find_all("li", class_="feature"):
        title = job.find("span", class_="title").text if job.find("span", "title") else "N/A"
        company = job.find("span", class_="company").text if job.find("span", "company") else "N/A"
        link = "https://weworkremotely.com" + job.find("a")["href"] if job.find("a") else "N/A"
        jobs.append({"Title": title, "Company": company, "Link": link})
    return pd.DataFrame(jobs)

# Function to fetch Google Trends
def fetch_google_trends(search_term):
    pytrends = TrendReq()
    pytrends.build_payload([search_term], cat=0, timeframe="today 12-m", geo="", gprop="")
    trends = pytrends.interest_over_time()
    if not trends.empty:
        trends.reset_index(inplace=True)
        trends["date"] = trends["date"].dt.strftime("%Y-%m-%d")  # Format date
        trends.rename(columns={search_term: "Interest"}, inplace=True)  # Rename column
        trends.drop(columns=["isPartial"], inplace=True)  # Drop unnecessary columns
        return trends
    else:
        messagebox.showwarning("Warning", f"No Google Trends data found for '{search_term}'")
        return pd.DataFrame()

# Function to save DataFrame to CSV
def save_to_csv(df):
    if not df.empty:
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", "File saved successfully!")
    else:
        messagebox.showwarning("Warning", "No data to save.")

# Function to display a graph in a Tkinter tab
def display_graph(tab, df, column, title, xlabel, ylabel):
    figure = plt.Figure(figsize=(6, 4), dpi=100)
    ax = figure.add_subplot(111)
    df[column].value_counts().plot(kind="bar", ax=ax, color="skyblue", edgecolor="black")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    canvas = FigureCanvasTkAgg(figure, tab)
    canvas.get_tk_widget().pack()

# Tkinter GUI
root = tk.Tk()
root.title("Enhanced Learning and Job Finder")
root.geometry("1000x700")

# Search term input
search_frame = tk.Frame(root)
search_frame.pack(pady=10)
tk.Label(search_frame, text="Search Term:").pack(side=tk.LEFT, padx=5)
search_term_entry = tk.Entry(search_frame, width=30)
search_term_entry.pack(side=tk.LEFT, padx=5)
search_term_entry.insert(0, "python")

# Tab control
tab_control = ttk.Notebook(root)
tab_control.pack(expand=1, fill="both")

# Tabs
udemy_tab = ttk.Frame(tab_control)
coursera_tab = ttk.Frame(tab_control)
jobs_tab = ttk.Frame(tab_control)
trends_tab = ttk.Frame(tab_control)
tab_control.add(udemy_tab, text="Udemy Courses")
tab_control.add(coursera_tab, text="Coursera Courses")
tab_control.add(jobs_tab, text="Jobs")
tab_control.add(trends_tab, text="Google Trends")

# Udemy Tab
def show_udemy_courses():
    search_term = search_term_entry.get()
    courses_df = fetch_udemy_courses(search_term, max_pages=3)
    if not courses_df.empty:
        table = ttk.Treeview(udemy_tab, columns=("Title", "Price", "URL"), show="headings")
        table.heading("Title", text="Title")
        table.heading("Price", text="Price")
        table.heading("URL", text="URL")
        table.pack(fill="both", expand=1)
        for _, row in courses_df.iterrows():
            table.insert("", tk.END, values=(row["title"], row["price"], row["url"]))
        save_button = tk.Button(udemy_tab, text="Save to CSV", command=lambda: save_to_csv(courses_df))
        save_button.pack(pady=5)
        display_graph(udemy_tab, courses_df, "price", "Price Distribution", "Price", "Frequency")

tk.Button(udemy_tab, text="Fetch Udemy Courses", command=show_udemy_courses).pack(pady=10)

# Coursera Tab
def show_coursera_courses():
    search_term = search_term_entry.get()
    courses_df = fetch_coursera_courses(search_term)
    if not courses_df.empty:
        table = ttk.Treeview(coursera_tab, columns=("Title", "Link"), show="headings")
        table.heading("Title", text="Title")
        table.heading("Link", text="Link")
        table.pack(fill="both", expand=1)
        for _, row in courses_df.iterrows():
            table.insert("", tk.END, values=(row["Title"], row["Link"]))
        save_button = tk.Button(coursera_tab, text="Save to CSV", command=lambda: save_to_csv(courses_df))
        save_button.pack(pady=5)

tk.Button(coursera_tab, text="Fetch Coursera Courses", command=show_coursera_courses).pack(pady=10)

# Jobs Tab
def show_jobs():
    search_term = search_term_entry.get()
    jobs_df = fetch_jobs(search_term)
    if not jobs_df.empty:
        table = ttk.Treeview(jobs_tab, columns=("Title", "Company", "Link"), show="headings")
        table.heading("Title", text="Title")
        table.heading("Company", text="Company")
        table.heading("Link", text="Link")
        table.pack(fill="both", expand=1)
        for _, row in jobs_df.iterrows():
            table.insert("", tk.END, values=(row["Title"], row["Company"], row["Link"]))
        save_button = tk.Button(jobs_tab, text="Save to CSV", command=lambda: save_to_csv(jobs_df))
        save_button.pack(pady=5)

tk.Button(jobs_tab, text="Fetch Jobs", command=show_jobs).pack(pady=10)

# Google Trends Tab
def show_trends():
    search_term = search_term_entry.get()
    trends_df = fetch_google_trends(search_term)
    if not trends_df.empty:
        figure = plt.Figure(figsize=(6, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.plot(trends_df["date"], trends_df["Interest"], marker="o", linestyle="-", color="skyblue")
        ax.set_title(f"Google Trends for '{search_term}'")
        ax.set_xlabel("Date")
        ax.set_ylabel("Interest")
        ax.tick_params(axis="x", rotation=45)
        canvas = FigureCanvasTkAgg(figure, trends_tab)
        canvas.get_tk_widget().pack()

        # Add Save to CSV button
        save_button = tk.Button(trends_tab, text="Save to CSV", command=lambda: save_to_csv(trends_df))
        save_button.pack(pady=5)

tk.Button(trends_tab, text="Fetch Google Trends", command=show_trends).pack(pady=10)

# Run the Tkinter application
root.mainloop()

