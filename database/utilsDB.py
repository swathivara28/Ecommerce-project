from database.connection import DatabaseConnection

class AuthQueries:
    # get user data using email
    @staticmethod
    def getUserData(email:str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            query = """select * from users where email = %s"""
            cursor.execute(query,(email,))
            user = cursor.fetchone()
            if user:
                return True,user
            else:
                return False,"Email not Exists"
        except Exception as e:
            return False, f"Something wrong in database/utilsDB.AuthQueries.getUserData():{e}"
        finally:
            if db_config:
                db_config.close()
            if cursor:
                cursor.close()

    @staticmethod
    def createUserAccount(name:str, email:str, password:str, phone:str):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            query = """insert into users(username, email, hashpassword, phone)
                        values(%s, %s, %s, %s)"""
            cursor.execute(query, (name,email,password,phone))
            db_config.commit()
            return True, "Successfully account created"
        except Exception as e:
            return False, f"Something wrong in database/utilsDB.AuthQueries.createUserAccount():{e}"
        finally:
            if db_config:
                db_config.close()
            if cursor:
                cursor.close()

