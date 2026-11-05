\set ON_ERROR_STOP on
\encoding UTF8
BEGIN;
SET LOCAL search_path = fleet, public;
-- Для новой схемы после 01_create.sql. Все имена и данные вымышлены.
INSERT INTO employee(login,password_hash,name,is_master,is_manager,is_staff) VALUES
('todd','DEMO_NOT_A_PASSWORD_HASH','Суини Тодд',true,false,false),
('lovett','DEMO_NOT_A_PASSWORD_HASH','Миссис Ловетт',false,true,false),
('toby','DEMO_NOT_A_PASSWORD_HASH','Тоби',false,false,true);
INSERT INTO client(name,segment) VALUES ('Учебный клиент','regular');
INSERT INTO service_type(name,description) VALUES ('Стрижка','Учебная услуга');
INSERT INTO visit(employee_id,client_id,service_type_id,start_time,end_time,outcome,request_id)
VALUES (1,1,1,now()-interval '2 hours',now()-interval '1 hour','transferred','10000000-0000-0000-0000-000000000001');
INSERT INTO chute_log(visit_id,dispatch_time,arrival_time,status,delivery_deadline)
VALUES (1,now()-interval '1 hour',now()-interval '50 minutes','arrived',now());
INSERT INTO stock_item(name,unit,min_threshold,is_legal) VALUES
('Мука','kg',2,true),('Сырьё категории A','kg',1,false);
INSERT INTO raw_material_lot(chute_log_id,stock_item_id,weight_kg,quality_category,remaining_kg)
VALUES (1,2,5,'A',3);
INSERT INTO recipe(recipe_code,name,version,yield_quantity,quality_category)
VALUES ('PIE','Учебный пирог',1,1,'A');
INSERT INTO recipe_ingredient VALUES (1,1,0.100),(1,2,0.100);
INSERT INTO production_batch(recipe_id,start_time,finish_time,planned_quantity,actual_quantity,status,unit_price,request_id) VALUES
(1,now()-interval '40 minutes',now()-interval '10 minutes',10,10,'ready',100,'20000000-0000-0000-0000-000000000001'),
(1,now()-interval '40 minutes',now()-interval '10 minutes',10,10,'ready',120,'20000000-0000-0000-0000-000000000002');
INSERT INTO production_material_usage VALUES (1,1,1),(2,1,1);
INSERT INTO stock_movement(stock_item_id,employee_id,raw_material_lot_id,production_batch_id,movement_type,quantity,reason,request_id) VALUES
(1,2,NULL,NULL,'receipt',10,'Закупка муки','30000000-0000-0000-0000-000000000001'),
(2,2,1,NULL,'receipt',5,'Приём сырьевого лота','30000000-0000-0000-0000-000000000002'),
(1,2,NULL,1,'usage',1,'Выпуск партии 1','30000000-0000-0000-0000-000000000003'),
(2,2,1,1,'usage',1,'Выпуск партии 1','30000000-0000-0000-0000-000000000004'),
(1,2,NULL,2,'usage',1,'Выпуск партии 2','30000000-0000-0000-0000-000000000005'),
(2,2,1,2,'usage',1,'Выпуск партии 2','30000000-0000-0000-0000-000000000006');
SELECT register_sale(3,'40000000-0000-0000-0000-000000000001',
    '[{"batch_id":1,"quantity":2},{"batch_id":2,"quantity":1}]');
INSERT INTO sales_return(sale_item_id,employee_id,quantity,refund_amount,restock_quantity,reason,request_id)
VALUES (1,2,1,100,0,'Учебный возврат без восстановления остатка','50000000-0000-0000-0000-000000000001');
INSERT INTO complaint(sales_transaction_id,production_batch_id,employee_id,description,status)
VALUES (1,1,2,'Учебная претензия к первой партии','open');
INSERT INTO solid_waste(production_batch_id,waste_type,quantity,unit) VALUES (1,'Упаковка',0.100,'kg');
INSERT INTO task(created_by,assigned_to,solid_waste_id,description,location,deadline)
VALUES (2,3,1,'Утилизировать упаковку','Пекарня',now()+interval '1 day');
INSERT INTO buyer(name) VALUES ('Учебный скупщик');
INSERT INTO asset_sale(buyer_id,employee_id,total_amount,request_id)
VALUES (1,1,50,'60000000-0000-0000-0000-000000000001');
INSERT INTO side_asset(visit_id,asset_sale_id,name,estimated_value,status) VALUES (1,1,'Учебный аксессуар',50,'sold');
COMMIT;
\echo 'Тестовые данные загружены во все 22 таблицы.'
