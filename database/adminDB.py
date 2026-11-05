from database.connection import DatabaseConnection

class AdminQueries:
    @staticmethod
    def insertProductRecord(product_data:tuple[str|int]):
        cursor = db_config = None
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query= """insert into products(productname,description,category,saleprice,quantity,imgname,storedpath)
            values(%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(query,product_data)
            db_config.commit()
            return True, "product Added"
        except Exception as e:
            return False,f"Something wrong in database/adminDB.AdminQueries.insertProductRecord():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    
    
    @staticmethod
    def getAllProducts(product_name: str = None,
                   product_id: int = None,
                   category: str = None,
                   page_no: int = 1,
                   per_page: int = 7):
        cursor = db_config = None
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = """SELECT * FROM products WHERE 1=1"""
            values = []

            if product_name:
                query += " AND productname LIKE %s"
                values.append(f"%{product_name}%")

            if category:
                query += " AND category = %s"
                values.append(category)

            if product_id:
                query += " AND productid = %s"
                values.append(product_id)

            # Pagination
            offset = (page_no - 1) * per_page

            query += " ORDER BY updated_at DESC LIMIT %s OFFSET %s"

            values.extend([per_page, offset])

            cursor.execute(query, values)

            data = cursor.fetchone() if product_id else cursor.fetchall()

            return True, data

        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.getAllProducts(): {e}"

        finally:
            if cursor:
                cursor.close()

            if db_config:
                db_config.close()


    @staticmethod
    def getAllCategories():
        cursor = db_config = None
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = """
            SELECT DISTINCT category
            FROM products
            WHERE category IS NOT NULL
            AND TRIM(category) != ''
            ORDER BY category ASC
            """

            cursor.execute(query)
            data = cursor.fetchall()

            return True, data

        except Exception as e:
            return False, f"Something wrong in getAllCategories(): {e}"

        finally:
            if cursor:
                cursor.close()

            if db_config:
                db_config.close()

    from database.connection import DatabaseConnection

class AdminQueries:
    @staticmethod
    def insertProductRecord(product_data:tuple[str|int]):
        cursor = db_config = None
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query= """insert into products(productname,description,category,saleprice,quantity,imgname,storedpath)
            values(%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(query,product_data)
            db_config.commit()
            return True, "product Added"
        except Exception as e:
            return False,f"Something wrong in database/adminDB.AdminQueries.insertProductRecord():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    
    
    @staticmethod
    def getAllProducts(product_name: str = None,
                   product_id: int = None,
                   category: str = None,
                   page_no: int = 1,
                   per_page: int = 7):
        cursor = db_config = None
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = """SELECT * FROM products WHERE 1=1"""
            values = []

            if product_name:
                query += " AND productname LIKE %s"
                values.append(f"%{product_name}%")

            if category:
                query += " AND category = %s"
                values.append(category)

            if product_id:
                query += " AND productid = %s"
                values.append(product_id)

            # Pagination
            offset = (page_no - 1) * per_page

            query += " ORDER BY updated_at DESC LIMIT %s OFFSET %s"

            values.extend([per_page, offset])

            cursor.execute(query, values)

            data = cursor.fetchone() if product_id else cursor.fetchall()

            return True, data

        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.getAllProducts(): {e}"

        finally:
            if cursor:
                cursor.close()

            if db_config:
                db_config.close()


    @staticmethod
    def getAllCategories():
        cursor = db_config = None
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
    
            query = """
                SELECT DISTINCT category
                FROM products
                WHERE category IS NOT NULL
                AND TRIM(category) != ''
                ORDER BY category ASC
            """
    
            cursor.execute(query)
            data = cursor.fetchall()
            return True, data
    
        except Exception as e:
            return False, f"Error: {e}"
    
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    @staticmethod
    def updateProductRecord(product_id, product_data: tuple):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
            UPDATE products
            SET productname = %s,
                description = %s,
                category = %s,
                saleprice = %s,
                quantity = %s,
                imgname = %s,
                storedpath = %s
            WHERE productid = %s
            """

            cursor.execute(query, product_data + (product_id,))
            db_config.commit()

            return True, "Product Updated Successfully"

        except Exception as e:
            return False, f"Something wrong in AdminQueries.updateProductRecord(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close() 

    @staticmethod
    def getAllUsers():
                cursor = db_config = None
                try:
                    db_config = DatabaseConnection()
                    cursor = db_config.cursor(dictionary=True)
        
                    query= """select * from users;"""
                    cursor.execute(query)
                    data = cursor.fetchall()
                    return True, data
                except Exception as e:
                    return False,f"Something wrong in database/adminDB.AdminQueries.getAllusers():{e}"
                finally:
                    if cursor:
                        cursor.close()
                    if db_config:
                        db_config.close()


    @staticmethod
    def getProductsCount(product_name=None, category=None):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = "SELECT COUNT(*) AS total FROM products WHERE 1=1"
            values = []

            if product_name:
                query += " AND productname LIKE %s"
                values.append(f"%{product_name}%")

            if category:
                query += " AND category = %s"
                values.append(category)

            cursor.execute(query, values)
            data = cursor.fetchone()

            return True, data['total']

        except Exception as e:
            return False, f"Error fetching product count: {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()