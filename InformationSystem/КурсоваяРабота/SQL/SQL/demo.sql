\set ON_ERROR_STOP on
\if :{?schema}
\else
\set schema public
\endif
BEGIN;
SET search_path TO :"schema", pg_catalog;
-- Once on a fresh database. Demo hashes cannot be used to log in.
DO $$
DECLARE master_id integer; manager_id integer; staff_id integer; cli integer; svc integer;
 v1 integer; v2 integer; c1 integer; c2 integer; raw_id integer; flour_id integer;
 l1 integer; l2 integer; rec integer; b1 integer; b2 integer; sale integer; item integer;
 buyer_id integer; asset1 integer; asset2 integer; deal integer; waste integer; task_id integer;
BEGIN
 IF EXISTS(SELECT 1 FROM employee) THEN RAISE EXCEPTION 'Demo requires empty schema'; END IF;
 INSERT INTO employee(login,password_hash,name,role_code) VALUES('master','!DEMO_ACCOUNT_DISABLED!','Суини Тодд','master') RETURNING id INTO master_id;
 PERFORM set_config('fleet.employee_id',master_id::varchar,true);
 INSERT INTO employee(login,password_hash,name,role_code) VALUES('manager','!DEMO_ACCOUNT_DISABLED!','Миссис Ловетт','manager') RETURNING id INTO manager_id;
 INSERT INTO employee(login,password_hash,name,role_code) VALUES('staff','!DEMO_ACCOUNT_DISABLED!','Тобиас','staff') RETURNING id INTO staff_id;
 INSERT INTO client(name,segment) VALUES('Учебный клиент','обычный') RETURNING id INTO cli;
 INSERT INTO service_type(name,description) VALUES('Бритьё','Учебный пример') RETURNING id INTO svc;
 INSERT INTO visit(client_id,employee_id,service_type_id,start_time,end_time,outcome,request_id)
 VALUES(cli,master_id,svc,current_timestamp-interval '2 hours',current_timestamp-interval '90 minutes','sent_to_chute','visit-demo-1') RETURNING id INTO v1;
 INSERT INTO visit(client_id,employee_id,service_type_id,start_time,end_time,outcome,request_id)
 VALUES(cli,master_id,svc,current_timestamp-interval '1 hour',current_timestamp-interval '30 minutes','sent_to_chute','visit-demo-2') RETURNING id INTO v2;
 INSERT INTO chute_log(visit_id,dispatch_time,delivery_deadline) VALUES(v1,current_timestamp-interval '90 minutes',current_timestamp+interval '1 hour') RETURNING id INTO c1;
 INSERT INTO chute_log(visit_id,dispatch_time,delivery_deadline) VALUES(v2,current_timestamp-interval '30 minutes',current_timestamp+interval '1 hour') RETURNING id INTO c2;
 INSERT INTO stock_item(name,unit,min_threshold,is_legal) VALUES('Основное сырьё','kg',2,false) RETURNING id INTO raw_id;
 INSERT INTO stock_item(name,unit,min_threshold) VALUES('Мука','kg',2) RETURNING id INTO flour_id;
 INSERT INTO raw_material_lot(chute_log_id,stock_item_id,weight_kg,quality_category) VALUES(c1,raw_id,4,'A') RETURNING id INTO l1;
 INSERT INTO raw_material_lot(chute_log_id,stock_item_id,weight_kg,quality_category) VALUES(c2,raw_id,100,'A') RETURNING id INTO l2;
 INSERT INTO stock_movement(stock_item_id,raw_material_lot_id,employee_id,movement_type,quantity,reason,request_id)
 VALUES(raw_id,l1,manager_id,'receipt',4,'Первый приём сырья','receipt-demo-1'),
 (raw_id,l2,manager_id,'receipt',100,'Второй приём сырья','receipt-demo-2');
 UPDATE chute_log SET status='delivered',arrival_time=clock_timestamp() WHERE id IN(c1,c2);
 INSERT INTO stock_movement(stock_item_id,employee_id,movement_type,quantity,reason,request_id)
 VALUES(flour_id,manager_id,'receipt',100,'Закупка муки','receipt-demo-3');
 INSERT INTO recipe(recipe_code,name,version,yield_quantity,quality_category)
 VALUES('PIE','Пирог',1,10,'A') RETURNING id INTO rec;
 INSERT INTO recipe_ingredient VALUES(rec,raw_id,0.5),(rec,flour_id,0.2);
 UPDATE recipe SET status='current' WHERE id=rec;
 INSERT INTO production_batch(recipe_id,planned_quantity,unit_price,request_id) VALUES(rec,10,100,'production-demo-1') RETURNING id INTO b1;
 INSERT INTO production_material_usage VALUES(b1,l1,4),(b1,l2,1);
 INSERT INTO stock_movement(stock_item_id,production_batch_id,employee_id,movement_type,quantity,reason,request_id)
 VALUES(raw_id,b1,manager_id,'production_out',5,'Расход по рецептуре','production-demo-1'),
 (flour_id,b1,manager_id,'production_out',2,'Расход по рецептуре','production-demo-1');
 UPDATE production_batch SET status='ready',actual_quantity=10,finish_time=clock_timestamp() WHERE id=b1;
 INSERT INTO production_batch(recipe_id,planned_quantity,unit_price,request_id) VALUES(rec,20,120,'production-demo-2') RETURNING id INTO b2;
 INSERT INTO production_material_usage VALUES(b2,l2,10);
 INSERT INTO stock_movement(stock_item_id,production_batch_id,employee_id,movement_type,quantity,reason,request_id)
 VALUES(raw_id,b2,manager_id,'production_out',10,'Расход по рецептуре','production-demo-2'),
 (flour_id,b2,manager_id,'production_out',4,'Расход по рецептуре','production-demo-2');
 UPDATE production_batch SET status='ready',actual_quantity=20,finish_time=clock_timestamp() WHERE id=b2;
 INSERT INTO sales_transaction(employee_id,request_id) VALUES(staff_id,'sale-demo-1') RETURNING id INTO sale;
 INSERT INTO sale_item(sales_transaction_id,production_batch_id,line_number,quantity,unit_price)
 VALUES(sale,b1,1,2,100) RETURNING id INTO item;
 INSERT INTO sale_item(sales_transaction_id,production_batch_id,line_number,quantity,unit_price) VALUES(sale,b2,2,3,120);
 INSERT INTO sales_return(sale_item_id,employee_id,quantity,refund_amount,restock_quantity,reason,request_id)
 VALUES(item,manager_id,1,100,1,'Ошибочный заказ, товар не использован','return-demo-1');
 INSERT INTO complaint(sales_transaction_id,production_batch_id,employee_id,description)
 VALUES(sale,b1,manager_id,'Учебное обращение');
 INSERT INTO buyer(name) VALUES('Учебный скупщик') RETURNING id INTO buyer_id;
 INSERT INTO side_asset(visit_id,name,estimated_value) VALUES(v1,'Часы',200) RETURNING id INTO asset1;
 INSERT INTO side_asset(visit_id,name,estimated_value) VALUES(v2,'Портсигар',100) RETURNING id INTO asset2;
 INSERT INTO asset_sale(buyer_id,employee_id,total_amount,request_id) VALUES(buyer_id,master_id,250,'asset-sale-demo-1') RETURNING id INTO deal;
 UPDATE side_asset SET status='sold',asset_sale_id=deal WHERE id IN(asset1,asset2);
 INSERT INTO solid_waste(raw_material_lot_id,waste_type,quantity,unit,disposal_method)
 VALUES(l1,'Отходы обработки',0.2,'kg','transport') RETURNING id INTO waste;
 INSERT INTO task(solid_waste_id,created_by,assigned_to,description,location,deadline)
 VALUES(waste,manager_id,staff_id,'Утилизировать отходы','Подвал',current_timestamp+interval '1 day') RETURNING id INTO task_id;
 UPDATE task SET status='done',completed_at=clock_timestamp(),completion_comment='Выполнено' WHERE id=task_id;
 UPDATE task SET status='confirmed',confirmed_at=clock_timestamp(),confirmed_by=manager_id WHERE id=task_id;
END $$;
COMMIT;
SELECT * FROM v_sale_totals;
SELECT * FROM v_batch_balance;
