
from database.connection import DatabaseConnection


class UserQueries:
    @staticmethod
    def addCartItem(product_id:int, userid:int,quantity:int):

        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            # update cart item quantity
            query = """update cart set quantity = quantity + %s where productid = %s and userid = %s"""
            cursor.execute(query, (quantity, product_id,userid))
            if cursor.rowcount:
                return True, "Cart Item Quantity Updated"
            # insert item to cart
            query = """ INSERT INTO cart (userid, productid, quantity)
                                 VALUES (%s, %s, %s)"""
            cursor.execute(query, (userid, product_id,quantity))
            db_config.commit()
            return True, "Item added to cart"
        except Exception as e:
            return False, f"Something wrong in database/userDB.UserQueries.addCartItem: {e}"

        finally:

            if cursor:
                cursor.close()

            if db_config:
                db_config.close()

    

    @staticmethod
    def getCartItems(userid: int):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = """SELECT 
                c.cartid,
                c.productid,
                c.quantity,
                p.productname,
                p.category,
                p.saleprice,
                p.storedpath,
                p.quantity AS stock,
                (c.quantity * p.saleprice) AS subtotal
            FROM cart c
            JOIN products p ON c.productid = p.productid
            WHERE c.userid = %s
            """

            cursor.execute(query, (userid,))
            data = cursor.fetchall()

            return True, data

        except Exception as e:
            return False, f"Error fetching cart items: {e}"

        finally:
            if cursor:
                cursor.close()

            if db_config:
                db_config.close()


    
    
    @staticmethod
    def updateCartQuantity(cartid: int, userid: int, quantity: int):
        cursor = db_config = None
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()
            # Check cart item exists
            query = """SELECT cartid FROM cart WHERE cartid = %s AND userid = %s"""
            cursor.execute(query, (cartid, userid))
            data = cursor.fetchone()
            if not data:
                return False, "Cart item not found"
                # Update quantity
            query = """UPDATE cart SET quantity = %s WHERE cartid = %s AND userid = %s"""
            cursor.execute(query, (quantity, cartid, userid))
            db_config.commit()
            return True, "Cart Quantity Updated Successfully"
        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Error updating cart quantity: {e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()


    @staticmethod
    def getCartCount(userid: int):
        cursor = db_config = None
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """SELECT SUM(quantity)FROM cart WHERE userid = %s"""
            cursor.execute(query, (userid,))
            data = cursor.fetchone()
            return True, data[0] if data[0] else 0
        except Exception as e:
            return False, f"Error fetching cart count: {e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()


    @staticmethod
    def deleteCartItem(cartid:int):
        cursor = db_config = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)
            # get cart item products info
            query = """delete from cart where cartid = %s"""
            
            cursor.execute(query, (cartid, ))
            db_config.commit()
            return True, "Item deleted"
        
        except Exception as e:
            return False, f"Something wrong in \
                        database/userDB.UserQueries.deleteCartItem():{e}"
        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

