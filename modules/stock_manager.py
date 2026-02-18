"""
Smart Inventory & Expiry Management System
FILE: modules/stock_manager.py
PURPOSE: Add batches, view inventory, lookup products/suppliers/categories.
"""

from mysql.connector import Error
from db_config import get_connection, close_connection
from modules.error_handler import handle_db_error


def add_batch(product_id, supplier_id, mfg_date, exp_date, cost_price, quantity):
    """Calls sp_add_batch to atomically add a batch + set inventory."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('sp_add_batch',
                        [product_id, supplier_id, mfg_date, exp_date, cost_price, quantity])
        result = None
        for res in cursor.stored_results():
            result = res.fetchone()
        conn.commit()
        return result
    except Error as e:
        conn.rollback()
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def get_all_inventory():
    """Returns all inventory rows with product, supplier, expiry status."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                i.inventory_id,
                i.batch_id,
                p.product_id,
                p.product_name,
                c.category_name,
                s.supplier_name,
                b.manufacture_date,
                b.expiry_date,
                b.cost_price,
                i.quantity_available,
                CASE
                    WHEN b.expiry_date < CURDATE()
                        THEN 'Expired'
                    WHEN b.expiry_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
                        THEN 'Expiring Soon'
                    ELSE 'OK'
                END AS expiry_status
            FROM      inventory  i
            JOIN      batches    b ON b.batch_id    = i.batch_id
            JOIN      products   p ON p.product_id  = b.product_id
            JOIN      categories c ON c.category_id = p.category_id
            JOIN      suppliers  s ON s.supplier_id = b.supplier_id
            ORDER BY  b.expiry_date ASC, p.product_name ASC
        """)
        return cursor.fetchall()
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def get_product_stock(product_id):
    """Returns total non-expired available stock for a product."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(i.quantity_available), 0)
            FROM   batches   b
            JOIN   inventory i ON i.batch_id = b.batch_id
            WHERE  b.product_id        = %s
              AND  b.expiry_date      >= CURDATE()
              AND  i.quantity_available > 0
        """, (product_id,))
        row = cursor.fetchone()
        return int(row[0]) if row else 0
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def get_all_products():
    """Returns all products with category name."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.product_id, p.product_name, c.category_name, p.reorder_level
            FROM   products   p
            JOIN   categories c ON c.category_id = p.category_id
            ORDER BY p.product_name ASC
        """)
        return cursor.fetchall()
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def get_all_suppliers():
    """Returns all suppliers."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM suppliers ORDER BY supplier_name ASC")
        return cursor.fetchall()
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def get_all_categories():
    """Returns all categories."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories ORDER BY category_name ASC")
        return cursor.fetchall()
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def add_product(product_name, category_id, reorder_level):
    """Inserts a new product."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (product_name, category_id, reorder_level) VALUES (%s, %s, %s)",
            (product_name, category_id, reorder_level)
        )
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        conn.rollback()
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def add_supplier(supplier_name, phone, email):
    """Inserts a new supplier."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO suppliers (supplier_name, phone, email) VALUES (%s, %s, %s)",
            (supplier_name, phone, email)
        )
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        conn.rollback()
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def add_category(category_name):
    """Inserts a new category."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categories (category_name) VALUES (%s)",
            (category_name,)
        )
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        conn.rollback()
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)
