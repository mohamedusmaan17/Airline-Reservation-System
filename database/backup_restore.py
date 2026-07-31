import os
import shutil
from tkinter import filedialog, messagebox

from app.config import DB_PATH


def backup_database():
    """Backup the SQLite database file or MySQL database to a user-selected destination."""
    try:
        if os.path.exists(DB_PATH):
            dest = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                title="Save Database Backup As"
            )
            if dest:
                shutil.copy2(DB_PATH, dest)
                messagebox.showinfo("Success", f"Database backup saved successfully to:\n{dest}")
        else:
            messagebox.showwarning("Warning", "Database file not found. Please initialize the database first.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to backup database: {str(e)}")


def restore_database():
    """Restore the SQLite database file from a user-selected backup file."""
    try:
        src = filedialog.askopenfilename(
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            title="Select Backup File to Restore"
        )
        if src:
            if os.path.exists(src):
                shutil.copy2(src, DB_PATH)
                messagebox.showinfo("Success", "Database restored successfully!")
            else:
                messagebox.showerror("Error", "Selected backup file does not exist.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to restore database: {str(e)}")
