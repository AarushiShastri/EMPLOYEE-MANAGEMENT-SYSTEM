import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Label, Entry, Button, Text, Scrollbar
import mysql.connector
from mysql.connector import Error
import os

def create_connection():
    try:
        # Using environment variables for security
        host = os.getenv('DB_HOST', 'localhost')
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', 'Aarushi@1809')
        connection = mysql.connector.connect(host=host, user=user, password=password)
        print("Successfully connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
    
def create_database(cursor):
    cursor.execute("CREATE DATABASE IF NOT EXISTS EmployeeDatabase")
    cursor.execute("USE EmployeeDatabase")

def create_tables(cursor):
    # Dictionary of table creation SQL commands
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

def view_table(conn, table_name):
    window = Toplevel()
    window.title(f"View Table: {table_name}")
    text = Text(window, wrap="none")
    scrollbar_x = Scrollbar(window, orient="horizontal", command=text.xview)
    scrollbar_y = Scrollbar(window, orient="vertical", command=text.yview)
    text.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)
    scrollbar_x.pack(side="bottom", fill="x")
    scrollbar_y.pack(side="right", fill="y")
    text.pack(side="left", fill="both", expand=True)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    results = cursor.fetchall()
    cursor.execute(f"DESCRIBE {table_name}")
    fields = cursor.fetchall()
    if results:
        header = " | ".join([f"{field[0]}" for field in fields])
        text.insert("end", header + "\n")
        for row in results:
            row_data = " | ".join([str(item) for item in row])
            text.insert("end", row_data + "\n")
    else:
        text.insert("end", "No data found.")
    cursor.close()

def insert_into_table(conn, table_name):
    window = Toplevel()
    window.title(f"Insert into Table: {table_name}")
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    fields = cursor.fetchall()
    entries = {}
    for index, field in enumerate(fields):
        Label(window, text=field[0]).grid(row=index, column=0)
        entry = Entry(window)
        entry.grid(row=index, column=1)
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
    Button(window, text="Insert Record", command=submit).grid(row=len(fields), columnspan=2)

def update_table(conn, table_name):
    window = Toplevel()
    window.title(f"Update Table: {table_name}")
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    fields = cursor.fetchall()
    entries = {}
    for index, field in enumerate(fields):
        Label(window, text=field[0]).grid(row=index, column=0)
        entry = Entry(window)
        entry.grid(row=index, column=1)
        entries[field[0]] = entry
    def submit():
        set_clause = ', '.join([f"{k} = %s" for k in entries.keys()])
        values = [entry.get() for entry in entries.values()]
        where_condition = simpledialog.askstring("Update Condition", "Enter the condition (e.g., aadhar = '123456789012'):")
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_condition}"
        try:
            cursor.execute(query, values)
            conn.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Record updated successfully.")
            else:
                messagebox.showinfo("No Action", "No record was updated.")
            window.destroy()
        except Error as e:
            messagebox.showerror("Error", f"Failed to update record: {e}")
    Button(window, text="Update Record", command=submit).grid(row=len(fields), columnspan=2)

def delete_from_table(conn, table_name):
    window = Toplevel()
    window.title(f"Delete from Table: {table_name}")
    def submit():
        where_condition = simpledialog.askstring("Delete Condition", "Enter the condition for deleting (e.g., aadhar = '123456789012'):")
        if not where_condition:
            messagebox.showerror("Error", "You must enter a condition to delete.")
            return
        query = f"DELETE FROM {table_name} WHERE {where_condition}"
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Record deleted successfully.")
            else:
                messagebox.showinfo("No Action", "No record was deleted.")
            window.destroy()
        except Error as e:
            messagebox.showerror("Error", f"Failed to delete record: {e}")
    Button(window, text="Delete Record", command=submit).pack()
def create_table_buttons(root, conn):
    tables = ["Employee", "Department", "Project", "Dependent", "Works_On", "Manages", "Assigned_To", "Supervision"]
    for table in tables:
        frame = tk.Frame(root)
        frame.pack(pady=5)
        tk.Label(frame, text=table).pack(side=tk.LEFT)
        # Fixing the lambda capture issue
        tk.Button(frame, text="View", command=lambda t=table: view_table(conn, t)).pack(side=tk.LEFT)
        tk.Button(frame, text="Insert", command=lambda t=table: insert_into_table(conn, t)).pack(side=tk.LEFT)
        tk.Button(frame, text="Update", command=lambda t=table: update_table(conn, t)).pack(side=tk.LEFT)
        tk.Button(frame, text="Delete", command=lambda t=table: delete_from_table(conn, t)).pack(side=tk.LEFT)

def main():
    conn = create_connection()
    if conn is not None:
        with conn.cursor() as cursor:
            create_database(cursor)
            create_tables(cursor)
        root = tk.Tk()
        root.title("Database Management System")
        create_table_buttons(root, conn)
        root.mainloop()
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == "__main__": 
    main()
