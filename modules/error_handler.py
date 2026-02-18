"""
Smart Inventory & Expiry Management System
FILE: modules/error_handler.py
PURPOSE: Custom exceptions and DB error parsing.
"""


class SmartInventoryError(Exception):
    pass

class InsufficientStockError(SmartInventoryError):
    pass

class ExpiredBatchError(SmartInventoryError):
    pass

class InvalidInputError(SmartInventoryError):
    pass

class DatabaseError(SmartInventoryError):
    pass


def handle_db_error(e):
    """Maps MySQL SIGNAL errors to typed Python exceptions."""
    msg = str(e)
    lower = msg.lower()
    if 'expired' in lower:
        raise ExpiredBatchError(f"Batch has expired: {msg}")
    elif 'insufficient' in lower:
        raise InsufficientStockError(f"Not enough stock: {msg}")
    elif 'quantity' in lower or 'price' in lower or 'date' in lower:
        raise InvalidInputError(f"Invalid input: {msg}")
    else:
        raise DatabaseError(f"Database error: {msg}")
