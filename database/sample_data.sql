-- ============================================================
-- Smart Inventory & Expiry Management System
-- FILE: database/sample_data.sql
-- THEME: Pharmacy / Medical Store
-- Run AFTER schema.sql, triggers.sql, procedures.sql
-- ============================================================

USE smart_inventory;

-- ============================================================
-- Additional categories
-- ============================================================
INSERT IGNORE INTO categories (category_name) VALUES
    ('Antihistamines & Allergy'),
    ('Cough & Cold'),
    ('Diabetes & Cardiac'),
    ('Eye & Ear Drops'),
    ('Injections & IV');

-- ============================================================
-- Additional suppliers (pharma distributors)
-- ============================================================
INSERT IGNORE INTO suppliers (supplier_name, phone, email) VALUES
    ('Dr. Reddy Wholesale Dist.',  '9001122334', 'orders@drreddy-dist.in'),
    ('Mankind Pharma Supply',      '9112233445', 'supply@mankind.in'),
    ('Lupin Healthcare Dist.',     '9223344556', 'orders@lupin-dist.in'),
    ('Zydus MedSupply',            '9334455667', 'zydus@medsupply.in'),
    ('Alkem Laboratories Dist.',   '9445566778', 'alkem@dist.in');

-- ============================================================
-- Additional products (pharmacy drugs & medicines)
-- ============================================================
INSERT IGNORE INTO products (product_name, category_id, reorder_level) VALUES
    -- Analgesics & Antipyretics (cat 1)
    ('Ibuprofen 400mg',              1, 80),
    ('Aspirin 75mg',                 1, 60),
    ('Diclofenac 50mg',              1, 50),

    -- Antibiotics (cat 2)
    ('Azithromycin 500mg',           2, 40),
    ('Ciprofloxacin 500mg',          2, 45),
    ('Metronidazole 400mg',          2, 50),

    -- Vitamins & Supplements (cat 3)
    ('Vitamin D3 60K IU',            3, 70),
    ('Calcium + D3 Tablet',          3, 60),
    ('Multivitamin Tablet',          3, 80),

    -- Antacids & GI (cat 4)
    ('Omeprazole 20mg',              4, 55),
    ('Domperidone 10mg',             4, 50),
    ('ORS Powder Sachet',            4, 100),

    -- Topical & Antiseptics (cat 5)
    ('Clotrimazole Cream 15g',       5, 30),
    ('Mupirocin Ointment 5g',        5, 25),

    -- Antihistamines & Allergy (cat 6)
    ('Cetirizine 10mg',              6, 70),
    ('Loratadine 10mg',              6, 50),

    -- Cough & Cold (cat 7)
    ('Ambroxol Syrup 100ml',         7, 40),
    ('Dextromethorphan 15mg',        7, 35),

    -- Diabetes & Cardiac (cat 8)
    ('Metformin 500mg',              8, 60),
    ('Atorvastatin 10mg',            8, 55),
    ('Amlodipine 5mg',               8, 50),

    -- Eye & Ear Drops (cat 9)
    ('Ciprofloxacin Eye Drops 5ml',  9, 30),
    ('Moxifloxacin Eye Drops 5ml',   9, 25),

    -- Injections & IV (cat 10)
    ('Insulin Regular 10ml Vial',   10, 20),
    ('Normal Saline 500ml',         10, 30);

-- ============================================================
-- BATCHES — Normal healthy stock
-- sp_add_batch(product_id, supplier_id, mfg_date, exp_date, cost, qty)
-- ============================================================

-- Paracetamol 500mg (product 1)
CALL sp_add_batch(1, 1, '2025-06-01', '2027-06-01',  2.50, 500);
CALL sp_add_batch(1, 2, '2025-10-01', '2027-10-01',  2.40, 300);

-- Amoxicillin 250mg (product 2)
CALL sp_add_batch(2, 2, '2025-07-01', '2027-07-01',  8.00, 200);
CALL sp_add_batch(2, 4, '2025-11-01', '2027-11-01',  7.80, 150);

-- Vitamin C 500mg (product 3)
CALL sp_add_batch(3, 1, '2025-08-01', '2027-08-01',  4.00, 400);

-- Pantoprazole 40mg (product 4)
CALL sp_add_batch(4, 3, '2025-09-01', '2027-09-01',  6.50, 250);

-- Betadine Solution (product 5)
CALL sp_add_batch(5, 1, '2025-05-01', '2027-05-01', 45.00, 120);

-- Ibuprofen 400mg (product 6)
CALL sp_add_batch(6, 4, '2025-10-01', '2027-10-01',  3.20, 350);

-- Azithromycin 500mg (product 9)
CALL sp_add_batch(9, 2, '2025-11-01', '2027-11-01', 28.00, 180);

-- Vitamin D3 60K IU (product 12)
CALL sp_add_batch(12, 1, '2025-09-01', '2027-09-01', 18.00, 220);

-- Omeprazole 20mg (product 15)
CALL sp_add_batch(15, 3, '2025-10-01', '2027-10-01',  5.00, 300);

-- ORS Powder Sachet (product 17)
CALL sp_add_batch(17, 5, '2025-12-01', '2027-12-01',  3.50, 500);

-- Cetirizine 10mg (product 19)
CALL sp_add_batch(19, 4, '2025-08-01', '2027-08-01',  2.80, 400);

-- Metformin 500mg (product 22)
CALL sp_add_batch(22, 3, '2025-07-01', '2027-07-01',  4.50, 280);

-- Atorvastatin 10mg (product 23)
CALL sp_add_batch(23, 2, '2025-09-01', '2027-09-01', 12.00, 200);

-- Insulin Regular 10ml Vial (product 29)
CALL sp_add_batch(29, 1, '2026-01-01', '2027-01-01', 180.00, 60);

-- Normal Saline 500ml (product 30)
CALL sp_add_batch(30, 5, '2025-11-01', '2027-11-01',  22.00, 150);

-- ============================================================
-- BATCHES — Expiring SOON (within 7 days of 2026-02-18)
-- ============================================================
CALL sp_add_batch(1,  2, '2025-02-01', '2026-02-20',  2.50,  40);  -- Paracetamol  (2 days)
CALL sp_add_batch(3,  1, '2025-02-01', '2026-02-22',  4.00,  25);  -- Vitamin C    (4 days)
CALL sp_add_batch(6,  4, '2025-02-01', '2026-02-19',  3.20,  60);  -- Ibuprofen    (1 day)
CALL sp_add_batch(19, 4, '2025-01-01', '2026-02-24',  2.80,  15);  -- Cetirizine   (6 days)
CALL sp_add_batch(4,  3, '2025-01-15', '2026-02-23',  6.50,  10);  -- Pantoprazole (5 days)

-- ============================================================
-- BATCHES — LOW STOCK (well below reorder level)
-- ============================================================
CALL sp_add_batch(2,  2, '2025-10-01', '2027-10-01',  8.00,   5);  -- Amoxicillin  (reorder=50)
CALL sp_add_batch(29, 1, '2025-12-01', '2026-12-01', 180.00,  3);  -- Insulin      (reorder=20)
CALL sp_add_batch(23, 2, '2025-08-01', '2027-08-01', 12.00,   4);  -- Atorvastatin (reorder=55)

-- ============================================================
-- BATCHES — Already EXPIRED (for expiry log demo)
-- Insert directly to bypass trigger date check, then log them
-- ============================================================
INSERT INTO batches (product_id, supplier_id, manufacture_date, expiry_date, cost_price)
VALUES (1, 1, '2023-01-01', '2024-01-01', 2.20);   -- Old Paracetamol batch
SET @eb1 = LAST_INSERT_ID();
UPDATE inventory SET quantity_available = 80 WHERE batch_id = @eb1;

INSERT INTO batches (product_id, supplier_id, manufacture_date, expiry_date, cost_price)
VALUES (2, 2, '2023-06-01', '2024-06-01', 7.50);   -- Old Amoxicillin batch
SET @eb2 = LAST_INSERT_ID();
UPDATE inventory SET quantity_available = 45 WHERE batch_id = @eb2;

INSERT INTO batches (product_id, supplier_id, manufacture_date, expiry_date, cost_price)
VALUES (5, 1, '2023-03-01', '2024-03-01', 42.00);  -- Old Betadine batch
SET @eb3 = LAST_INSERT_ID();
UPDATE inventory SET quantity_available = 20 WHERE batch_id = @eb3;

INSERT INTO batches (product_id, supplier_id, manufacture_date, expiry_date, cost_price)
VALUES (29, 1, '2023-09-01', '2024-09-01', 170.00); -- Old Insulin batch
SET @eb4 = LAST_INSERT_ID();
UPDATE inventory SET quantity_available = 12 WHERE batch_id = @eb4;

-- Log all expired batches → expiry_log, zero inventory
CALL sp_check_expiry();

-- ============================================================
-- SALES — FIFO sales across various products
-- ============================================================
CALL sp_fifo_sale(1,  120, 5.00);    -- Paracetamol
CALL sp_fifo_sale(2,   40, 18.00);   -- Amoxicillin
CALL sp_fifo_sale(3,   80, 9.00);    -- Vitamin C
CALL sp_fifo_sale(4,   60, 14.00);   -- Pantoprazole
CALL sp_fifo_sale(5,   25, 90.00);   -- Betadine
CALL sp_fifo_sale(6,   90, 7.50);    -- Ibuprofen
CALL sp_fifo_sale(9,   50, 55.00);   -- Azithromycin
CALL sp_fifo_sale(12,  70, 38.00);   -- Vitamin D3
CALL sp_fifo_sale(15,  80, 12.00);   -- Omeprazole
CALL sp_fifo_sale(17, 150, 8.00);    -- ORS Sachet
CALL sp_fifo_sale(19, 100, 6.00);    -- Cetirizine
CALL sp_fifo_sale(22,  60, 10.00);   -- Metformin
CALL sp_fifo_sale(23,  30, 28.00);   -- Atorvastatin
CALL sp_fifo_sale(30,  40, 50.00);   -- Normal Saline

-- A few repeat sales to build richer history
CALL sp_fifo_sale(1,   50, 5.00);
CALL sp_fifo_sale(4,   30, 14.00);
CALL sp_fifo_sale(19,  40, 6.00);
CALL sp_fifo_sale(22,  20, 10.00);

-- ============================================================
-- Verification — row counts per table
-- ============================================================
SELECT 'categories' AS tbl, COUNT(*) AS row_count FROM categories
UNION ALL SELECT 'suppliers',  COUNT(*) FROM suppliers
UNION ALL SELECT 'products',   COUNT(*) FROM products
UNION ALL SELECT 'batches',    COUNT(*) FROM batches
UNION ALL SELECT 'inventory',  COUNT(*) FROM inventory
UNION ALL SELECT 'sales',      COUNT(*) FROM sales
UNION ALL SELECT 'expiry_log', COUNT(*) FROM expiry_log;
