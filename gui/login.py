import tkinter as tk
from tkinter import messagebox
from database.db import connect_db


class LoginWindow:

    def __init__(self, root):

        self.root = root

        self.root.title("Airline Reservation System")

        self.root.geometry("600x400")

        self.root.resizable(False, False)

        title = tk.Label(
            root,
            text="AIRLINE RESERVATION SYSTEM",
            font=("Arial",20,"bold")
        )

        title.pack(pady=20)

        tk.Label(
            root,
            text="Admin Login",
            font=("Arial",14)
        ).pack()

        tk.Label(
            root,
            text="Username"
        ).pack(pady=5)

        self.username = tk.Entry(root,width=30)

        self.username.pack()

        tk.Label(
            root,
            text="Password"
        ).pack(pady=5)

        self.password = tk.Entry(root,width=30,show="*")

        self.password.pack()

        tk.Button(
            root,
            text="Login",
            width=15,
            command=self.login
        ).pack(pady=20)

        tk.Button(
            root,
            text="Exit",
            width=15,
            command=root.destroy
        ).pack()

    def login(self):

        user = self.username.get()

        pwd = self.password.get()

        conn = connect_db()

        cursor = conn.cursor()

        query = """
        SELECT *
        FROM admin
        WHERE username=%s
        AND password=%s
        """

        cursor.execute(query,(user,pwd))

        result = cursor.fetchone()

        if result:

         messagebox.showinfo(
          "Success",
          "Login Successful!"
        )
 
         self.root.destroy()

         import tkinter as tk
         from gui.dashboard import Dashboard

         dashboard_window = tk.Tk()
         Dashboard(dashboard_window)
         dashboard_window.mainloop()
        else:

            messagebox.showerror(
                "Error",
                "Invalid Username or Password"
            )

        conn.close()