
from database.connection import DatabaseConnection

from psycopg2.extras import RealDictCursor

class AuthQueries:

    # Get user data using email
    @staticmethod
    def getUserData(email: str):

        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(cursor_factory=RealDictCursor)

            query = """SELECT * FROM users WHERE email = %s"""

            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user:
                return True, user
            else:
                return False, "Email not Exists"

        except Exception as e:
            return False, f"Something wrong in database/utilsDB.AuthQueries.getUserData(): {e}"

        finally:
            if cursor:
                cursor.close()

            if db_config:
                db_config.close()


    
    @staticmethod
    def createUserAccount(name: str, email: str, password: str, phone: str):

        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(cursor_factory=RealDictCursor)

            query = """
            INSERT INTO users(username, email, hashpassword, phone, role)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING userid, username, email, role
            """

            cursor.execute(query, (name, email, password, phone, 'user'))

            user = cursor.fetchone()

            db_config.commit()

            return True, user

        except Exception as e:
            if db_config:
                db_config.rollback()

            return False, f"Something wrong in database/utilsDB.AuthQueries.createUserAccount(): {e}"

        finally:
            if cursor:
                cursor.close()

            if db_config:
                db_config.close()
