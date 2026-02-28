"""
Smart Inventory & Expiry Management System
FILE: modules/expiry_monitor.py
PURPOSE: Expiry detection, alerting, and audit logging.
"""

from mysql.connector import Error
from db_config import get_connection, close_connection
from modules.error_handler import handle_db_error


def run_expiry_check():
    """
    Calls sp_check_expiry to log expired stock and zero inventory.
    Returns number of batches processed.
    """
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('sp_check_expiry')
        result = None
        for res in cursor.stored_results():
            result = res.fetchone()
        conn.commit()
        return result.get('expired_batches_logged', 0) if result else 0
    except Error as e:
        conn.rollback()
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def get_expiring_soon(days=7):
    """
    Returns batches expiring within the next `days` days
    that still have stock available.
    """
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                b.batch_id,
                p.product_name,
                c.category_name,
                s.supplier_name,
                b.expiry_date,
                i.quantity_available,
                DATEDIFF(b.expiry_date, CURDATE()) AS days_left
            FROM      batches    b
            JOIN      products   p ON p.product_id  = b.product_id
            JOIN      categories c ON c.category_id = p.category_id
            JOIN      suppliers  s ON s.supplier_id = b.supplier_id
            JOIN      inventory  i ON i.batch_id    = b.batch_id
            WHERE  b.expiry_date >= CURDATE()
              AND  b.expiry_date <= DATE_ADD(CURDATE(), INTERVAL %s DAY)
              AND  i.quantity_available > 0
            ORDER BY b.expiry_date ASC
        """, (days,))
        return cursor.fetchall()
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def get_expiry_log():
    """Returns the full expiry audit log with product details."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                el.expiry_id,
                el.batch_id,
                p.product_name,
                c.category_name,
                el.quantity_expired,
                el.expiry_date,
                el.logged_on,
                ROUND(el.quantity_expired * b.cost_price, 2) AS waste_value
            FROM      expiry_log  el
            JOIN      batches     b  ON b.batch_id    = el.batch_id
            JOIN      products    p  ON p.product_id  = b.product_id
            JOIN      categories  c  ON c.category_id = p.category_id
            ORDER BY  el.logged_on DESC
        """)
        return cursor.fetchall()
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def get_expiry_summary():
    """Returns KPI counts: expiring_soon, already_expired_with_stock."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN b.expiry_date >= CURDATE()
                          AND b.expiry_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
                          AND i.quantity_available > 0 THEN 1 ELSE 0 END), 0) AS expiring_soon,
                COALESCE(SUM(CASE WHEN b.expiry_date < CURDATE()
                          AND i.quantity_available > 0 THEN 1 ELSE 0 END), 0) AS expired_with_stock
            FROM batches b
            JOIN inventory i ON i.batch_id = b.batch_id
        """)
        return cursor.fetchone()
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)
