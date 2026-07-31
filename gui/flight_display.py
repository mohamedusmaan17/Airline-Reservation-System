import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import ttk

from database.db import connect_db


class FlightDisplay:

    def __init__(self, root):

        self.root = root
        self.root.title("Airport Flight Information")
        self.root.geometry("1100x600")

        title = tk.Label(
            root,
            text="✈ AIRPORT FLIGHT INFORMATION",
            font=("Arial",22,"bold"),
            bg="#003366",
            fg="white"
        )

        title.pack(fill="x")

        self.table = ttk.Treeview(
            root,
            columns=(
                "flight",
                "from",
                "to",
                "gate",
                "terminal",
                "status"
            ),
            show="headings"
        )

        headings = [
            "Flight",
            "From",
            "To",
            "Gate",
            "Terminal",
            "Status"
        ]

        for col, head in zip(self.table["columns"], headings, strict=False):
            self.table.heading(col, text=head)
            self.table.column(col, width=160)

        self.table.pack(fill="both", expand=True)

        self.show_data()

        self.auto_refresh()
    def show_data(self):

        self.table.delete(*self.table.get_children())

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                f.flight_number,
                s.airport_name,
                d.airport_name,
                f.gate_no,
                f.terminal_no,
                f.flight_status
            FROM flights f
            JOIN airports s
                ON f.source_airport = s.airport_id
            JOIN airports d
                ON f.destination_airport = d.airport_id
        """)

        rows = cursor.fetchall()

        for row in rows:

            item = self.table.insert(
                "",
                tk.END,
                values=row
            )

            status = row[5]

            if status == "Boarding":
                self.table.item(item, tags=("boarding",))

            elif status == "Delayed":
                self.table.item(item, tags=("delayed",))

            elif status == "Cancelled":
                self.table.item(item, tags=("cancelled",))

            elif status == "Departed":
                self.table.item(item, tags=("departed",))

        conn.close()

        self.table.tag_configure(
            "boarding",
            background="#90EE90"
        )

        self.table.tag_configure(
            "delayed",
            background="#FFD580"
        )

        self.table.tag_configure(
            "cancelled",
            background="#FF9999"
        )

        self.table.tag_configure(
            "departed",
            background="#ADD8E6"
        )
    def auto_refresh(self):

        self.show_data()

        self.root.after(
            10000,
            self.auto_refresh
        )
