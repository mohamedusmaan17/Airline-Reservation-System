from tkinter import messagebox

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from database.db import connect_db


class TicketGenerator:

    def __init__(self, booking_id):

        conn = connect_db()
        cursor = conn.cursor()

        is_sqlite = not hasattr(conn, "is_connected") or type(conn).__module__.startswith("sqlite3")
        placeholder = "?" if is_sqlite else "%s"

        cursor.execute(f"""
        SELECT
            b.booking_id,
            p.first_name,
            p.last_name,
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
        WHERE b.booking_id={placeholder}
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

        passenger_name = f"{row[1] or ''} {row[2] or ''}".strip() or "N/A"

        data = [
            ["Booking ID", row[0]],
            ["Passenger", passenger_name],
            ["Flight Number", row[3]],
            ["Seat Number", row[4]],
            ["Booking Date", str(row[5])],
            ["Booking Status", row[6]],
            ["Passport Number", row[7] or "N/A"],
            ["Email", row[8] or "N/A"]
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
