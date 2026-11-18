
from database.connection import DatabaseConnection

try:
    db = DatabaseConnection()
    cursor = db.cursor()

    cursor.execute("SELECT version();")
    result = cursor.fetchone()

    print("Database Connected Successfully!")
    print(result[0])

    cursor.close()
    db.close()

except Exception as e:
    print("Database Connection Failed:", e)
