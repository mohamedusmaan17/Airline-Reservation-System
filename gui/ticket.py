from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from tkinter import messagebox
from database.db import connect_db


class TicketGenerator:

    def __init__(self, booking_id):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            b.booking_id,
            CONCAT(p.first_name,' ',p.last_name),
            f.flight_number,
            b.seat_number,
            b.booking_date,
            b.booking_status,
            p.passport_number,
            p.email
        FROM bookings b
        JOIN passengers p
            ON b.passenger_id = p.passenger_id
        JOIN flights f
            ON b.flight_id = f.flight_id
        WHERE b.booking_id=%s
        """, (booking_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            messagebox.showerror(
                "Error",
                "Booking not found."
            )
            return

        file_name = f"Ticket_{booking_id}.pdf"

        doc = SimpleDocTemplate(file_name)
        styles = getSampleStyleSheet()
        story = []

        story.append(
            Paragraph(
                "AIRLINE E-TICKET",
                styles["Title"]
            )
        )

        story.append(Spacer(1, 20))

        data = [
            ["Booking ID", row[0]],
            ["Passenger", row[1]],
            ["Flight Number", row[2]],
            ["Seat Number", row[3]],
            ["Booking Date", str(row[4])],
            ["Booking Status", row[5]],
            ["Passport Number", row[6]],
            ["Email", row[7]]
        ]

        table = Table(data, colWidths=[180, 250])

        table.setStyle(TableStyle([

            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (1, 0), (1, -1), colors.whitesmoke)

        ]))

        story.append(table)

        doc.build(story)

        messagebox.showinfo(
            "Success",
            f"Ticket saved as {file_name}"
        )