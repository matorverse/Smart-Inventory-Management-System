"""
Smart Inventory & Expiry Management System
FILE: db_config.py
PURPOSE: Shared DB connection — imported by all modules.
Set your MySQL password in DB_CONFIG below.
"""

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host':       'localhost',
    'user':       'root',
    'password':   'tiger',          # ← Set your MySQL password here
    'database':   'smart_inventory',
    'charset':    'utf8mb4',
    'autocommit': False,
}


def get_connection():
    """Returns an active MySQL connection, or None on failure."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"[DB ERROR] {e}")
        return None


def close_connection(conn):
    """Safely closes a MySQL connection."""
    try:
        if conn and conn.is_connected():
            conn.close()
    except Error:
        pass
