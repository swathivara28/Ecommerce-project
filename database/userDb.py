
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

    
    # @staticmethod
    # def createOrder(userid: int, address: str, payment_method: str,
    #             razorapy_id: str = None, razorapay_order_id: str = None):

    #     cursor = db_config = None

    #     try:
    #         db_config = DatabaseConnection()
    #         cursor = db_config.cursor(dictionary=True)

    #        # Get cart items and lock the selected rows
    #         query = """SELECT
    #             c.cartid,
    #             c.userid,
    #             c.productid,
    #             c.quantity,
    #             p.productname,
    #             p.category,
    #             p.saleprice,
    #             p.quantity AS stock,
    #             (c.quantity * p.saleprice) AS subtotal
    #             FROM cart c
    #             INNER JOIN products p ON c.productid = p.productid
    #             WHERE c.userid = %s
    #             FOR UPDATE"""

    #         cursor.execute(query, (userid,))
    #         items = cursor.fetchall()

    #         if not items:
    #             return False, "Cart is Empty"

    #         # Check stock availability
    #         for item in items:
    #             if item['quantity'] > item['stock']:
    #                 return False, f"{item['productname']} product does not have enough stock"

    #     # Calculate subtotal and total
    #         sub_total = sum(float(item['subtotal']) for item in items)
    #         shipping = sub_total * 0.0001
    #         total = sub_total + shipping

    #     # Update product stock
    #         query = """
    #         UPDATE products
    #         SET quantity = quantity - %s
    #         WHERE productid = %s
    #         """

    #         for item in items:
    #             cursor.execute(query, (item['quantity'], item['productid']))

    #     # Insert order
    #         query = """
    #         INSERT INTO orders(userid, address, status)
    #         VALUES(%s, %s, %s)
    #         """

    #         cursor.execute(query, (userid, address, 'pending'))
    #         orderid = cursor.lastrowid

    #     # Insert order details
    #         query = """
    #         INSERT INTO order_details(orderid, productid, quantity, price)
    #         VALUES(%s, %s, %s, %s)
    #         """

    #         for item in items:
    #             cursor.execute(query, (
    #             orderid,
    #             item['productid'],
    #             item['quantity'],
    #             item['saleprice']))

    #     # Insert payment
    #         query = """
    #         INSERT INTO payments(orderid, userid, method, amount)
    #         VALUES(%s, %s, %s, %s)
    #         """

    #         method = payment_method.strip().lower().replace(" ", "")

    #         if method not in ['cash', 'upi', 'netbanking']:
    #             return False, "Invalid payment method selected"

    #         cursor.execute(query, (orderid, userid, method, total))

    #     # Clear cart
    #         query = "DELETE FROM cart WHERE userid = %s"
    #         cursor.execute(query, (userid,))

    #         db_config.commit()

    #         return True, {'order_id': orderid,
    #         'subtotal': sub_total,
    #         'shipping': shipping,
    #         'total': total}

    #     except Exception as e:
    #         if db_config:
    #             db_config.rollback()

    #         return False, f"Something wrong in database/userDB.UserQueries.createOrder(): {e}"

    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if db_config:
    #             db_config.close()


    # # @staticmethod
    # # def getOrderDetails(userid: int):
    # #     cursor = db_config = None
    # #     try:
    # #         db_config = DatabaseConnection()
    # #         cursor = db_config.cursor(dictionary=True)

    # #         query = """SELECT o.orderid,o.userid,o.status,o.address,o.created_at,od.productid,od.quantity,od.price,od.subtotal,p.productname,p.category,p.storedpath FROM orders o JOIN order_details od ON o.orderid = od.orderid
    # #         JOIN products p
    # #             ON od.productid = p.productid
    # #         WHERE o.userid = %s
    # #         ORDER BY o.created_at DESC"""

    # #         cursor.execute(query, (userid,))
    # #         data = cursor.fetchall()

    # #         return True, data

    # #     except Exception as e:
    # #         return False, f"Error fetching order details: {e}"

    # #     finally:
    # #         if cursor:
    # #             cursor.close()

    # #         if db_config:
    # #             db_config.close()

    # @staticmethod
    # def getOrderDetails(userid: int):
    #     cursor = db_config = None

    #     try:
    #         db_config = DatabaseConnection()
    #         cursor = db_config.cursor(dictionary=True)

    #         query = """
    #             SELECT
    #                 o.orderid AS id,
    #                 o.created_at,
    #                 o.status,
    #                 o.address,
    #                 COUNT(od.productid) AS item_count,
    #                 COALESCE(SUM(od.subtotal), 0) AS total_amount,
    #                 pay.method AS payment_method,
    #                 pay.amount AS payment_amount,
    #                 pay.paymentid
    #             FROM orders o
    #             LEFT JOIN order_details od ON o.orderid = od.orderid
    #             LEFT JOIN payments pay ON o.orderid = pay.orderid
    #             WHERE o.userid = %s
    #             GROUP BY
    #                 o.orderid, o.created_at, o.status, o.address,
    #                 pay.method, pay.amount, pay.paymentid
    #             ORDER BY o.created_at DESC
    #         """

    #         cursor.execute(query, (userid,))
    #         data = cursor.fetchall()

    #         return True, data

    #     except Exception as e:
    #         return False, f"Error fetching orders: {e}"

    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if db_config:
    #             db_config.close()


    # @staticmethod
    # def getSingleOrderDetails(userid: int, orderid: int):
    #     cursor = db_config = None

    #     try:
    #         db_config = DatabaseConnection()
    #         cursor = db_config.cursor(dictionary=True)

    #         query = """
    #             SELECT
    #                 o.orderid AS id,
    #                 o.userid,
    #                 o.status,
    #                 o.address,
    #                 o.created_at,
    #                 pay.paymentid,
    #                 pay.method AS payment_method,
    #                 pay.amount AS total_amount
    #             FROM orders o
    #             LEFT JOIN payments pay ON o.orderid = pay.orderid
    #             WHERE o.orderid = %s AND o.userid = %s
    #         """

    #         cursor.execute(query, (orderid, userid))
    #         data = cursor.fetchone()

    #         if not data:
    #             return False, "Order not found"

    #         return True, data

    #     except Exception as e:
    #         return False, f"Error fetching order: {e}"

    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if db_config:
    #             db_config.close()


    # @staticmethod
    # def getOrderItems(orderid: int):
    #     cursor = db_config = None

    #     try:
    #         db_config = DatabaseConnection()
    #         cursor = db_config.cursor(dictionary=True)

    #         query = """
    #             SELECT
    #                 p.productname AS product_name,
    #                 p.category,
    #                 p.storedpath AS image,
    #                 od.quantity,
    #                 od.price,
    #                 od.subtotal
    #             FROM order_details od
    #             JOIN products p ON od.productid = p.productid
    #             WHERE od.orderid = %s
    #         """

    #         cursor.execute(query, (orderid,))
    #         data = cursor.fetchall()

    #         return True, data

    #     except Exception as e:
    #         return False, f"Error fetching order items: {e}"

    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if db_config:
    #             db_config.close()

# create order
    @staticmethod
    def createOrder(userid:int, address:str,payment_method:str, razorpay_order_id:str=None, razorpay_payment_id:str=None):
        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(dictionary=True)

            query = """select c.cartid, c.userid, c.quantity, p.productname, 
                        p.productid, p.quantity as stock, p.saleprice from cart c
                        join products p on c.productid = p.productid
                        where c.userid = %s FOR UPDATE"""
            cursor.execute(query, (userid, ))
            items = cursor.fetchall()
            print("cart items:",items)
            if not items:
                return False, "Cart is empty"
            # check each product stock is avilable as per the quantity
            sub_total = 0
            for item in items:
                if item['quantity'] > item['stock']:
                    return False, f"{item['productname']} current {item['quantity']}  not avilable"
                sub_total += item['quantity'] * item['saleprice']

            # Reduce the each product stocks
            for item in items:
                query = "update products set quantity = quantity - %s where productid = %s"
                cursor.execute(query, (item['quantity'], item['productid']))
            
            # add order record
            shipping = sub_total * 0.01
            query = """insert into orders(userid, status, address, total)
                        values(%s, %s, %s, %s)"""
            cursor.execute(query, (userid,"pending", address, sub_total+shipping))
            # cursor.execute("select orderid from orders where userid = %s order by orderid desc", (userid,))
            # # add payment record
            # orderid = cursor.fetchone()[0]
            orderid = cursor.lastrowid

            #add items to order details
            for item in items:
                query = """insert into order_details(orderid,productid, quantity, price)
                values(%s, %s, %s, %s)"""
                # item_sub_total = item['quantity'] * item['saleprice']
                cursor.execute(query, (orderid,item['productid'], item['quantity'], item['saleprice']))

            # insert payment in payments table
            status = "pending"
            method = payment_method.lower()
            
            query = """insert into payments(userid, orderid, status, method, amount, razorpay_order_id, razorpay_payment_id)
                    values(%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (userid, orderid,status, 'cash' if method=='cod' else method, sub_total +shipping,razorpay_order_id, razorpay_payment_id ))

             # Clear cart
            cursor.execute(
                "DELETE FROM cart WHERE userid = %s",
                (userid,)
            )

            db_config.commit()
            cursor.close()
            db_config.close()
            return True, {"order_id":orderid, "amount":sub_total+ shipping}
        except Exception as e:
            db_config.rollback()
            return False, f"Something wrong in database/userDB.py/UserQueries.createOrder():{e}"
            


    @staticmethod
    def updateCartQuantity(cartid, quantity, userid):
        try: quantity = int(quantity)
        except (ValueError, TypeError): return False, 'Invalid quantity'
        if quantity < 1: return False, 'Quantity must be at least 1'
        db = DatabaseConnection(); cur = db.cursor(dictionary=True)
        try:
            cur.execute('''SELECT p.quantity AS stock FROM cart c
                           JOIN products p ON p.productid=c.productid
                           WHERE c.cartid=%s AND c.userid=%s''', (cartid, userid))
            row = cur.fetchone()
            if not row: return False, 'Cart item not found'
            if quantity > int(row['stock']): return False, 'Quantity exceeds available stock'
            cur.execute('UPDATE cart SET quantity=%s WHERE cartid=%s AND userid=%s', (quantity, cartid, userid))
            db.commit()
            return True, 'Quantity updated'
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            cur.close()
            db.close()

    @staticmethod
    def removeCartItem(cartid, userid):
        db = DatabaseConnection(); cur = db.cursor()
        try:
            cur.execute('DELETE FROM cart WHERE cartid=%s AND userid=%s', (cartid, userid))
            deleted = cur.rowcount
            db.commit(); return deleted > 0, ('Item removed' if deleted else 'Item not found')
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            cur.close()
            db.close()

    @staticmethod
    def getUser(userid):
        db = DatabaseConnection()
        cur = db.cursor(dictionary=True)
        try:
            cur.execute('''SELECT userid,username,email,phone,gender,dateofbirth,
                           profilename,profilepath,is_active,created_at
                           FROM users WHERE userid=%s''', (userid,))
            return True, cur.fetchone()
        finally:
            cur.close()
            db.close()

    @staticmethod
    def getOrders(userid):
        db = DatabaseConnection()
        cur = db.cursor(dictionary=True)

        try:
            query = '''SELECT
                        o.orderid AS id,
                        o.status,
                        o.total AS total_amount,
                        o.address,
                        o.created_at,
                        p.method AS payment_method,
                        p.status AS payment_status,
                        p.razorpay_payment_id AS payment_id
                    FROM orders o
                    LEFT JOIN payments p ON o.orderid = p.orderid
                    WHERE o.userid = %s
                    ORDER BY o.created_at DESC'''

            cur.execute(query, (userid,))
            return True, cur.fetchall()

        except Exception as e:
            return False, str(e)

        finally:
            cur.close()
            db.close()

    @staticmethod
    def getOrderDetails(orderid, userid):
        db = DatabaseConnection()
        cur = db.cursor(dictionary=True)

        try:
            query = '''SELECT
                        o.*,
                        o.orderid AS id,
                        p.method AS payment_method,
                        p.status AS payment_status,
                        p.razorpay_payment_id AS payment_id,
                        p.razorpay_order_id,
                        p.amount AS total_amount,
                        u.username AS customer_name,
                        u.phone AS customer_phone
                    FROM orders o
                    JOIN users u ON u.userid = o.userid
                    LEFT JOIN payments p ON p.orderid = o.orderid
                    WHERE o.orderid = %s AND o.userid = %s'''

            cur.execute(query, (orderid, userid))
            order = cur.fetchone()

            if not order:
                return False, "Order not found"

            query = '''SELECT
                        od.*,
                        p.productname AS product_name,
                        p.storedpath AS image,
                        p.category
                    FROM order_details od
                    JOIN products p ON p.productid = od.productid
                    WHERE od.orderid = %s'''

            cur.execute(query, (orderid,))
            order['items'] = cur.fetchall()

            # Calculate subtotal
            order['subtotal'] = sum(
                float(item['subtotal']) for item in order['items']
            )

            # Calculate actual shipping charge
            order['shipping'] = (
                float(order['total']) - order['subtotal']
            )

            order['delivery_address'] = order.get('address')

            return True, order

        except Exception as e:
            return False, str(e)

        finally:
            cur.close()
            db.close()

    @staticmethod
    def markPaid(userid, orderid, razorpay_order_id, payment_id):

        db = DatabaseConnection()
        cur = db.cursor(dictionary=True)

        try:
            db.start_transaction()

            query = '''SELECT *
                    FROM payments
                    WHERE orderid = %s
                    AND userid = %s
                    AND method = 'RAZORPAY'
                    FOR UPDATE'''

            cur.execute(query, (orderid, userid))
            payment = cur.fetchone()

            if not payment:
                db.rollback()
                return False, "Payment record not found"

            if payment['status'] == 'paid':
                db.rollback()
                return False, "Payment already verified"

            if payment['razorpay_order_id'] != razorpay_order_id:
                db.rollback()
                return False, "Razorpay order ID mismatch"

            query = '''UPDATE payments
                    SET status = 'paid',
                        razorpay_payment_id = %s
                    WHERE orderid = %s
                    AND userid = %s'''

            cur.execute(query, (payment_id, orderid, userid))

            if cur.rowcount != 1:
                db.rollback()
                return False, "Could not update payment status"

            # Remove cart items after successful verification
            cur.execute(
                "DELETE FROM cart WHERE userid = %s",
                (userid,)
            )

            db.commit()

            return True, "Payment verified successfully"

        except Exception as e:
            db.rollback()
            return False, str(e)

        finally:
            cur.close()
            db.close()



    @staticmethod
    def failPayment(userid, orderid, reason='Payment failed'):

        db = DatabaseConnection()
        cur = db.cursor(dictionary=True)

        try:
            db.start_transaction()

            # Get payment details
            query = '''SELECT *
                    FROM payments
                    WHERE orderid = %s
                    AND userid = %s
                    AND method = 'RAZORPAY'
                    FOR UPDATE'''

            cur.execute(query, (orderid, userid))
            payment = cur.fetchone()

            if not payment:
                db.rollback()
                return False, "Payment record not found"

            if payment['status'] == 'paid':
                db.rollback()
                return False, "This order is already paid"

            if payment['status'] == 'failed':
                db.rollback()
                return True, "Payment already marked as failed"

            # Restore product stock
            query = '''SELECT productid, quantity
                    FROM order_details
                    WHERE orderid = %s'''

            cur.execute(query, (orderid,))
            items = cur.fetchall()

            for item in items:
                query = '''UPDATE products
                        SET quantity = quantity + %s
                        WHERE productid = %s'''

                cur.execute(query, (
                    item['quantity'],
                    item['productid']
                ))

            # Update payment status
            query = '''UPDATE payments
                    SET status = 'failed'
                    WHERE orderid = %s AND userid = %s'''

            cur.execute(query, (orderid, userid))

            # Cancel order
            query = '''UPDATE orders
                    SET status = 'cancelled'
                    WHERE orderid = %s AND userid = %s'''

            cur.execute(query, (orderid, userid))

            db.commit()

            return True, "Payment failed and order cancelled"

        except Exception as e:
            db.rollback()
            return False, str(e)

        finally:
            cur.close()
            db.close()


    @staticmethod
    def cancelPendingOrder(userid, orderid):

        return UserQueries.failPayment(
            userid,
            orderid,
            "Customer cancelled payment"
        )
    # @staticmethod
    # def failPayment(userid, orderid, reason='Payment failed'):
    #     """Mark online payment failed and release the stock reserved for that order."""
    #     db = DatabaseConnction()
    #     cur = db.cursor(dictionary=True)
    #     try:
    #         cur.execute('''SELECT orderid,payment_status,status FROM orders
    #                        WHERE orderid=%s AND userid=%s AND payment_method='RAZORPAY' FOR UPDATE''',
    #                     (orderid, userid))
    #         order = cur.fetchone()
    #         if not order: 
    #             return False, 'Order not found'
    #         if order['payment_status'] == 'paid': return False, 'This order is already paid'
    #         if order['status'] == 'cancelled': return True, 'Payment already marked as failed'

    #         cur.execute('SELECT productid,quantity FROM order_details WHERE orderid=%s', (orderid,))
    #         lines = cur.fetchall()
    #         for line in lines:
    #             cur.execute('UPDATE products SET quantity=quantity+%s WHERE productid=%s',
    #                         (line['quantity'], line['productid']))

    #         cur.execute('''UPDATE orders SET status='cancelled',payment_status='failed'
    #                        WHERE orderid=%s AND userid=%s''', (orderid, userid))
    #         cur.execute('''UPDATE transactions SET status='failed',failure_reason=%s
    #                        WHERE orderid=%s AND status='pending' ''', (reason[:255], orderid))
    #         cur.execute('''UPDATE payments SET status='failed' WHERE orderid=%s AND status='pending' ''', (orderid,))
    #         db.commit()
    #         return True, 'Payment failed and order was cancelled'
    #     except Exception as e:
    #         db.rollback()
    #         return False, str(e)
    #     finally:
    #         cur.close()
    #         db.close()

    # @staticmethod
    # def cancelPendingOrder(userid, orderid):
    #     return UserQueries.failPayment(userid, orderid, 'Customer cancelled payment')

    # @staticmethod
    # def completeCOD(userid, orderid):
    #     db = DatabaseConnction(); 
    #     cur = db.cursor(dictionary=True)
    #     try:
    #         cur.execute('''SELECT orderid,status,payment_status FROM orders
    #                        WHERE orderid=%s AND userid=%s AND payment_method='COD' FOR UPDATE''', (orderid, userid))
    #         order = cur.fetchone()
    #         if not order: 
    #             return False, 'Order not found'
    #         if order['status'] == 'cancelled': 
    #             return False, 'Order is cancelled'

    #         # Stock was already reserved by createOrder().
    #         cur.execute("UPDATE orders SET status='processing',payment_status='pending' WHERE orderid=%s", (orderid,))
    #         cur.execute("UPDATE transactions SET status='pending' WHERE orderid=%s", (orderid,))
    #         cur.execute("UPDATE payments SET status='pending' WHERE orderid=%s", (orderid,))
    #         cur.execute('DELETE FROM cart WHERE userid=%s', (userid,))
    #         db.commit(); return True, 'Order placed successfully'
    #     except Exception as e:
    #         db.rollback(); 
    #         return False, str(e)
    #     finally:
    #         cur.close(); db.close()