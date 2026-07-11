import tkinter as tk
from tkinter import messagebox
from database.db import connect_db
from tkinter import ttk

class AirportWindow:

    def __init__(self, root):

        self.root = root

        self.root.title("Airport Management")

        self.root.geometry("1000x650")

        self.root.configure(bg="white")

        # ==========================
        # Title
        # ==========================

        title = tk.Label(

            root,

            text="AIRPORT MANAGEMENT",

            font=("Arial",22,"bold"),

            bg="#003366",

            fg="white",

            pady=10

        )

        title.pack(fill="x")

        # ==========================
        # Form Frame
        # ==========================

        form = tk.Frame(root,bg="white")

        form.pack(pady=20)

        tk.Label(form,text="Airport Name",font=("Arial",12),bg="white").grid(row=0,column=0,padx=10,pady=10)

        self.airport_name=tk.Entry(form,width=30)

        self.airport_name.grid(row=0,column=1)

        tk.Label(form,text="Airport Code",font=("Arial",12),bg="white").grid(row=1,column=0,padx=10,pady=10)

        self.airport_code=tk.Entry(form,width=30)

        self.airport_code.grid(row=1,column=1)

        tk.Label(form,text="City",font=("Arial",12),bg="white").grid(row=2,column=0,padx=10,pady=10)

        self.city=tk.Entry(form,width=30)

        self.city.grid(row=2,column=1)

        tk.Label(form,text="Country",font=("Arial",12),bg="white").grid(row=3,column=0,padx=10,pady=10)

        self.country=tk.Entry(form,width=30)

        self.country.grid(row=3,column=1)

        # ==========================
        # Buttons
        # ==========================

        button_frame=tk.Frame(root,bg="white")

        button_frame.pack()

        tk.Button(
            button_frame,
             text="Add",
             width=12,
             command=self.add_airport
            ).grid(row=0,column=0,padx=10)

        tk.Button(button_frame,text="Update",width=12).grid(row=0,column=1,padx=10)

        tk.Button(button_frame,text="Delete",width=12).grid(row=0,column=2,padx=10)

        tk.Button(
           button_frame,
           text="Clear",
           width=12,
           command=self.clear_fields
        ).grid(row=0,column=3,padx=10)

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

        # Placeholder
        self.search.insert(0, "Search Airport...")
        self.search.config(fg="gray")

        # Events
        self.search.bind("<FocusIn>", self.clear_placeholder)
        self.search.bind("<FocusOut>", self.add_placeholder)

        # Live Search
        self.search.bind("<KeyRelease>", self.search_data)
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
# Airport Table
# ==========================

        table_frame = tk.Frame(root)
        table_frame.pack(pady=20)

        self.airport_table = ttk.Treeview(
             table_frame,
             columns=("ID", "Name", "Code", "City", "Country"),
             show="headings",
             height=10
        )

        self.airport_table.heading("ID", text="ID")
        self.airport_table.heading("Name", text="Airport Name")
        self.airport_table.heading("Code", text="Airport Code")
        self.airport_table.heading("City", text="City")
        self.airport_table.heading("Country", text="Country")

        self.airport_table.column("ID", width=50)
        self.airport_table.column("Name", width=250)
        self.airport_table.column("Code", width=100)
        self.airport_table.column("City", width=150)
        self.airport_table.column("Country", width=150)

        self.airport_table.pack()
        self.selected_airport_id = None
        self.airport_table.bind(
            "<<TreeviewSelect>>",
             self.get_selected_row
        )
        self.load_airports()
    def add_airport(self):

        airport_name = self.airport_name.get().strip().title()
        airport_code = self.airport_code.get().strip().upper()
        city = self.city.get().strip().title()
        country = self.country.get().strip().title()

    # Validation
        if airport_name == "" or airport_code == "":
            messagebox.showerror(
              "Error",
              "Airport Name and Airport Code are required."
        )
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            sql = """
            INSERT INTO airports
            (airport_name, airport_code, city, country)
            VALUES (%s, %s, %s, %s)
            """

            cursor.execute(sql, (
               airport_name,
               airport_code,
               city,
               country
            ))

            conn.commit()
            self.load_airports()

            messagebox.showinfo(
               "Success",
               "Airport Added Successfully!"
            )

            self.clear_fields()

        except Exception as e:
          messagebox.showerror(
            "Database Error",
            str(e)
        )

        finally:
         conn.close()
    def clear_fields(self):

        self.airport_name.delete(0, tk.END)
        self.airport_code.delete(0, tk.END)
        self.city.delete(0, tk.END)
        self.country.delete(0, tk.END)

        self.selected_airport_id = None
    def get_selected_row(self, event):

        selected = self.airport_table.focus()

        if not selected:
           return

        values = self.airport_table.item(selected, "values")

        if values:

            self.selected_airport_id = values[0]

            self.clear_fields()

            self.airport_name.insert(0, values[1])
            self.airport_code.insert(0, values[2])
            self.city.insert(0, values[3])
            self.country.insert(0, values[4])
    def load_airports(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT airport_id,
                   airport_name,
                   airport_code,
                   city,
                   country
            FROM airports
         """)

        rows = cursor.fetchall()

    # Clear existing rows
        for item in self.airport_table.get_children():
             self.airport_table.delete(item)

    # Insert new rows
        for row in rows:
            self.airport_table.insert("", tk.END, values=row)

        conn.close()
    def search_data(self, event=None):

        keyword = self.search.get().strip()

        if keyword == "" or keyword == "Search Airport...":
            self.load_airports()
            return

        conn = connect_db()
        cursor = conn.cursor()

        search = "%" + keyword + "%"

        cursor.execute("""
            SELECT
                airport_id,
                airport_name,
                airport_code,
                city,
                country
            FROM airports
            WHERE
                CAST(airport_id AS CHAR) LIKE %s
                OR LOWER(airport_name) LIKE LOWER(%s)
                OR LOWER(airport_code) LIKE LOWER(%s)
                OR LOWER(city) LIKE LOWER(%s)
                OR LOWER(country) LIKE LOWER(%s)
            ORDER BY airport_id
        """, (
            search,
            search,
            search,
            search,
            search
        ))

        rows = cursor.fetchall()

        self.airport_table.delete(*self.airport_table.get_children())

        for row in rows:
            self.airport_table.insert("", tk.END, values=row)

        conn.close()
    def show_data(self):
        self.load_airports() 
    def clear_placeholder(self, event):

        if self.search.get() == "Search Airport...":
            self.search.delete(0, tk.END)
            self.search.config(fg="black")


    def add_placeholder(self, event):

        if self.search.get() == "":
            self.search.insert(0, "Search Airport...")
            self.search.config(fg="gray")