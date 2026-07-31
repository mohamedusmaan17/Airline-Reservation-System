import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import re
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from database.db import connect_db


class FlightWindow:

    def __init__(self, root):

        self.root = root
        self.root.title("Flight Management")
        self.root.geometry("1100x700")
        self.root.configure(bg="white")
        self.flight_id=None

        title = tk.Label(
            root,
            text="FLIGHT MANAGEMENT",
            font=("Arial", 24, "bold"),
            bg="#003366",
            fg="white",
            pady=10
        )

        title.pack(fill="x")

        form = tk.Frame(root, bg="white")
        form.pack(pady=10)

        self.airline = ttk.Combobox(form, width=30, state="readonly")
        self.source = ttk.Combobox(form, width=30, state="readonly")
        self.destination = ttk.Combobox(form, width=30, state="readonly")
        self.flight_no = tk.Entry(form,width=35)

        # NEW
        self.boarding_time = tk.Entry(form, width=35)

        self.departure_time = tk.Entry(form, width=35)

        self.arrival_time = tk.Entry(form, width=35)

        self.total_seats = tk.Entry(form, width=35)

        self.ticket_price = tk.Entry(form, width=35)

        self.flight_status = ttk.Combobox(
            form,
            width=32,
            values=[
                "Scheduled",
                "Boarding",
                "Delayed",
                "Cancelled",
                "Departed",
                "Arrived"
            ],
            state="readonly"
        )

        self.gate_no = tk.Entry(form, width=35)

        self.terminal_no = tk.Entry(form, width=35)

       # ===========================
# LEFT COLUMN
# ===========================

        tk.Label(form, text="Airline", bg="white", font=("Arial",12)).grid(row=0,column=0,padx=10,pady=8,sticky="w")
        self.airline.grid(row=0,column=1,padx=10)

        tk.Label(form, text="Source Airport", bg="white", font=("Arial",12)).grid(row=1,column=0,padx=10,pady=8,sticky="w")
        self.source.grid(row=1,column=1,padx=10)

        tk.Label(form, text="Destination Airport", bg="white", font=("Arial",12)).grid(row=2,column=0,padx=10,pady=8,sticky="w")
        self.destination.grid(row=2,column=1,padx=10)

        tk.Label(form, text="Flight Number", bg="white", font=("Arial",12)).grid(row=3,column=0,padx=10,pady=8,sticky="w")
        self.flight_no.grid(row=3,column=1,padx=10)

        tk.Label(form, text="Departure Time", bg="white", font=("Arial",12)).grid(row=4,column=0,padx=10,pady=8,sticky="w")
        self.departure_time.grid(row=4,column=1,padx=10)

        tk.Label(form, text="Arrival Time", bg="white", font=("Arial",12)).grid(row=5,column=0,padx=10,pady=8,sticky="w")
        self.arrival_time.grid(row=5,column=1,padx=10)

        # ===========================
        # RIGHT COLUMN
        # ===========================

        tk.Label(form, text="Boarding Time", bg="white", font=("Arial",12)).grid(row=0,column=2,padx=40,pady=8,sticky="w")
        self.boarding_time.grid(row=0,column=3,padx=10)

        tk.Label(form, text="Flight Status", bg="white", font=("Arial",12)).grid(row=1,column=2,padx=40,pady=8,sticky="w")
        self.flight_status.grid(row=1,column=3,padx=10)

        tk.Label(form, text="Gate No", bg="white", font=("Arial",12)).grid(row=2,column=2,padx=40,pady=8,sticky="w")
        self.gate_no.grid(row=2,column=3,padx=10)

        tk.Label(form, text="Terminal No", bg="white", font=("Arial",12)).grid(row=3,column=2,padx=40,pady=8,sticky="w")
        self.terminal_no.grid(row=3,column=3,padx=10)

        tk.Label(form, text="Total Seats", bg="white", font=("Arial",12)).grid(row=4,column=2,padx=40,pady=8,sticky="w")
        self.total_seats.grid(row=4,column=3,padx=10)

        tk.Label(form, text="Ticket Price", bg="white", font=("Arial",12)).grid(row=5,column=2,padx=40,pady=8,sticky="w")
        self.ticket_price.grid(row=5,column=3,padx=10)

        self.load_airlines()
        self.load_airports()
        self.flight_status.current(0)      # Default = Scheduled
        # =====================

         # Button Frame
        # ==========================

        button_frame = tk.Frame(root, bg="white")
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Add",
            width=12,
            command=self.add_flight
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            button_frame,
            text="Update",
            width=12,
            command=self.update_flight
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            button_frame,
            text="Delete",
            width=12,
            command=self.delete_flight
        ).grid(row=0, column=2, padx=10)

        tk.Button(
            button_frame,
            text="Clear",
            width=12,
            command=self.clear_fields
        ).grid(row=0, column=3, padx=10)

        search_frame = tk.Frame(root, bg="white")
        search_frame.pack(pady=8)

        tk.Label(
            search_frame,
            text="Search:",
            bg="white",
            font=("Arial", 12)
        ).pack(side="left")

        self.search = tk.Entry(search_frame, width=40)
        self.search.pack(side="left", padx=10)

        # Placeholder text
        self.search.insert(0, "Search Flight...")
        self.search.config(fg="gray")

        # Events
        self.search.bind("<FocusIn>", self.clear_placeholder)
        self.search.bind("<FocusOut>", self.add_placeholder)
        self.search.bind("<KeyRelease>", self.live_search)
        tk.Button(
            search_frame,
            text="Search",
            command=self.search_data
        ).pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="Show All",
            command=self.show_data
        ).pack(side="left")
                # ==========================
                # Flight Table
                # ==========================

        table_frame = tk.Frame(self.root, bg="white")
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)
        scroll_x = tk.Scrollbar(table_frame, orient="horizontal")
        scroll_y = tk.Scrollbar(table_frame, orient="vertical")

        self.flight_table = ttk.Treeview(
            table_frame,
            columns=(
                "id",
                "airline",
                "source",
                "destination",
                "flight_no",
                "departure",
                "arrival",
                "boarding",
                "status",
                "gate",
                "terminal",
                "seats",
                "price"
                ),
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set
        )

        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")

        scroll_x.config(command=self.flight_table.xview)
        scroll_y.config(command=self.flight_table.yview)

        self.flight_table.heading("id", text="ID")
        self.flight_table.heading("airline", text="Airline")
        self.flight_table.heading("source", text="Source")
        self.flight_table.heading("destination", text="Destination")
        self.flight_table.heading("flight_no", text="Flight No")
        self.flight_table.heading("departure", text="Departure")
        self.flight_table.heading("arrival", text="Arrival")
        self.flight_table.heading("boarding", text="Boarding")
        self.flight_table.heading("status", text="Status")
        self.flight_table.heading("gate", text="Gate")
        self.flight_table.heading("terminal", text="Terminal")
        self.flight_table.heading("seats", text="Seats")
        self.flight_table.heading("price", text="Ticket Price")

        self.flight_table["show"] = "headings"

        self.flight_table.column("id", width=50)
        self.flight_table.column("airline", width=150)
        self.flight_table.column("source", width=150)
        self.flight_table.column("destination", width=150)
        self.flight_table.column("flight_no", width=100)
        self.flight_table.column("departure", width=150)
        self.flight_table.column("arrival", width=150)
        self.flight_table.column("boarding", width=130)
        self.flight_table.column("status", width=120)
        self.flight_table.column("gate", width=80)
        self.flight_table.column("terminal", width=90)
        self.flight_table.column("seats", width=80)
        self.flight_table.column("price", width=100)

        self.flight_table.pack(fill="both", expand=True)
        self.show_data()
        self.flight_table.bind("<ButtonRelease-1>", self.get_cursor)

    def load_airlines(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT airline_name
            FROM airlines
            ORDER BY airline_name
        """)

        rows = cursor.fetchall()

        self.airline["values"] = [
            str(row[0]) if isinstance(row, (tuple, list)) else str(next(iter(row.values())))
            for row in rows
        ]

        conn.close()
    def load_airports(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT airport_name
            FROM airports
            ORDER BY airport_name
        """)

        rows = cursor.fetchall()

        names = [
            str(row[0]) if isinstance(row, (tuple, list)) else str(next(iter(row.values())))
            for row in rows
        ]

        self.source["values"] = names
        self.destination["values"] = names

        conn.close()
    def get_cursor(self, event=""):

        cursor_row = self.flight_table.focus()

        contents = self.flight_table.item(cursor_row)

        row = contents["values"]
        print(row)
        print(len(row))

        if not row:
            return

        self.flight_id = row[0]

        self.airline.set(row[1])
        self.source.set(row[2])
        self.destination.set(row[3])

        self.flight_no.delete(0, tk.END)
        self.flight_no.insert(0, row[4])

        self.departure_time.delete(0, tk.END)
        self.departure_time.insert(0, row[5])

        self.arrival_time.delete(0, tk.END)
        self.arrival_time.insert(0, row[6])

        self.boarding_time.delete(0, tk.END)
        self.boarding_time.insert(0, row[7])

        self.flight_status.set(row[8])

        self.gate_no.delete(0, tk.END)
        self.gate_no.insert(0, row[9])

        self.terminal_no.delete(0, tk.END)
        self.terminal_no.insert(0, row[10])

        self.total_seats.delete(0, tk.END)
        self.total_seats.insert(0, row[11])

        self.ticket_price.delete(0, tk.END)
        self.ticket_price.insert(0, row[12])


    def add_flight(self):

         if self.airline.get() == "":
            messagebox.showerror("Error","Select Airline")
            return

         if self.source.get() == "":
             messagebox.showerror("Error","Select Source Airport")
             return

         if self.destination.get() == "":
             messagebox.showerror("Error","Select Destination Airport")
             return

         if self.flight_no.get() == "":
            messagebox.showerror("Error","Enter Flight Number")
            return

         if self.boarding_time.get() == "":
                messagebox.showerror("Error","Enter Boarding Time")
                return
         if self.flight_status.get() == "":
            messagebox.showerror("Error","Select Flight Status")
            return

         gate_no = self.gate_no.get().strip().upper()

         if gate_no == "":
                messagebox.showerror("Error", "Enter Gate Number")
                return

         if not re.match(r"^[A-Z]?[0-9]{1,3}$", gate_no):
                messagebox.showerror(
                    "Error",
                    "Invalid Gate Number.\nExample: A1, B12, 15"
                )
                return

         terminal_no = self.terminal_no.get().strip().upper()

         if terminal_no == "":
            messagebox.showerror("Error", "Enter Terminal Number")
            return

         if not re.match(r"^[A-Z0-9]{1,5}$", terminal_no):
            messagebox.showerror(
                "Error",
                "Invalid Terminal.\nExample: T1, T2, A"
            )
            return
         if self.departure_time.get() == "":
            messagebox.showerror("Error","Enter Departure Time")
            return

         if self.arrival_time.get() == "":
            messagebox.showerror("Error","Enter Arrival Time")
            return

         if self.total_seats.get() == "":
             messagebox.showerror("Error","Enter Total Seats")
             return
         if self.ticket_price.get() == "":
            messagebox.showerror("Error", "Enter Ticket Price")
            return

            # Validate Source and Destination
         if self.source.get() == self.destination.get():
                messagebox.showerror(
                    "Error",
                    "Source and Destination cannot be the same."
                )
                return

         conn = connect_db()
         cursor = conn.cursor()

         is_sqlite = not hasattr(conn, "is_connected") or type(conn).__module__.startswith("sqlite3")
         p = "?" if is_sqlite else "%s"

            # Get Airline ID
         cursor.execute(
            f"SELECT airline_id FROM airlines WHERE airline_name={p}",
            (self.airline.get(),)
         )
         row = cursor.fetchone()

         if row is None:
             messagebox.showerror(
                   "Error",
                    "Please select a valid airline."
            )
             conn.close()
             return

         airline_id: int = int(str(row[0] if isinstance(row, (tuple, list)) else list(row.values())[0]))

            # Get Source Airport ID
         cursor.execute(
              f"SELECT airport_id FROM airports WHERE airport_name={p}",
              (self.source.get(),)
            )
         row = cursor.fetchone()

         if row is None:
           messagebox.showerror(
               "Error",
               "Please select a valid source airport."
           )
           conn.close()
           return

         source_id: int = int(str(row[0] if isinstance(row, (tuple, list)) else list(row.values())[0]))
            # Get Destination Airport ID
         cursor.execute(
              f"SELECT airport_id FROM airports WHERE airport_name={p}",
                (self.destination.get(),)
            )
         row = cursor.fetchone()

         if row is None:
            messagebox.showerror(
                "Error",
                "Please select a valid destination airport."
            )
            conn.close()
            return

         destination_id: int = int(str(row[0] if isinstance(row, (tuple, list)) else list(row.values())[0]))
            # Get values from Entry widgets
         flight_no = self.flight_no.get().strip().upper()
         # Flight Number Format
         # Example: AI101, 6E2345, UK890

         if not re.match(r"^[A-Z]{2}[0-9]{3,4}$|^[0-9][A-Z][0-9]{3,4}$", flight_no):
                messagebox.showerror(
                    "Error",
                    "Invalid Flight Number.\nExample: AI101, 6E2345"
                )
                conn.close()
                return
         cursor.execute(
                f"SELECT * FROM flights WHERE flight_number={p}",
                (flight_no,)
            )

         if cursor.fetchone():
                messagebox.showerror(
                    "Error",
                    "Flight Number already exists."
                )
                conn.close()
                return
         boarding_time = self.boarding_time.get()
         departure_time = self.departure_time.get().strip()
         arrival_time = self.arrival_time.get().strip()
         # Validate Time Format (HH:MM)

         try:
            datetime.strptime(boarding_time, "%H:%M")
            datetime.strptime(departure_time, "%H:%M")
            datetime.strptime(arrival_time, "%H:%M")
            if boarding_time >= departure_time:
                messagebox.showerror(
                    "Error",
                    "Boarding Time must be before Departure Time."
                )
                conn.close()
                return

            if departure_time >= arrival_time:
                messagebox.showerror(
                    "Error",
                    "Departure Time must be before Arrival Time."
                )
                conn.close()
                return
            if departure_time == arrival_time:
                messagebox.showerror(
                    "Error",
                    "Departure and Arrival time cannot be the same."
                )
                conn.close()
                return

         except ValueError:
            messagebox.showerror(
                "Error",
                "Time must be in 24-hour format.\nExample: 08:30 or 17:45"
            )
            conn.close()
            return

         total_seats = self.total_seats.get().strip()
         # Seats Validation

         if not total_seats.isdigit():
                messagebox.showerror(
                    "Error",
                    "Seats must be numbers only."
                )
                conn.close()
                return

         total_seats = int(total_seats)

         if total_seats <= 0:
                messagebox.showerror(
                    "Error",
                    "Seats must be greater than 0."
                )
                conn.close()
                return

         if total_seats > 500:
                messagebox.showerror(
                    "Error",
                    "Seats cannot exceed 500."
                )
                conn.close()
                return
         ticket_price = self.ticket_price.get().strip()
         # Ticket Price Validation

         try:
            ticket_price = float(ticket_price)

            if ticket_price <= 0:
                messagebox.showerror(
                    "Error",
                    "Ticket price must be greater than 0."
                )
                conn.close()
                return

            if ticket_price > 100000:
                messagebox.showerror(
                    "Error",
                    "Ticket price is too high."
                )
                conn.close()
                return

         except ValueError:
            messagebox.showerror(
                "Error",
                "Ticket price must be numeric."
            )
            conn.close()
            return

         sql = f"""
           INSERT INTO flights
            (
            airline_id,
            source_airport,
            destination_airport,
            flight_number,
            departure_time,
            arrival_time,
            boarding_time,
            total_seats,
            available_seats,
            ticket_price,
            flight_status,
            gate_no,
            terminal_no
            )

            VALUES
            ({p},{p},{p},{p},{p},{p},{p},{p},{p},{p},{p},{p},{p})
            """

         cursor.execute(sql,(
            airline_id,
            source_id,
            destination_id,
            flight_no,
            departure_time,
            arrival_time,
            boarding_time,
            total_seats,
            total_seats,
            ticket_price,
            self.flight_status.get(),
            gate_no,
            terminal_no
        ))
         try:
            conn.commit()

            self.show_data()
            self.clear_fields()

            messagebox.showinfo(
                "Success",
                "Flight Added Successfully!"
            )

         except Exception as e:
            conn.rollback()          # Undo incomplete transaction
            messagebox.showerror(
                "Database Error",
                str(e)
            )

         finally:
            conn.close()

    def clear_fields(self):

            self.airline.set("")
            self.source.set("")
            self.destination.set("")

            self.flight_no.delete(0, tk.END)
            self.departure_time.delete(0, tk.END)
            self.arrival_time.delete(0, tk.END)
            self.boarding_time.delete(0, tk.END)

            self.flight_status.current(0)
            self.gate_no.delete(0, tk.END)
            self.terminal_no.delete(0, tk.END)
            self.total_seats.delete(0, tk.END)
            self.ticket_price.delete(0, tk.END)

            self.flight_id = None
    def update_flight(self):

        if self.flight_id is None:
            messagebox.showerror(
                "Error",
                "Please select a flight."
            )
            return
        flight_id = self.flight_id

        if self.source.get() == self.destination.get():
            messagebox.showerror(
                "Error",
                "Source and Destination cannot be the same."
            )
            return

        conn = connect_db()
        cursor = conn.cursor()

        is_sqlite = not hasattr(conn, "is_connected") or type(conn).__module__.startswith("sqlite3")
        p = "?" if is_sqlite else "%s"

        # Airline ID
        cursor.execute(
            f"SELECT airline_id FROM airlines WHERE airline_name={p}",
            (self.airline.get(),)
        )
        row = cursor.fetchone()
        if row is None:
            messagebox.showerror("Error", "Please select a valid airline.")
            conn.close()
            return
        airline_id: int = int(str(row[0] if isinstance(row, (tuple, list)) else list(row.values())[0]))

        # Source Airport ID
        cursor.execute(
            f"SELECT airport_id FROM airports WHERE airport_name={p}",
            (self.source.get(),)
        )
        row = cursor.fetchone()
        if row is None:
            messagebox.showerror("Error", "Please select a valid source airport.")
            conn.close()
            return
        source_id: int = int(str(row[0] if isinstance(row, (tuple, list)) else list(row.values())[0]))

        # Destination Airport ID
        cursor.execute(
            f"SELECT airport_id FROM airports WHERE airport_name={p}",
            (self.destination.get(),)
        )
        row = cursor.fetchone()
        if row is None:
            messagebox.showerror("Error", "Please select a valid destination airport.")
            conn.close()
            return
        destination_id: int = int(str(row[0] if isinstance(row, (tuple, list)) else list(row.values())[0]))

        total_seats_val = int(self.total_seats.get()) if self.total_seats.get().isdigit() else 0
        try:
            ticket_price_val = float(self.ticket_price.get())
        except ValueError:
            ticket_price_val = 0.0

        cursor.execute(f"""
            UPDATE flights
            SET
                airline_id={p},
                source_airport={p},
                destination_airport={p},
                flight_number={p},
                departure_time={p},
                arrival_time={p},
                boarding_time={p},
                flight_status={p},
                gate_no={p},
                terminal_no={p},
                total_seats={p},
                available_seats={p},
                ticket_price={p}
            WHERE flight_id={p}
        """,(
            airline_id,
            source_id,
            destination_id,
            self.flight_no.get(),
            self.departure_time.get(),
            self.arrival_time.get(),
            self.boarding_time.get(),
            self.flight_status.get(),
            self.gate_no.get(),
            self.terminal_no.get(),
            total_seats_val,
            total_seats_val,
            ticket_price_val,
            flight_id
        ))

        conn.commit()

        conn.close()

        self.show_data()

        self.clear_fields()

        self.flight_id = None

        messagebox.showinfo(
            "Success",
            "Flight Updated Successfully!"
        )
    def delete_flight(self):

        if self.flight_id is None:
            messagebox.showerror(
                "Error",
                "Please select a flight."
            )
            return

        confirm = messagebox.askyesno(
            "Delete",
            "Do you really want to delete this flight?"
        )

        if not confirm:
            return

        conn = connect_db()
        cursor = conn.cursor()

        is_sqlite = not hasattr(conn, "is_connected") or type(conn).__module__.startswith("sqlite3")
        p = "?" if is_sqlite else "%s"

        cursor.execute(
            f"DELETE FROM flights WHERE flight_id={p}",
            (self.flight_id,)
        )

        conn.commit()

        conn.close()

        self.show_data()

        self.clear_fields()

        self.flight_id = None

        messagebox.showinfo(
            "Success",
            "Flight Deleted Successfully!"
     )
    def show_data(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
          SELECT
                f.flight_id,
                a.airline_name,
                ap1.airport_name,
                ap2.airport_name,
                f.flight_number,
                f.departure_time,
                f.arrival_time,
                f.boarding_time,
                f.flight_status,
                f.gate_no,
                f.terminal_no,
                f.total_seats,
                f.ticket_price
            FROM flights f
            JOIN airlines a
            ON f.airline_id=a.airline_id
            JOIN airports ap1
            ON f.source_airport=ap1.airport_id
            JOIN airports ap2
            ON f.destination_airport=ap2.airport_id
            ORDER BY f.flight_id
        """)

        rows = cursor.fetchall()

        self.flight_table.delete(*self.flight_table.get_children())

        for row in rows:
            val_tuple = tuple(row) if isinstance(row, (tuple, list)) else tuple(row.values())
            self.flight_table.insert("", tk.END, values=val_tuple)

        conn.close()
    def search_data(self):

        keyword = self.search.get().strip()

        # Show all records if search box is empty
        if keyword == "" or keyword == "Search Flight...":
            self.show_data()
            return

        conn = connect_db()
        cursor = conn.cursor()

        is_sqlite = not hasattr(conn, "is_connected") or type(conn).__module__.startswith("sqlite3")
        p = "?" if is_sqlite else "%s"
        cast_type = "TEXT" if is_sqlite else "CHAR"

        search = "%" + keyword + "%"

        cursor.execute(f"""
            SELECT
                f.flight_id,
                a.airline_name,
                ap1.airport_name,
                ap2.airport_name,
                f.flight_number,
                f.departure_time,
                f.arrival_time,
                f.boarding_time,
                f.flight_status,
                f.gate_no,
                f.terminal_no,
                f.total_seats,
                f.ticket_price
            FROM flights f
            JOIN airlines a
                ON f.airline_id = a.airline_id
            JOIN airports ap1
                ON f.source_airport = ap1.airport_id
            JOIN airports ap2
                ON f.destination_airport = ap2.airport_id
            WHERE
                LOWER(a.airline_name) LIKE LOWER({p})
                OR LOWER(ap1.airport_name) LIKE LOWER({p})
                OR LOWER(ap2.airport_name) LIKE LOWER({p})
                OR LOWER(f.flight_number) LIKE LOWER({p})
                OR CAST(f.flight_id AS {cast_type}) LIKE {p}
            ORDER BY f.flight_id
        """, (
            search,
            search,
            search,
            search,
            search
        ))

        rows = cursor.fetchall()


        self.flight_table.delete(*self.flight_table.get_children())

        for row in rows:
            val_tuple = tuple(row) if isinstance(row, (tuple, list)) else tuple(row.values())
            self.flight_table.insert("", tk.END, values=val_tuple)

        conn.close()
    def clear_placeholder(self, event):

            if self.search.get() == "Search Flight...":
                self.search.delete(0, tk.END)
                self.search.config(fg="black")


    def add_placeholder(self, event):

        if self.search.get().strip() == "":
            self.search.delete(0, tk.END)
            self.search.insert(0, "Search Flight...")
            self.search.config(fg="gray")
    def live_search(self, event):
        self.search_data()


if __name__ == "__main__":
    root = tk.Tk()
    app = FlightWindow(root)
    root.mainloop()
