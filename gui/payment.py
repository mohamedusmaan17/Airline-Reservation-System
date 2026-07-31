import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from database.db import connect_db


class PaymentWindow:

    def __init__(self, root):

        self.root = root
        self.root.title("Payment Management")
        self.root.geometry("1400x850")
        self.root.configure(bg="white")

        self.payment_id = None

        # ==========================
        # TITLE
        # ==========================

        title = tk.Label(
            root,
            text="PAYMENT MANAGEMENT",
            font=("Arial", 24, "bold"),
            bg="#003366",
            fg="white",
            pady=10
        )

        title.pack(fill="x")

        # ==========================
        # FORM FRAME
        # ==========================

        form = tk.Frame(root, bg="white")
        form.pack(pady=20)

        # Widgets

        self.booking = ttk.Combobox(form, width=35)

        self.amount = tk.Entry(form, width=38)

        self.payment_method = ttk.Combobox(
            form,
            width=35,
            state="readonly",
            values=[
                "UPI",
                "CREDIT_CARD",
                "DEBIT_CARD",
                "CASH",
                "NETBANKING"
            ]
        )

        self.payment_date = tk.Entry(form, width=38)

        self.payment_status = ttk.Combobox(
            form,
            width=35,
            state="readonly",
          values=[
            "Success",
            "Failed",
            "Pending"
        ]
        )

        self.payment_date.insert(
            0,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.load_bookings()
        # Labels

        tk.Label(form, text="Booking", bg="white", font=("Arial",12)).grid(row=0,column=0,padx=10,pady=10)
        self.booking.grid(row=0,column=1)

        tk.Label(form, text="Amount", bg="white", font=("Arial",12)).grid(row=1,column=0,padx=10,pady=10)
        self.amount.grid(row=1,column=1)

        tk.Label(form, text="Payment Method", bg="white", font=("Arial",12)).grid(row=2,column=0,padx=10,pady=10)
        self.payment_method.grid(row=2,column=1)

        tk.Label(form, text="Payment Date", bg="white", font=("Arial",12)).grid(row=3,column=0,padx=10,pady=10)
        self.payment_date.grid(row=3,column=1)

        tk.Label(form, text="Status", bg="white", font=("Arial",12)).grid(row=4,column=0,padx=10,pady=10)
        self.payment_status.grid(row=4,column=1)

        button_frame = tk.Frame(root, bg="white")
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="Add",
            width=12,
            command=self.add_payment
        ).grid(row=0,column=0,padx=10)

        tk.Button(
            button_frame,
            text="Update",
            width=12,
            command=self.update_payment
        ).grid(row=0,column=1,padx=10)

        tk.Button(
            button_frame,
            text="Delete",
            width=12,
            command=self.delete_payment
        ).grid(row=0,column=2,padx=10)

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

        # Placeholder text
        self.search.insert(0, "Search Payment...")
        self.search.config(fg="gray")

        # Events
        self.search.bind("<FocusIn>", self.clear_placeholder)
        self.search.bind("<FocusOut>", self.add_placeholder)
        self.search.bind("<KeyRelease>", lambda event: self.search_data())
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

        table_frame = tk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.payment_table = ttk.Treeview(
        table_frame,
            columns=(
                "payment_id",
                "booking_id",
                "passenger",
                "flight",
                "amount",
                "payment_method",
                "payment_date",
                "payment_status"
            ),
        show="headings"
        )
        self.payment_table.heading("payment_id", text="Payment ID")
        self.payment_table.heading("booking_id", text="Booking ID")
        self.payment_table.heading("passenger", text="Passenger")
        self.payment_table.heading("flight", text="Flight")
        self.payment_table.heading("amount", text="Amount")
        self.payment_table.heading("payment_method", text="Method")
        self.payment_table.heading("payment_date", text="Payment Date")
        self.payment_table.heading("payment_status", text="Status")

        self.payment_table.column("payment_id", width=80, anchor="center")
        self.payment_table.column("booking_id", width=100, anchor="center")
        self.payment_table.column("passenger", width=180)
        self.payment_table.column("flight", width=90, anchor="center")
        self.payment_table.column("amount", width=100, anchor="center")
        self.payment_table.column("payment_method", width=130, anchor="center")
        self.payment_table.column("payment_date", width=170, anchor="center")
        self.payment_table.column("payment_status", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.payment_table.yview)
        self.payment_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.payment_table.pack(fill="both", expand=True, side="left")
        self.payment_table.bind(
            "<ButtonRelease-1>",
            self.get_cursor
        )
        self.show_data()

    def load_bookings(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                booking_id,
                seat_number
            FROM bookings
            ORDER BY booking_id
        """)

        rows = cursor.fetchall()

        self.booking_dict = {}

        booking_list = []

        for booking_id, seat in rows:

            display = f"Booking {booking_id} - Seat {seat}"

            booking_list.append(display)

            self.booking_dict[display] = booking_id

        self.booking["values"] = booking_list

        conn.close()
    def show_data(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                payments.payment_id,
                payments.booking_id,
                CONCAT(passengers.first_name,' ',passengers.last_name),
                flights.flight_number,
                payments.amount,
                payments.payment_method,
                payments.payment_date,
                payments.payment_status
            FROM payments
            JOIN bookings
                ON payments.booking_id = bookings.booking_id
            JOIN passengers
                ON bookings.passenger_id = passengers.passenger_id
            JOIN flights
                ON bookings.flight_id = flights.flight_id
            ORDER BY payments.payment_id
        """)

        rows = cursor.fetchall()

        self.payment_table.delete(*self.payment_table.get_children())

        for row in rows:
            self.payment_table.insert("", tk.END, values=row)

        conn.close()
    def search_data(self):

        keyword = self.search.get().strip()

        if keyword == "" or keyword == "Search Payment...":
            self.show_data()
            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                payments.payment_id,
                payments.booking_id,
                CONCAT(passengers.first_name,' ',passengers.last_name),
                flights.flight_number,
                payments.amount,
                payments.payment_method,
                payments.payment_date,
                payments.payment_status
            FROM payments
            JOIN bookings
                ON payments.booking_id = bookings.booking_id
            JOIN passengers
                ON bookings.passenger_id = passengers.passenger_id
            JOIN flights
                ON bookings.flight_id = flights.flight_id
            WHERE
                CAST(payments.payment_id AS CHAR) LIKE %s
                OR CAST(payments.booking_id AS CHAR) LIKE %s
                OR CONCAT(passengers.first_name,' ',passengers.last_name) LIKE %s
                OR flights.flight_number LIKE %s
                OR payments.payment_method LIKE %s
                OR payments.payment_status LIKE %s
            ORDER BY payments.payment_id
        """, (
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        ))

        rows = cursor.fetchall()

        self.payment_table.delete(*self.payment_table.get_children())

        for row in rows:
            self.payment_table.insert("", tk.END, values=row)

        conn.close()

    def clear_placeholder(self, event):

        if self.search.get() == "Search Payment...":
            self.search.delete(0, tk.END)
            self.search.config(fg="black")


    def add_placeholder(self, event):

        if self.search.get() == "":
            self.search.insert(0, "Search Payment...")
            self.search.config(fg="gray")
    def get_cursor(self, event):

        cursor_row = self.payment_table.focus()

        contents = self.payment_table.item(cursor_row)

        row = contents["values"]

        if len(row) == 0:
            return

        self.payment_id = row[0]

        booking_display = ""

        for key, value in self.booking_dict.items():

            if value == row[1]:

                booking_display = key

                break

        self.booking.set(booking_display)

        self.amount.delete(0, tk.END)
        self.amount.insert(0, row[4])

        self.payment_method.set(row[5])
        self.payment_date.delete(0, tk.END)
        self.payment_date.insert(0, row[6])

        self.payment_status.set(row[7])
    def add_payment(self):

        if self.booking.get() == "":
            messagebox.showerror(
                "Error",
                "Please select a booking."
            )
            return

        if self.amount.get() == "":
            messagebox.showerror(
                "Error",
                "Amount cannot be empty."
            )
            return
        if self.payment_status.get() == "":
            messagebox.showerror(
                "Error",
                "Please select Payment Status."
            )
            return

        conn = None

        try:

            conn = connect_db()

            cursor = conn.cursor()

            booking_id = self.booking_dict[self.booking.get()]

            sql = """
            INSERT INTO payments
            (
                booking_id,
                amount,
                payment_method,
                payment_date,
                payment_status
            )
            VALUES (%s,%s,%s,%s,%s)
            """

            cursor.execute(sql, (

                booking_id,

                self.amount.get(),

                self.payment_method.get(),

                self.payment_date.get(),

                self.payment_status.get()

            ))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Payment Added Successfully!"
            )

            self.show_data()

            self.clear_fields()

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:

            if conn:
                conn.close()

    def update_payment(self):

        if self.payment_id is None:

            messagebox.showerror(
                "Error",
                "Please select a payment."
            )
            return

        conn = None

        try:

            conn = connect_db()

            cursor = conn.cursor()

            booking_id = self.booking_dict[self.booking.get()]

            sql = """
            UPDATE payments
            SET
                booking_id=%s,
                amount=%s,
                payment_method=%s,
                payment_date=%s,
                payment_status=%s
            WHERE payment_id=%s
            """

            cursor.execute(sql, (

                booking_id,

                self.amount.get(),

                self.payment_method.get(),

                self.payment_date.get(),

                self.payment_status.get(),

                self.payment_id

            ))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Payment Updated Successfully!"
            )

            self.show_data()

            self.clear_fields()

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:

            if conn:
                conn.close()
    def delete_payment(self):

        if self.payment_id is None:

            messagebox.showerror(
                "Error",
                "Please select a payment."
            )
            return

        confirm = messagebox.askyesno(
            "Delete",
            "Do you really want to delete this payment?"
        )

        if not confirm:
            return

        conn = None

        try:

            conn = connect_db()

            cursor = conn.cursor()

            cursor.execute(

                "DELETE FROM payments WHERE payment_id=%s",

                (self.payment_id,)

            )

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Payment Deleted Successfully!"
            )

            self.show_data()

            self.clear_fields()

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:

            if conn:
                conn.close()
    def clear_fields(self):

        self.booking.set("")

        self.amount.delete(0, tk.END)

        self.payment_method.set("")

        self.payment_date.delete(0, tk.END)

        self.payment_date.insert(
            0,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        self.payment_status.set("")

        self.payment_id = None


if __name__ == "__main__":
    root = tk.Tk()
    PaymentWindow(root)
    root.mainloop()
