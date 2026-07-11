from ast import keyword
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from regex import search

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
        form.pack(pady=20)

        self.airline = ttk.Combobox(form, width=30, state="readonly")
        self.source = ttk.Combobox(form, width=30, state="readonly")
        self.destination = ttk.Combobox(form, width=30, state="readonly")
        self.flight_no = tk.Entry(form,width=35)

        self.departure = tk.Entry(form,width=35)

        self.arrival = tk.Entry(form,width=35)

        self.total_seats = tk.Entry(form,width=35)

        self.ticket_price = tk.Entry(form,width=35)

        tk.Label(form, text="Airline", font=("Arial",12), bg="white").grid(row=0, column=0, padx=10, pady=10)
        self.airline.grid(row=0, column=1)

        tk.Label(form, text="Source Airport", font=("Arial",12), bg="white").grid(row=1, column=0, padx=10, pady=10)
        self.source.grid(row=1, column=1)

        tk.Label(form, text="Destination Airport", font=("Arial",12), bg="white").grid(row=2, column=0, padx=10, pady=10)
        self.destination.grid(row=2, column=1)

        tk.Label(form, text="Flight Number", font=("Arial",12), bg="white").grid(row=3, column=0, padx=10, pady=10)
        self.flight_no.grid(row=3, column=1)

        tk.Label(form, text="Departure", font=("Arial",12), bg="white").grid(row=4, column=0, padx=10, pady=10)
        self.departure.grid(row=4, column=1)

        tk.Label(form, text="Arrival", font=("Arial",12), bg="white").grid(row=5, column=0, padx=10, pady=10)
        self.arrival.grid(row=5, column=1)

        tk.Label(form, text="Total Seats", font=("Arial",12), bg="white").grid(row=6, column=0, padx=10, pady=10)
        self.total_seats.grid(row=6, column=1)

        tk.Label(form, text="Ticket Price", font=("Arial",12), bg="white").grid(row=7, column=0, padx=10, pady=10)
        self.ticket_price.grid(row=7, column=1)

        self.load_airlines()
        self.load_airports()
        # =====================
        
         # Button Frame
        # ==========================

        button_frame = tk.Frame(root, bg="white")
        button_frame.pack(pady=15)

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
        search_frame.pack(pady=5)

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
        table_frame.pack(pady=20)

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

        self.airline["values"] = [row[0] for row in rows]

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

        names = [row[0] for row in rows]

        self.source["values"] = names
        self.destination["values"] = names

        conn.close()
    def get_cursor(self, event=""):

        cursor_row = self.flight_table.focus()

        contents = self.flight_table.item(cursor_row)

        row = contents["values"]

        if not row:
            return
        
        self.flight_id = row[0]

        self.airline.set(row[1])
        self.source.set(row[2])
        self.destination.set(row[3])

        self.flight_no.delete(0, tk.END)
        self.flight_no.insert(0, row[4])

        self.departure.delete(0, tk.END)
        self.departure.insert(0, row[5])

        self.arrival.delete(0, tk.END)
        self.arrival.insert(0, row[6])

        self.total_seats.delete(0, tk.END)
        self.total_seats.insert(0, row[7])

        self.ticket_price.delete(0, tk.END)
        self.ticket_price.insert(0, row[8])

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

         if self.departure.get() == "":
             messagebox.showerror("Error","Enter Departure Time")
             return

         if self.arrival.get() == "":
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

            # Get Airline ID
         cursor.execute(
            "SELECT airline_id FROM airlines WHERE airline_name=%s",
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

         airline_id = row[0]

            # Get Source Airport ID
         cursor.execute(
              "SELECT airport_id FROM airports WHERE airport_name=%s",
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

         source_id = row[0]
            # Get Destination Airport ID
         cursor.execute(
              "SELECT airport_id FROM airports WHERE airport_name=%s",
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

         destination_id = row[0]
            # Get values from Entry widgets
         flight_no = self.flight_no.get()
         departure = self.departure.get()
         arrival = self.arrival.get()
         total_seats = self.total_seats.get()
         ticket_price = self.ticket_price.get()

         sql = """
            INSERT INTO flights
            (
                airline_id,
                source_airport,
                destination_airport,
                flight_number,
                departure_time,
                arrival_time,
                total_seats,
                available_seats,
                ticket_price
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

         cursor.execute(sql,(
                airline_id,
                source_id,
                destination_id,
                flight_no,
                departure,
                arrival,
                total_seats,
                total_seats,
                ticket_price
         ))

         conn.commit()
         self.show_data()

         messagebox.showinfo(
                "Success",
                "Flight Added Successfully!"
         )
         self.clear_fields()
         conn.close()

    def clear_fields(self):

            self.airline.set("")
            self.source.set("")
            self.destination.set("")

            self.flight_no.delete(0, tk.END)
            self.departure.delete(0, tk.END)
            self.arrival.delete(0, tk.END)
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
        if self.source.get() == self.destination.get():
            messagebox.showerror(
                "Error",
                "Source and Destination cannot be the same."
            )
            return

        conn = connect_db()
        cursor = conn.cursor()

        # Airline ID
        cursor.execute(
            "SELECT airline_id FROM airlines WHERE airline_name=%s",
            (self.airline.get(),)
        )
        airline_id = cursor.fetchone()[0]

        # Source Airport ID
        cursor.execute(
            "SELECT airport_id FROM airports WHERE airport_name=%s",
            (self.source.get(),)
        )
        source_id = cursor.fetchone()[0]

        # Destination Airport ID
        cursor.execute(
            "SELECT airport_id FROM airports WHERE airport_name=%s",
            (self.destination.get(),)
        )
        destination_id = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE flights
            SET
                airline_id=%s,
                source_airport=%s,
                destination_airport=%s,
                flight_number=%s,
                departure_time=%s,
                arrival_time=%s,
                total_seats=%s,
                available_seats=%s,
                ticket_price=%s
            WHERE flight_id=%s
        """,(
            airline_id,
            source_id,
            destination_id,
            self.flight_no.get(),
            self.departure.get(),
            self.arrival.get(),
            self.total_seats.get(),
            self.total_seats.get(),
            self.ticket_price.get(),
            self.flight_id
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

        cursor.execute(
            "DELETE FROM flights WHERE flight_id=%s",
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
                f.total_seats,
                f.ticket_price
            FROM flights f
            JOIN airlines a
                ON f.airline_id = a.airline_id
            JOIN airports ap1
                ON f.source_airport = ap1.airport_id
            JOIN airports ap2
                ON f.destination_airport = ap2.airport_id
            ORDER BY f.flight_id
        """)

        rows = cursor.fetchall()

        self.flight_table.delete(*self.flight_table.get_children())

        for row in rows:
            self.flight_table.insert("", tk.END, values=row)

        conn.close()
    def search_data(self):

        keyword = self.search.get().strip()

        # Show all records if search box is empty
        if keyword == "" or keyword == "Search Flight...":
            self.show_data()
            return

        conn = connect_db()
        cursor = conn.cursor()

        search = "%" + keyword + "%"

        cursor.execute("""
            SELECT
                f.flight_id,
                a.airline_name,
                ap1.airport_name,
                ap2.airport_name,
                f.flight_number,
                f.departure_time,
                f.arrival_time,
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
                LOWER(a.airline_name) LIKE LOWER(%s)
                OR LOWER(ap1.airport_name) LIKE LOWER(%s)
                OR LOWER(ap2.airport_name) LIKE LOWER(%s)
                OR LOWER(f.flight_number) LIKE LOWER(%s)
                OR CAST(f.flight_id AS CHAR) LIKE %s
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
            self.flight_table.insert("", tk.END, values=row)

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