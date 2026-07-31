import tkinter as tk
from tkinter import messagebox, ttk

from database.db import connect_db


class AirlineWindow:

    def __init__(self, root):

        self.root = root
        self.root.title("Airline Management")
        self.root.geometry("1100x700")
        self.root.configure(bg="white")

        self.selected_id = None

        # ==========================
        # Title
        # ==========================

        title = tk.Label(
            root,
            text="AIRLINE MANAGEMENT",
            font=("Arial", 22, "bold"),
            bg="#003366",
            fg="white",
            pady=10
        )
        title.pack(fill="x")

        # ==========================
        # Form
        # ==========================

        form = tk.Frame(root, bg="white")
        form.pack(pady=20)

        tk.Label(form, text="Airline Name", bg="white", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)

        self.airline_name = tk.Entry(form, width=30)
        self.airline_name.grid(row=0, column=1)

        tk.Label(form, text="Airline Code", bg="white", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)

        self.airline_code = tk.Entry(form, width=30)
        self.airline_code.grid(row=1, column=1)

        tk.Label(form, text="Headquarters", bg="white", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10)

        self.headquarters = tk.Entry(form, width=30)
        self.headquarters.grid(row=2, column=1)

        tk.Label(form, text="Contact Number", bg="white", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10)

        self.contact = tk.Entry(form, width=30)
        self.contact.grid(row=3, column=1)

        # ==========================
        # Buttons
        # ==========================

        button_frame = tk.Frame(root, bg="white")
        button_frame.pack()

        tk.Button(
            button_frame,
            text="Add",
            width=12,
            command=self.add_airline
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            button_frame,
            text="Update",
            width=12,
            command=self.update_airline
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            button_frame,
            text="Delete",
            width=12,
            command=self.delete_airline
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

        self.search.insert(0, "Search Airline...")
        self.search.config(fg="gray")

        self.search.bind("<FocusIn>", self.clear_placeholder)
        self.search.bind("<FocusOut>", self.add_placeholder)

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
        # Table
        # ==========================

        table_frame = tk.Frame(root)
        table_frame.pack(pady=20)

        columns = (
            "ID",
            "Airline Name",
            "Code",
            "Headquarters",
            "Contact"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=10
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)

        self.tree.pack()

        self.tree.bind("<<TreeviewSelect>>", self.select_airline)

        self.load_airlines()

    # ==================================

    def load_airlines(self):

        self.tree.delete(*self.tree.get_children())

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM airlines
            ORDER BY airline_id
        """)

        rows = cursor.fetchall()

        for row in rows:
            self.tree.insert("", tk.END, values=row)

        conn.close()

    # ==================================

    def add_airline(self):

        name = self.airline_name.get().strip()
        code = self.airline_code.get().strip().upper()
        head = self.headquarters.get().strip()
        contact = self.contact.get().strip()

        if name == "" or code == "":
            messagebox.showerror(
                "Error",
                "Airline Name and Airline Code are required."
            )
            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO airlines
            (airline_name, airline_code, headquarters, contact_number)
            VALUES (%s,%s,%s,%s)
        """, (
            name,
            code,
            head,
            contact
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "Airline Added Successfully!"
        )

        self.clear_fields()
        self.load_airlines()

    # ==================================

    def select_airline(self, event):

        selected = self.tree.focus()

        if not selected:
            return

        values = self.tree.item(selected)["values"]

        self.selected_id = values[0]

        self.clear_fields()

        self.airline_name.insert(0, values[1])
        self.airline_code.insert(0, values[2])
        self.headquarters.insert(0, values[3])
        self.contact.insert(0, values[4])

    # ==================================

    def update_airline(self):

        if self.selected_id is None:
            messagebox.showerror(
                "Error",
                "Please select an airline."
            )
            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE airlines
            SET
                airline_name=%s,
                airline_code=%s,
                headquarters=%s,
                contact_number=%s
            WHERE airline_id=%s
        """, (
            self.airline_name.get(),
            self.airline_code.get().upper(),
            self.headquarters.get(),
            self.contact.get(),
            self.selected_id
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "Airline Updated Successfully!"
        )

        self.clear_fields()
        self.load_airlines()

    # ==================================

    def delete_airline(self):

        if self.selected_id is None:
            messagebox.showerror(
                "Error",
                "Please select an airline."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm",
            "Delete this airline?"
        )

        if not confirm:
            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM airlines
            WHERE airline_id=%s
        """, (self.selected_id,))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "Airline Deleted Successfully!"
        )

        self.clear_fields()
        self.load_airlines()

    # ==================================

    def clear_fields(self):

        self.airline_name.delete(0, tk.END)
        self.airline_code.delete(0, tk.END)
        self.headquarters.delete(0, tk.END)
        self.contact.delete(0, tk.END)

        self.selected_id = None
    def search_data(self,event=None):

        keyword = self.search.get().strip()

        if keyword == "":
            self.show_data()
            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM airlines
            WHERE
                CAST(airline_id AS CHAR) LIKE %s
                OR LOWER(airline_name) LIKE LOWER(%s)
                OR LOWER(airline_code) LIKE LOWER(%s)
                OR LOWER(headquarters) LIKE LOWER(%s)
                OR LOWER(contact_number) LIKE LOWER(%s)
            ORDER BY airline_id
        """,(
                f"%{keyword}%",
                f"%{keyword}%",
                f"%{keyword}%",
                f"%{keyword}%",
                f"%{keyword}%"
            )
        )

        rows = cursor.fetchall()

        self.tree.delete(*self.tree.get_children())

        for row in rows:
            self.tree.insert("", tk.END, values=row)
        conn.close()
    def show_data(self):
         self.load_airlines()
    def clear_placeholder(self, event):

            if self.search.get() == "Search Airline...":
                self.search.delete(0, tk.END)
                self.search.config(fg="black")


    def add_placeholder(self, event):

            if self.search.get() == "":
                self.search.insert(0, "Search Airline...")
                self.search.config(fg="gray")
