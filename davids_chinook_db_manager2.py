#!/usr/bin/env python3

import sqlite3
import re

DB_PATH = 'chinook.db'  # Adjust if using a different path

TABLES = [
    'albums', 'artists', 'customers', 'employees', 'genres',
    'invoice_items', 'invoices', 'media_types',
    'playlist_track', 'playlists', 'tracks'
]

def connect_db():
    try:
        return sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def list_tables():
    print("\nAvailable tables:")
    for i, table in enumerate(TABLES, 1):
        print(f"{i}. {table}")
    print(f"{len(TABLES) + 1}. Exit")

def get_table_columns(cur, table):
    try:
        columns = cur.execute(f"PRAGMA table_info({table})").fetchall()
        return columns
    except sqlite3.Error as e:
        print(f"Error fetching columns for {table}: {e}")
        return []

def validate_table(table):
    if table not in TABLES:
        print("Invalid table name.")
        return False
    return True

def validate_column(table, column, cur):
    columns = [col[1] for col in get_table_columns(cur, table)]
    if column not in columns:
        print(f"Invalid column name: {column}")
        return False
    return True

def validate_value(value, max_length=100):
    if value is None or not str(value).strip():
        print("Value cannot be empty.")
        return None
    value = str(value).strip()
    if len(value) > max_length:
        print(f"Value too long (max {max_length} chars)")
        return None
    if re.search(r"[;\'\"\\]", value):
        print("Value contains invalid characters.")
        return None
    return value

def view_table(cur, table):
    if not validate_table(table):
        return
    try:
        res = cur.execute(f"SELECT * FROM {table} LIMIT 20")
        columns = [desc[0] for desc in res.description]
        print(" | ".join(columns))
        print("-" * 50)
        for row in res.fetchall():
            print(" | ".join(str(x) for x in row))
    except Exception as e:
        print(f"Error viewing {table}: {e}")

def add_record(cur, table):
    if not validate_table(table):
        return
    print(f"\nInsert into `{table}`:")
    columns = get_table_columns(cur, table)
    col_names = [col[1] for col in columns if col[5] == 0]  # exclude auto-increment PK
    values = []
    for col in col_names:
        val = input(f"{col}: ")
        val = validate_value(val)
        if val is None:
            return
        values.append(val)
    placeholders = ', '.join(['?' for _ in values])
    sql = f"INSERT INTO {table} ({', '.join(col_names)}) VALUES ({placeholders})"
    try:
        cur.execute(sql, values)
        print(f"Successfully inserted record into {table}.")
    except sqlite3.Error as e:
        print(f"Error inserting record: {e}")

def edit_record(cur, table):
    if not validate_table(table):
        return
    columns = get_table_columns(cur, table)
    pk_cols = [col[1] for col in columns if col[5] == 1]
    if not pk_cols:
        print("No primary key found for this table.")
        return
    pk_col = pk_cols[0]
    pk_val = input(f"Enter the {pk_col} of the record to edit: ")
    pk_val = validate_value(pk_val)
    if pk_val is None:
        return
    col_names = [col[1] for col in columns]
    print(f"Columns: {', '.join(col_names)}")
    column = input("Enter column to update: ")
    if not validate_column(table, column, cur):
        return
    new_value = input("Enter new value: ")
    new_value = validate_value(new_value)
    if new_value is None:
        return
    sql = f"UPDATE {table} SET {column} = ? WHERE {pk_col} = ?"
    try:
        cur.execute(sql, (new_value, pk_val))
        if cur.rowcount == 0:
            print("No record updated. Check the primary key value.")
        else:
            print(f"Successfully updated record in {table}.")
    except sqlite3.Error as e:
        print(f"Error updating record: {e}")

def delete_record(cur, table):
    if not validate_table(table):
        return
    columns = get_table_columns(cur, table)
    pk_cols = [col[1] for col in columns if col[5] == 1]
    if not pk_cols:
        print("No primary key found for this table.")
        return
    pk_col = pk_cols[0]
    pk_val = input(f"Enter the {pk_col} of the record to delete: ")
    pk_val = validate_value(pk_val)
    if pk_val is None:
        return
    confirm = input(f"Are you sure you want to delete record with {pk_col}={pk_val} from {table}? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Deletion cancelled.")
        return
    sql = f"DELETE FROM {table} WHERE {pk_col} = ?"
    try:
        cur.execute(sql, (pk_val,))
        if cur.rowcount == 0:
            print("No record deleted. Check the primary key value.")
        else:
            print(f"Successfully deleted record from {table}.")
    except sqlite3.Error as e:
        print(f"Error deleting record: {e}")

def table_menu(cur, table, con):
    while True:
        print(f"\n--- Managing Table: {table} ---")
        print("1. View Records")
        print("2. Add Record")
        print("3. Edit Record")
        print("4. Delete Record")
        print("5. Back to Table List")

        action = input("Choose an action: ")

        try:
            if action == "1":
                view_table(cur, table)
            elif action == "2":
                add_record(cur, table)
                con.commit()
            elif action == "3":
                edit_record(cur, table)
                con.commit()
            elif action == "4":
                delete_record(cur, table)
                con.commit()
            elif action == "5":
                break
            else:
                print("Invalid option.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
        except Exception as e:
            print(f"Error: {e}")

def main():
    con = connect_db()
    if not con:
        print("Failed to connect to database. Exiting.")
        return
    cur = con.cursor()

    while True:
        list_tables()
        choice = input("Choose a table to manage: ")

        if choice == str(len(TABLES) + 1):
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(TABLES):
            table = TABLES[int(choice) - 1]
            table_menu(cur, table, con)
        else:
            print("Invalid selection.")

    con.close()

if __name__ == "__main__":
    main()
