import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime,date
import re
from database.db import connect_db
COUNTRY_CODES = {
    "India": "+91",
    "United States": "+1",
    "United Kingdom": "+44",
    "Canada": "+1",
    "Australia": "+61",
    "Singapore": "+65",
    "Malaysia": "+60",
    "UAE": "+971",
    "Saudi Arabia": "+966",
    "Qatar": "+974",
    "Kuwait": "+965",
    "Oman": "+968",
    "Sri Lanka": "+94",
    "Bangladesh": "+880",
    "Pakistan": "+92",
    "Nepal": "+977"
}


class PassengerWindow:

    def __init__(self, root):

        self.root = root
        self.root.title("Passenger Management")
        self.root.geometry("1200x700")
        self.root.configure(bg="white")
        self.root.resizable(False, False)

        # ==========================
        # Title
        # ==========================

        title = tk.Label(
            root,
            text="PASSENGER MANAGEMENT",
            font=("Arial", 24, "bold"),
            bg="#003366",
            fg="white",
            pady=10
        )

        title.pack(fill="x")

        # ==========================
        # Form Frame
        # ==========================

        form = tk.Frame(root, bg="white")
        form.pack(pady=20)

                # First Name
        tk.Label(form, text="First Name").grid(row=0, column=0, padx=10, pady=10)
        self.first_name = tk.Entry(form, width=30, fg="gray")
        self.first_name.insert(0, "Enter First Name")
        self.first_name.grid(row=0, column=1)
        self.first_name.bind("<FocusIn>", self.clear_first_placeholder)
        self.first_name.bind("<FocusOut>", self.restore_first_placeholder)
        # Last Name
        tk.Label(form, text="Last Name", bg="white",
                font=("Arial",12)).grid(row=1,column=0,padx=10,pady=10)

        self.last_name = tk.Entry(form, width=30, fg="gray")
        self.last_name.insert(0, "Enter Last Name")
        self.last_name.grid(row=1, column=1)

        self.last_name.bind("<FocusIn>", self.clear_last_placeholder)
        self.last_name.bind("<FocusOut>", self.restore_last_placeholder)
        # Gender
        tk.Label(form, text="Gender", bg="white",
                font=("Arial",12)).grid(row=2,column=0,padx=10,pady=10)

        self.gender = ttk.Combobox(
            form,
            width=32,
            state="readonly"
        )

        self.gender["values"] = ("Male", "Female", "Other")
        self.gender.grid(row=2,column=1)

        # Date of Birth
        tk.Label(form, text="Date of Birth", bg="white",
                font=("Arial",12)).grid(row=3,column=0,padx=10,pady=10)
        self.dob = DateEntry(
            form,
            width=27,
            date_pattern="yyyy-mm-dd",
            maxdate=date.today()
        )
        self.dob.grid(row=3, column=1)
      
        # Phone
        tk.Label(form, text="Phone", bg="white",
                font=("Arial",12)).grid(row=4,column=0,padx=10,pady=10)
        
        phone_frame = tk.Frame(form, bg="white")
        phone_frame.grid(row=4, column=1)

        self.country_code = tk.Label(
            phone_frame,
            text="+91",
            width=5,
            bg="white",
            fg="blue",
            font=("Arial",11,"bold")
        )

        self.country_code.pack(side="left")

        self.phone = tk.Entry(
            phone_frame,
            width=24
        )

        self.phone.pack(side="left")
        vcmd = self.root.register(self.validate_phone)

        self.phone.config(
            validate="key",
            validatecommand=(vcmd, "%P")
        )
        self.phone.insert(0, "Enter 10-digit Phone")
       
        self.phone.bind("<FocusIn>", self.clear_phone_placeholder)
        self.phone.bind("<FocusOut>", self.restore_phone_placeholder)

        # Email
        tk.Label(form, text="Email", bg="white",
                font=("Arial",12)).grid(row=5,column=0,padx=10,pady=10)

        self.email = tk.Entry(form, width=30, fg="gray")
        self.email.insert(0, "example@gmail.com")
        self.email.grid(row=5,column=1)
        self.email.bind("<FocusIn>", self.clear_email_placeholder)
        self.email.bind("<FocusOut>", self.restore_email_placeholder)
                # Passport Number
        tk.Label(form, text="Passport Number", bg="white",
                font=("Arial",12)).grid(row=6,column=0,padx=10,pady=10)

        self.passport = tk.Entry(form, width=30, fg="gray")
        self.passport.insert(0, "Enter Passport Number")
        self.passport.grid(row=6,column=1,pady=5)

        self.passport.bind("<FocusIn>", self.clear_passport_placeholder)
        self.passport.bind("<FocusOut>", self.restore_passport_placeholder)

        # Nationality
        tk.Label(form, text="Nationality", bg="white",
                font=("Arial",12)).grid(row=7,column=0,padx=10,pady=10)

        self.nationality = ttk.Combobox(
            form,
            width=28,
            values=list(COUNTRY_CODES.keys()),
            state="readonly"
        )
        self.nationality.insert(0, "Enter Nationality")
        self.nationality.grid(row=7,column=1)
        self.nationality.bind(
            "<<ComboboxSelected>>",
            self.update_country_code
        )
        self.nationality.bind("<FocusIn>", self.clear_nationality_placeholder)
        self.nationality.bind("<FocusOut>", self.restore_nationality_placeholder)
        # Store selected passenger ID
        self.passenger_id = None

        # ==========================
        # Buttons
        # ==========================

        button_frame = tk.Frame(root,bg="white")
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="Add",
            width=12,
            command=self.add_passenger
        ).grid(row=0,column=0,padx=10)

        tk.Button(
            button_frame,
            text="Update",
            width=12,
            command=self.update_passenger
        ).grid(row=0,column=1,padx=10)

        tk.Button(
            button_frame,
            text="Delete",
            width=12,
            command=self.delete_passenger
        ).grid(row=0,column=2,padx=10)

        tk.Button(
            button_frame,
            text="Clear",
            width=12,
            command=self.clear_fields
        ).grid(row=0,column=3,padx=10)

                # ==========================
                # Search Frame
                # ==========================

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
        self.search.insert(0, "Search Passenger...")
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

        # ==========================
        # Treeview
        # ==========================

        table_frame = tk.Frame(root)
        table_frame.pack(fill="both",expand=True,padx=20,pady=10)

        scroll_x = tk.Scrollbar(
            table_frame,
            orient="horizontal"
        )

        scroll_y = tk.Scrollbar(
            table_frame,
            orient="vertical"
        )

        self.passenger_table = ttk.Treeview(
            table_frame,
            columns=(
                "id",
                "first_name",
                "last_name",
                "gender",
                "dob",
                "phone",
                "email",
                "passport",
                "nationality"
            ),
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set
        )

        scroll_x.pack(side="bottom",fill="x")
        scroll_y.pack(side="right",fill="y")

        scroll_x.config(command=self.passenger_table.xview)
        scroll_y.config(command=self.passenger_table.yview)

        self.passenger_table.heading("id", text="ID")
        self.passenger_table.heading("first_name", text="First Name")
        self.passenger_table.heading("last_name", text="Last Name")
        self.passenger_table.heading("gender", text="Gender")
        self.passenger_table.heading("dob", text="Date of Birth")
        self.passenger_table.heading("phone", text="Phone")
        self.passenger_table.heading("email", text="Email")
        self.passenger_table.heading("passport", text="Passport No")
        self.passenger_table.heading("nationality", text="Nationality")
        self.passenger_table["show"] = "headings"

        self.passenger_table.column("id", width=60)
        self.passenger_table.column("first_name", width=150)
        self.passenger_table.column("last_name", width=150)
        self.passenger_table.column("gender", width=100)
        self.passenger_table.column("dob", width=120)
        self.passenger_table.column("phone", width=150)
        self.passenger_table.column("email", width=220)
        self.passenger_table.column("passport", width=150)
        self.passenger_table.column("nationality", width=150)

        self.passenger_table.pack(fill="both", expand=True)

        self.passenger_table.bind(
            "<ButtonRelease-1>",
            self.get_cursor
        )

        self.show_data()
    # ==========================
    # Empty Methods
    # ==========================
    def validate_inputs(self):

        import re

        first_name = self.first_name.get().strip()
        last_name = self.last_name.get().strip()
        dob = self.dob.get().strip()
        phone = self.phone.get().strip()
        email = self.email.get().strip()
        passport = self.passport.get().strip()
        nationality = self.nationality.get().strip()

        # First Name
        if first_name == "":
            messagebox.showerror("Error", "First Name is required.")
            return False

        if not first_name.replace(" ", "").isalpha():
            messagebox.showerror(
                "Invalid First Name",
                "Only alphabets are allowed."
            )
            return False

        # Last Name
        if last_name == "":
            messagebox.showerror("Error", "Last Name is required.")
            return False

        if not last_name.replace(" ", "").isalpha():
            messagebox.showerror(
                "Invalid Last Name",
                "Only alphabets are allowed."
            )
            return False
        
        if self.gender.get() == "":
            messagebox.showerror(
                "Error",
                "Please select Gender."
            )
            return False

         # Date of Birth
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', dob):
            messagebox.showerror(
                "Invalid Date",
                "Use YYYY-MM-DD format."
            )
            return False

        # Age Validation
        age = self.calculate_age()

        if age < 1:
            messagebox.showerror(
                "Invalid DOB",
                "Date of Birth cannot be in the future."
            )
            return False

        if age > 120:
            messagebox.showerror(
                "Invalid DOB",
                "Age cannot be more than 120 years."
            )
            return False
        # Phone Number
        if not phone.isdigit():
            messagebox.showerror(
                "Invalid Phone",
                "Phone number should contain only digits."
            )
            return False

        if len(phone) != 10:
            messagebox.showerror(
                "Invalid Phone",
                "Phone number must contain exactly 10 digits."
            )
            return False

        # Email
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

        if not re.match(email_pattern, email):
            messagebox.showerror(
                "Invalid Email",
                "Enter a valid email address."
            )
            return False

        # Passport
        if not re.match(r'^[A-Za-z0-9]{6,15}$', passport):
            messagebox.showerror(
                "Invalid Passport",
                "Passport must contain 6-15 letters or numbers."
            )
            return False

        # Nationality
        if self.nationality.get() not in COUNTRY_CODES:
            messagebox.showerror(
                "Error",
                "Nationality is required."
            )
            return False

        if not nationality.replace(" ", "").isalpha():
            messagebox.showerror(
                "Invalid Nationality",
                "Only alphabets are allowed."
            )
            return False

        return True
    def calculate_age(self):

        dob = self.dob.get()

        birth = datetime.strptime(
            dob,
            "%Y-%m-%d"
        )

        today = datetime.today()

        age = today.year - birth.year

        if (
            today.month,
            today.day
        ) < (
            birth.month,
            birth.day
        ):
            age -= 1

        return age
    def add_passenger(self):

        
        if self.first_name.get() == "":
            messagebox.showerror(
                "Error",
                "First Name is required"
            )
            return
        if not self.validate_inputs():
            return
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM passengers WHERE passport_number=%s",
            (self.passport.get().strip(),)
        )

        if cursor.fetchone():
            messagebox.showerror(
                "Duplicate",
                "Passport Number already exists."
            )
            conn.close()
            return
        
        cursor.execute(
            "SELECT * FROM passengers WHERE email=%s",
            (self.email.get().strip(),)
        )

        if cursor.fetchone():
            messagebox.showerror(
                "Duplicate",
                "Email already exists."
            )
            conn.close()
            return
        
        sql = """
        INSERT INTO passengers
        (
            first_name,
            last_name,
            gender,
            date_of_birth,
            phone,
            email,
            passport_number,
            nationality
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        # Combine country code with phone number
        full_phone = self.country_code.cget("text") + " " + self.phone.get().strip()

        cursor.execute(sql, (

            self.first_name.get().strip(),
            self.last_name.get().strip(),
            self.gender.get(),
            self.dob.get(),
            full_phone,                     # <-- Changed here
            self.email.get().strip(),
            self.passport.get().strip().upper(),
            self.nationality.get()

        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "Passenger Added Successfully!"
        )

        self.show_data()
        self.clear_fields()
    
    def update_passenger(self):

        if self.passenger_id is None:
            messagebox.showerror(
                "Error",
                "Please select a passenger first."
            )
            return

        conn = connect_db()
        cursor = conn.cursor()

        sql = """
        UPDATE passengers
        SET
            first_name=%s,
            last_name=%s,
            gender=%s,
            date_of_birth=%s,
            phone=%s,
            email=%s,
            passport_number=%s,
            nationality=%s
        WHERE passenger_id=%s
        """

        cursor.execute(sql, (

            self.first_name.get().strip(),
            self.last_name.get().strip(),
            self.gender.get(),
            self.dob.get(),
            self.country_code.cget("text") + " " + self.phone.get().strip(),
            self.email.get(),
            self.passport.get(),
            self.nationality.get(),
            self.passenger_id

        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "Passenger Updated Successfully!"
        )

        self.show_data()
        self.clear_fields()

    def delete_passenger(self):

        if self.passenger_id is None:
            messagebox.showerror(
                "Error",
                "Please select a passenger first."
            )
            return

        answer = messagebox.askyesno(
            "Confirm Delete",
            "Delete this passenger?"
        )

        if not answer:
            return

        conn = connect_db()
        cursor = conn.cursor()
        
        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this passenger?"
        )

        if not confirm:
            return
        # Delete bookings of this passenger
        cursor.execute(
            "DELETE FROM bookings WHERE passenger_id=%s",
            (self.passenger_id,)
        )

        # Delete passenger
        cursor.execute(
            "DELETE FROM passengers WHERE passenger_id=%s",
            (self.passenger_id,)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "Passenger Deleted Successfully!"
        )

        self.show_data()
        self.clear_fields()
    def clear_fields(self):

        self.first_name.delete(0, tk.END)
        self.last_name.delete(0, tk.END)
        self.gender.set("")
        self.dob.set_date(date.today())
        self.phone.delete(0, tk.END)
        self.email.delete(0, tk.END)
        self.passport.delete(0, tk.END)
        self.nationality.delete(0, tk.END)
        self.country_code.config(text="+91")
        self.passenger_id = None

    def get_cursor(self, event):

        cursor_row = self.passenger_table.focus()
        contents = self.passenger_table.item(cursor_row)
        row = contents["values"]
     

        if len(row) == 0:
            return
        self.passenger_id = row[0]

        self.first_name.delete(0, tk.END)
        self.first_name.insert(0, row[1])

        self.last_name.delete(0, tk.END)
        self.last_name.insert(0, row[2])

        self.gender.set(row[3])

        self.dob.set_date(datetime.strptime(row[4], "%Y-%m-%d").date())

        # Phone
        phone_data = str(row[5])

        self.phone.delete(0, tk.END)

        if phone_data.startswith("+"):
            parts = phone_data.split(" ", 1)

            if len(parts) == 2:
                self.country_code.config(text=parts[0])
                self.phone.insert(0, parts[1])
            else:
                self.phone.insert(0, phone_data)
        else:
            self.phone.insert(0, phone_data)

        self.email.delete(0, tk.END)
        self.email.insert(0, row[6])

        self.passport.delete(0, tk.END)
        self.passport.insert(0, row[7])

        self.nationality.set(row[8])
    def show_data(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM passengers
            ORDER BY passenger_id
        """)

        rows = cursor.fetchall()

        self.passenger_table.delete(
            *self.passenger_table.get_children()
        )

        for row in rows:
            self.passenger_table.insert(
                "",
                tk.END,
                values=row
            )

        conn.close()
    def search_data(self):

        keyword = self.search.get().strip()

        if keyword == "" or keyword == "Search Passenger...":
            self.show_data()
            return

        conn = connect_db()
        cursor = conn.cursor()

        search = "%" + keyword + "%"

        cursor.execute("""
            SELECT *
            FROM passengers
            WHERE
                CAST(passenger_id AS CHAR) LIKE %s
                OR first_name LIKE %s
                OR last_name LIKE %s
                OR passport_number LIKE %s
                OR phone LIKE %s
                OR email LIKE %s
                OR nationality LIKE %s
            ORDER BY passenger_id
        """, (
            search,
            search,
            search,
            search,
            search,
            search,
            search
        ))

        rows = cursor.fetchall()

        self.passenger_table.delete(
            *self.passenger_table.get_children()
        )

        for row in rows:
            self.passenger_table.insert(
                "",
                tk.END,
                values=row
            )

        conn.close()
    def clear_placeholder(self, event):

        if self.search.get() == "Search Passenger...":
            self.search.delete(0, tk.END)
            self.search.config(fg="black")


    def add_placeholder(self, event):

        if self.search.get() == "":
            self.search.insert(0, "Search Passenger...")
            self.search.config(fg="gray")
    def clear_first_placeholder(self, event):
        if self.first_name.get() == "Enter First Name":
            self.first_name.delete(0, tk.END)
            self.first_name.config(fg="black")


    def restore_first_placeholder(self, event):
        if self.first_name.get() == "":
            self.first_name.insert(0, "Enter First Name")
            self.first_name.config(fg="gray")
    
   
    def clear_email_placeholder(self, event):
        if self.email.get() == "example@gmail.com":
            self.email.delete(0, tk.END)
            self.email.config(fg="black")


    def restore_email_placeholder(self, event):
        if self.email.get() == "":
            self.email.insert(0, "example@gmail.com")
            self.email.config(fg="gray")
    
    def clear_phone_placeholder(self, event):
        if self.phone.get() == "Enter 10-digit Phone":
            self.phone.delete(0, tk.END)
            self.phone.config(fg="black")


    def restore_phone_placeholder(self, event):
        if self.phone.get() == "":
            self.phone.insert(0, "Enter 10-digit Phone")
            self.phone.config(fg="gray")

    def clear_last_placeholder(self, event):
        if self.last_name.get() == "Enter Last Name":
            self.last_name.delete(0, tk.END)
            self.last_name.config(fg="black")


    def restore_last_placeholder(self, event):
        if self.last_name.get() == "":
            self.last_name.insert(0, "Enter Last Name")
            self.last_name.config(fg="gray")
    
    def clear_passport_placeholder(self, event):
        if self.passport.get() == "Enter Passport Number":
            self.passport.delete(0, tk.END)
            self.passport.config(fg="black")


    def restore_passport_placeholder(self, event):
        if self.passport.get() == "":
            self.passport.insert(0, "Enter Passport Number")
            self.passport.config(fg="gray")
    
    def clear_nationality_placeholder(self, event):
        if self.nationality.get() == "Enter Nationality":
            self.nationality.delete(0, tk.END)
            self.nationality.config(fg="black")


    def restore_nationality_placeholder(self, event):
        if self.nationality.get() == "":
            self.nationality.insert(0, "Enter Nationality")
            self.nationality.config(fg="gray")
    
    def update_country_code(self, event=None):

        country = self.nationality.get()

        if country in COUNTRY_CODES:
            self.country_code.config(
                text=COUNTRY_CODES[country]
            )


    def validate_phone(self, value):

        if value == "":
            return True

        return value.isdigit()