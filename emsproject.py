import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel
import mysql.connector
from mysql.connector import Error
import os

# Database connection setup
def create_connection():
    try:
        host = os.getenv('DB_HOST', 'localhost')
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', 'Aarushi@1809')  # Update credentials
        connection = mysql.connector.connect(host=host, user=user, password=password)
        print("Successfully connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

# Create database and tables
def create_database_and_tables(conn):
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS EmployeeDatabase")
    cursor.execute("USE EmployeeDatabase")

    tables = {
        "Employee": """
            CREATE TABLE IF NOT EXISTS Employee (
                aadhar CHAR(12) NOT NULL,
                first_name VARCHAR(50),
                middle_initial CHAR(1),
                last_name VARCHAR(50),
                birth_date DATE,
                address VARCHAR(255),
                sex CHAR(1),
                salary DECIMAL(10, 2),
                status VARCHAR(50),
                PRIMARY KEY (aadhar)
            );
        """,
        "Department": """
            CREATE TABLE IF NOT EXISTS Department (
                name VARCHAR(50) NOT NULL,
                location VARCHAR(255),
                PRIMARY KEY (name)
            );
        """,
        "Project": """
            CREATE TABLE IF NOT EXISTS Project (
                name VARCHAR(50) NOT NULL,
                location VARCHAR(255),
                budget DECIMAL(18, 2),
                PRIMARY KEY (name)
            );
        """,
        "Dependent": """
            CREATE TABLE IF NOT EXISTS Dependent (
                aadhar CHAR(12) NOT NULL,
                name VARCHAR(50) NOT NULL,
                sex CHAR(1),
                birth_date DATE,
                relationship VARCHAR(50),
                PRIMARY KEY (aadhar, name),
                FOREIGN KEY (aadhar) REFERENCES Employee(aadhar)
            );
        """,
        "Works_On": """
            CREATE TABLE IF NOT EXISTS Works_On (
                aadhar CHAR(12) NOT NULL,
                project_name VARCHAR(50) NOT NULL,
                hours DECIMAL(5, 2),
                start_date DATE,
                PRIMARY KEY (aadhar, project_name),
                FOREIGN KEY (aadhar) REFERENCES Employee(aadhar),
                FOREIGN KEY (project_name) REFERENCES Project(name)
            );
        """,
        "Manages": """
            CREATE TABLE IF NOT EXISTS Manages (
                aadhar CHAR(12) NOT NULL,
                department_name VARCHAR(50) NOT NULL,
                start_date DATE,
                PRIMARY KEY (aadhar, department_name),
                FOREIGN KEY (aadhar) REFERENCES Employee(aadhar),
                FOREIGN KEY (department_name) REFERENCES Department(name)
            );
        """,
        "Assigned_To": """
            CREATE TABLE IF NOT EXISTS Assigned_To (
                project_name VARCHAR(50) NOT NULL,
                department_name VARCHAR(50) NOT NULL,
                start_date DATE,
                PRIMARY KEY (project_name, department_name),
                FOREIGN KEY (project_name) REFERENCES Project(name),
                FOREIGN KEY (department_name) REFERENCES Department(name)
            );
        """,
        "Supervision": """
            CREATE TABLE IF NOT EXISTS Supervision (
                supervisor_aadhar CHAR(12) NOT NULL,
                supervisee_aadhar CHAR(12) NOT NULL,
                start_date DATE,
                PRIMARY KEY (supervisor_aadhar, supervisee_aadhar),
                FOREIGN KEY (supervisor_aadhar) REFERENCES Employee(aadhar),
                FOREIGN KEY (supervisee_aadhar) REFERENCES Employee(aadhar)
            );
        """
    }

    for table_name, query in tables.items():
        try:
            cursor.execute(query)
            print(f"Table {table_name} created or already exists.")
        except mysql.connector.Error as err:
            print(f"Failed to create {table_name}: {err}")
    cursor.close()

# Switch between frames
def switch_frame(root, frames, frame_name):
    for frame in frames.values():
        frame.pack_forget()
    frames[frame_name].pack(fill=tk.BOTH, expand=True)

# Welcome page
def create_welcome_frame(root, switch_to_tables):
    frame = ttk.Frame(root)
    ttk.Label(frame, text="Welcome to the Employee Management System", font=("Helvetica", 20, "bold")).pack(pady=20)
    ttk.Label(frame, text="Manage your employee database efficiently with this tool.", font=("Helvetica", 14)).pack(pady=10)
    ttk.Button(frame, text="Start Managing Tables", command=switch_to_tables).pack(pady=30)
    return frame

# Tables management page
def create_tables_frame(root, conn, frames, switch_to_home):
    frame = ttk.Frame(root)
    ttk.Label(frame, text="Manage Tables", font=("Helvetica", 16, "bold")).pack(pady=20)
    tables = ["Employee", "Department", "Project", "Dependent", "Works_On", "Manages", "Assigned_To", "Supervision"]

    ttk.Button(frame, text="Back to Home", command=switch_to_home).pack(pady=5)

    for table in tables:
        ttk.Button(frame, text=f"{table} Table", command=lambda t=table: view_table_in_window(conn, t)).pack(pady=5)

    return frame

# View table and CRUD operations
def view_table_in_window(conn, table_name):
    window = Toplevel()
    window.title(f"{table_name} Table")
    window.geometry("900x600")
    window.configure(bg="#F0F8FF")

    # Treeview frame
    tree_frame = ttk.Frame(window)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tree = ttk.Treeview(tree_frame, show="headings", selectmode="browse")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbars
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    hsb = ttk.Scrollbar(window, orient="horizontal", command=tree.xview)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    # Fetch data
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    columns = [col[0] for col in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Set columns in Treeview
    tree["columns"] = columns
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor=tk.CENTER)

    for row in rows:
        tree.insert("", "end", values=row)

    # CRUD Buttons
    buttons_frame = ttk.Frame(window)
    buttons_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Button(buttons_frame, text="Insert", command=lambda: insert_into_table(conn, table_name)).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="Update", command=lambda: update_table(conn, table_name)).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="Delete", command=lambda: delete_from_table(conn, table_name)).pack(side=tk.LEFT, padx=5)

# Insert data into table
def insert_into_table(conn, table_name):
    window = Toplevel()
    window.title(f"Insert into {table_name}")
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    fields = cursor.fetchall()
    entries = {}

    for idx, field in enumerate(fields):
        ttk.Label(window, text=field[0]).grid(row=idx, column=0, padx=10, pady=5)
        entry = ttk.Entry(window)
        entry.grid(row=idx, column=1, padx=10, pady=5)
        entries[field[0]] = entry

    def submit():
        columns = ', '.join(entries.keys())
        placeholders = ', '.join(['%s'] * len(entries))
        values = [entry.get() for entry in entries.values()]
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        try:
            cursor.execute(query, values)
            conn.commit()
            messagebox.showinfo("Success", "Record inserted successfully.")
            window.destroy()
        except Error as e:
            messagebox.showerror("Error", f"Failed to insert record: {e}")

    ttk.Button(window, text="Submit", command=submit).grid(row=len(fields), columnspan=2, pady=10)

# Update data in table
def update_table(conn, table_name):
    window = Toplevel()
    window.title(f"Update {table_name}")
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    fields = cursor.fetchall()
    entries = {}

    ttk.Label(window, text="Condition for update (e.g., aadhar='123'):").grid(row=0, columnspan=2, pady=10)
    condition_entry = ttk.Entry(window)
    condition_entry.grid(row=1, columnspan=2, pady=5)

    for idx, field in enumerate(fields, start=2):
        ttk.Label(window, text=field[0]).grid(row=idx, column=0, padx=10, pady=5)
        entry = ttk.Entry(window)
        entry.grid(row=idx, column=1, padx=10, pady=5)
        entries[field[0]] = entry

    def submit():
        set_clause = ', '.join([f"{key}=%s" for key in entries.keys()])
        values = [entry.get() for entry in entries.values()]
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition_entry.get()}"
        try:
            cursor.execute(query, values)
            conn.commit()
            messagebox.showinfo("Success", "Record updated successfully.")
            window.destroy()
        except Error as e:
            messagebox.showerror("Error", f"Failed to update record: {e}")

    ttk.Button(window, text="Update", command=submit).grid(row=len(fields) + 2, columnspan=2, pady=10)

# Delete data from table
def delete_from_table(conn, table_name):
    window = Toplevel()
    window.title(f"Delete from {table_name}")

    ttk.Label(window, text="Condition for deletion (e.g., aadhar='123'):").pack(pady=5)
    condition_entry = ttk.Entry(window)
    condition_entry.pack(pady=5)

    def submit():
        query = f"DELETE FROM {table_name} WHERE {condition_entry.get()}"
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            messagebox.showinfo("Success", "Record deleted successfully.")
            window.destroy()
        except Error as e:
            messagebox.showerror("Error", f"Failed to delete record: {e}")

    ttk.Button(window, text="Delete", command=submit).pack(pady=10)

# Main application
def main():
    conn = create_connection()
    if conn:
        create_database_and_tables(conn)

        root = tk.Tk()
        root.title("Database Management System")
        root.geometry("900x600")
        root.configure(bg="#ADD8E6")

        frames = {}
        frames["Welcome"] = create_welcome_frame(root, lambda: switch_frame(root, frames, "Tables"))
        frames["Tables"] = create_tables_frame(root, conn, frames, lambda: switch_frame(root, frames, "Welcome"))

        switch_frame(root, frames, "Welcome")

        root.mainloop()
        conn.close()

if __name__ == "__main__":
    main()
