-- ============================================================
-- Smart Inventory & Expiry Management System
-- FILE: database/procedures.sql
-- Run AFTER schema.sql and triggers.sql
-- ============================================================

USE smart_inventory;

-- ============================================================
-- PROCEDURE 1: sp_add_batch
-- Atomically inserts a batch and sets its inventory quantity.
-- The trigger creates the inventory row with qty=0;
-- this procedure then updates it to the actual quantity.
-- ============================================================
DELIMITER //
CREATE PROCEDURE sp_add_batch(
    IN p_product_id  INT,
    IN p_supplier_id INT,
    IN p_mfg_date    DATE,
    IN p_exp_date    DATE,
    IN p_cost_price  DECIMAL(10,2),
    IN p_quantity    INT
)
BEGIN
    DECLARE v_new_batch_id INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_quantity <= 0 THEN
        SIGNAL SQLSTATE '45002'
            SET MESSAGE_TEXT = 'Quantity must be greater than zero.';
    END IF;
    IF p_exp_date <= p_mfg_date THEN
        SIGNAL SQLSTATE '45003'
            SET MESSAGE_TEXT = 'Expiry date must be after manufacture date.';
    END IF;
    IF p_cost_price < 0 THEN
        SIGNAL SQLSTATE '45004'
            SET MESSAGE_TEXT = 'Cost price cannot be negative.';
    END IF;

    START TRANSACTION;

    INSERT INTO batches (product_id, supplier_id, manufacture_date, expiry_date, cost_price)
    VALUES (p_product_id, p_supplier_id, p_mfg_date, p_exp_date, p_cost_price);

    SET v_new_batch_id = LAST_INSERT_ID();

    UPDATE inventory
    SET    quantity_available = p_quantity
    WHERE  batch_id = v_new_batch_id;

    COMMIT;

    SELECT v_new_batch_id AS batch_id,
           p_quantity     AS quantity_added,
           'SUCCESS'      AS status;
END //
DELIMITER ;


-- ============================================================
-- PROCEDURE 2: sp_fifo_sale
-- Processes a sale using strict FIFO logic via cursor.
-- Iterates batches ordered by expiry_date ASC (oldest first),
-- deducting from each until the full quantity is fulfilled.
-- Full ACID transaction with rollback on any error.
-- ============================================================
DELIMITER //
CREATE PROCEDURE sp_fifo_sale(
    IN p_product_id    INT,
    IN p_quantity      INT,
    IN p_selling_price DECIMAL(10,2)
)
BEGIN
    DECLARE v_batch_id    INT;
    DECLARE v_available   INT;
    DECLARE v_deduct      INT;
    DECLARE v_remaining   INT;
    DECLARE v_total_avail INT DEFAULT 0;
    DECLARE v_done        INT DEFAULT 0;

    DECLARE fifo_cur CURSOR FOR
        SELECT b.batch_id, i.quantity_available
        FROM   batches   b
        JOIN   inventory i ON i.batch_id = b.batch_id
        WHERE  b.product_id        = p_product_id
          AND  b.expiry_date      >= CURDATE()
          AND  i.quantity_available > 0
        ORDER BY b.expiry_date ASC, b.batch_id ASC;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_quantity <= 0 THEN
        SIGNAL SQLSTATE '45005'
            SET MESSAGE_TEXT = 'Sale quantity must be greater than zero.';
    END IF;
    IF p_selling_price < 0 THEN
        SIGNAL SQLSTATE '45006'
            SET MESSAGE_TEXT = 'Selling price cannot be negative.';
    END IF;

    SELECT COALESCE(SUM(i.quantity_available), 0)
    INTO   v_total_avail
    FROM   batches   b
    JOIN   inventory i ON i.batch_id = b.batch_id
    WHERE  b.product_id        = p_product_id
      AND  b.expiry_date      >= CURDATE()
      AND  i.quantity_available > 0;

    IF v_total_avail < p_quantity THEN
        SIGNAL SQLSTATE '45007'
            SET MESSAGE_TEXT = 'Insufficient total stock for this product.';
    END IF;

    SET v_remaining = p_quantity;

    START TRANSACTION;

    OPEN fifo_cur;

    fifo_loop: LOOP
        IF v_remaining <= 0 THEN LEAVE fifo_loop; END IF;

        FETCH fifo_cur INTO v_batch_id, v_available;

        IF v_done = 1 THEN LEAVE fifo_loop; END IF;

        IF v_available >= v_remaining THEN
            SET v_deduct = v_remaining;
        ELSE
            SET v_deduct = v_available;
        END IF;

        INSERT INTO sales (product_id, batch_id, quantity_sold, sale_date, selling_price)
        VALUES (p_product_id, v_batch_id, v_deduct, CURDATE(), p_selling_price);

        SET v_remaining = v_remaining - v_deduct;
    END LOOP fifo_loop;

    CLOSE fifo_cur;
    COMMIT;

    SELECT p_quantity AS total_sold, 'SUCCESS' AS status;
END //
DELIMITER ;


-- ============================================================
-- PROCEDURE 3: sp_check_expiry
-- Scans expired batches with remaining stock, logs them to
-- expiry_log (audit trail), and zeros out their inventory.
-- Data is NEVER deleted — only logged.
-- ============================================================
DELIMITER //
CREATE PROCEDURE sp_check_expiry()
BEGIN
    DECLARE v_batch_id INT;
    DECLARE v_qty      INT;
    DECLARE v_exp_date DATE;
    DECLARE v_count    INT DEFAULT 0;
    DECLARE v_done     INT DEFAULT 0;

    DECLARE expiry_cur CURSOR FOR
        SELECT b.batch_id, i.quantity_available, b.expiry_date
        FROM   batches   b
        JOIN   inventory i ON i.batch_id = b.batch_id
        WHERE  b.expiry_date      <  CURDATE()
          AND  i.quantity_available > 0;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    OPEN expiry_cur;

    expiry_loop: LOOP
        FETCH expiry_cur INTO v_batch_id, v_qty, v_exp_date;
        IF v_done = 1 THEN LEAVE expiry_loop; END IF;

        INSERT INTO expiry_log (batch_id, quantity_expired, expiry_date)
        VALUES (v_batch_id, v_qty, v_exp_date);

        UPDATE inventory
        SET    quantity_available = 0
        WHERE  batch_id = v_batch_id;

        SET v_count = v_count + 1;
    END LOOP expiry_loop;

    CLOSE expiry_cur;
    COMMIT;

    SELECT v_count AS expired_batches_logged, 'SUCCESS' AS status;
END //
DELIMITER ;


-- ============================================================
-- PROCEDURE 4: sp_get_low_stock
-- Returns products where total non-expired stock < reorder_level
-- ============================================================
DELIMITER //
CREATE PROCEDURE sp_get_low_stock()
BEGIN
    SELECT
        p.product_id,
        p.product_name,
        c.category_name,
        p.reorder_level,
        COALESCE(SUM(i.quantity_available), 0)                       AS current_stock,
        (p.reorder_level - COALESCE(SUM(i.quantity_available), 0))   AS shortage
    FROM      products   p
    JOIN      categories c ON c.category_id = p.category_id
    LEFT JOIN batches    b ON b.product_id  = p.product_id
                           AND b.expiry_date >= CURDATE()
    LEFT JOIN inventory  i ON i.batch_id    = b.batch_id
    GROUP BY  p.product_id, p.product_name, c.category_name, p.reorder_level
    HAVING    current_stock < p.reorder_level
    ORDER BY  shortage DESC;
END //
DELIMITER ;

-- ============================================================
-- END OF STORED PROCEDURES
-- ============================================================
