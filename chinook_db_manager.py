#!/usr/bin/env python3
import sqlite3

def connect_db():
    return sqlite3.connect('chinook.db')  # Use your path

def list_albums(cur):
    print("\n=== Albums ===")
    query = """
        SELECT albums.AlbumId, albums.Title, artists.Name
        FROM albums
        JOIN artists ON albums.ArtistId = artists.ArtistId
        ORDER BY albums.AlbumId
    """
    for row in cur.execute(query):
        print(f"{row[0]} | {row[1]} | {row[2]}")

def list_artists(cur):
    print("\n=== Artists ===")
    for row in cur.execute("SELECT ArtistId, Name FROM artists ORDER BY ArtistId"):
        print(f"{row[0]} | {row[1]}")

def add_album(cur):
    title = input("Enter album title: ")
    artist_id = input("Enter artist ID: ")

    #
    sql = f"INSERT INTO albums (Title, ArtistId) VALUES ('{title}', {artist_id})"
    print(f"Executing: {sql}")
    cur.execute(sql)

def edit_album(cur):
    album_id = input("Enter AlbumId to edit: ")
    new_title = input("New album title: ")
    new_artist_id = input("New artist ID: ")

    #
    sql = f"UPDATE albums SET Title = '{new_title}', ArtistId = {new_artist_id} WHERE AlbumId = {album_id}"
    print(f"Executing: {sql}")
    cur.execute(sql)

def delete_album(cur):
    album_id = input("Enter AlbumId to delete: ")

    #
    sql = f"DELETE FROM albums WHERE AlbumId = {album_id}"
    print(f"Executing: {sql}")
    cur.execute(sql)

def main():
    con = connect_db()
    cur = con.cursor()

    while True:
        print("\n--- Album Management Menu (Vulnerable Version) ---")
        print("1. List Albums")
        print("2. List Artists")
        print("3. Add Album")
        print("4. Edit Album")
        print("5. Delete Album")
        print("6. Exit")

        choice = input("Choose an option: ")

        try:
            if choice == "1":
                list_albums(cur)
            elif choice == "2":
                list_artists(cur)
            elif choice == "3":
                add_album(cur)
                con.commit()
            elif choice == "4":
                edit_album(cur)
                con.commit()
            elif choice == "5":
                delete_album(cur)
                con.commit()
            elif choice == "6":
                break
            else:
                print("Invalid choice.")
        except Exception as e:
            print(f"Error: {e}")

    con.close()

if __name__ == "__main__":
    main()
