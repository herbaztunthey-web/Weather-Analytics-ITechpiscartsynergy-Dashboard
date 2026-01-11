import sqlite3
import os

# Get the correct path to your database
db_path = os.path.join(os.getcwd(), 'final_weather.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # This command adds the missing 'unit' column
    cursor.execute("ALTER TABLE history ADD COLUMN unit TEXT;")

    conn.commit()
    print("✅ Success! The 'unit' column has been added to your database.")

except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ The column already exists. Your database is already up to date!")
    else:
        print(f"❌ Error: {e}")
finally:
    if conn:
        conn.close()
