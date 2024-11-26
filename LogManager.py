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
        global conn
        conn = pyodbc.connect(connection_string)
        messagebox.showinfo("Soco", "Se pudo conectar exitosamente")
        LogScreen()

    except Exception as e:
        messagebox.showerror("Error", f"No soca:\n{e}")

def filtrar_logs():
    for item in tree.get_children():
        tree.delete(item)

    log_option_value = log_option.get()
    try:
        cursor = conn.cursor()
        if log_option_value == "online":
            query = "SELECT [Operation], [Context], [Transaction ID], [AllocUnitName], [Begin Time], [End Time], [Log Record Length], [Current LSN] FROM sys.fn_dblog(NULL, NULL)"
        else:
            query = "SELECT 'Backup logs not yet implemented' AS [Operation]"

        cursor.execute(query)
        for row in cursor.fetchall():
            operation = row[0]
            if (operation == "LOP_INSERT_ROWS" and var_insert.get()) or \
               (operation == "LOP_MODIFY_ROW" and var_update.get()) or \
               (operation == "LOP_DELETE_ROWS" and var_delete.get()):
                tree.insert("", "end", values=row)
        cursor.close()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener el log:\n{e}")


def LogScreen():
    root.geometry("800x600")

    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Transaction Log Viewer", fg="white", bg="#2D2D30", font=("Arial", 14)).pack(pady=10)
    filter_frame = tk.Frame(root, bg="#2D2D30")
    filter_frame.pack(pady=10)

    global var_insert, var_update, var_delete
    var_insert = tk.BooleanVar(value=True)
    var_update = tk.BooleanVar(value=True)
    var_delete = tk.BooleanVar(value=True)

    tk.Checkbutton(
        filter_frame, text="Insert", variable=var_insert, 
        bg="#2D2D30", fg="white", font=("Arial", 10), 
        selectcolor="#3A3A3D"  
    ).grid(row=0, column=0, padx=10)

    tk.Checkbutton(
        filter_frame, text="Update", variable=var_update, 
        bg="#2D2D30", fg="white", font=("Arial", 10), 
        selectcolor="#3A3A3D"
    ).grid(row=0, column=1, padx=10)

    tk.Checkbutton(
        filter_frame, text="Delete", variable=var_delete, 
        bg="#2D2D30", fg="white", font=("Arial", 10), 
        selectcolor="#3A3A3D"
    ).grid(row=0, column=2, padx=10)

    apply_button = tk.Button(filter_frame, text="Apply", command=filtrar_logs, bg="#3A3A3D", fg="white", font=("Arial", 10))
    apply_button.grid(row=0, column=3, padx=10)

    global tree
    tree = ttk.Treeview(root, columns=("operation", "schema", "object", "user", "begin_time", "end_time", "transaction_id", "lsn"), show="headings")
    tree.pack(expand=True, fill="both")

    tree.heading("operation", text="Operation")
    tree.heading("schema", text="Schema")
    tree.heading("object", text="Object")
    tree.heading("user", text="User")
    tree.heading("begin_time", text="Begin Time")
    tree.heading("end_time", text="End Time")
    tree.heading("transaction_id", text="Transaction ID")
    tree.heading("lsn", text="LSN")

    for col in tree["columns"]:
        tree.column(col, anchor="w", width=100)

    tk.Button(root, text="Volver", command=ConnectionScreen, bg="#3A3A3D", fg="white", font=("Arial", 10)).pack(pady=10)

    filtrar_logs()



def ConnectionScreen():
    root.geometry("370x400")
    for widget in root.winfo_children():
        widget.destroy()

    global auth_combo, user_entry, password_entry, db_combo, log_option, from_date_entry, to_date_entry,server_entry    
    tk.Label(root, text="Server:", fg="white", bg="#2D2D30", font=("Arial", 10)).place(x=30, y=30)
    server_entry = tk.Entry(root, width=30)
    server_entry.place(x=150, y=30)
    tk.Label(root, text="Authentication:", fg="white", bg="#2D2D30", font=("Arial", 10)).place(x=30, y=70)
    auth_combo = ttk.Combobox(root, values=["Windows", "SQL Server"], width=27, state="readonly")
    auth_combo.current(0)  
    auth_combo.place(x=150, y=70)

    tk.Label(root, text="User:", fg="white", bg="#2D2D30", font=("Arial", 10)).place(x=30, y=110)
    user_entry = tk.Entry(root, width=30)
    user_entry.place(x=150, y=110)

    tk.Label(root, text="Password:", fg="white", bg="#2D2D30", font=("Arial", 10)).place(x=30, y=150)
    password_entry = tk.Entry(root, show="*", width=30)
    password_entry.place(x=150, y=150)

    tk.Label(root, text="Database:", fg="white", bg="#2D2D30", font=("Arial", 10)).place(x=30, y=190)
    db_combo = ttk.Combobox(root, values=["master"], width=27, state="readonly")
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
    
    

root = tk.Tk()
root.title("Transaction Log Manager")
root.configure(bg="#2D2D30")
ConnectionScreen()

root.mainloop()

