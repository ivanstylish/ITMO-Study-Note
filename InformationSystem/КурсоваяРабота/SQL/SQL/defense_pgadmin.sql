-- Выполнять выделенные команды по шагам. База: fleet_street_defense_v48_test.
-- 1. Чек и повтор запроса
BEGIN;
SET LOCAL search_path TO public, pg_catalog;
SELECT register_sale(3, ARRAY[1,2], ARRAY[1,1],
                     'defense-sale') AS first_id;
SELECT register_sale(3, NULL, NULL,
                     'defense-sale') AS replay_id;
SELECT v.id, v.total_price, count(i.id) AS lines
FROM sales_transaction t
JOIN v_sale_totals v ON v.id = t.id
JOIN sale_item i ON i.sales_transaction_id = t.id
WHERE t.request_id = 'defense-sale'
GROUP BY v.id, v.total_price;
SET CONSTRAINTS ALL IMMEDIATE;
ROLLBACK;

-- 2. Отказ при возврате. После ошибки отдельно выполни ROLLBACK.
BEGIN;
SET LOCAL search_path TO public, pg_catalog;
INSERT INTO sales_return(sale_item_id, employee_id, quantity,
  refund_amount, reason, request_id)
VALUES (1, 2, 999, 99900, 'Test return', 'test-return');
ROLLBACK;
