-- ============================================================
-- Smart Inventory & Expiry Management System
-- FILE: database/er_diagram.md
-- Render in VS Code Markdown Preview or GitHub
-- ============================================================

# Smart Inventory — ER Diagram

```mermaid
erDiagram
    CATEGORIES {
        INT category_id PK
        VARCHAR category_name
    }
    SUPPLIERS {
        INT supplier_id PK
        VARCHAR supplier_name
        VARCHAR phone
        VARCHAR email
    }
    PRODUCTS {
        INT product_id PK
        VARCHAR product_name
        INT category_id FK
        INT reorder_level
    }
    BATCHES {
        INT batch_id PK
        INT product_id FK
        INT supplier_id FK
        DATE manufacture_date
        DATE expiry_date
        DECIMAL cost_price
    }
    INVENTORY {
        INT inventory_id PK
        INT batch_id FK
        INT quantity_available
    }
    SALES {
        INT sale_id PK
        INT product_id FK
        INT batch_id FK
        INT quantity_sold
        DATE sale_date
        DECIMAL selling_price
    }
    EXPIRY_LOG {
        INT expiry_id PK
        INT batch_id
        INT quantity_expired
        DATE expiry_date
        TIMESTAMP logged_on
    }

    CATEGORIES ||--o{ PRODUCTS   : "classifies"
    SUPPLIERS  ||--o{ BATCHES    : "supplies"
    PRODUCTS   ||--o{ BATCHES    : "has batches"
    BATCHES    ||--|| INVENTORY  : "tracked in"
    PRODUCTS   ||--o{ SALES      : "sold via"
    BATCHES    ||--o{ SALES      : "deducted from"
    BATCHES    ||--o{ EXPIRY_LOG : "logged in"
```
