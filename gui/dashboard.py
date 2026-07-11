import tkinter as tk
from tkinter import messagebox
from database.db import connect_db
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
class Dashboard:

    def __init__(self, root):

        self.root = root

        self.root.title("Airline Reservation System")

        self.root.geometry("1400x850")

        self.root.configure(bg="white")

        self.root.resizable(False, False)

        # ==========================
        # HEADER
        # ==========================

        header = tk.Frame(root, bg="#003366", height=70)

        header.pack(fill="x")

        title = tk.Label(
            header,
            text="✈ AIRLINE RESERVATION SYSTEM",
            bg="#003366",
            fg="white",
            font=("Arial", 22, "bold")
        )

        title.pack(side="left", padx=20, pady=15)

        admin = tk.Label(
            header,
            text="Welcome Admin",
            bg="#003366",
            fg="white",
            font=("Arial", 13)
        )

        admin.pack(side="right", padx=20)
        
        
        # ==========================
        # LEFT MENU
        # ==========================
        

        menu = tk.Frame(root, bg="#E8F0FE", width=220)
        menu.pack(side="left", fill="y")

        tk.Button(
            menu,
            text="🏠 Dashboard",
            width=20,
            height=2,
            font=("Arial", 11)
        ).pack(pady=5)

        tk.Button(
           menu,
           text="🛫 Airports",
           width=20,
           height=2,
           font=("Arial", 11),
           command=self.open_airport
        ).pack(pady=5)

        tk.Button(
           menu,
           text="🏢 Airlines",
           width=20,
           height=2,
           font=("Arial", 11),
           command=self.open_airline
        ).pack(pady=5)

        tk.Button(
            menu,
            text="✈ Flights",
            width=20,
            height=2,
            font=("Arial", 11),
            command=self.open_flight
        ).pack(pady=5)

        tk.Button(
            menu,
            text="👤 Passengers",
            width=20,
            height=2,
            font=("Arial", 11),
            command=self.open_passenger
        ).pack(pady=5)

        tk.Button(
           menu,
            text="🎫 Bookings",
            width=20,
            height=2,
            font=("Arial", 11),
            command=self.open_booking
        ).pack(pady=5)

        tk.Button(
            menu,
            text="💳 Payments",
            width=20,
            height=2,
            font=("Arial", 11),
            command=self.open_payment
        ).pack(pady=5)

        tk.Button(
            menu,
            text="📊 Reports",
            width=20,
            height=2,
            font=("Arial", 11),
            command=self.open_report
        ).pack(pady=5)
        tk.Button(
            menu,
            text="💾 Database",
            width=20,
            height=2,
            font=("Arial",11),
            command=self.open_database_tools
        ).pack(pady=5)
        tk.Button(
            menu,
            text="🚪 Logout",
            width=20,
            height=2,
            font=("Arial", 11),
            command=self.root.destroy
        ).pack(pady=5)

        
        # ==========================
        # MAIN CONTENT
        # ==========================
        content = tk.Frame(root, bg="white")

        content.pack(fill="both", expand=True)

        tk.Label(

            content,

            text="Dashboard",

            bg="white",

            font=("Arial",22,"bold")

        ).pack(pady=20)

        tk.Label(

            content,

            text="Welcome to Airline Reservation Management System",

            bg="white",

            font=("Arial",14)

        ).pack()

        tk.Label(

            content,

            text="Database Status : Connected",

            bg="white",

            fg="green",

            font=("Arial",12)

        ).pack(pady=20)

        # Statistics

        stats = tk.Frame(content, bg="white")
        stats.pack(pady=30)

        self.airline_count = self.card(stats, "Airlines", "0", 0, 0)

        self.airport_count = self.card(stats, "Airports", "0", 0, 1)

        self.flight_count = self.card(stats, "Flights", "0", 0, 2)

        self.passenger_count = self.card(stats, "Passengers", "0", 1, 0)

        self.booking_count = self.card(stats, "Bookings", "0", 1, 1)

        self.revenue_count = self.card(stats, "Revenue", "₹0", 1, 2)
        self.load_dashboard_statistics()
        
        # ==========================
        # Dashboard Charts
        # ==========================

        self.chart_frame = tk.Frame(content, bg="white")
        self.chart_frame.pack(fill="both", expand=True, pady=10)

        self.show_payment_chart()

        card_frame = tk.Frame(content, bg="white")
        card_frame.pack(pady=30)
        passenger_card = tk.Label(
            card_frame,
            text=f"Passengers\n{self.get_total_passengers()}",
            font=("Arial",16,"bold"),
            bg="#3498db",
            fg="white",
            width=18,
            height=6
        )

        passenger_card.grid(
            row=0,
            column=0,
            padx=20
        )
        flight_card = tk.Label(
            card_frame,
            text=f"Flights\n{self.get_total_flights()}",
            font=("Arial",16,"bold"),
            bg="#27ae60",
            fg="white",
            width=18,
            height=6
        )

        flight_card.grid(
            row=0,
            column=1,
            padx=20
        )
        booking_card = tk.Label(
            card_frame,
            text=f"Bookings\n{self.get_total_bookings()}",
            font=("Arial",16,"bold"),
            bg="#e67e22",
            fg="white",
            width=15,
            height=5
        )

        booking_card.grid(
            row=0,
            column=2,
            padx=20
        )
        airline_card = tk.Label(
            card_frame,
            text=f"Airlines\n{self.get_total_airlines()}",
            font=("Arial",16,"bold"),
            bg="#9b59b6",
            fg="white",
            width=15,
            height=5
        )

        airline_card.grid(
            row=0,
            column=3,
            padx=20
        )
        revenue_card = tk.Label(
            card_frame,
            text=f"Revenue\n₹{self.get_total_revenue()}",
            font=("Arial",16,"bold"),
            bg="#e74c3c",
            fg="white",
            width=18,
            height=6
        )

        revenue_card.grid(
            row=0,
            column=4,
            padx=20
        )
        today_card = tk.Label(
            card_frame,
            text=f"Today's Bookings\n{self.get_today_bookings()}",
            font=("Arial",16,"bold"),
            bg="#16a085",
            fg="white",
            width=18,
            height=6
        )

        today_card.grid(
            row=0,
            column=5,
            padx=20
        )
    def card(self,parent,title,value,row,column):

        frame=tk.Frame(

            parent,

            bg="#F2F2F2",

            width=250,

            height=120,

            relief="raised",

            bd=2

        )

        frame.grid(

            row=row,

            column=column,

            padx=20,

            pady=20

        )

        frame.grid_propagate(False)

        tk.Label(

            frame,

            text=title,

            bg="#F2F2F2",

            font=("Arial",14,"bold")

        ).pack(pady=10)

        value_label = tk.Label(
            frame,
            text=value,
            bg="#F2F2F2",
            fg="blue",
            font=("Arial",22,"bold")
        )

        value_label.pack()

        return value_label
    def open_airport(self):

        import tkinter as tk
        from gui.airport import AirportWindow

        airport = tk.Toplevel(self.root)
        AirportWindow(airport)
   
    def open_airline(self):

        import tkinter as tk
        from gui.airline import AirlineWindow

        airline = tk.Toplevel(self.root)
        AirlineWindow(airline)
    def open_flight(self):
        
        import tkinter as tk
        from gui.flight import FlightWindow

        flight = tk.Toplevel(self.root)
        FlightWindow(flight)
    def open_passenger(self):
        import tkinter as tk
        from gui.passenger import PassengerWindow

        passenger = tk.Toplevel(self.root)
        PassengerWindow(passenger)
    def open_booking(self):

        import tkinter as tk
        from gui.booking import BookingWindow

        booking = tk.Toplevel(self.root)
        BookingWindow(booking)
    
    def open_payment(self):

        import tkinter as tk
        from gui.payment import PaymentWindow

        payment = tk.Toplevel(self.root)

        PaymentWindow(payment)
    def load_dashboard_statistics(self):

        try:

            conn = connect_db()

            cursor = conn.cursor()

            # Total Airlines
            cursor.execute("SELECT COUNT(*) FROM airlines")
            self.airline_count.config(text=str(cursor.fetchone()[0]))

            # Total Airports
            cursor.execute("SELECT COUNT(*) FROM airports")
            self.airport_count.config(text=str(cursor.fetchone()[0]))

            # Total Flights
            cursor.execute("SELECT COUNT(*) FROM flights")
            self.flight_count.config(text=str(cursor.fetchone()[0]))

            # Total Passengers
            cursor.execute("SELECT COUNT(*) FROM passengers")
            self.passenger_count.config(text=str(cursor.fetchone()[0]))

            # Total Bookings
            cursor.execute("SELECT COUNT(*) FROM bookings")
            self.booking_count.config(text=str(cursor.fetchone()[0]))

            # Total Revenue
            cursor.execute("""
                SELECT IFNULL(SUM(amount),0)
                FROM payments
                WHERE payment_status='Success'
            """)

            revenue = cursor.fetchone()[0]

            self.revenue_count.config(
                text=f"₹{revenue:,.0f}"
            )

            conn.close()

        except Exception as e:
                messagebox.showerror(
                    "Dashboard Error",
                    str(e)
                )
        finally:
         if conn:
            conn.close()
    def show_payment_chart(self):

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
                return

            labels = [row[0] for row in data]
            values = [row[1] for row in data]

            fig = plt.Figure(figsize=(7,5), dpi=100)
            ax = fig.add_subplot(111)

            ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90,
                textprops={"fontsize": 12},
                wedgeprops={"edgecolor": "white", "linewidth": 2}
            )

            ax.set_title(
                "Payment Status Distribution",
                fontsize=16,
                fontweight="bold"
            )

            canvas = FigureCanvasTkAgg(
                fig,
                master=self.chart_frame
            )

            canvas.draw()

            canvas.get_tk_widget().pack(
                fill="both",
                expand=True,
                padx=20,
                pady=10
            )

        except Exception as e:

            messagebox.showerror(
                "Chart Error",
                str(e)
            )
    def open_report(self):

        import tkinter as tk
        from gui.report import ReportWindow

        report = tk.Toplevel(self.root)

        ReportWindow(report)
    def open_database_tools(self):

        import tkinter as tk
        from gui.database_tools import DatabaseTools

        window = tk.Toplevel(self.root)

        DatabaseTools(window)
    
    def get_total_passengers(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM passengers
        """)

        total = cursor.fetchone()[0]

        conn.close()

        return total
    def get_total_flights(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM flights
        """)

        total = cursor.fetchone()[0]

        conn.close()

        return total
    
    def get_total_bookings(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM bookings
        """)

        total = cursor.fetchone()[0]

        conn.close()

        return total
    
    def get_total_airlines(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM airlines
        """)

        total = cursor.fetchone()[0]

        conn.close()

        return total
    def get_total_revenue(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT IFNULL(SUM(amount),0)
            FROM payments
            WHERE payment_status='Success'
        """)

        total = cursor.fetchone()[0]

        conn.close()

        return total
    def get_today_bookings(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM bookings
            WHERE DATE(booking_date)=CURDATE()
        """)

        total = cursor.fetchone()[0]

        conn.close()

        return total