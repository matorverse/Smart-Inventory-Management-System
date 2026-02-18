# Smart Inventory & Expiry Management System

A Python + MySQL desktop application for batch-level inventory management with FIFO sales, automated expiry monitoring, and a reporting dashboard.

## Tech Stack
- **GUI**: Python `tkinter` (built-in, no install needed)
- **Database**: MySQL 8.x
- **DB Driver**: `mysql-connector-python`
- **Scheduling**: `schedule`

## Setup Instructions

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up the database
Open MySQL CLI or MySQL Workbench and run in order:
```sql
SOURCE database/schema.sql;
SOURCE database/triggers.sql;
SOURCE database/procedures.sql;
```

### 3. Configure DB connection
Edit `db_config.py` and set your MySQL password:
```python
DB_CONFIG = {
    'password': 'your_password_here',
    ...
}
```

### 4. Run the application
```bash
python main.py
```

## Project Structure
```
SmartInventory/
├── main.py                   # Entry point
├── db_config.py              # DB connection config
├── requirements.txt
├── database/
│   ├── schema.sql            # 7 tables, constraints, indexes
│   ├── triggers.sql          # 3 triggers
│   ├── procedures.sql        # 4 stored procedures
│   └── er_diagram.md         # ER diagram (Mermaid)
├── modules/
│   ├── stock_manager.py      # Inventory & batch operations
│   ├── sales_manager.py      # FIFO sales processing
│   ├── expiry_monitor.py     # Expiry detection & logging
│   ├── reports.py            # All report queries
│   └── scheduler.py          # Background expiry scheduler
└── gui/
    ├── app.py                # Main window & theme
    ├── dashboard_tab.py      # KPI cards + expiring-soon table
    ├── inventory_tab.py      # Inventory view + add forms
    ├── sales_tab.py          # FIFO sale form + sales history
    ├── expiry_tab.py         # Expiry alerts + audit log
    └── reports_tab.py        # 4 report sub-tabs
```

## Database Schema (7 Tables)
| Table | Purpose |
|---|---|
| `categories` | Product classification |
| `suppliers` | Vendor master data |
| `products` | Product master (no stock stored here) |
| `batches` | Per-shipment records with expiry dates |
| `inventory` | Batch-specific stock quantities |
| `sales` | FIFO-linked sale transactions |
| `expiry_log` | Permanent audit trail for expired stock |

## Key Features
- **FIFO Sales**: Automatically sells from the oldest non-expired batch
- **Batch Tracking**: Every stock arrival is a separate batch with its own expiry
- **Expiry Monitoring**: Daily background check + manual trigger
- **Audit Trail**: Expired stock is logged, never deleted
- **Reports**: Low stock, inventory valuation, sales summary, waste report