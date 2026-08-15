import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import smtplib
import tkinter as tk
from datetime import datetime
from email.message import EmailMessage
from tkinter import messagebox, ttk

import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from database.db import connect_db


class BookingWindow:

    def __init__(self, root):

        self.root = root
        self.root.title("Booking Management")
        self.root.geometry("1200x700")
        self.root.configure(bg="white")

        title = tk.Label(
            root,
            text="BOOKING MANAGEMENT",
            font=("Arial", 24, "bold"),
            bg="#003366",
            fg="white",
            pady=10
        )

        title.pack(fill="x")

        form = tk.Frame(root, bg="white")
        form.pack(pady=20)

        self.passenger = ttk.Combobox(form, width=35,state="readonly")
        self.flight = ttk.Combobox(form, width=35,state="readonly")
        self.booking_date = tk.Entry(form, width=38)
        self.booking_date.insert(
            0,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.seat_number = tk.Entry(
            form,
            width=38,
            state="readonly"
        )
        self.status = ttk.Combobox(
            form,
            width=35,
            values=["Confirmed", "Pending", "Cancelled"],
            state="readonly"
        )
        self.booking_id = None

        tk.Label(form, text="Passenger", font=("Arial",12), bg="white").grid(row=0, column=0, padx=10, pady=10)
        self.passenger.grid(row=0, column=1)

        tk.Label(form, text="Flight", font=("Arial",12), bg="white").grid(row=1, column=0, padx=10, pady=10)
        self.flight.grid(row=1, column=1)

        tk.Label(form, text="Booking Date", font=("Arial",12), bg="white").grid(row=2, column=0, padx=10, pady=10)
        self.booking_date.grid(row=2, column=1)

        tk.Label(form, text="Seat Number", font=("Arial",12), bg="white").grid(row=3, column=0, padx=10, pady=10)
        self.seat_number.grid(row=3, column=1)
        tk.Button(
            form,
            text="Select Seat",
            command=self.open_seat_selection
        ).grid(row=3, column=2, padx=10)


        tk.Label(form, text="Status", font=("Arial",12), bg="white").grid(row=4, column=0, padx=10, pady=10)
        self.status.grid(row=4, column=1)

        button_frame = tk.Frame(root, bg="white")
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="Add",
            width=12,
            command=self.add_booking
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            button_frame,
            text="Update",
            width=12,
            command=self.update_booking
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            button_frame,
            text="Delete",
            width=12,
            command=self.delete_booking
        ).grid(row=0, column=2, padx=10)

        tk.Button(
            button_frame,
            text="Clear",
            width=12,
            command=self.clear_fields
        ).grid(row=0, column=3, padx=10)

        tk.Button(
            button_frame,
            text="Generate Ticket",
            width=15,
            command=self.generate_ticket
        ).grid(row=0, column=4, padx=10)

        tk.Button(
            button_frame,
            text="Check-In",
            width=15,
            command=self.check_in
        ).grid(row=0, column=5, padx=10)

        tk.Button(
            button_frame,
            text="Boarding Pass",
            width=15,
            command=self.print_boarding_pass
        ).grid(row=0, column=6, padx=10)
        # ==========================
        # Search Frame
        # ==========================

        search_frame = tk.Frame(root, bg="white")
        search_frame.pack(pady=10)

        tk.Label(
            search_frame,
            text="Search:",
            bg="white",
            font=("Arial",12)
        ).pack(side="left")

        self.search = tk.Entry(search_frame, width=40)
        self.search.pack(side="left", padx=10)

        self.search.insert(0, "Search Booking...")
        self.search.config(fg="gray")

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

        table_frame = tk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.booking_table = ttk.Treeview(
            table_frame,
            columns=(
                "booking_id",
                "pnr",
                "passenger",
                "flight",
                "seat",
                "date",
                "status"
            ),
            show="headings"
        )
        self.booking_table.heading("booking_id", text="Booking ID")
        self.booking_table.heading("pnr", text="PNR")
        self.booking_table.heading("passenger", text="Passenger")
        self.booking_table.heading("flight", text="Flight")
        self.booking_table.heading("date", text="Booking Date")
        self.booking_table.heading("seat", text="Seat Number")
        self.booking_table.heading("status", text="Status")

        self.booking_table.column("booking_id", width=80)
        self.booking_table.column("pnr",width=150)
        self.booking_table.column("passenger", width=220)
        self.booking_table.column("flight", width=150)
        self.booking_table.column("date", width=180)
        self.booking_table.column("seat", width=120)
        self.booking_table.column("status", width=120)

        self.booking_table.pack(fill="both", expand=True)
        self.booking_table.bind(
        "<ButtonRelease-1>",
        self.get_cursor
         )
        self.load_passengers()
        self.load_flights()
        self.show_data()

    def load_passengers(self):

         conn = connect_db()
         cursor = conn.cursor()

         cursor.execute("""
                SELECT passenger_id,
                    CONCAT(first_name,' ',last_name)
                FROM passengers
                ORDER BY first_name
            """)

         rows = cursor.fetchall()

         print(rows)

         self.passenger_data = rows

         self.passenger["values"] = [
                row[1] for row in rows
         ]

         conn.close()

    def load_flights(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT flight_id,
                flight_number
            FROM flights
            ORDER BY flight_number
        """)

        rows = cursor.fetchall()
        print(rows)

        self.flight_data = rows

        self.flight["values"] = [
            row[1] for row in rows
        ]

        conn.close()

    def generate_seat(self, flight_id):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM bookings
            WHERE flight_id=%s
            AND booking_status != 'Cancelled'
        """, (flight_id,))

        count = cursor.fetchone()[0]

        conn.close()

        row = count // 6 + 1
        col = count % 6

        letters = ["A", "B", "C", "D", "E", "F"]

        return f"{row}{letters[col]}"

    def check_available_seats(self, flight_id):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT available_seats
            FROM flights
            WHERE flight_id=%s
        """, (flight_id,))

        seats = cursor.fetchone()[0]

        conn.close()

        return seats
    def generate_pnr(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM bookings
        """)

        count = cursor.fetchone()[0] + 1

        conn.close()

        year = datetime.now().year

        pnr = f"AI{year}{count:04d}"

        return pnr
    def create_ticket_pdf(
            self,
            pnr,
            passenger,
            flight,
            seat,
            date,
            status
    ):

        tickets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tickets"))
        os.makedirs(tickets_dir, exist_ok=True)

        filename = f"Ticket_{pnr}.pdf"
        file_path = os.path.join(tickets_dir, filename)
        rel_path = f"tickets/{filename}"

        c = canvas.Canvas(
            file_path,
            pagesize=letter
        )

        c.setFont("Helvetica-Bold", 18)
        c.drawString(
            180,
            750,
            "AIRLINE TICKET"
        )

        c.setFont("Helvetica", 12)
        qr_file = self.generate_qr(pnr)

        y = 680

        details = [

            f"PNR : {pnr}",
            f"Passenger : {passenger}",
            f"Flight : {flight}",
            f"Seat : {seat}",
            f"Booking Date : {date}",
            f"Status : {status}"

        ]

        for item in details:
            c.drawString(80, y, item)
            y -= 40
        c.drawImage(
            qr_file,
            400,
            500,
            width=120,
            height=120
        )
        c.save()

        # Save to database tickets table
        try:
            with open(file_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()

            conn = connect_db()
            cursor = conn.cursor()
            is_sqlite = not hasattr(conn, "is_connected") or type(conn).__module__.startswith("sqlite3")
            ph = "?" if is_sqlite else "%s"

            cursor.execute(f"SELECT booking_id FROM bookings WHERE pnr={ph}", (pnr,))
            row = cursor.fetchone()
            if row:
                b_id = row[0] if not isinstance(row, dict) else row.get("booking_id")
                cursor.execute(f"SELECT COUNT(*) FROM tickets WHERE booking_id={ph}", (b_id,))
                exists = cursor.fetchone()[0] > 0
                if exists:
                    cursor.execute(f"UPDATE tickets SET file_path={ph}, pdf_data={ph} WHERE booking_id={ph}", (rel_path, pdf_bytes, b_id))
                else:
                    cursor.execute(f"INSERT INTO tickets (booking_id, file_path, pdf_data) VALUES ({ph}, {ph}, {ph})", (b_id, rel_path, pdf_bytes))
                conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Failed to save ticket to SQL DB: {e}")

        messagebox.showinfo(
            "Ticket Generated",
            f"{filename} created successfully in tickets folder & SQL database."
        )
    def generate_qr(self, pnr):

        qr = qrcode.make(pnr)

        filename = f"{pnr}.png"

        qr.save(filename)

        return filename
    def send_ticket_email(
            self,
            receiver_email,
            pnr
    ):

        sender_email = "airline.reservation.project@gmail.com"
        app_password = "YOUR_APP_PASSWORD"

        msg = EmailMessage()

        msg["Subject"] = "Your Airline Ticket"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        msg.set_content(
            f"""
    Booking Confirmed

    PNR : {pnr}

    Thank you for booking with us.
    """
        )

        filename = f"Ticket_{pnr}.pdf"

        with open(filename, "rb") as file:
            data = file.read()

        msg.add_attachment(
            data,
            maintype="application",
            subtype="pdf",
            filename=filename
        )

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as smtp:

            smtp.login(
                sender_email,
                app_password
            )

            smtp.send_message(msg)

    def get_passenger_email(
            self,
            passenger_id
    ):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT email
            FROM passengers
            WHERE passenger_id=%s
            """,
            (passenger_id,)
        )

        email = cursor.fetchone()[0]

        conn.close()

        return email
    def generate_boarding_number(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM boarding_passes
        """)

        count = cursor.fetchone()[0] + 1

        conn.close()

        return f"BP{datetime.now().year}{count:04d}"
    def check_in(self):

        if self.booking_id is None:
            messagebox.showerror(
                "Error",
                "Please select a booking."
            )
            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM boarding_passes
            WHERE booking_id=%s
        """, (self.booking_id,))

        if cursor.fetchone():
            messagebox.showinfo(
                "Already Checked In",
                "Passenger has already completed check-in."
            )
            conn.close()
            return

        boarding_no = self.generate_boarding_number()

        cursor.execute("""
            INSERT INTO boarding_passes
            (
                booking_id,
                boarding_number,
                gate_no,
                boarding_time,
                checkin_status
            )
            VALUES
            (%s,%s,%s,%s,%s)
        """, (
            self.booking_id,
            boarding_no,
            "G12",
            datetime.now(),
            "Checked In"
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            f"Check-In Complete\nBoarding No: {boarding_no}"
        )
    def open_seat_selection(self):

        if self.flight.get() == "":
            messagebox.showerror(
                "Error",
                "Please select a flight first."
            )
            return

        flight_number = self.flight.get()

        flight_id = None

        for row in self.flight_data:
            if row[1] == flight_number:
                flight_id = row[0]
                break

        seat_window = tk.Toplevel(self.root)
        seat_window.title("Seat Selection")
        seat_window.geometry("500x500")

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT seat_number
            FROM bookings
            WHERE flight_id=%s
            AND booking_status!='Cancelled'
        """, (flight_id,))

        booked = [row[0] for row in cursor.fetchall()]

        conn.close()

        letters = ["A", "B", "C", "D", "E", "F"]

        for r in range(1, 11):
            for c in range(6):

                seat = f"{r}{letters[c]}"

                btn = tk.Button(
                    seat_window,
                    text=seat,
                    width=5,
                    command=lambda s=seat:
                    self.select_seat(s, seat_window)
                )

                btn.grid(
                    row=r,
                    column=c,
                    padx=5,
                    pady=5
                )

                if seat in booked:
                    btn.config(
                        bg="red",
                        state="disabled"
                    )
    def select_seat(self, seat, window):

        self.seat_number.config(state="normal")
        self.seat_number.delete(0, tk.END)
        self.seat_number.insert(0, seat)
        self.seat_number.config(state="readonly")

        window.destroy()

    def add_booking(self):

        passenger_name = self.passenger.get()
        flight_number = self.flight.get()
        booking_date = self.booking_date.get()
        status = self.status.get()
        pnr = self.generate_pnr()
        seat_number = self.seat_number.get()

        if seat_number == "":
            messagebox.showerror(
                "Error",
                "Please select a seat."
            )
            return

        if (
            passenger_name == ""
            or flight_number == ""
            or seat_number == ""
            or status == ""
        ):
            messagebox.showerror(
                "Error",
                "Passenger, Flight, Seat and Status are required."
            )
            return

        passenger_id = None
        for row in self.passenger_data:
            if row[1] == passenger_name:
                passenger_id = row[0]
                break

        flight_id = None
        for row in self.flight_data:
            if row[1] == flight_number:
                flight_id = row[0]
                break
        print("Selected Passenger:", passenger_name)
        print("Selected Flight:", flight_number)
        print("Passenger ID:", passenger_id)
        print("Flight ID:", flight_id)

        if flight_id is None:
            messagebox.showerror(
                "Error",
                "Please select a valid flight."
            )
            return


        conn = connect_db()
        cursor = conn.cursor()

        available = self.check_available_seats(flight_id)

        if available <= 0:
            messagebox.showerror(
                "No Seats",
                "This flight is fully booked."
            )
            conn.close()
            return

        # Check whether this seat is already booked
        cursor.execute("""
            SELECT *
            FROM bookings
            WHERE flight_id=%s
            AND seat_number=%s
            AND booking_status != 'Cancelled'
        """, (
            flight_id,
            self.seat_number.get()
        ))

        if cursor.fetchone():
            messagebox.showerror(
                "Seat Occupied",
                f"Seat {self.seat_number.get()} is already booked."
            )
            conn.close()
            return

        sql = """
        INSERT INTO bookings
        (
            passenger_id,
            flight_id,
            booking_date,
            seat_number,
            booking_status,
            pnr
        )
        VALUES
        (%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(sql, (
            passenger_id,
            flight_id,
            booking_date,
            self.seat_number.get(),
            status,
            pnr
        ))
        cursor.execute("""
            UPDATE flights
            SET available_seats = available_seats - 1
            WHERE flight_id = %s
        """, (flight_id,))

        conn.commit()
        self.create_ticket_pdf(
            pnr,
            passenger_name,
            flight_number,
            self.seat_number.get(),
            booking_date,
            status
        )
        email = self.get_passenger_email(
            passenger_id
        )

        self.send_ticket_email(
            email,
            pnr
        )
        conn.close()

        messagebox.showinfo(
            "Booking Successful",
            f"Booking Added Successfully!\n\nPNR: {pnr}"
        )


        self.clear_fields()
        self.show_data()


    def show_data(self):

        conn = connect_db()
        cursor = conn.cursor()

        sql = """
        SELECT
            b.booking_id,
            b.pnr,
            CONCAT(p.first_name,' ',p.last_name),
            f.flight_number,
            b.seat_number,
            b.booking_date,
            b.booking_status
        FROM bookings b
        JOIN passengers p
            ON b.passenger_id = p.passenger_id
        JOIN flights f
            ON b.flight_id = f.flight_id
        ORDER BY b.booking_id
        """

        cursor.execute(sql)

        rows = cursor.fetchall()

        self.booking_table.delete(
            *self.booking_table.get_children()
        )

        for row in rows:
            self.booking_table.insert(
                "",
                tk.END,
                values=row
            )

        conn.close()

    def search_data(self, event=None):

        keyword = self.search.get().strip()

        if keyword == "" or keyword == "Search Booking...":
            self.show_data()
            return

        conn = connect_db()
        cursor = conn.cursor()

        search = "%" + keyword + "%"

        cursor.execute("""
            SELECT
                b.booking_id,
                b.pnr,
                CONCAT(p.first_name,' ',p.last_name),
                f.flight_number,
                b.seat_number,
                b.booking_date,
                b.booking_status
            FROM bookings b

            JOIN passengers p
                ON b.passenger_id = p.passenger_id

            JOIN flights f
                ON b.flight_id = f.flight_id

            WHERE

                CAST(b.booking_id AS CHAR) LIKE %s
                OR CONCAT(p.first_name,' ',p.last_name) LIKE %s
                OR f.flight_number LIKE %s
                OR b.seat_number LIKE %s
                OR b.booking_status LIKE %s

            ORDER BY b.booking_id

        """, (

            search,
            search,
            search,
            search,
            search

        ))

        rows = cursor.fetchall()

        self.booking_table.delete(*self.booking_table.get_children())

        for row in rows:
            self.booking_table.insert("", tk.END, values=row)

        conn.close()
    def get_cursor(self, event):

        cursor_row = self.booking_table.focus()

        contents = self.booking_table.item(cursor_row)

        row = contents["values"]

        if not row:
            return

        self.booking_id = row[0]

        self.passenger.set(row[2])
        self.flight.set(row[3])

        self.seat_number.config(state="normal")
        self.seat_number.delete(0, tk.END)
        self.seat_number.insert(0, row[4])
        self.seat_number.config(state="readonly")

        self.booking_date.delete(0, tk.END)
        self.booking_date.insert(0, row[5])

        self.status.set(row[6])
    def update_booking(self):

        if self.booking_id is None:
            messagebox.showerror(
                "Error",
                "Please select a booking first."
            )
            return

        passenger_name = self.passenger.get()
        flight_number = self.flight.get()

        passenger_id = None
        for row in self.passenger_data:
            if row[1] == passenger_name:
                passenger_id = row[0]
                break

        flight_id = None
        for row in self.flight_data:
            if row[1] == flight_number:
                flight_id = row[0]
                break

        conn = connect_db()
        cursor = conn.cursor()

        sql = """
        UPDATE bookings
        SET
            passenger_id=%s,
            flight_id=%s,
            booking_date=%s,
            seat_number=%s,
            booking_status=%s
        WHERE booking_id=%s
        """

        cursor.execute(sql, (

            passenger_id,
            flight_id,
            self.booking_date.get(),
            self.seat_number.get(),
            self.status.get(),
            self.booking_id

        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "Booking Updated Successfully!"
        )

        self.show_data()
        self.clear_fields()
    def delete_booking(self):

        if self.booking_id is None:
            messagebox.showerror(
                "Error",
                "Please select a booking."
            )
            return

        answer = messagebox.askyesno(
            "Delete",
            "Do you want to delete this booking?"
        )

        if not answer:
            return

        conn = connect_db()
        cursor = conn.cursor()

        # Find the flight of this booking
        cursor.execute("""
            SELECT flight_id
            FROM bookings
            WHERE booking_id=%s
        """, (self.booking_id,))

        flight_id = cursor.fetchone()[0]

        # Delete booking
        # Delete ticket first
        cursor.execute("""
            DELETE FROM tickets
            WHERE booking_id=%s
        """, (self.booking_id,))

        # Then delete booking
        cursor.execute("""
            DELETE FROM bookings
            WHERE booking_id=%s
        """, (self.booking_id,))
        # Restore available seat
        cursor.execute("""
            UPDATE flights
            SET available_seats = available_seats + 1
            WHERE flight_id=%s
        """, (flight_id,))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "Booking Deleted Successfully!"
        )

        self.show_data()
        self.clear_fields()
    def clear_fields(self):

        self.passenger.set("")
        self.flight.set("")

        self.booking_date.delete(0, tk.END)
        self.booking_date.insert(
            0,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        self.seat_number.config(state="normal")
        self.seat_number.delete(0, tk.END)
        self.seat_number.config(state="readonly")
        self.status.set("")

        self.booking_id = None
    def clear_placeholder(self, event):

        if self.search.get() == "Search Booking...":
            self.search.delete(0, tk.END)
            self.search.config(fg="black")


    def add_placeholder(self, event):

        if self.search.get() == "":
            self.search.insert(0, "Search Booking...")
            self.search.config(fg="gray")

    def print_boarding_pass(self):

        if self.booking_id is None:
            messagebox.showerror(
                "Error",
                "Select a booking first."
            )
            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                bp.boarding_number,
                CONCAT(p.first_name,' ',p.last_name),
                f.flight_number,
                b.seat_number,
                b.pnr,
                bp.gate_no
            FROM boarding_passes bp
            JOIN bookings b
                ON bp.booking_id=b.booking_id
            JOIN passengers p
                ON b.passenger_id=p.passenger_id
            JOIN flights f
                ON b.flight_id=f.flight_id
            WHERE b.booking_id=%s
        """, (self.booking_id,))

        row = cursor.fetchone()

        conn.close()

        if not row:
            messagebox.showerror(
                "Error",
                "Passenger has not checked in."
            )
            return

        self.generate_boarding_pass(
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5]
        )
    def generate_boarding_pass(
            self,
            boarding_no,
            passenger,
            flight,
            seat,
            pnr,
            gate
    ):

        filename = f"Boarding_{boarding_no}.pdf"

        c = canvas.Canvas(filename)

        c.setFont("Helvetica-Bold", 20)
        c.drawString(
            180,
            800,
            "BOARDING PASS"
        )

        c.setFont("Helvetica", 12)

        y = 730

        details = [

            f"Boarding No : {boarding_no}",
            f"Passenger : {passenger}",
            f"Flight : {flight}",
            f"PNR : {pnr}",
            f"Seat : {seat}",
            f"Gate : {gate}"

        ]

        for item in details:
            c.drawString(80, y, item)
            y -= 40

        c.save()

        messagebox.showinfo(
            "Success",
            f"{filename} created successfully."
        )
    def generate_ticket(self):

        if self.booking_id is None:
            messagebox.showerror(
                "Error",
                "Please select a booking first."
            )
            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                b.pnr,
                CONCAT(p.first_name,' ',p.last_name),
                f.flight_number,
                b.seat_number,
                b.booking_date,
                b.booking_status
            FROM bookings b
            JOIN passengers p
                ON b.passenger_id = p.passenger_id
            JOIN flights f
                ON b.flight_id = f.flight_id
            WHERE b.booking_id=%s
        """, (self.booking_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return

        self.create_ticket_pdf(
            row[0],
            row[1],
            row[2],
            row[3],
            str(row[4]),
            row[5]
        )
