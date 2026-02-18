"""
Smart Inventory & Expiry Management System
FILE: modules/reports.py
PURPOSE: All reporting queries — low stock, valuation, sales summary, waste.
"""

from mysql.connector import Error
from db_config import get_connection, close_connection
from modules.error_handler import handle_db_error


def get_low_stock_report():
    """Returns products below reorder level (calls sp_get_low_stock)."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('sp_get_low_stock')
        result = []
        for res in cursor.stored_results():
            result = res.fetchall()
        return result
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def get_inventory_valuation():
    """
    Returns inventory value per product:
    SUM(quantity_available * cost_price) for non-expired batches.
    """
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                p.product_id,
                p.product_name,
                c.category_name,
                COALESCE(SUM(i.quantity_available), 0)                          AS total_units,
                COALESCE(ROUND(SUM(i.quantity_available * b.cost_price), 2), 0) AS stock_value
            FROM      products   p
            JOIN      categories c ON c.category_id = p.category_id
            LEFT JOIN batches    b ON b.product_id  = p.product_id
                                  AND b.expiry_date >= CURDATE()
            LEFT JOIN inventory  i ON i.batch_id    = b.batch_id
            GROUP BY  p.product_id, p.product_name, c.category_name
            ORDER BY  stock_value DESC
        """)
        return cursor.fetchall()
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def get_sales_summary():
    """
    Returns sales summary grouped by product:
    total units sold, total revenue, total cost, total profit.
    """
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                p.product_name,
                c.category_name,
                SUM(s.quantity_sold)                                          AS units_sold,
                ROUND(SUM(s.quantity_sold * s.selling_price), 2)              AS revenue,
                ROUND(SUM(s.quantity_sold * b.cost_price),    2)              AS cost,
                ROUND(SUM((s.selling_price - b.cost_price) * s.quantity_sold), 2) AS profit
            FROM      sales      s
            JOIN      products   p ON p.product_id  = s.product_id
            JOIN      categories c ON c.category_id = p.category_id
            JOIN      batches    b ON b.batch_id     = s.batch_id
            GROUP BY  p.product_id, p.product_name, c.category_name
            ORDER BY  revenue DESC
        """)
        return cursor.fetchall()
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def get_waste_report():
    """
    Returns waste summary from expiry_log:
    total units wasted and waste value per product.
    """
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                p.product_name,
                c.category_name,
                SUM(el.quantity_expired)                                   AS total_wasted,
                ROUND(SUM(el.quantity_expired * b.cost_price), 2)          AS waste_value
            FROM      expiry_log  el
            JOIN      batches     b ON b.batch_id    = el.batch_id
            JOIN      products    p ON p.product_id  = b.product_id
            JOIN      categories  c ON c.category_id = p.category_id
            GROUP BY  p.product_id, p.product_name, c.category_name
            ORDER BY  waste_value DESC
        """)
        return cursor.fetchall()
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def get_dashboard_kpis():
    """Returns all KPI values for the dashboard home screen."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM products)                                AS total_products,
                (SELECT COUNT(*) FROM suppliers)                               AS total_suppliers,
                (SELECT COALESCE(SUM(i.quantity_available), 0)
                 FROM inventory i
                 JOIN batches b ON b.batch_id = i.batch_id
                 WHERE b.expiry_date >= CURDATE())                             AS total_stock,
                (SELECT COUNT(*) FROM (
                    SELECT p.product_id
                    FROM products p
                    LEFT JOIN batches b ON b.product_id = p.product_id
                                       AND b.expiry_date >= CURDATE()
                    LEFT JOIN inventory i ON i.batch_id = b.batch_id
                    GROUP BY p.product_id, p.reorder_level
                    HAVING COALESCE(SUM(i.quantity_available), 0) < p.reorder_level
                 ) AS low_stock_sub)                                           AS low_stock_count,
                (SELECT COUNT(*) FROM batches b
                 JOIN inventory i ON i.batch_id = b.batch_id
                 WHERE b.expiry_date >= CURDATE()
                   AND b.expiry_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
                   AND i.quantity_available > 0)                               AS expiring_soon,
                (SELECT COALESCE(ROUND(SUM(quantity_sold * selling_price),2),0)
                 FROM sales WHERE sale_date = CURDATE())                       AS today_revenue
        """)
        return cursor.fetchone()
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)
