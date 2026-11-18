
from database.connection import DatabaseConnection
from psycopg2.extras import RealDictCursor
from decimal import Decimal

class UserQueries:

    # 1. Add item to cart
    @staticmethod
    def addCartItem(product_id: int, userid: int, quantity: int):
        db_config = cursor = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                UPDATE cart
                SET quantity = quantity + %s
                WHERE productid = %s AND userid = %s
            """
            cursor.execute(query, (quantity, product_id, userid))

            if cursor.rowcount:
                db_config.commit()
                return True, "Cart Item Quantity Updated"

            query = """
                INSERT INTO cart (userid, productid, quantity)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (userid, product_id, quantity))

            db_config.commit()
            return True, "Item added to cart"

        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Error adding cart item: {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # 2. Get cart items
    @staticmethod
    def getCartItems(userid: int):
        db_config = cursor = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(cursor_factory=RealDictCursor)

            query = """SELECT
                    c.cartid,
                    c.quantity,
                    p.productid,
                    p.productname,
                    p.category,
                    p.saleprice,
                    p.quantity AS stock,
                    p.imgname,
                    p.storedpath,
                    (c.quantity * p.saleprice) AS subtotal FROM cart c

                    JOIN products p
                    ON c.productid = p.productid

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

    # 3. Update cart quantity
    @staticmethod
    def updateCartQuantity(cartid: int, quantity: int, userid: int):
        db_config = cursor = None

        try:
            quantity = int(quantity)

            if quantity < 1:
                return False, "Quantity must be at least 1"

            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                SELECT cartid
                FROM cart
                WHERE cartid = %s AND userid = %s
            """
            cursor.execute(query, (cartid, userid))

            data = cursor.fetchone()

            if not data:
                return False, "Cart item not found"

            query = """
                SELECT p.quantity AS stock
                FROM cart c
                JOIN products p ON p.productid = c.productid
                WHERE c.cartid = %s AND c.userid = %s
            """
            cursor.execute(query, (cartid, userid))
            stock = cursor.fetchone()

            if quantity > stock[0]:
                return False, "Quantity exceeds available stock"

            query = """
                UPDATE cart
                SET quantity = %s
                WHERE cartid = %s AND userid = %s
            """
            cursor.execute(query, (quantity, cartid, userid))

            db_config.commit()
            return True, "Quantity updated"

        except (ValueError, TypeError):
            return False, "Invalid quantity"

        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Error updating cart quantity: {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # 4. Get cart count
    @staticmethod
    def getCartCount(userid: int):
        db_config = cursor = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                SELECT COALESCE(SUM(quantity), 0)
                FROM cart
                WHERE userid = %s
            """
            cursor.execute(query, (userid,))

            data = cursor.fetchone()
            return True, data[0]

        except Exception as e:
            return False, f"Error fetching cart count: {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # 5. Delete cart item
    @staticmethod
    def deleteCartItem(cartid: int):
        db_config = cursor = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor()

            query = """
                DELETE FROM cart
                WHERE cartid = %s
            """
            cursor.execute(query, (cartid,))

            db_config.commit()
            return True, "Item deleted"

        except Exception as e:
            if db_config:
                db_config.rollback()
            return False, f"Error deleting cart item: {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # 6. Create order
    @staticmethod
    def createOrder(
        userid: int,
        address: str,
        payment_method: str,
        razorpay_order_id: str = None,
        razorpay_payment_id: str = None
    ):
        db_config = cursor = None

        try:
            db_config = DatabaseConnection()
            cursor = db_config.cursor(cursor_factory=RealDictCursor)

            # Get cart items
            query = """
                SELECT
                    c.cartid,
                    c.userid,
                    c.quantity,
                    p.productname,
                    p.productid,
                    p.quantity AS stock,
                    p.saleprice
                FROM cart c
                JOIN products p ON c.productid = p.productid
                WHERE c.userid = %s
                FOR UPDATE OF c, p
            """
            cursor.execute(query, (userid,))
            items = cursor.fetchall()

            if not items:
                return False, "Cart is empty"

            # Check stock and calculate subtotal
            sub_total = 0

            for item in items:
                if item['quantity'] > item['stock']:
                    return False, (
                        f"{item['productname']} does not have enough stock"
                    )

                sub_total += item['quantity'] * item['saleprice']

            shipping = sub_total * Decimal("0.01")
            total = sub_total + shipping

            # Reduce product stock
            for item in items:
                query = """
                    UPDATE products
                    SET quantity = quantity - %s
                    WHERE productid = %s
                """
                cursor.execute(
                    query,
                    (item['quantity'], item['productid'])
                )

            # Insert order and get order ID
            query = """
                INSERT INTO orders (userid, status, address, total)
                VALUES (%s, %s, %s, %s)
                RETURNING orderid
            """
            cursor.execute(
                query,
                (userid, "pending", address, total)
            )

            orderid = cursor.fetchone()['orderid']

            # Insert order details
            query = """
                INSERT INTO order_details
                (orderid, productid, quantity, price)
                VALUES (%s, %s, %s, %s)
            """

            for item in items:
                cursor.execute(
                    query,
                    (
                        orderid,
                        item['productid'],
                        item['quantity'],
                        item['saleprice']
                    )
                )

            # Insert payment
            method = payment_method.strip().lower()

            if method == 'cod':
                method = 'cash'

            if method not in ['cash', 'upi', 'netbanking', 'razorpay']:
                raise ValueError("Invalid payment method selected")

            query = """
                INSERT INTO payments
                (
                    userid,
                    orderid,
                    status,
                    method,
                    amount,
                    razorpay_order_id,
                    razorpay_payment_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    userid,
                    orderid,
                    "pending",
                    method,
                    total,
                    razorpay_order_id,
                    razorpay_payment_id
                )
            )

            # Clear cart
            cursor.execute(
                "DELETE FROM cart WHERE userid = %s",
                (userid,)
            )

            db_config.commit()

            return True, {
                "order_id": orderid,
                "amount": total
            }

        except Exception as e:
            if db_config:
                db_config.rollback()

            return False, f"Error creating order: {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # 7. Remove cart item
    @staticmethod
    def removeCartItem(cartid: int, userid: int):
        db = cur = None

        try:
            db = DatabaseConnection()
            cur = db.cursor()

            query = """
                DELETE FROM cart
                WHERE cartid = %s AND userid = %s
            """
            cur.execute(query, (cartid, userid))

            deleted = cur.rowcount
            db.commit()

            return (
                deleted > 0,
                "Item removed" if deleted else "Item not found"
            )

        except Exception as e:
            if db:
                db.rollback()
            return False, str(e)

        finally:
            if cur:
                cur.close()
            if db:
                db.close()

    # 8. Get user details
    @staticmethod
    def getUser(userid: int):
        db = cur = None

        try:
            db = DatabaseConnection()
            cur = db.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT
                    userid, username, email, phone,
                    gender, dateofbirth, profilename,
                    profilepath, is_active, created_at
                FROM users
                WHERE userid = %s
            """
            cur.execute(query, (userid,))

            return True, cur.fetchone()

        except Exception as e:
            return False, str(e)

        finally:
            if cur:
                cur.close()
            if db:
                db.close()

    # 9. Get all user orders
    @staticmethod
    def getOrders(userid: int):
        db = cur = None

        try:
            db = DatabaseConnection()
            cur = db.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT
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
                ORDER BY o.created_at DESC
            """

            cur.execute(query, (userid,))
            return True, cur.fetchall()

        except Exception as e:
            return False, str(e)

        finally:
            if cur:
                cur.close()
            if db:
                db.close()

    # 10. Get single order details
         # 10. Get single order details
    @staticmethod
    def getOrderDetails(orderid: int, userid: int):

        db = cur = None

        try:
            db = DatabaseConnection()
            cur = db.cursor(cursor_factory=RealDictCursor)

           # 1. Get order and payment details
            query = """
            SELECT
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

            JOIN users u
                ON u.userid = o.userid

            LEFT JOIN payments p
                ON p.orderid = o.orderid

            WHERE o.orderid = %s
            AND o.userid = %s
            """

            cur.execute(query, (orderid, userid))

            order = cur.fetchone()

            if not order:
                return False, "Order not found"

        # 2. Get ordered product details
            query = """
            SELECT
                od.*,
                p.productname AS product_name,
                p.storedpath AS image,
                p.imgname,
                p.category,
                (od.quantity * od.price) AS subtotal

            FROM order_details od

            LEFT JOIN products p
                ON p.productid = od.productid

            WHERE od.orderid = %s
            """

            cur.execute(query, (orderid,))

            order['items'] = cur.fetchall()

        # 3. Calculate total items
            order['total_items'] = sum(
            item['quantity']
            for item in order['items']
            )

        # 4. Calculate subtotal
            order['subtotal'] = sum(
            float(item['subtotal'])
            for item in order['items']
            )

        # 5. Calculate shipping
            order['shipping'] = (
            float(order['total']) - order['subtotal']
            )

        # 6. Delivery address
            order['delivery_address'] = order.get('address')

            return True, order

        except Exception as e:

            return False, f"Error fetching order details: {e}"

        finally:

            if cur:
                cur.close()

            if db:
                db.close()

    # 11. Verify Razorpay payment
    @staticmethod
    def markPaid(
        userid: int,
        orderid: int,
        razorpay_order_id: str,
        payment_id: str
    ):
        db = cur = None

        try:
            db = DatabaseConnection()
            cur = db.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT *
                FROM payments
                WHERE orderid = %s
                AND userid = %s
                AND method = 'razorpay'
                FOR UPDATE
            """

            cur.execute(query, (orderid, userid))
            payment = cur.fetchone()

            if not payment:
                return False, "Payment record not found"

            if payment['status'] == 'paid':
                return False, "Payment already verified"

            if payment['razorpay_order_id'] != razorpay_order_id:
                return False, "Razorpay order ID mismatch"

            query = """
                UPDATE payments
                SET status = 'paid',
                    razorpay_payment_id = %s
                WHERE orderid = %s AND userid = %s
            """

            cur.execute(query, (payment_id, orderid, userid))

            if cur.rowcount != 1:
                return False, "Could not update payment status"

            cur.execute(
                "DELETE FROM cart WHERE userid = %s",
                (userid,)
            )

            db.commit()
            return True, "Payment verified successfully"

        except Exception as e:
            if db:
                db.rollback()
            return False, str(e)

        finally:
            if cur:
                cur.close()
            if db:
                db.close()

    # 12. Handle failed Razorpay payment
    @staticmethod
    def failPayment(
        userid: int,
        orderid: int,
        reason: str = 'Payment failed'
    ):
        db = cur = None

        try:
            db = DatabaseConnection()
            cur = db.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT *
                FROM payments
                WHERE orderid = %s
                AND userid = %s
                AND method = 'razorpay'
                FOR UPDATE
            """

            cur.execute(query, (orderid, userid))
            payment = cur.fetchone()

            if not payment:
                return False, "Payment record not found"

            if payment['status'] == 'paid':
                return False, "This order is already paid"

            if payment['status'] == 'failed':
                return True, "Payment already marked as failed"

            # Restore product stock
            query = """
                SELECT productid, quantity
                FROM order_details
                WHERE orderid = %s
            """

            cur.execute(query, (orderid,))
            items = cur.fetchall()

            for item in items:
                query = """
                    UPDATE products
                    SET quantity = quantity + %s
                    WHERE productid = %s
                """
                cur.execute(
                    query,
                    (item['quantity'], item['productid'])
                )

            # Update payment status
            query = """
                UPDATE payments
                SET status = 'failed'
                WHERE orderid = %s AND userid = %s
            """
            cur.execute(query, (orderid, userid))

            # Cancel order
            query = """
                UPDATE orders
                SET status = 'cancelled'
                WHERE orderid = %s AND userid = %s
            """
            cur.execute(query, (orderid, userid))

            db.commit()
            return True, "Payment failed and order cancelled"

        except Exception as e:
            if db:
                db.rollback()
            return False, str(e)

        finally:
            if cur:
                cur.close()
            if db:
                db.close()

    # 13. Cancel pending order
    @staticmethod
    def cancelPendingOrder(userid: int, orderid: int):
        return UserQueries.failPayment(
            userid,
            orderid,
            "Customer cancelled payment"
        )
