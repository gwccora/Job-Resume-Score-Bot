import tkinter as tk
from tkinter import ttk, messagebox
import threading
import pandas as pd
import os
from datetime import datetime
from jobspy import scrape_jobs


# =====================================
# SCRAPE FUNCTION
# =====================================
def run_scraper():

    search_term = search_entry.get()
    results = results_entry.get()

    selected_sites = []

    if linkedin_var.get():
        selected_sites.append("linkedin")

    if indeed_var.get():
        selected_sites.append("indeed")

    if len(selected_sites) == 0:
        messagebox.showerror("Error", "Select at least one job site.")
        return

    try:
        results = int(results)
    except:
        messagebox.showerror("Error", "Results must be a number.")
        return

    scrape_button.config(state="disabled")

    def scrape_thread():

        try:

            # =====================================
            # EMPLOYMENT FILTER
            # =====================================
            employment_terms = []

            if internship_var.get():
                employment_terms.append("internship")

            if fulltime_var.get():
                employment_terms.append("full time")

            if parttime_var.get():
                employment_terms.append("part time")

            final_search = f"{search_term} remote {' '.join(employment_terms)}"

            # =====================================
            # SCRAPE JOBS
            # =====================================
            jobs = scrape_jobs(
                site_name=selected_sites,
                search_term=final_search,
                location="United States",
                results_wanted=results,
                hours_old=72,
                linkedin_fetch_description=True,
                country_indeed="USA",
                is_remote=True
            )

            total_jobs = len(jobs)

            # =====================================
            # AUTO SAVE TO SCRIPT FOLDER
            # =====================================
            script_dir = os.path.dirname(os.path.abspath(__file__))
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            file_path = os.path.join(
                script_dir,
                f"job_scrape_{timestamp}.csv"
            )

            jobs.to_csv(file_path, index=False)

            # =====================================
            # CLEAR TABLE
            # =====================================
            for row in tree.get_children():
                tree.delete(row)

            # =====================================
            # REAL PROGRESS LOOP
            # =====================================
            for i, (_, row) in enumerate(jobs.iterrows(), start=1):

                description = row.get("description", "")
                has_description = "Yes" if description and len(str(description).strip()) > 0 else "No"

                tree.insert(
                    "",
                    tk.END,
                    values=(
                        row.get("site", ""),
                        row.get("title", ""),
                        row.get("company", ""),
                        row.get("location", ""),
                        row.get("job_url", ""),
                        row.get("job_id", ""),
                        has_description
                    )
                )

                # =====================================
                # REAL PROGRESS CALCULATION
                # =====================================
                if total_jobs > 0:
                    percent = int((i / total_jobs) * 100)
                    progress_bar["value"] = percent
                    progress_label.config(
                        text=f"{i}/{total_jobs} jobs processed ({percent}%)"
                    )
                    root.update_idletasks()

            status_label.config(
                text=f"Finished. Found {total_jobs} jobs. Saved locally."
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

        scrape_button.config(state="normal")


    threading.Thread(target=scrape_thread).start()


# =====================================
# UI
# =====================================
root = tk.Tk()
root.title("Remote JobSpy Scraper (Real Progress Version)")
root.geometry("1200x720")


# INPUT
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Search Term").grid(row=0, column=0, padx=5)

search_entry = tk.Entry(input_frame, width=40)
search_entry.insert(0, "data analyst")
search_entry.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="Results").grid(row=0, column=2, padx=5)

results_entry = tk.Entry(input_frame, width=10)
results_entry.insert(0, "25")
results_entry.grid(row=0, column=3, padx=5)


# STATUS
status_label = tk.Label(root, text="Ready", fg="blue")
status_label.pack()


# SITE CHECKBOXES
site_frame = tk.Frame(root)
site_frame.pack(pady=10)

linkedin_var = tk.BooleanVar(value=True)
indeed_var = tk.BooleanVar(value=True)

tk.Checkbutton(site_frame, text="LinkedIn", variable=linkedin_var).pack(side=tk.LEFT, padx=10)
tk.Checkbutton(site_frame, text="Indeed", variable=indeed_var).pack(side=tk.LEFT, padx=10)


# EMPLOYMENT TYPE
emp_frame = tk.Frame(root)
emp_frame.pack(pady=5)

internship_var = tk.BooleanVar(value=False)
fulltime_var = tk.BooleanVar(value=True)
parttime_var = tk.BooleanVar(value=False)

tk.Checkbutton(emp_frame, text="Internship", variable=internship_var).pack(side=tk.LEFT, padx=10)
tk.Checkbutton(emp_frame, text="Full Time", variable=fulltime_var).pack(side=tk.LEFT, padx=10)
tk.Checkbutton(emp_frame, text="Part Time", variable=parttime_var).pack(side=tk.LEFT, padx=10)


# SCRAPE BUTTON
scrape_button = tk.Button(
    root,
    text="Start Scraping Remote Jobs",
    command=run_scraper,
    height=2,
    width=30
)
scrape_button.pack(pady=10)


# PROGRESS BAR
progress_bar = ttk.Progressbar(root, length=500, mode="determinate", maximum=100)
progress_bar.pack(pady=5)

progress_label = tk.Label(root, text="0/0 jobs processed (0%)")
progress_label.pack()


# TABLE
columns = (
    "Site",
    "Title",
    "Company",
    "Location",
    "Job URL",
    "Job ID",
    "Has Description"
)

tree = ttk.Treeview(
    root,
    columns=columns,
    show="headings",
    height=20
)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=170)

tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


root.mainloop()