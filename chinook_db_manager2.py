#!/usr/bin/env python3

import sqlite3

DB_PATH = 'chinook.db'  # Adjust if using a different path

TABLES = [
    'albums', 'artists', 'customers', 'employees', 'genres',
    'invoice_items', 'invoices', 'media_types',
    'playlist_track', 'playlists', 'tracks'
]

def connect_db():
    return sqlite3.connect(DB_PATH)

def list_tables():
    print("\nAvailable tables:")
    for i, table in enumerate(TABLES, 1):
        print(f"{i}. {table}")
    print(f"{len(TABLES) + 1}. Exit")

def view_table(cur, table):
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
    print(f"\nInsert into `{table}`:")
    columns = cur.execute(f"PRAGMA table_info({table})").fetchall()
    col_names = [col[1] for col in columns if col[5] == 0]  # exclude auto-increment PK

    values = []
    for col in col_names:
        val = input(f"{col}: ")
        values.append(val)

    val_str = "', '".join(values)
    sql = f"INSERT INTO {table} ({', '.join(col_names)}) VALUES ('{val_str}')"
    print(f"Executing: {sql}")
    cur.execute(sql)

def edit_record(cur, table):
    pk = input(f"Enter the primary key ID or condition to edit (e.g., 1 or ArtistId=1): ")
    column = input("Enter column to update: ")
    new_value = input("Enter new value: ")

    sql = f"UPDATE {table} SET {column} = '{new_value}' WHERE {pk}"
    print(f"Executing: {sql}")
    cur.execute(sql)

def delete_record(cur, table):
    condition = input(f"Enter WHERE condition to delete (e.g., AlbumId=1 or 1=1): ")
    sql = f"DELETE FROM {table} WHERE {condition}"
    print(f"Executing: {sql}")
    cur.execute(sql)

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
        except Exception as e:
            print(f"Error: {e}")

def main():
    con = connect_db()
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
