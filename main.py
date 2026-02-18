"""
Smart Inventory & Expiry Management System
FILE: main.py
PURPOSE: Application entry point. Run this file to start the GUI.
         Usage: python main.py
"""

import sys
import tkinter as tk
from tkinter import messagebox

# ── Verify DB connection before launching GUI ─────────────────
from db_config import get_connection, close_connection

def check_db():
    conn = get_connection()
    if conn is None:
        messagebox.showerror(
            "Database Connection Failed",
            "Could not connect to MySQL.\n\n"
            "Please check:\n"
            "  1. MySQL server is running\n"
            "  2. Your password in db_config.py is correct\n"
            "  3. The 'smart_inventory' database exists\n\n"
            "Run database/schema.sql first if you haven't already."
        )
        return False
    close_connection(conn)
    return True


def main():
    # Quick pre-check before building the full GUI
    root = tk.Tk()
    root.withdraw()  # Hide blank window during check

    if not check_db():
        root.destroy()
        sys.exit(1)

    root.destroy()

    # Launch main application
    from gui.app import SmartInventoryApp
    app = SmartInventoryApp()
    app.mainloop()


if __name__ == '__main__':
    main()
