import psycopg2
import csv

conn = psycopg2.connect(
    "postgresql://neondb_owner:npg_nweOQjR2ryC3@ep-still-thunder-a54pyfes-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS PhoneBook (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        phone VARCHAR(20)
    )
""")
conn.commit()

def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone: ")
    cur.execute("INSERT INTO PhoneBook (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    print("Inserted successfully.\n")

def insert_from_csv():
    file = input("Enter CSV file path: ")
    try:
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                cur.execute("INSERT INTO PhoneBook (name, phone) VALUES (%s, %s)", row)
        conn.commit()
        print("CSV data inserted.\n")
    except Exception as e:
        print("Error:", e)

def update_data():
    name = input("Enter the name of user to update: ")
    new_phone = input("Enter new phone: ")
    cur.execute("UPDATE PhoneBook SET phone = %s WHERE name = %s", (new_phone, name))
    conn.commit()
    print("Updated.\n")

def query_data():
    print("Choose filter type:")
    print("1. Name starts with")
    print("2. Name equals")
    print("3. Phone equals")
    print("4. Phone contains part")
    choice = input("Enter choice: ")

    if choice == '1':
        filter = input("Enter name prefix: ")
        cur.execute("SELECT * FROM PhoneBook WHERE name ILIKE %s", (filter + '%',))
    elif choice == '2':
        name = input("Enter exact name: ")
        cur.execute("SELECT * FROM PhoneBook WHERE name = %s", (name,))
    elif choice == '3':
        phone = input("Enter exact phone: ")
        cur.execute("SELECT * FROM PhoneBook WHERE phone = %s", (phone,))
    elif choice == '4':
        part = input("Enter part of phone number: ")
        cur.execute("SELECT * FROM PhoneBook WHERE phone LIKE %s", ('%' + part + '%',))
    else:
        print("Invalid filter option.")
        return

    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(row)
    else:
        print("No results found.")
    print()

def delete_data():
    mode = input("Delete by (1) name or (2) phone? Enter 1 or 2: ")
    if mode == '1':
        name = input("Enter name to delete: ")
        cur.execute("DELETE FROM PhoneBook WHERE name = %s", (name,))
    elif mode == '2':
        phone = input("Enter phone to delete: ")
        cur.execute("DELETE FROM PhoneBook WHERE phone = %s", (phone,))
    conn.commit()
    print("Deleted.\n")

while True:
    print("1. Insert from console")
    print("2. Insert from CSV")
    print("3. Update phone by name")
    print("4. Query with filter")
    print("5. Delete")
    print("6. Exit")

    choice = input("Choose option: ")
    print()

    if choice == '1':
        insert_from_console()
    elif choice == '2':
        insert_from_csv()
    elif choice == '3':
        update_data()
    elif choice == '4':
        query_data()
    elif choice == '5':
        delete_data()
    elif choice == '6':
        break
    else:
        print("Invalid option.\n")

cur.close()
conn.close()
