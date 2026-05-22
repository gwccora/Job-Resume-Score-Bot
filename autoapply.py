import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import threading
import time
import os
import json
from dotenv import load_dotenv
from groq import Groq

# =========================
# GROQ SETUP
# =========================
load_dotenv("key.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# GLOBAL STATE
# =========================
resume_text = ""
csv_data = None
paused = False
seen_jobs = set()
results_output = []

output_file = os.path.join(os.getcwd(), "job_results_output.csv")

# =========================
# LOAD RESUME
# =========================
def load_resume():
    global resume_text

    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not path:
        return

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        resume_text = f.read()

    resume_label.config(text=f"Resume: {os.path.basename(path)}")

# =========================
# LOAD CSV
# =========================
def load_csv():
    global csv_data

    path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not path:
        return

    df = pd.read_csv(path)

    if "title" not in df.columns or "company" not in df.columns or "description" not in df.columns:
        messagebox.showerror("Error", "CSV must contain: title, company, description")
        return

    if "url" not in df.columns:
        df["url"] = ""

    csv_data = df
    csv_label.config(text=f"CSV: {os.path.basename(path)}")

# =========================
# AI EVALUATION (YOUR ORIGINAL RESTORED)
# =========================
def evaluate_job(resume, job_desc):

    prompt = f"""
You are a job matching system.

Return ONLY ONE valid JSON OBJECT (NOT a list).

Schema:
{{
  "score": number from 0 to 10,
  "reason": "one sentence explanation"
}}

SCORING RULES:
10 = perfect match
8-9 = very strong match
6-7 = good match
4-5 = partial match
2-3 = weak match
0-1 = no match

IMPORTANT:
- Return ONLY a JSON object
- DO NOT return a list
- DO NOT wrap in []

Resume:
{resume}

Job Description:
{job_desc}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()

    # =========================
    # SAFE PARSE (prevents crashes)
    # =========================
    try:
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except:
        return {"score": 0, "reason": "parse_error"}

# =========================
# SAVE CSV
# =========================
def save_progress():
    df = pd.DataFrame(results_output)
    df.to_csv(output_file, index=False)

# =========================
# PAUSE / RESUME
# =========================
def toggle_pause():
    global paused
    paused = not paused

    if paused:
        pause_button.config(text="Resume")
        status_label.config(text="Paused - saving...")
        save_progress()
    else:
        pause_button.config(text="Pause")
        status_label.config(text="Running")

# =========================
# PROCESS LOOP
# =========================
def process_loop():
    global csv_data, seen_jobs, results_output

    if resume_text == "" or csv_data is None:
        messagebox.showerror("Error", "Load resume and CSV first")
        return

    for i in range(len(csv_data)):

        while paused:
            time.sleep(1)

        row = csv_data.iloc[i]

        title = str(row["title"])
        company = str(row["company"])
        desc = str(row["description"])
        url = str(row.get("url", ""))

        job_id = f"{title}-{company}"

        if job_id in seen_jobs:
            continue

        seen_jobs.add(job_id)

        status_label.config(text=f"Processing: {title}")
        root.update_idletasks()

        result = evaluate_job(resume_text, desc)

        try:
            score = float(result.get("score", 0))
        except:
            score = 0

        reason = result.get("reason", "")

        decision = "YES" if score >= 7 else "NO"

        tree.insert("", tk.END, values=(company, title, decision, score, reason))

        results_output.append({
            "company": company,
            "title": title,
            "decision": decision,
            "score": score,
            "reason": reason,
            "url": url
        })

        progress["value"] = int((i + 1) / len(csv_data) * 100)
        progress_label.config(text=f"{i+1}/{len(csv_data)}")

        time.sleep(5)

    save_progress()
    status_label.config(text="DONE - CSV saved")

# =========================
# UI
# =========================
root = tk.Tk()
root.title("AI Job Matcher")
root.geometry("1100x700")

tk.Button(root, text="Load Resume", command=load_resume).pack(pady=5)
resume_label = tk.Label(root, text="No resume loaded")
resume_label.pack()

tk.Button(root, text="Load CSV", command=load_csv).pack(pady=5)
csv_label = tk.Label(root, text="No CSV loaded")
csv_label.pack()

tk.Button(root, text="START", command=lambda: threading.Thread(target=process_loop, daemon=True).start()).pack(pady=10)

pause_button = tk.Button(root, text="Pause", command=toggle_pause)
pause_button.pack(pady=5)

status_label = tk.Label(root, text="Ready")
status_label.pack()

progress = ttk.Progressbar(root, length=500, mode="determinate", maximum=100)
progress.pack(pady=5)

progress_label = tk.Label(root, text="0/0")
progress_label.pack()

# =========================
# TABLE
# =========================
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

columns = ("Company", "Title", "Decision", "Score", "Reason")

tree = ttk.Treeview(frame, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=180)

scroll_y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)

tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
tree.pack(fill=tk.BOTH, expand=True)

root.mainloop()