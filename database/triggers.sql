-- ============================================================
-- Smart Inventory & Expiry Management System
-- FILE: database/triggers.sql
-- Run AFTER schema.sql
-- ============================================================

USE smart_inventory;

-- ============================================================
-- TRIGGER 1: trg_after_batch_insert
-- Auto-creates an inventory row (qty=0) for every new batch.
-- sp_add_batch then updates it to the actual quantity.
-- ============================================================
DELIMITER //
CREATE TRIGGER trg_after_batch_insert
AFTER INSERT ON batches
FOR EACH ROW
BEGIN
    INSERT INTO inventory (batch_id, quantity_available)
    VALUES (NEW.batch_id, 0);
END //
DELIMITER ;


-- ============================================================
-- TRIGGER 2: trg_before_sale
-- Guards against selling from an expired batch or selling
-- more than what is available. Last line of defence.
-- ============================================================
DELIMITER //
CREATE TRIGGER trg_before_sale
BEFORE INSERT ON sales
FOR EACH ROW
BEGIN
    DECLARE v_available INT DEFAULT 0;
    DECLARE v_expiry    DATE;

    SELECT i.quantity_available, b.expiry_date
    INTO   v_available, v_expiry
    FROM   inventory i
    JOIN   batches   b ON b.batch_id = i.batch_id
    WHERE  i.batch_id = NEW.batch_id;

    IF v_expiry < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Sale rejected: batch has expired.';
    END IF;

    IF v_available < NEW.quantity_sold THEN
        SIGNAL SQLSTATE '45001'
            SET MESSAGE_TEXT = 'Sale rejected: insufficient stock in batch.';
    END IF;
END //
DELIMITER ;


-- ============================================================
-- TRIGGER 3: trg_after_sale
-- Automatically deducts quantity_sold from inventory
-- after a sale record is successfully inserted.
-- ============================================================
DELIMITER //
CREATE TRIGGER trg_after_sale
AFTER INSERT ON sales
FOR EACH ROW
BEGIN
    UPDATE inventory
    SET    quantity_available = quantity_available - NEW.quantity_sold
    WHERE  batch_id = NEW.batch_id;
END //
DELIMITER ;

-- ============================================================
-- END OF TRIGGERS
-- ============================================================
