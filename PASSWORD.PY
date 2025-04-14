import customtkinter as ctk
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime
import threading
import csv
import os
import tkinter as tk

# ---------------------- Email Info ---------------------- #
SENDER_EMAIL = "mailpassrezaabdi@gmail.com"
SENDER_PASSWORD = "uvho jdzv eofg xips"
RECEIVER_EMAIL = "savedpaassrezaabdi@gmail.com"

# ---------------------- Save Path ---------------------- #
SAVE_FILE_PATH = "D:/Lessons/پایانامه/LastChanges/OneDrive/passwords.txt"
CSV_EXPORT_PATH = "D:/Lessons/پایانامه/LastChanges/OneDrive/passwords_export.csv"

# ---------------------- App Setup ---------------------- #
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("🔐 Password Generator & Email Sender")
app.geometry("520x560")
app.resizable(False, False)

show_password = tk.BooleanVar(value=False)

# ---------------------- Save to File ---------------------- #
def save_to_file(topic, password):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SAVE_FILE_PATH, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] Topic: {topic} - Password: {password}\n")

# ---------------------- Password Strength ---------------------- #
def password_strength(password):
    length = len(password) >= 12
    digits = any(c.isdigit() for c in password)
    symbols = any(c in '@#' for c in password)
    upper = any(c.isupper() for c in password)
    lower = any(c.islower() for c in password)
    score = sum([length, digits, symbols, upper, lower])
    if score <= 2:
        return "Weak", "red"
    elif score == 3 or score == 4:
        return "Medium", "orange"
    else:
        return "Strong", "lightgreen"

# ---------------------- Password Generator ---------------------- #
def generate_password():
    allowed_chars = '123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@#'
    password = ''.join(random.choice(allowed_chars) for _ in range(16))
    password_entry.delete(0, 'end')
    password_entry.insert(0, password)
    strength, color = password_strength(password)
    strength_label.configure(text=f"Strength: {strength}", text_color=color)
    status_label.configure(text="✅ Password generated. Ready to send.", text_color="lightblue")

# ---------------------- Copy Password ---------------------- #
def copy_password():
    password = password_entry.get()
    app.clipboard_clear()
    app.clipboard_append(password)
    app.update()
    status_label.configure(text="📋 Password copied to clipboard.", text_color="lightblue")

# ---------------------- Clear Fields ---------------------- #
def clear_fields():
    topic_entry.delete(0, 'end')
    password_entry.delete(0, 'end')
    status_label.configure(text="")
    strength_label.configure(text="")

# ---------------------- Export to CSV ---------------------- #
def export_passwords():
    if not os.path.exists(SAVE_FILE_PATH):
        status_label.configure(text="❌ No saved passwords to export.", text_color="red")
        return
    with open(SAVE_FILE_PATH, "r", encoding="utf-8") as txtfile, open(CSV_EXPORT_PATH, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Timestamp", "Topic", "Password"])
        for line in txtfile:
            if line.startswith("[") and "Topic:" in line:
                timestamp = line.split("]")[0][1:]
                rest = line.split("Topic: ")[1].strip()
                topic, password = rest.split(" - Password: ")
                writer.writerow([timestamp, topic, password])
    status_label.configure(text="✅ Exported to CSV successfully.", text_color="lightgreen")

# ---------------------- Send Email (Threaded) ---------------------- #
def send_email():
    def task():
        topic = topic_entry.get().strip()
        password_to_send = password_entry.get().strip()

        if not topic:
            status_label.configure(text="⚠️ Please enter a topic.", text_color="orange")
            return

        if not password_to_send:
            status_label.configure(text="⚠️ Please generate a password first.", text_color="orange")
            return

        status_label.configure(text="📨 Sending email...", text_color="lightblue")

        try:
            msg = EmailMessage()
            msg['Subject'] = f'Password for {topic}'
            msg['From'] = SENDER_EMAIL
            msg['To'] = RECEIVER_EMAIL
            msg.set_content(f"Here is your password for {topic}:\n\n{password_to_send}")

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
                smtp.send_message(msg)

            save_to_file(topic, password_to_send)
            status_label.configure(text=f"✅ Email sent & saved for '{topic}'.", text_color="lightgreen")

        except Exception as e:
            status_label.configure(text=f"❌ Failed to send email.\n{e}", text_color="red")

    threading.Thread(target=task, daemon=True).start()

# ---------------------- UI Design ---------------------- #
frame = ctk.CTkFrame(app, corner_radius=25, fg_color=("gray75", "gray25"))
frame.pack(pady=(30, 0), padx=30, fill="both", expand=True)

title = ctk.CTkLabel(frame, text="🔐 Password Generator", font=("Helvetica", 22, "bold"), text_color="white")
title.pack(pady=(20, 10))

topic_entry = ctk.CTkEntry(frame, placeholder_text="Enter Topic (e.g. Gmail, WiFi)", width=300, height=40, corner_radius=10)
topic_entry.pack(pady=10)

password_entry = ctk.CTkEntry(frame, placeholder_text="Generated Password", width=300, height=40, corner_radius=10)
password_entry.pack(pady=10)

# Buttons row
button_row = ctk.CTkFrame(frame, fg_color="transparent")
button_row.pack(pady=5)
#ctk.CTkButton(button_row, text="👁 Show", command=toggle_password, width=90).pack(side="left", padx=5)
ctk.CTkButton(button_row, text="📋 Copy", command=copy_password, width=90).pack(side="left", padx=5)
ctk.CTkButton(button_row, text="❌ Clear", command=clear_fields, width=90).pack(side="left", padx=5)

generate_btn = ctk.CTkButton(frame, text="✨ Generate Password", command=generate_password, width=300, height=40, corner_radius=10, fg_color="#8A2BE2", hover_color="#7A2BE2")
generate_btn.pack(pady=10)

send_btn = ctk.CTkButton(frame, text="📧 Send Email", command=send_email, width=300, height=40, corner_radius=10, fg_color="#32CD32", hover_color="#2D9C2D")
send_btn.pack(pady=10)

export_btn = ctk.CTkButton(frame, text="📁 Export to CSV", command=export_passwords, width=300, height=40, corner_radius=10, fg_color="#1E90FF", hover_color="#1C7ED6")
export_btn.pack(pady=10)

strength_label = ctk.CTkLabel(frame, text="", font=("Helvetica", 12, "bold"))
strength_label.pack(pady=(5, 5))

status_label = ctk.CTkLabel(frame, text="", font=("Helvetica", 12), text_color="lightgreen", wraplength=400, justify="center")
status_label.pack(pady=(10, 10))

# ---------------------- Copyright Label ---------------------- #
copyright_label = ctk.CTkLabel(
    master=app,
    text="© 2025 Reza.M.T",
    font=("Arial", 11, "italic"),
    text_color="gray"
)
copyright_label.pack(pady=(5, 10))

# ---------------------- Start App ---------------------- #
app.mainloop()
