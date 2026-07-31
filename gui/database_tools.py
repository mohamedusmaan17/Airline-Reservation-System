import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk

from database.backup_restore import backup_database, restore_database


class DatabaseTools:

    def __init__(self, root):

        self.root = root

        self.root.title("Database Utilities")

        self.root.geometry("450x250")

        tk.Label(
            root,
            text="DATABASE UTILITIES",
            font=("Arial",20,"bold")
        ).pack(pady=20)

        tk.Button(
            root,
            text="Backup Database",
            width=25,
            command=backup_database
        ).pack(pady=10)

        tk.Button(
            root,
            text="Restore Database",
            width=25,
            command=restore_database
        ).pack(pady=10)
