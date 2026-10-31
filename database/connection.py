import mysql.connector as SQLC

def DatabaseConnection():
    try:
        db_config = SQLC.connect(
            host = 'localhost',
            user = 'root',
            password = 'root',
            database = "ecommerce3"
        )
        return db_config
    except Exception as e:
        return f"Something wrong in Database/connection.py:{e}"