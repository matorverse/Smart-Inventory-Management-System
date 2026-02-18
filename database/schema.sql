-- ============================================================
-- Smart Inventory & Expiry Management System
-- FILE: database/schema.sql
-- Run this FIRST before triggers.sql and procedures.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS smart_inventory
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE smart_inventory;

-- ============================================================
-- TABLE 1: categories
-- ============================================================
CREATE TABLE IF NOT EXISTS categories (
    category_id   INT          NOT NULL AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL,
    CONSTRAINT pk_categories  PRIMARY KEY (category_id),
    CONSTRAINT uq_category_name UNIQUE (category_name)
);

-- ============================================================
-- TABLE 2: suppliers
-- ============================================================
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id   INT          NOT NULL AUTO_INCREMENT,
    supplier_name VARCHAR(150) NOT NULL,
    phone         VARCHAR(20),
    email         VARCHAR(100),
    CONSTRAINT pk_suppliers PRIMARY KEY (supplier_id)
);

-- ============================================================
-- TABLE 3: products
-- NOTE: Stock quantity is NEVER stored here.
--       It lives per-batch in the inventory table.
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
    product_id    INT          NOT NULL AUTO_INCREMENT,
    product_name  VARCHAR(150) NOT NULL,
    category_id   INT          NOT NULL,
    reorder_level INT          NOT NULL DEFAULT 10,
    CONSTRAINT pk_products PRIMARY KEY (product_id),
    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_reorder_level CHECK (reorder_level >= 0)
);

-- ============================================================
-- TABLE 4: batches
-- Each stock arrival = one unique batch record
-- ============================================================
CREATE TABLE IF NOT EXISTS batches (
    batch_id         INT           NOT NULL AUTO_INCREMENT,
    product_id       INT           NOT NULL,
    supplier_id      INT           NOT NULL,
    manufacture_date DATE          NOT NULL,
    expiry_date      DATE          NOT NULL,
    cost_price       DECIMAL(10,2) NOT NULL,
    CONSTRAINT pk_batches PRIMARY KEY (batch_id),
    CONSTRAINT fk_batch_product
        FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_batch_supplier
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_expiry_after_mfg CHECK (expiry_date > manufacture_date),
    CONSTRAINT chk_cost_price        CHECK (cost_price >= 0)
);

-- ============================================================
-- TABLE 5: inventory
-- Tracks available stock PER BATCH (not per product)
-- ============================================================
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id       INT NOT NULL AUTO_INCREMENT,
    batch_id           INT NOT NULL,
    quantity_available INT NOT NULL DEFAULT 0,
    CONSTRAINT pk_inventory       PRIMARY KEY (inventory_id),
    CONSTRAINT uq_inventory_batch UNIQUE (batch_id),
    CONSTRAINT fk_inventory_batch
        FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_qty_non_negative CHECK (quantity_available >= 0)
);

-- ============================================================
-- TABLE 6: sales
-- Each row = one FIFO-linked sale transaction
-- ============================================================
CREATE TABLE IF NOT EXISTS sales (
    sale_id       INT           NOT NULL AUTO_INCREMENT,
    product_id    INT           NOT NULL,
    batch_id      INT           NOT NULL,
    quantity_sold INT           NOT NULL,
    sale_date     DATE          NOT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    CONSTRAINT pk_sales PRIMARY KEY (sale_id),
    CONSTRAINT fk_sales_product
        FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_sales_batch
        FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_qty_sold     CHECK (quantity_sold > 0),
    CONSTRAINT chk_selling_price CHECK (selling_price >= 0)
);

-- ============================================================
-- TABLE 7: expiry_log
-- Permanent audit trail — rows are NEVER deleted
-- ============================================================
CREATE TABLE IF NOT EXISTS expiry_log (
    expiry_id        INT       NOT NULL AUTO_INCREMENT,
    batch_id         INT       NOT NULL,
    quantity_expired INT       NOT NULL,
    expiry_date      DATE      NOT NULL,
    logged_on        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_expiry_log PRIMARY KEY (expiry_id),
    CONSTRAINT chk_qty_expired CHECK (quantity_expired > 0)
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_batch_expiry         ON batches(expiry_date);
CREATE INDEX idx_batch_product_expiry ON batches(product_id, expiry_date);
CREATE INDEX idx_inventory_batch      ON inventory(batch_id);
CREATE INDEX idx_sales_product        ON sales(product_id);
CREATE INDEX idx_sales_date           ON sales(sale_date);

-- ============================================================
-- SEED DATA (Pharmacy Theme)
-- ============================================================
INSERT INTO categories (category_name) VALUES
    ('Analgesics & Antipyretics'),
    ('Antibiotics'),
    ('Vitamins & Supplements'),
    ('Antacids & GI'),
    ('Topical & Antiseptics');

INSERT INTO suppliers (supplier_name, phone, email) VALUES
    ('Sun Pharma Distributors',  '9876543210', 'orders@sunpharma.com'),
    ('Cipla MedPro Wholesale',   '9123456780', 'supply@cipla.com'),
    ('Abbott Healthcare Dist.',  '9988776655', 'sales@abbott.in');

INSERT INTO products (product_name, category_id, reorder_level) VALUES
    ('Paracetamol 500mg',   1, 100),
    ('Amoxicillin 250mg',   2,  50),
    ('Vitamin C 500mg',     3,  80),
    ('Pantoprazole 40mg',   4,  60),
    ('Betadine Solution',   5,  40);

-- ============================================================
-- END OF SCHEMA
-- ============================================================
