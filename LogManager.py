import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc
from datetime import datetime
import binascii

#------------------------Funcionalidades---------------------------------#
def conectar():
    server = server_entry.get()
    auth = auth_combo.get()
    user = user_entry.get()
    password = password_entry.get()
    database = db_entry.get()

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

    try:
        cursor = conn.cursor()

        operation_filter = []
        if var_insert.get():
            operation_filter.append("log.[Operation] = 'LOP_INSERT_ROWS'")
        if var_update.get():
            operation_filter.append("log.[Operation] = 'LOP_MODIFY_ROW'")
        if var_delete.get():
            operation_filter.append("log.[Operation] = 'LOP_DELETE_ROWS'")

        operation_filter_str = " OR ".join(operation_filter)

        query = f"""
SELECT
    CASE 
        WHEN log.[Operation] = 'LOP_INSERT_ROWS' THEN 'INSERT'
        WHEN log.[Operation] = 'LOP_DELETE_ROWS' THEN 'DELETE'
        WHEN log.[Operation] = 'LOP_MODIFY_ROW' THEN 'UPDATE'
        ELSE log.[Operation]
    END AS [OperationType],
CONVERT(VARCHAR(MAX), log.[Transaction ID], 1) AS [TransactionID],
    log.[Current LSN] AS [CurrentLSN],
    log.[Previous LSN] AS [PreviousLSN],
    log.[AllocUnitName] AS [Schema_Object],
    -- Normaliza las fechas a formato completo
    CONVERT(VARCHAR, begin_log.[Begin Time], 120) AS [BeginTime],  -- yyyy-MM-dd HH:mm:ss
    CONVERT(VARCHAR, end_log.[Begin Time], 120) AS [EndTime],      -- yyyy-MM-dd HH:mm:ss
    COALESCE(SUSER_SNAME(), 'Unknown') AS [UserName]  -- Maneja el caso donde el usuario sea NULL
FROM sys.fn_dblog(NULL, NULL) log
LEFT JOIN sys.fn_dblog(NULL, NULL) begin_log
    ON log.[Transaction ID] = begin_log.[Transaction ID]
    AND begin_log.[Operation] = 'LOP_BEGIN_XACT'
LEFT JOIN sys.fn_dblog(NULL, NULL) end_log
    ON log.[Transaction ID] = end_log.[Transaction ID]
    AND end_log.[Operation] IN ('LOP_COMMIT_XACT', 'LOP_ABORT_XACT')
WHERE 
    ({operation_filter_str}) 
    AND log.[AllocUnitName] NOT LIKE 'sys%' 
    AND log.[AllocUnitName] NOT LIKE 'MS%' 
    AND log.[AllocUnitName] NOT LIKE 'Unknown Alloc Unit%' 
    AND log.[AllocUnitName] IS NOT NULL
ORDER BY log.[Current LSN];
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            tree.insert("", "end", values=row)
    
    except Exception as e:
        print("Error al filtrar logs:", e)
        messagebox.showerror("Error", f"No se pudo obtener el log:\n{e}")


def show_transaction_details(event):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showinfo("Info", "Por favor, selecciona una transacción.")
        return

    transaction_data = tree.item(selected_item, "values")
    if transaction_data:
        TransactionInformationScreen(transaction_data)


#------------------------Visual---------------------------------#

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
    tree = ttk.Treeview(root, columns=("operation_type", "transaction_id", "current_lsn", "previous_lsn", "schema_object", "begin_time", "end_time", "user_name"), show="headings")
    tree.pack(expand=True, fill="both")

    tree.heading("operation_type", text="Operation")
    tree.heading("transaction_id", text="Transaction ID")
    tree.heading("current_lsn", text="Current LSN")
    tree.heading("previous_lsn", text="Previous LSN")
    tree.heading("schema_object", text="Schema_Object")
    tree.heading("begin_time", text="Begin Time")
    tree.heading("end_time", text="End Time")
    tree.heading("user_name", text="User")

    for col in tree["columns"]:
        tree.column(col, anchor="w", width=100)

    tk.Button(root, text="Volver", command=ConnectionScreen, bg="#3A3A3D", fg="white", font=("Arial", 10)).pack(pady=10)
    tree.bind("<<TreeviewSelect>>", show_transaction_details)
    filtrar_logs()


def ConnectionScreen():
    root.geometry("370x400")
    for widget in root.winfo_children():
        widget.destroy()

    global auth_combo, user_entry, password_entry, log_option, from_date_entry, to_date_entry,server_entry,db_entry,FromEntry,ToEntry
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
    db_entry = tk.Entry(root, width=30)
    db_entry.place(x=150, y=190)

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
    FromEntry = tk.Entry(root, width=30)
    FromEntry.place(x=80, y=270
    )
    tk.Label(root, text="To:", fg="white", bg="#2D2D30", font=("Arial", 10)).place(x=30, y=310)
    ToEntry = tk.Entry(root, width=30)
    ToEntry.place(x=80, y=310)

    connect_button = tk.Button(root, text="Conectarse", command=conectar, bg="#3A3A3D", fg="white", font=("Arial", 10))
    connect_button.place(x=150, y=350)
    

def bin_to_str(binary_data):
    if isinstance(binary_data, bytes):
        try:
            # Intenta decodificar el valor binario en texto legible
            decoded_value = binary_data.decode('utf-8').strip('\x00')
            return decoded_value if decoded_value else '[Empty String]'
        except UnicodeDecodeError:
            # Si no se puede decodificar, muestra los bytes como cadena hexadecimal
            return binascii.hexlify(binary_data).decode('utf-8')
    return binary_data


def TransactionScreen(transaction_id, tree):
    try:
        cursor = conn.cursor()
        print(transaction_id)
        print(type(transaction_id))

        transaction_id = transaction_id.replace(",", "")

#        cursor.execute(f"SELECT * FROM sys.fn_dblog(NULL, NULL) WHERE [Transaction ID] = {transaction_id}")

        consulta = f"""
        SELECT
            CONCAT(s.name, '.', o.name, '.', c.name) AS "Field", -- esquema.tabla.columna
            t.name AS "Type",
            d.[RowLog Contents 0] AS "Old Value",
            d.[RowLog Contents 1] AS "New Value"
        FROM
            fn_dblog(NULL, NULL) d
        JOIN
            sys.allocation_units au ON d.AllocUnitId = au.allocation_unit_id
        JOIN
            sys.partitions p ON au.container_id = p.partition_id
        JOIN
            sys.objects o ON p.object_id = o.object_id
        JOIN
            sys.schemas s ON o.schema_id = s.schema_id
        JOIN
            sys.columns c ON c.object_id = o.object_id
        JOIN
            sys.types t ON c.user_type_id = t.user_type_id
        WHERE
            d.[transaction ID]   = {transaction_id}  -- Asegúrate de que sea hexadecimal sin los dos puntos
            AND d.Operation IN ('LOP_MODIFY_ROW', 'LOP_INSERT_ROWS', 'LOP_DELETE_ROWS')
        ORDER BY
            d.[Current LSN];
        """
        
        cursor.execute(consulta)
        rows = cursor.fetchall()
        for row in rows:
            decoded_row = [bin_to_str(cell) for cell in row]
            print(decoded_row)
            tree.insert("", "end", values=decoded_row)
    except Exception as e:
        print("Error al filtrar logs:", e)
        messagebox.showerror("Error", f"No se pudo obtener el log:\n{e}")

def TransactionInformationScreen(transaction_data):
    transaction_id = transaction_data[1]  
    
    details_window = tk.Toplevel(root)
    details_window.title(f"Detalles de la transacción: {transaction_id}")
    details_window.geometry("600x400")
    details_window.configure(bg="#2D2D30")

    notebook = ttk.Notebook(details_window)
    notebook.pack(expand=True, fill="both", padx=10, pady=10)

    operation_frame = ttk.Frame(notebook)
    tree = ttk.Treeview(operation_frame, columns=("field", "type", "old_value", "new_value"), show="headings")
    
    # Configura los encabezados del Treeview
    tree.heading("field", text="Field")
    tree.heading("type", text="Type")
    tree.heading("old_value", text="Old Value")
    tree.heading("new_value", text="New Value")
    
    # Llamada para cargar los datos en el Treeview
    TransactionScreen(transaction_id, tree)
    
    tree.pack(expand=True, fill="both")
    notebook.add(operation_frame, text="Operation details")

    # Agregar otras pestañas
    row_history_frame = ttk.Frame(notebook)
    notebook.add(row_history_frame, text="Row history")
    ttk.Label(row_history_frame, text="Historial de filas afectadas", font=("Arial", 10)).pack(pady=10)

    undo_frame = ttk.Frame(notebook)
    notebook.add(undo_frame, text="Undo script")
    ttk.Label(undo_frame, text="Generación del script UNDO", font=("Arial", 10)).pack(pady=10)

    redo_frame = ttk.Frame(notebook)
    notebook.add(redo_frame, text="Redo script")
    ttk.Label(redo_frame, text="Generación del script REDO", font=("Arial", 10)).pack(pady=10)

    transaction_info_frame = ttk.Frame(notebook)
    notebook.add(transaction_info_frame, text="Transaction information")
    ttk.Label(transaction_info_frame, text=f"Información de la transacción {transaction_id}", font=("Arial", 10)).pack(pady=10)

#------------------------Main---------------------------------#

root = tk.Tk()
root.title("Transaction Log Manager")
root.configure(bg="#2D2D30")
ConnectionScreen()

root.mainloop()

