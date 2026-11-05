\set ON_ERROR_STOP on
\encoding UTF8
\pset pager off
BEGIN ISOLATION LEVEL READ COMMITTED;
SET LOCAL search_path = fleet, public;
SET LOCAL TIME ZONE 'Europe/Moscow';

\echo '1. Структура: 22 таблицы и 34 внешних ключа'
SELECT count(*) AS tables FROM information_schema.tables WHERE table_schema='fleet' AND table_type='BASE TABLE';
SELECT count(*) AS foreign_keys FROM information_schema.table_constraints WHERE constraint_schema='fleet' AND constraint_type='FOREIGN KEY';

\echo '2. Рецептура: связь M:N и нормы на изделие'
SELECT r.name AS recipe, s.name AS ingredient, i.quantity_per_unit, s.unit
FROM recipe r JOIN recipe_ingredient i ON i.recipe_id=r.id JOIN stock_item s ON s.id=i.stock_item_id;
\echo '3. Прослеживаемость: партия -> сырьевой лот -> визит -> клиент'
SELECT b.id AS batch, l.id AS lot, u.used_weight_kg, v.id AS visit, c.name AS client
FROM production_batch b JOIN production_material_usage u ON u.production_batch_id=b.id
JOIN raw_material_lot l ON l.id=u.raw_material_lot_id JOIN chute_log ch ON ch.id=l.chute_log_id
JOIN visit v ON v.id=ch.visit_id JOIN client c ON c.id=v.client_id;

\echo '4. Исходный чек = 320, возврат = 100, чистая выручка = 220'
SELECT t.id, t.total_price,
       (SELECT coalesce(sum(r.refund_amount),0) FROM sales_return r
        JOIN sale_item i ON i.id=r.sale_item_id WHERE i.sales_transaction_id=t.id) AS refunded
FROM v_sale_totals t;
SELECT (SELECT sum(total_price) FROM v_sale_totals) - (SELECT sum(refund_amount) FROM sales_return) AS net_revenue;
SELECT * FROM v_batch_balance ORDER BY id;

\echo '5. Новая цена 125 не меняет старый чек. Новая продажа двух партий = 370'
CALL change_batch_price(2,1,125);
SELECT register_sale(3,'70000000-0000-0000-0000-000000000001',
    '[{"batch_id":1,"quantity":2},{"batch_id":2,"quantity":1}]') AS sale_id;
SELECT * FROM v_sale_totals ORDER BY id;
SELECT * FROM v_batch_balance ORDER BY id;

\echo '6. Самопроверки: ожидаемые отказы перехватываются; неожиданная ошибка останавливает показ'
DO $$
BEGIN
    IF (SELECT total_price FROM v_sale_totals WHERE id=1) <> 320
       OR (SELECT total_price FROM v_sale_totals WHERE id<>1 ORDER BY id DESC LIMIT 1) <> 370
       OR (SELECT available_quantity FROM v_batch_balance WHERE id=1) <> 6
       OR (SELECT available_quantity FROM v_batch_balance WHERE id=2) <> 8 THEN
        RAISE EXCEPTION 'Не совпали сумма чека или остатки';
    END IF;
    BEGIN
        INSERT INTO sale_item(sales_transaction_id,production_batch_id,line_number,quantity,unit_price) VALUES (1,1,99,0,125);
        RAISE EXCEPTION 'Проверка не сработала: нулевое количество';
    EXCEPTION WHEN check_violation THEN RAISE NOTICE 'OK: CHECK отклоняет нулевое количество'; END;
    BEGIN
        INSERT INTO recipe_ingredient VALUES (999999,1,1);
        RAISE EXCEPTION 'Проверка не сработала: внешний ключ';
    EXCEPTION WHEN foreign_key_violation THEN RAISE NOTICE 'OK: FK отклоняет неизвестную рецептуру'; END;
    BEGIN
        INSERT INTO recipe_ingredient VALUES (1,1,1);
        RAISE EXCEPTION 'Проверка не сработала: составной ключ';
    EXCEPTION WHEN unique_violation THEN RAISE NOTICE 'OK: составной PK отклоняет повторный компонент'; END;
    BEGIN
        PERFORM register_sale(3,'70000000-0000-0000-0000-000000000002',
            '[{"batch_id":1,"quantity":1},{"batch_id":2,"quantity":999}]');
        RAISE EXCEPTION 'Проверка не сработала: перепродажа';
    EXCEPTION WHEN raise_exception THEN
        IF SQLERRM <> 'Недостаточно готовой продукции' THEN RAISE; END IF;
        RAISE NOTICE 'OK: перепродажа отклонена, вся продажа отменена';
    END;
    IF (SELECT count(*) FROM sales_transaction) <> 2
       OR (SELECT available_quantity FROM v_batch_balance WHERE id=1) <> 6 THEN
        RAISE EXCEPTION 'Частичная продажа осталась после ошибки';
    END IF;
    BEGIN
        INSERT INTO sales_return(sale_item_id,employee_id,quantity,refund_amount,restock_quantity,reason,request_id)
        VALUES (1,2,2,200,0,'Ошибка','70000000-0000-0000-0000-000000000003');
        RAISE EXCEPTION 'Проверка не сработала: повторный возврат';
    EXCEPTION WHEN raise_exception THEN
        IF SQLERRM <> 'Возврат превышает проданное количество или сумму' THEN RAISE; END IF;
        RAISE NOTICE 'OK: возврат сверх проданного отклонён';
    END;
    BEGIN
        INSERT INTO stock_movement(stock_item_id,employee_id,movement_type,quantity,reason,request_id)
        VALUES (1,2,'loss',999,'Ошибка','70000000-0000-0000-0000-000000000004');
        RAISE EXCEPTION 'Проверка не сработала: отрицательный склад';
    EXCEPTION WHEN raise_exception THEN
        IF SQLERRM <> 'Недостаточный складской остаток или неизвестная позиция' THEN RAISE; END IF;
        RAISE NOTICE 'OK: отрицательный складской остаток запрещён';
    END;
    BEGIN
        UPDATE sale_item SET quantity=100 WHERE id=1;
        RAISE EXCEPTION 'Проверка не сработала: изменение истории';
    EXCEPTION WHEN raise_exception THEN
        IF SQLERRM NOT LIKE 'История sale_item неизменяема:%' THEN RAISE; END IF;
        RAISE NOTICE 'OK: изменение истории запрещено';
    END;
    BEGIN
        INSERT INTO sales_transaction(employee_id,request_id) VALUES (3,'70000000-0000-0000-0000-000000000005');
        SET CONSTRAINTS ALL IMMEDIATE;
        RAISE EXCEPTION 'Проверка не сработала: пустой чек';
    EXCEPTION WHEN raise_exception THEN
        IF SQLERRM <> 'Продажа должна содержать хотя бы одну позицию' THEN RAISE; END IF;
        RAISE NOTICE 'OK: отложенный триггер отклоняет пустую продажу';
    END;
END $$;
\echo '7. Склад, открытое задание и аудит выполненных команд'
SELECT name,current_quantity,unit FROM stock_item ORDER BY id;
SELECT id,description,status,deadline FROM task WHERE assigned_to=3 AND status <> 'confirmed' ORDER BY deadline;
SELECT action_type,target_entity,target_id,result,details FROM audit_log ORDER BY id;
SET CONSTRAINTS ALL IMMEDIATE;
ROLLBACK;
\echo 'Демонстрация завершена. Изменения отменены; можно запустить 03_demo.sql снова (значения identity могут иметь пропуски).'
