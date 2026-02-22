import sqlite3


def check_db():
    try:
        # Pointing to the DB in your main folder
        conn = sqlite3.connect("final_weather.db")
        cursor = conn.cursor()

        # Get list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print("--- Database Scan ---")
        if not tables:
            print("No tables found! Is the database empty?")
        else:
            for table in tables:
                print(f"Table Found: {table[0]}")
                # Show the column names too
                cursor.execute(f"PRAGMA table_info({table[0]})")
                columns = [col[1] for col in cursor.fetchall()]
                print(f"   Columns: {columns}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_db()
