"""
Smart Inventory & Expiry Management System
FILE: modules/sales_manager.py
PURPOSE: FIFO sale processing and sales history queries.
"""

from mysql.connector import Error
from db_config import get_connection, close_connection
from modules.error_handler import handle_db_error


def process_sale(product_id, quantity, selling_price):
    """Calls sp_fifo_sale to process a FIFO sale."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('sp_fifo_sale', [product_id, quantity, selling_price])
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


def get_sales_history(from_date=None, to_date=None):
    """Returns sales records with product, batch, and profit details."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT
                s.sale_id,
                p.product_name,
                c.category_name,
                s.batch_id,
                b.expiry_date,
                s.quantity_sold,
                s.sale_date,
                s.selling_price,
                ROUND(s.quantity_sold * s.selling_price, 2)              AS revenue,
                ROUND(s.quantity_sold * b.cost_price,    2)              AS cost,
                ROUND((s.selling_price - b.cost_price) * s.quantity_sold, 2) AS profit
            FROM      sales      s
            JOIN      products   p ON p.product_id  = s.product_id
            JOIN      categories c ON c.category_id = p.category_id
            JOIN      batches    b ON b.batch_id     = s.batch_id
        """
        params = []
        conditions = []
        if from_date:
            conditions.append("s.sale_date >= %s")
            params.append(from_date)
        if to_date:
            conditions.append("s.sale_date <= %s")
            params.append(to_date)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY s.sale_date DESC, s.sale_id DESC"
        cursor.execute(query, params)
        return cursor.fetchall()
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)


def get_today_sales_summary():
    """Returns today's transaction count, units sold, and revenue."""
    conn = get_connection()
    if not conn:
        raise Exception("Cannot connect to database.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                COUNT(*)                                                   AS transactions,
                COALESCE(SUM(quantity_sold), 0)                            AS units_sold,
                COALESCE(ROUND(SUM(quantity_sold * selling_price), 2), 0)  AS revenue
            FROM sales
            WHERE sale_date = CURDATE()
        """)
        return cursor.fetchone()
    except Error as e:
        handle_db_error(e)
    finally:
        cursor.close()
        close_connection(conn)
