import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc


def conectar():
    server = server_entry.get()
    auth = auth_combo.get()
    user = user_entry.get()
    password = password_entry.get()
    database = db_combo.get()

    if auth == "Windows":
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    else:
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={user};PWD={password};"

    try:
        conn = pyodbc.connect(connection_string)
        messagebox.showinfo("Soco", "Se pudo conectar exitosamente")
    except Exception as e:
        messagebox.showerror("Error", f"No soca:\n{e}")

root = tk.Tk()
root.title("Transaction Log Manager")
root.geometry("370x400")
root.configure(bg="#2D2D30")

tk.Label(root, text="Server:", fg="white", bg="#2D2D30", font=("Arial", 10)).place(x=30, y=30)
server_entry = tk.Entry(root, width=30)
server_entry.place(x=150, y=30)

tk.Label(root, text="Authentication:", fg="white", bg="#2D2D30", font=("Arial", 10)).place(x=30, y=70)
auth_combo = ttk.Combobox(root, values=["Windows", "SQL Server"], width=27, state="readonly")
auth_combo.current(0)  # Selección predeterminada
auth_combo.place(x=150, y=70)

tk.Label(root, text="User:", fg="white", bg="#2D2D30", font=("Arial", 10)).place(x=30, y=110)
user_entry = tk.Entry(root, width=30)
user_entry.place(x=150, y=110)

tk.Label(root, text="Password:", fg="white", bg="#2D2D30", font=("Arial", 10)).place(x=30, y=150)
password_entry = tk.Entry(root, show="*", width=30)
password_entry.place(x=150, y=150)

tk.Label(root, text="Database:", fg="white", bg="#2D2D30", font=("Arial", 10)).place(x=30, y=190)
db_combo = ttk.Combobox(root, values=["demobd"], width=27, state="readonly")
db_combo.current(0)
db_combo.place(x=150, y=190)

log_option = tk.StringVar(value="online")
tk.Radiobutton(
    root, text="Online transaction log", variable=log_option, value="online",
    bg="#2D2D30", fg="white", selectcolor="#2D2D30", font=("Arial", 10)
).place(x=30, y=230)
tk.Radiobutton(
    root, text="Backup file", variable=log_option, value="backup",
    bg="#2D2D30", fg="white", selectcolor="#2D2D30", font=("Arial", 10)
).place(x=200, y=230)

tk.Label(root, text="From:", fg="white", bg="#2D2D30", font=("Arial", 10)).place(x=30, y=270)
from_date_entry = DateEntry(root, width=27, background="darkblue", foreground="white", borderwidth=2, state="readonly")
from_date_entry.place(x=80, y=270)

tk.Label(root, text="To:", fg="white", bg="#2D2D30", font=("Arial", 10)).place(x=30, y=310)
to_date_entry = DateEntry(root, width=27, background="darkblue", foreground="white", borderwidth=2, state="readonly")
to_date_entry.place(x=80, y=310)

connect_button = tk.Button(root, text="Conectarse", command=conectar, bg="#3A3A3D", fg="white", font=("Arial", 10))
connect_button.place(x=150, y=350)

root.mainloop()

