import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tkinter as tk
from tkinter import messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database.db import connect_db


class Dashboard:

    def __init__(self, root):

        self.root = root
        self.root.title("Airline Reservation System")
        self.root.geometry("1200x780")
        self.root.configure(bg="#F0F4F8")
        self.root.resizable(True, True)

        self._build_header()
        self._build_sidebar()
        self._build_main_content()

    # ─────────────────────────────────────────────────────────
    # Layout builders
    # ─────────────────────────────────────────────────────────

    def _build_header(self):
        header = tk.Frame(self.root, bg="#003366", height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="✈  AIRLINE RESERVATION SYSTEM",
            bg="#003366", fg="white",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=20, pady=10)

        tk.Label(
            header,
            text="Admin Dashboard",
            bg="#003366", fg="#90CAF9",
            font=("Arial", 12)
        ).pack(side="right", padx=20)

    def _build_sidebar(self):
        sidebar = tk.Frame(self.root, bg="#1E3A5F", width=190)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        buttons = [
            ("🏠  Dashboard",     None),
            ("🛫  Airports",      self.open_airport),
            ("🏢  Airlines",      self.open_airline),
            ("✈   Flights",       self.open_flight),
            ("👤  Passengers",    self.open_passenger),
            ("🎫  Bookings",      self.open_booking),
            ("💳  Payments",      self.open_payment),
            ("📊  Reports",       self.open_report),
            ("🖥   Flight Display",self.open_display),
            ("💾  Database",      self.open_database_tools),
            ("🚪  Logout",        self.root.destroy),
        ]

        tk.Label(sidebar, text="", bg="#1E3A5F").pack(pady=8)

        for text, cmd in buttons:
            btn = tk.Button(
                sidebar,
                text=text,
                width=18,
                height=2,
                anchor="w",
                padx=10,
                bg="#1E3A5F" if cmd is not None else "#2A4F7C",
                fg="white",
                activebackground="#2563EB",
                activeforeground="white",
                relief="flat",
                font=("Arial", 10),
                cursor="hand2",
                command=cmd if cmd else lambda: None,
            )
            btn.pack(fill="x", padx=6, pady=2)

    def _build_main_content(self):
        # scrollable main area
        self.main = tk.Frame(self.root, bg="#F0F4F8")
        self.main.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # ── Page title
        tk.Label(
            self.main,
            text="Dashboard Overview",
            bg="#F0F4F8", fg="#1E3A5F",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(10, 0), padx=5)

        tk.Label(
            self.main,
            text="Welcome back, Admin!",
            bg="#F0F4F8", fg="#64748B",
            font=("Arial", 11)
        ).pack(anchor="w", padx=5)

        # ── Stat cards row
        cards_frame = tk.Frame(self.main, bg="#F0F4F8")
        cards_frame.pack(fill="x", pady=(18, 6))

        card_configs = [
            ("✈  Flights",      "0",  "#2563EB", "flight_card"),
            ("👤  Passengers",  "0",  "#16A34A", "passenger_card"),
            ("🎫  Bookings",    "0",  "#D97706", "booking_card"),
            ("💳  Revenue",     "₹0", "#DC2626", "revenue_card"),
            ("🏢  Airlines",    "0",  "#7C3AED", "airline_card"),
            ("📅  Today",       "0",  "#0891B2", "today_card"),
        ]

        for i, (title, val, color, attr) in enumerate(card_configs):
            frame, val_lbl = self._stat_card(cards_frame, title, val, color)
            frame.grid(row=0, column=i, padx=8, pady=4, sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)
            setattr(self, attr, val_lbl)

        # ── Chart  (fixed height — no expand so it can't push layout)
        chart_container = tk.LabelFrame(
            self.main,
            text="  Payment Status Distribution",
            bg="#F0F4F8", fg="#1E3A5F",
            font=("Arial", 11, "bold"),
            bd=1, relief="groove",
            height=320
        )
        chart_container.pack(fill="x", expand=False, pady=8, padx=5)
        chart_container.pack_propagate(False)  # keep fixed height

        self.chart_frame = tk.Frame(chart_container, bg="#F0F4F8")
        self.chart_frame.pack(fill="both", expand=True)

        # ── Load data
        self.load_dashboard_statistics()
        self.show_payment_chart()

    def _stat_card(self, parent, title, value, color):
        """Return (card_frame, value_Label) so the caller can grid the frame."""
        frame = tk.Frame(parent, bg="white", bd=0, relief="flat",
                         highlightbackground="#E2E8F0", highlightthickness=1)
        # coloured top bar
        tk.Frame(frame, bg=color, height=4).pack(fill="x")

        tk.Label(frame, text=title, bg="white", fg="#64748B",
                 font=("Arial", 9, "bold")).pack(pady=(8, 0))

        val_lbl = tk.Label(frame, text=value, bg="white", fg=color,
                           font=("Arial", 20, "bold"))
        val_lbl.pack(pady=(2, 10))

        return frame, val_lbl

    # ─────────────────────────────────────────────────────────
    # Data loading
    # ─────────────────────────────────────────────────────────

    def _fetch_one(self, sql, fallback=0):
        """Run a scalar SELECT and return the first column of the first row."""
        conn = None
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(sql)
            row = cur.fetchone()
            if row is None:
                return fallback
            val = row[0] if isinstance(row, (tuple, list)) else list(row.values())[0]
            return val if val is not None else fallback
        except Exception:
            return fallback
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def load_dashboard_statistics(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            def count(table):
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row = cursor.fetchone()
                return str(row[0] if isinstance(row, (tuple, list)) else list(row.values())[0])

            self.flight_card.config(text=count("flights"))
            self.passenger_card.config(text=count("passengers"))
            self.booking_card.config(text=count("bookings"))
            self.airline_card.config(text=count("airlines"))

            # Revenue — COALESCE works in both MySQL and SQLite
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM payments
                WHERE payment_status = 'Success'
            """)
            row = cursor.fetchone()
            rev = row[0] if isinstance(row, (tuple, list)) else list(row.values())[0]
            self.revenue_card.config(text=f"₹{float(rev or 0):,.0f}")

            # Today's bookings — compatible SQL
            is_sqlite = not hasattr(conn, "is_connected") or type(conn).__module__.startswith("sqlite3")
            if is_sqlite:
                cursor.execute("""
                    SELECT COUNT(*) FROM bookings
                    WHERE DATE(booking_date) = DATE('now')
                """)
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM bookings
                    WHERE DATE(booking_date) = CURDATE()
                """)
            row = cursor.fetchone()
            self.today_card.config(
                text=str(row[0] if isinstance(row, (tuple, list)) else list(row.values())[0])
            )

            conn.close()

        except Exception as e:
            messagebox.showerror("Dashboard Error", f"Could not load statistics:\n{e}")

    def show_payment_chart(self):
        # clear old chart
        for w in self.chart_frame.winfo_children():
            w.destroy()

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT payment_status, COUNT(*)
                FROM payments
                GROUP BY payment_status
            """)
            data = cursor.fetchall()
            conn.close()

            if not data:
                tk.Label(
                    self.chart_frame,
                    text="No payment data available yet.",
                    bg="#F0F4F8", fg="#94A3B8",
                    font=("Arial", 12)
                ).pack(expand=True)
                return

            labels = [
                str(row[0] if isinstance(row, (tuple, list)) else list(row.values())[0])
                for row in data
            ]
            values = [
                float(row[1] if isinstance(row, (tuple, list)) else list(row.values())[1])
                for row in data
            ]

            colors = ["#2563EB", "#16A34A", "#DC2626", "#D97706", "#7C3AED"]

            fig = plt.Figure(figsize=(6, 2.8), dpi=100)
            fig.patch.set_facecolor("#F0F4F8")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#F0F4F8")

            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                startangle=140,
                colors=colors[:len(values)],
                textprops={"fontsize": 10},
                wedgeprops={"edgecolor": "white", "linewidth": 2},
                pctdistance=0.82,
            )
            for at in autotexts:
                at.set_fontsize(9)
                at.set_color("white")
                at.set_fontweight("bold")

            ax.set_title("Payment Status", fontsize=12, fontweight="bold", color="#1E3A5F", pad=10)

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            # Pack without expand so chart doesn't push other widgets
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=4)

            # ── Return focus to root so matplotlib doesn't auto-scroll the window
            self.root.after(50, self.root.focus_set)

        except Exception as e:
            tk.Label(
                self.chart_frame,
                text=f"Chart error: {e}",
                bg="#F0F4F8", fg="#DC2626",
                font=("Arial", 10)
            ).pack(expand=True)

    # ─────────────────────────────────────────────────────────
    # Navigation openers
    # ─────────────────────────────────────────────────────────

    def _open(self, module_path, cls_name, title=""):
        """Generic window opener."""
        try:
            import importlib
            mod = importlib.import_module(module_path)
            cls = getattr(mod, cls_name)
            win = tk.Toplevel(self.root)
            if title:
                win.title(title)
            cls(win)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open {cls_name}:\n{e}")

    def open_airport(self):      self._open("gui.airport",        "AirportWindow",  "Airport Management")
    def open_airline(self):      self._open("gui.airline",        "AirlineWindow",  "Airline Management")
    def open_flight(self):       self._open("gui.flight",         "FlightWindow",   "Flight Management")
    def open_passenger(self):    self._open("gui.passenger",      "PassengerWindow","Passenger Management")
    def open_booking(self):      self._open("gui.booking",        "BookingWindow",  "Booking Management")
    def open_payment(self):      self._open("gui.payment",        "PaymentWindow",  "Payment Management")
    def open_report(self):       self._open("gui.report",         "ReportWindow",   "Reports")
    def open_display(self):      self._open("gui.flight_display", "FlightDisplay",  "Live Flight Display")
    def open_database_tools(self): self._open("gui.database_tools", "DatabaseTools", "Database Tools")


if __name__ == "__main__":
    root = tk.Tk()
    app = Dashboard(root)
    root.mainloop()
