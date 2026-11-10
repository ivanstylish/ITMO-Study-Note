-- Functions are VOLATILE unless stated otherwise: fresh READ COMMITTED snapshots after waiting for locks.
CREATE FUNCTION reject_change() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
BEGIN RAISE EXCEPTION 'Immutable history: %.%',TG_TABLE_SCHEMA,TG_TABLE_NAME USING ERRCODE='23514'; END $$;
CREATE FUNCTION audit_change() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE actor integer; object_id integer; description varchar(2000);
BEGIN
 IF TG_OP='UPDATE' AND NEW IS NOT DISTINCT FROM OLD THEN RETURN NULL; END IF;
 actor:=nullif(current_setting('fleet.employee_id',true),'')::integer;
 IF TG_TABLE_NAME='recipe_ingredient' THEN
  IF TG_OP='DELETE' THEN
   description:=format('recipe_id=%s; stock_item_id=%s',OLD.recipe_id,OLD.stock_item_id);
  ELSE description:=format('recipe_id=%s; stock_item_id=%s',NEW.recipe_id,NEW.stock_item_id);
  END IF;
 ELSIF TG_TABLE_NAME='production_material_usage' THEN
  IF TG_OP='DELETE' THEN
   description:=format('production_batch_id=%s; raw_material_lot_id=%s',OLD.production_batch_id,OLD.raw_material_lot_id);
  ELSE description:=format('production_batch_id=%s; raw_material_lot_id=%s',NEW.production_batch_id,NEW.raw_material_lot_id);
  END IF;
 ELSE
  IF TG_OP='DELETE' THEN object_id:=OLD.id; ELSE object_id:=NEW.id; END IF;
  description:=format('%s; id=%s',TG_OP,object_id);
 END IF;
 INSERT INTO audit_log(employee_id,action_type,target_entity,target_id,result,details)
 VALUES(actor,TG_OP,TG_TABLE_NAME,object_id,'success',description);
 RETURN NULL;
END $$;
CREATE FUNCTION protect_master() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
BEGIN
 IF OLD.role_code='master' AND OLD.status='active' AND
    (TG_OP='DELETE' OR NEW.role_code<>'master' OR NEW.status<>'active') THEN
   PERFORM 1 FROM employee WHERE role_code='master' ORDER BY id FOR UPDATE;
  IF NOT EXISTS(SELECT 1 FROM employee WHERE id<>OLD.id AND role_code='master' AND status='active') THEN
   RAISE EXCEPTION 'The last active master must remain' USING ERRCODE='23514';
  END IF;
 END IF;
 RETURN CASE WHEN TG_OP='DELETE' THEN OLD ELSE NEW END;
END $$;
CREATE TRIGGER employee_last_master BEFORE UPDATE OR DELETE ON employee FOR EACH ROW EXECUTE FUNCTION protect_master();
CREATE FUNCTION protect_balances() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
BEGIN
 IF TG_TABLE_NAME='stock_item' THEN
  IF TG_OP='INSERT' AND NEW.current_quantity<>0 THEN RAISE EXCEPTION 'Initial balance must be zero' USING ERRCODE='23514'; END IF;
  IF TG_OP='UPDATE' THEN
   IF NEW.current_quantity IS DISTINCT FROM OLD.current_quantity AND pg_trigger_depth()=1 THEN RAISE EXCEPTION 'Use stock movements' USING ERRCODE='23514'; END IF;
   IF NEW.unit IS DISTINCT FROM OLD.unit AND
    (EXISTS(SELECT 1 FROM stock_movement WHERE stock_item_id=OLD.id) OR EXISTS(SELECT 1 FROM recipe_ingredient WHERE stock_item_id=OLD.id)) THEN
    RAISE EXCEPTION 'Unit and stock kind already used' USING ERRCODE='23514';
   END IF;
  END IF;
 ELSE
  IF TG_OP='INSERT' AND NEW.remaining_kg<>0 THEN RAISE EXCEPTION 'Receive lot using a movement' USING ERRCODE='23514'; END IF;
  IF TG_OP='UPDATE' AND (NEW.remaining_kg IS DISTINCT FROM OLD.remaining_kg) AND pg_trigger_depth()=1 THEN
   RAISE EXCEPTION 'Use lot movements or production allocation' USING ERRCODE='23514';
  END IF;
  IF TG_OP='UPDATE' AND (NEW.id,NEW.chute_log_id,NEW.stock_item_id,NEW.weight_kg,NEW.quality_category,NEW.received_at) IS DISTINCT FROM (OLD.id,OLD.chute_log_id,OLD.stock_item_id,OLD.weight_kg,OLD.quality_category,OLD.received_at) THEN
   RAISE EXCEPTION 'Lot origin is immutable' USING ERRCODE='23514';
  END IF;
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER stock_balance_guard BEFORE INSERT OR UPDATE ON stock_item FOR EACH ROW EXECUTE FUNCTION protect_balances();
CREATE TRIGGER lot_balance_guard BEFORE INSERT OR UPDATE ON raw_material_lot FOR EACH ROW EXECUTE FUNCTION protect_balances();
CREATE FUNCTION apply_stock_movement() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE s stock_item%ROWTYPE; l raw_material_lot%ROWTYPE; delta numeric; b production_batch%ROWTYPE;
BEGIN
 SELECT * INTO STRICT s FROM stock_item WHERE id=NEW.stock_item_id FOR UPDATE;
 IF NOT s.is_active THEN RAISE EXCEPTION 'Stock item inactive' USING ERRCODE='23514'; END IF;
 delta:=CASE WHEN NEW.movement_type IN ('receipt','correction_in') THEN NEW.quantity ELSE -NEW.quantity END;
 IF s.current_quantity+delta<0 THEN RAISE EXCEPTION 'Insufficient stock %',s.id USING ERRCODE='23514'; END IF;
 IF NEW.production_batch_id IS NOT NULL THEN
  SELECT * INTO STRICT b FROM production_batch WHERE id=NEW.production_batch_id;
  IF b.status<>'producing' OR NOT EXISTS(SELECT 1 FROM recipe_ingredient WHERE recipe_id=b.recipe_id AND stock_item_id=s.id) THEN
   RAISE EXCEPTION 'Invalid production movement' USING ERRCODE='23514';
  END IF;
 ELSIF EXISTS(SELECT 1 FROM raw_material_lot WHERE stock_item_id=s.id) AND NEW.raw_material_lot_id IS NULL THEN
  RAISE EXCEPTION 'Raw stock movement requires lot' USING ERRCODE='23514';
 END IF;
 IF NEW.raw_material_lot_id IS NOT NULL THEN
  SELECT * INTO STRICT l FROM raw_material_lot WHERE id=NEW.raw_material_lot_id FOR UPDATE;
  IF l.stock_item_id<>s.id THEN RAISE EXCEPTION 'Lot stock mismatch' USING ERRCODE='23514'; END IF;
  IF NEW.movement_type='receipt' AND NEW.quantity<>l.weight_kg THEN RAISE EXCEPTION 'Receipt must match lot weight' USING ERRCODE='23514'; END IF;
  UPDATE raw_material_lot SET remaining_kg=remaining_kg+delta WHERE id=l.id;
 END IF;
 UPDATE stock_item SET current_quantity=current_quantity+delta WHERE id=s.id;
 RETURN NEW;
END $$;
CREATE TRIGGER stock_movement_apply BEFORE INSERT ON stock_movement FOR EACH ROW EXECUTE FUNCTION apply_stock_movement();
CREATE FUNCTION allocate_raw_material() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE l raw_material_lot%ROWTYPE; b production_batch%ROWTYPE; quality text;
BEGIN
 SELECT * INTO STRICT b FROM production_batch WHERE id=NEW.production_batch_id;
 SELECT * INTO STRICT l FROM raw_material_lot WHERE id=NEW.raw_material_lot_id FOR UPDATE;
 SELECT quality_category INTO STRICT quality FROM recipe WHERE id=b.recipe_id;
 IF b.status<>'producing' OR l.quality_category<>quality OR NOT EXISTS(
  SELECT 1 FROM recipe_ingredient WHERE recipe_id=b.recipe_id AND stock_item_id=l.stock_item_id) THEN
  RAISE EXCEPTION 'Wrong raw allocation' USING ERRCODE='23514';
 END IF;
 UPDATE raw_material_lot SET remaining_kg=remaining_kg-NEW.used_weight_kg WHERE id=l.id;
 RETURN NEW;
END $$;
CREATE TRIGGER raw_allocation_apply BEFORE INSERT ON production_material_usage FOR EACH ROW EXECUTE FUNCTION allocate_raw_material();
CREATE FUNCTION protect_recipe() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE rid integer;
BEGIN
 IF TG_TABLE_NAME='recipe_ingredient' THEN
  rid:=CASE WHEN TG_OP='DELETE' THEN OLD.recipe_id ELSE NEW.recipe_id END;
  IF TG_OP='UPDATE' AND NEW.recipe_id<>OLD.recipe_id THEN RAISE EXCEPTION 'Cannot move recipe component' USING ERRCODE='23514'; END IF;
  UPDATE recipe SET name=name WHERE id=rid;
  IF NOT EXISTS(SELECT 1 FROM recipe WHERE id=rid AND status='draft') THEN
   RAISE EXCEPTION 'Only draft recipe composition may be edited' USING ERRCODE='23514';
  END IF;
  IF EXISTS(SELECT 1 FROM production_batch WHERE recipe_id=rid) THEN RAISE EXCEPTION 'Used recipe composition is immutable' USING ERRCODE='23514'; END IF;
 ELSE
  IF TG_OP='UPDATE' AND NEW IS NOT DISTINCT FROM OLD THEN RETURN NEW; END IF;
  IF OLD.status='archived' OR
     (TG_OP='UPDATE' AND OLD.status='current' AND NEW.status='draft') THEN
   RAISE EXCEPTION 'Invalid recipe lifecycle change' USING ERRCODE='23514';
  END IF;
  IF EXISTS(SELECT 1 FROM production_batch WHERE recipe_id=OLD.id) AND
   (TG_OP='DELETE' OR (NEW.id,NEW.recipe_code,NEW.name,NEW.version,NEW.yield_quantity,NEW.quality_category,NEW.created_at) IS DISTINCT FROM (OLD.id,OLD.recipe_code,OLD.name,OLD.version,OLD.yield_quantity,OLD.quality_category,OLD.created_at)) THEN
   RAISE EXCEPTION 'Used recipe version is immutable' USING ERRCODE='23514';
  END IF;
 END IF;
 RETURN CASE WHEN TG_OP='DELETE' THEN OLD ELSE NEW END;
END $$;
CREATE TRIGGER recipe_used_guard BEFORE UPDATE OR DELETE ON recipe FOR EACH ROW EXECUTE FUNCTION protect_recipe();
CREATE TRIGGER recipe_composition_guard BEFORE INSERT OR UPDATE OR DELETE ON recipe_ingredient FOR EACH ROW EXECUTE FUNCTION protect_recipe();
CREATE FUNCTION check_nonempty() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE rid integer;
BEGIN
 IF TG_TABLE_NAME='sales_transaction' THEN
  IF EXISTS(SELECT 1 FROM sales_transaction WHERE id=NEW.id) AND NOT EXISTS(SELECT 1 FROM sale_item WHERE sales_transaction_id=NEW.id) THEN
   RAISE EXCEPTION 'Empty sale' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='asset_sale' THEN
  IF EXISTS(SELECT 1 FROM asset_sale WHERE id=NEW.id) AND NOT EXISTS(SELECT 1 FROM side_asset WHERE asset_sale_id=NEW.id) THEN
   RAISE EXCEPTION 'Empty asset sale' USING ERRCODE='23514'; END IF;
 ELSE
  IF TG_TABLE_NAME='recipe' THEN
   rid:=CASE WHEN TG_OP='DELETE' THEN OLD.id ELSE NEW.id END;
  ELSE
   rid:=CASE WHEN TG_OP='DELETE' THEN OLD.recipe_id ELSE NEW.recipe_id END;
  END IF;
  IF EXISTS(SELECT 1 FROM recipe WHERE id=rid) AND NOT EXISTS(SELECT 1 FROM recipe_ingredient WHERE recipe_id=rid) THEN
   RAISE EXCEPTION 'Empty recipe' USING ERRCODE='23514'; END IF;
 END IF;
 RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER sale_nonempty AFTER INSERT ON sales_transaction DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_nonempty();
CREATE CONSTRAINT TRIGGER asset_sale_nonempty AFTER INSERT ON asset_sale DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_nonempty();
CREATE CONSTRAINT TRIGGER recipe_nonempty AFTER INSERT OR UPDATE ON recipe DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_nonempty();
CREATE CONSTRAINT TRIGGER recipe_component_nonempty AFTER INSERT OR UPDATE OR DELETE ON recipe_ingredient DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_nonempty();
CREATE FUNCTION check_stock_reconciliation() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE sid integer;
BEGIN
 IF TG_TABLE_NAME='production_material_usage' THEN
  SELECT stock_item_id INTO sid FROM raw_material_lot WHERE id=NEW.raw_material_lot_id;
 ELSE sid:=NEW.stock_item_id;
 END IF;
 IF EXISTS(SELECT 1 FROM stock_item s WHERE s.id=sid AND EXISTS(SELECT 1 FROM raw_material_lot WHERE stock_item_id=s.id) AND s.current_quantity<>(
  SELECT coalesce(sum(l.remaining_kg),0) FROM raw_material_lot l WHERE l.stock_item_id=s.id)) THEN
  RAISE EXCEPTION 'Raw stock and lot balances disagree' USING ERRCODE='23514';
 END IF;
 RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER raw_stock_reconcile AFTER INSERT ON stock_movement DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_stock_reconciliation();
CREATE CONSTRAINT TRIGGER raw_usage_reconcile AFTER INSERT ON production_material_usage DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_stock_reconciliation();
CREATE CONSTRAINT TRIGGER raw_lot_reconcile AFTER INSERT ON raw_material_lot DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_stock_reconciliation();
CREATE FUNCTION check_production_reconciliation() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE bid integer; b production_batch%ROWTYPE; r record; moved numeric; allocated numeric;
BEGIN
 IF TG_TABLE_NAME='production_batch' THEN bid:=NEW.id;
 ELSE bid:=NEW.production_batch_id;
 END IF;
 IF bid IS NULL THEN RETURN NULL; END IF;
 SELECT * INTO STRICT b FROM production_batch WHERE id=bid;
 IF NOT EXISTS(SELECT 1 FROM production_material_usage WHERE production_batch_id=bid) THEN RAISE EXCEPTION 'Batch requires raw allocation' USING ERRCODE='23514'; END IF;
 FOR r IN SELECT i.*,EXISTS(SELECT 1 FROM raw_material_lot WHERE stock_item_id=s.id) AS is_raw FROM recipe_ingredient i JOIN stock_item s ON s.id=i.stock_item_id WHERE recipe_id=b.recipe_id LOOP
  SELECT coalesce(sum(quantity),0) INTO moved FROM stock_movement WHERE production_batch_id=bid AND stock_item_id=r.stock_item_id AND movement_type='production_out';
  IF moved<>r.quantity_per_unit*b.planned_quantity THEN RAISE EXCEPTION 'Production movement differs from recipe' USING ERRCODE='23514'; END IF;
  IF r.is_raw THEN
   SELECT coalesce(sum(u.used_weight_kg),0) INTO allocated FROM production_material_usage u JOIN raw_material_lot l ON l.id=u.raw_material_lot_id WHERE u.production_batch_id=bid AND l.stock_item_id=r.stock_item_id;
   IF allocated<>moved THEN RAISE EXCEPTION 'Allocation differs from production movement' USING ERRCODE='23514'; END IF;
  END IF;
 END LOOP;
 RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER production_reconcile AFTER INSERT ON production_batch DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_production_reconciliation();
CREATE CONSTRAINT TRIGGER production_move_reconcile AFTER INSERT ON stock_movement DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_production_reconciliation();
CREATE CONSTRAINT TRIGGER production_usage_reconcile AFTER INSERT ON production_material_usage DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_production_reconciliation();
CREATE FUNCTION guard_production_state() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE available integer;
BEGIN
 IF TG_OP='INSERT' THEN
  IF NEW.status<>'producing' OR NEW.written_off_quantity<>0 THEN
   RAISE EXCEPTION 'New batch must start producing' USING ERRCODE='23514';
  END IF;
  UPDATE recipe SET name=name WHERE id=NEW.recipe_id;
  IF NOT EXISTS(SELECT 1 FROM recipe WHERE id=NEW.recipe_id AND status='current') THEN
   RAISE EXCEPTION 'Recipe must be current and active' USING ERRCODE='23514';
  END IF;
  RETURN NEW;
 END IF;
 IF NEW IS NOT DISTINCT FROM OLD THEN RETURN NEW; END IF;
 IF (NEW.id,NEW.recipe_id,NEW.planned_quantity,NEW.start_time,NEW.request_id) IS DISTINCT FROM
    (OLD.id,OLD.recipe_id,OLD.planned_quantity,OLD.start_time,OLD.request_id) THEN
  RAISE EXCEPTION 'Production origin is immutable' USING ERRCODE='23514';
 END IF;
 IF OLD.status IN ('recalled','written_off') THEN
  RAISE EXCEPTION 'Terminal batch is immutable' USING ERRCODE='23514';
 END IF;
 IF NEW.status<>OLD.status AND NOT ((OLD.status='producing' AND NEW.status IN ('ready','written_off')) OR
    (OLD.status='ready' AND NEW.status IN ('recalled','written_off'))) THEN
  RAISE EXCEPTION 'Invalid production state transition' USING ERRCODE='23514';
 END IF;
 IF OLD.status<>'producing' AND (NEW.actual_quantity,NEW.finish_time) IS DISTINCT FROM (OLD.actual_quantity,OLD.finish_time) THEN
  RAISE EXCEPTION 'Output already recorded' USING ERRCODE='23514';
 END IF;
 IF NEW.status IN ('recalled','written_off') THEN
  IF OLD.status='producing' THEN
   NEW.actual_quantity:=coalesce(NEW.actual_quantity,0);
   NEW.finish_time:=coalesce(NEW.finish_time,clock_timestamp());
   available:=NEW.actual_quantity;
  ELSE SELECT quantity_balance INTO available FROM v_batch_balance WHERE id=OLD.id;
  END IF;
  NEW.written_off_quantity:=available;
  IF NEW.status='recalled' THEN NEW.recalled_at:=clock_timestamp(); END IF;
 ELSIF NEW.written_off_quantity<>0 THEN
  RAISE EXCEPTION 'Use recall or write-off status' USING ERRCODE='23514';
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER production_state BEFORE INSERT OR UPDATE ON production_batch FOR EACH ROW EXECUTE FUNCTION guard_production_state();
CREATE FUNCTION check_sale_item() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE b production_batch%ROWTYPE; available integer;
BEGIN
 UPDATE production_batch SET status=status WHERE id=NEW.production_batch_id RETURNING * INTO STRICT b;
 SELECT quantity_balance INTO available FROM v_batch_balance WHERE id=b.id;
 IF b.status<>'ready' OR available<NEW.quantity THEN RAISE EXCEPTION 'Batch unavailable or insufficient output' USING ERRCODE='23514'; END IF;
 IF NEW.unit_price<>b.unit_price THEN RAISE EXCEPTION 'Sale price must match current batch price' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER sale_item_stock BEFORE INSERT ON sale_item FOR EACH ROW EXECUTE FUNCTION check_sale_item();
CREATE FUNCTION check_return() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE i sale_item%ROWTYPE; b production_batch%ROWTYPE; q integer;
BEGIN
 SELECT * INTO STRICT i FROM sale_item WHERE id=NEW.sale_item_id;
 UPDATE production_batch SET status=status WHERE id=i.production_batch_id RETURNING * INTO STRICT b;
 SELECT coalesce(sum(quantity),0) INTO q FROM sales_return WHERE sale_item_id=i.id;
 IF q+NEW.quantity>i.quantity OR NEW.refund_amount>NEW.quantity*i.unit_price THEN
  RAISE EXCEPTION 'Return exceeds sold quantity or amount' USING ERRCODE='23514'; END IF;
 IF NEW.restock_quantity>0 AND b.status<>'ready' THEN RAISE EXCEPTION 'Cannot restock recalled or written-off product' USING ERRCODE='23514'; END IF;
 IF NEW.return_time<(SELECT sale_time FROM sales_transaction WHERE id=i.sales_transaction_id) THEN RAISE EXCEPTION 'Return predates sale' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER return_limit BEFORE INSERT ON sales_return FOR EACH ROW EXECUTE FUNCTION check_return();
CREATE FUNCTION check_complaint() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
BEGIN
 IF NEW.sales_transaction_id IS NOT NULL AND NEW.production_batch_id IS NOT NULL AND NOT EXISTS(
  SELECT 1 FROM sale_item WHERE sales_transaction_id=NEW.sales_transaction_id AND production_batch_id=NEW.production_batch_id) THEN
  RAISE EXCEPTION 'Complaint batch is not in sale' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER complaint_references BEFORE INSERT OR UPDATE ON complaint FOR EACH ROW EXECUTE FUNCTION check_complaint();
CREATE FUNCTION guard_asset() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
BEGIN
 IF TG_OP='DELETE' THEN
  IF OLD.asset_sale_id IS NOT NULL THEN RAISE EXCEPTION 'Sold asset is immutable' USING ERRCODE='23514'; END IF;
  RETURN OLD;
 END IF;
 IF TG_OP='UPDATE' AND OLD.asset_sale_id IS NOT NULL AND NEW IS DISTINCT FROM OLD THEN RAISE EXCEPTION 'Sold asset is immutable' USING ERRCODE='23514'; END IF;
 IF NOT EXISTS(SELECT 1 FROM visit WHERE id=NEW.visit_id AND outcome='sent_to_chute') THEN RAISE EXCEPTION 'Asset requires eligible visit' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER asset_guard BEFORE INSERT OR UPDATE OR DELETE ON side_asset FOR EACH ROW EXECUTE FUNCTION guard_asset();
CREATE FUNCTION guard_waste() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
BEGIN
 IF NEW.disposal_time IS NOT NULL AND pg_trigger_depth()=1 AND (TG_OP='INSERT' OR NEW.disposal_time IS DISTINCT FROM OLD.disposal_time) THEN
  RAISE EXCEPTION 'Confirm disposal through task' USING ERRCODE='23514'; END IF;
 IF TG_OP='UPDATE' AND OLD.disposal_time IS NOT NULL AND NEW IS DISTINCT FROM OLD THEN RAISE EXCEPTION 'Disposed waste is immutable' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
-- A received lot, its delivery and original warehouse receipt form one operation.
CREATE FUNCTION check_receipt() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE lot raw_material_lot%ROWTYPE; chute_id integer; delivered boolean;
BEGIN
 IF TG_TABLE_NAME='chute_log' THEN chute_id:=NEW.id;
 ELSIF TG_TABLE_NAME='raw_material_lot' THEN chute_id:=NEW.chute_log_id;
 ELSE
  IF NEW.raw_material_lot_id IS NULL THEN RETURN NULL; END IF;
  SELECT chute_log_id INTO chute_id FROM raw_material_lot WHERE id=NEW.raw_material_lot_id;
 END IF;
 SELECT status='delivered' INTO delivered FROM chute_log WHERE id=chute_id;
 SELECT * INTO lot FROM raw_material_lot WHERE chute_log_id=chute_id;
 IF lot.id IS NULL THEN
  IF delivered THEN RAISE EXCEPTION 'Delivered chute requires a received lot' USING ERRCODE='23514'; END IF;
  RETURN NULL;
 END IF;
 IF NOT delivered OR NOT EXISTS(SELECT 1 FROM stock_item WHERE id=lot.stock_item_id AND unit='kg') OR
    NOT EXISTS(SELECT 1 FROM stock_movement WHERE raw_material_lot_id=lot.id AND movement_type='receipt' AND quantity=lot.weight_kg) THEN
  RAISE EXCEPTION 'Lot, delivered chute and receipt must agree' USING ERRCODE='23514';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM chute_log c JOIN visit v ON v.id=c.visit_id WHERE c.id=chute_id AND v.outcome='sent_to_chute') THEN
  RAISE EXCEPTION 'Lot requires a visit sent to chute' USING ERRCODE='23514';
 END IF;
 RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER lot_receipt_complete AFTER INSERT ON raw_material_lot DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_receipt();
CREATE CONSTRAINT TRIGGER delivery_receipt_complete AFTER INSERT OR UPDATE ON chute_log DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_receipt();
CREATE CONSTRAINT TRIGGER movement_receipt_complete AFTER INSERT ON stock_movement DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_receipt();
CREATE FUNCTION guard_visit() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
BEGIN
 IF OLD.outcome<>'open' AND NEW IS DISTINCT FROM OLD THEN
  RAISE EXCEPTION 'Completed visit is immutable' USING ERRCODE='23514';
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER visit_history BEFORE UPDATE ON visit FOR EACH ROW EXECUTE FUNCTION guard_visit();

CREATE FUNCTION check_visit_chute() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE vid integer; v visit%ROWTYPE; pending integer;
BEGIN
 IF TG_TABLE_NAME='visit' THEN vid:=NEW.id; ELSE vid:=NEW.visit_id; END IF;
 SELECT * INTO v FROM visit WHERE id=vid;
 IF (v.outcome='sent_to_chute') IS DISTINCT FROM EXISTS(SELECT 1 FROM chute_log WHERE visit_id=vid) THEN
  RAISE EXCEPTION 'Visit outcome and chute must agree' USING ERRCODE='23514';
 END IF;
 -- Serialize the cross-visit check on the existing client row, including snapshot isolation.
 UPDATE client SET name=name WHERE id=v.client_id;
 SELECT count(*) INTO pending FROM chute_log c JOIN visit x ON x.id=c.visit_id
 WHERE x.client_id=v.client_id AND c.status IN ('in_transit','blocked');
 IF pending>1 THEN RAISE EXCEPTION 'Client already has a pending delivery' USING ERRCODE='23514'; END IF;
 RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER visit_chute_consistent AFTER INSERT OR UPDATE ON visit DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_visit_chute();
CREATE CONSTRAINT TRIGGER chute_visit_consistent AFTER INSERT OR UPDATE ON chute_log DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_visit_chute();
CREATE TRIGGER waste_guard BEFORE INSERT OR UPDATE ON solid_waste FOR EACH ROW EXECUTE FUNCTION guard_waste();
CREATE FUNCTION guard_task() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
BEGIN
 IF TG_OP='DELETE' THEN
  IF OLD.status<>'assigned' THEN RAISE EXCEPTION 'Task history is immutable' USING ERRCODE='23514'; END IF;
  RETURN OLD;
 END IF;
 IF TG_OP='INSERT' AND NEW.status<>'assigned' THEN RAISE EXCEPTION 'Task starts assigned' USING ERRCODE='23514'; END IF;
 IF TG_OP='UPDATE' THEN
  IF NEW.status<>OLD.status AND NOT ((OLD.status='assigned' AND NEW.status='done') OR (OLD.status='done' AND NEW.status='confirmed')) THEN RAISE EXCEPTION 'Invalid task transition' USING ERRCODE='23514'; END IF;
  IF OLD.status<>'assigned' AND (NEW.assigned_to,NEW.solid_waste_id,NEW.created_by,NEW.created_at) IS DISTINCT FROM (OLD.assigned_to,OLD.solid_waste_id,OLD.created_by,OLD.created_at) THEN RAISE EXCEPTION 'Task responsibility is fixed' USING ERRCODE='23514'; END IF;
  IF OLD.status='confirmed' AND NEW IS DISTINCT FROM OLD THEN RAISE EXCEPTION 'Confirmed task is immutable' USING ERRCODE='23514'; END IF;
 END IF;
 IF NOT EXISTS(SELECT 1 FROM employee WHERE id=NEW.assigned_to AND status='active') THEN RAISE EXCEPTION 'Inactive assignee' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER task_guard BEFORE INSERT OR UPDATE OR DELETE ON task FOR EACH ROW EXECUTE FUNCTION guard_task();
CREATE FUNCTION complete_disposal() RETURNS trigger LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
BEGIN
 IF NEW.status='confirmed' AND OLD.status<>'confirmed' AND NEW.solid_waste_id IS NOT NULL THEN
  UPDATE solid_waste SET disposal_time=NEW.completed_at WHERE id=NEW.solid_waste_id;
 END IF;
 RETURN NULL;
END $$;
CREATE TRIGGER task_disposal AFTER UPDATE ON task FOR EACH ROW EXECUTE FUNCTION complete_disposal();
DO $$ DECLARE n text; BEGIN
 FOREACH n IN ARRAY ARRAY['audit_log','stock_movement','sale_item','sales_return','production_material_usage','sales_transaction','asset_sale'] LOOP
  EXECUTE format('CREATE TRIGGER immutable_history BEFORE UPDATE OR DELETE ON %I FOR EACH ROW EXECUTE FUNCTION reject_change()',n);
  EXECUTE format('CREATE TRIGGER no_truncate BEFORE TRUNCATE ON %I FOR EACH STATEMENT EXECUTE FUNCTION reject_change()',n);
 END LOOP;
 FOREACH n IN ARRAY ARRAY['employee','client','service_type','visit','chute_log','stock_item','raw_material_lot','recipe','recipe_ingredient','production_batch','production_material_usage','stock_movement','sales_transaction','sale_item','sales_return','complaint','buyer','asset_sale','side_asset','solid_waste','task'] LOOP
  EXECUTE format('CREATE TRIGGER audit_row AFTER INSERT OR UPDATE OR DELETE ON %I FOR EACH ROW EXECUTE FUNCTION audit_change()',n);
 END LOOP;
END $$;
