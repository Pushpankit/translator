import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from deep_translator import GoogleTranslator
from langdetect import detect
import sqlite3
import pandas as pd
from datetime import datetime

conn = sqlite3.connect("translations.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS translations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_text TEXT,
    translated_text TEXT,
    source_lang TEXT,
    target_lang TEXT,
    timestamp TEXT
)
""")

conn.commit()

LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh-CN",
    "Russian": "ru",
    "Arabic": "ar",
    "Italian": "it",
    "Portuguese": "pt"
}

def translate_text():

    text = input_box.get("1.0", tk.END).strip()

    if not text:
        messagebox.showwarning(
            "Warning",
            "Please enter some text."
        )
        return

    try:

        source_code = "auto"

        try:
            detected = detect(text)
        except:
            detected = "unknown"

        target_lang = LANGUAGES[target_var.get()]

        translated = GoogleTranslator(
            source=source_code,
            target=target_lang
        ).translate(text)

        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, translated)

        cursor.execute("""
        INSERT INTO translations(
            original_text,
            translated_text,
            source_lang,
            target_lang,
            timestamp
        )
        VALUES(?,?,?,?,?)
        """, (
            text,
            translated,
            detected,
            target_var.get(),
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ))

        conn.commit()

        status_var.set(
            f"Detected Language: {detected}"
        )

    except Exception as e:
        messagebox.showerror(
            "Translation Error",
            str(e)
        )


def clear_text():
    input_box.delete("1.0", tk.END)
    output_box.delete("1.0", tk.END)


def copy_translation():

    translated = output_box.get(
        "1.0",
        tk.END
    ).strip()

    if translated:
        root.clipboard_clear()
        root.clipboard_append(translated)

        messagebox.showinfo(
            "Copied",
            "Translation copied!"
        )


def show_history():

    history_window = tk.Toplevel(root)
    history_window.title("Translation History")
    history_window.geometry("800x400")

    tree = ttk.Treeview(
        history_window,
        columns=(
            "Original",
            "Translated",
            "Source",
            "Target",
            "Time"
        ),
        show="headings"
    )

    tree.heading("Original", text="Original")
    tree.heading("Translated", text="Translated")
    tree.heading("Source", text="Source")
    tree.heading("Target", text="Target")
    tree.heading("Time", text="Timestamp")

    tree.pack(
        fill=tk.BOTH,
        expand=True
    )

    cursor.execute("""
    SELECT original_text,
           translated_text,
           source_lang,
           target_lang,
           timestamp
    FROM translations
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)


def export_csv():

    try:

        df = pd.read_sql_query(
            "SELECT * FROM translations",
            conn
        )

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv")
            ]
        )

        if file_path:
            df.to_csv(
                file_path,
                index=False
            )

            messagebox.showinfo(
                "Success",
                "History exported!"
            )

    except Exception as e:
        messagebox.showerror(
            "Export Error",
            str(e)
        )


def show_stats():

    cursor.execute(
        "SELECT COUNT(*) FROM translations"
    )

    total = cursor.fetchone()[0]

    cursor.execute("""
    SELECT target_lang,
           COUNT(*)
    FROM translations
    GROUP BY target_lang
    ORDER BY COUNT(*) DESC
    LIMIT 1
    """)

    result = cursor.fetchone()

    if result:
        most_used = result[0]
    else:
        most_used = "N/A"

    messagebox.showinfo(
        "Statistics",
        f"Total Translations: {total}\n"
        f"Most Used Language: {most_used}"
    )


# ---------------- GUI ---------------- #

root = tk.Tk()

root.title("AI Language Translator")
root.geometry("900x650")

title = tk.Label(
    root,
    text="AI Language Translator",
    font=("Arial", 20, "bold")
)

title.pack(pady=10)

frame1 = tk.Frame(root)
frame1.pack(fill=tk.X, padx=20)

tk.Label(
    frame1,
    text="Enter Text:"
).pack(anchor="w")

input_box = tk.Text(
    frame1,
    height=8
)

input_box.pack(
    fill=tk.X,
    pady=5
)

frame2 = tk.Frame(root)
frame2.pack(
    fill=tk.X,
    padx=20,
    pady=10
)

tk.Label(
    frame2,
    text="Translate To:"
).pack(side=tk.LEFT)

target_var = tk.StringVar()
target_var.set("Hindi")

language_menu = ttk.Combobox(
    frame2,
    textvariable=target_var,
    values=list(LANGUAGES.keys()),
    state="readonly"
)

language_menu.pack(
    side=tk.LEFT,
    padx=10
)

# Buttons

frame3 = tk.Frame(root)
frame3.pack(pady=10)

tk.Button(
    frame3,
    text="Translate",
    command=translate_text,
    width=15
).grid(row=0, column=0, padx=5)

tk.Button(
    frame3,
    text="Clear",
    command=clear_text,
    width=15
).grid(row=0, column=1, padx=5)

tk.Button(
    frame3,
    text="Copy",
    command=copy_translation,
    width=15
).grid(row=0, column=2, padx=5)

tk.Button(
    frame3,
    text="History",
    command=show_history,
    width=15
).grid(row=0, column=3, padx=5)

# Output

frame4 = tk.Frame(root)
frame4.pack(
    fill=tk.BOTH,
    expand=True,
    padx=20
)

tk.Label(
    frame4,
    text="Translated Text:"
).pack(anchor="w")

output_box = tk.Text(
    frame4,
    height=8
)

output_box.pack(
    fill=tk.BOTH,
    expand=True,
    pady=5
)


frame5 = tk.Frame(root)
frame5.pack(pady=10)

tk.Button(
    frame5,
    text="Export CSV",
    command=export_csv,
    width=15
).grid(row=0, column=0, padx=5)

tk.Button(
    frame5,
    text="Statistics",
    command=show_stats,
    width=15
).grid(row=0, column=1, padx=5)

# Status Bar

status_var = tk.StringVar()
status_var.set("Ready")

status = tk.Label(
    root,
    textvariable=status_var,
    relief=tk.SUNKEN,
    anchor="w"
)

status.pack(
    side=tk.BOTTOM,
    fill=tk.X
)

root.mainloop()

conn.close()