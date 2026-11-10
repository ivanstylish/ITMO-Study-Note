-- UC04, UC07, UC08, UC10 and UC14. Caller owns COMMIT/ROLLBACK.
CREATE FUNCTION check_actor(p_employee integer, p_manager_required boolean DEFAULT false)
RETURNS void LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
BEGIN
 IF NOT EXISTS (
  SELECT 1 FROM employee WHERE id=p_employee AND status='active'
   AND (NOT p_manager_required OR role_code IN ('manager','master'))
 ) THEN
  RAISE EXCEPTION '%', CASE WHEN p_manager_required THEN 'Active manager or master required'
                            ELSE 'Active employee required' END USING ERRCODE='42501';
 END IF;
END $$;

CREATE FUNCTION receive_raw_material(
 p_employee integer, p_chute integer, p_stock integer,
 p_weight numeric, p_quality varchar, p_request varchar
) RETURNS integer LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE result_id integer;
BEGIN
 PERFORM check_actor(p_employee,true);
 SELECT raw_material_lot_id INTO result_id FROM stock_movement WHERE request_id=p_request AND stock_item_id=p_stock AND movement_type='receipt' AND raw_material_lot_id IS NOT NULL;
 IF FOUND THEN RETURN result_id; END IF;
 PERFORM set_config('fleet.employee_id',p_employee::text,true);
 PERFORM 1 FROM stock_item WHERE id=p_stock AND is_active AND unit='kg' FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'Active stock item in kg required' USING ERRCODE='23514'; END IF;
 SELECT raw_material_lot_id INTO result_id FROM stock_movement WHERE request_id=p_request AND stock_item_id=p_stock AND movement_type='receipt' AND raw_material_lot_id IS NOT NULL;
 IF FOUND THEN RETURN result_id; END IF;
 PERFORM 1 FROM chute_log WHERE id=p_chute AND status IN ('in_transit','blocked') FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'Pending delivery required' USING ERRCODE='23514'; END IF;
 INSERT INTO raw_material_lot(chute_log_id,stock_item_id,weight_kg,quality_category)
 VALUES(p_chute,p_stock,p_weight,p_quality) RETURNING id INTO result_id;
 INSERT INTO stock_movement(stock_item_id,raw_material_lot_id,employee_id,
   movement_type,quantity,reason,request_id)
 VALUES(p_stock,result_id,p_employee,'receipt',p_weight,'Приём из жёлоба',p_request);
 UPDATE chute_log SET status='delivered',arrival_time=clock_timestamp() WHERE id=p_chute;
 RETURN result_id;
EXCEPTION WHEN unique_violation THEN
 SELECT raw_material_lot_id INTO result_id FROM stock_movement WHERE request_id=p_request AND stock_item_id=p_stock AND movement_type='receipt' AND raw_material_lot_id IS NOT NULL;
 IF FOUND THEN RETURN result_id; END IF;
 RAISE;
END $$;

CREATE FUNCTION start_production(
 p_employee integer, p_recipe integer, p_quantity integer,
 p_price numeric, p_request varchar
) RETURNS integer LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE result_id integer; ingredient record; lot record; needed numeric; used numeric;
 quality varchar;
BEGIN
 PERFORM check_actor(p_employee,true);
 SELECT id INTO result_id FROM production_batch WHERE request_id=p_request;
 IF FOUND THEN RETURN result_id; END IF;
 PERFORM set_config('fleet.employee_id',p_employee::text,true);
 SELECT quality_category INTO quality FROM recipe WHERE id=p_recipe AND status='current' FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'Current recipe required' USING ERRCODE='23514'; END IF;
 -- Lock all ingredients in a stable order before any stock movement.
 PERFORM s.id FROM stock_item s JOIN recipe_ingredient i ON i.stock_item_id=s.id
 WHERE i.recipe_id=p_recipe ORDER BY s.id FOR UPDATE OF s;
 INSERT INTO production_batch(recipe_id,planned_quantity,unit_price,request_id)
 VALUES(p_recipe,p_quantity,p_price,p_request) RETURNING id INTO result_id;
 FOR ingredient IN SELECT * FROM recipe_ingredient WHERE recipe_id=p_recipe ORDER BY stock_item_id LOOP
  needed:=ingredient.quantity_per_unit*p_quantity;
  IF EXISTS(SELECT 1 FROM raw_material_lot WHERE stock_item_id=ingredient.stock_item_id) THEN
   -- Deterministic choice by lot id; quality must match the recipe.
   FOR lot IN SELECT * FROM raw_material_lot
    WHERE stock_item_id=ingredient.stock_item_id AND quality_category=quality AND remaining_kg>0
    ORDER BY id FOR UPDATE LOOP
    used:=least(needed,lot.remaining_kg);
    INSERT INTO production_material_usage VALUES(result_id,lot.id,used);
    needed:=needed-used;
    EXIT WHEN needed=0;
   END LOOP;
   IF needed>0 THEN RAISE EXCEPTION 'Insufficient suitable raw material' USING ERRCODE='23514'; END IF;
  END IF;
  INSERT INTO stock_movement(stock_item_id,production_batch_id,employee_id,
    movement_type,quantity,reason,request_id)
  VALUES(ingredient.stock_item_id,result_id,p_employee,'production_out',
    ingredient.quantity_per_unit*p_quantity,'Расход по рецептуре',p_request);
 END LOOP;
 RETURN result_id;
EXCEPTION WHEN unique_violation THEN
 SELECT id INTO result_id FROM production_batch WHERE request_id=p_request;
 IF FOUND THEN RETURN result_id; END IF;
 RAISE;
END $$;

CREATE FUNCTION register_sale(
 p_employee integer, p_batches integer[], p_quantities integer[], p_request varchar
) RETURNS integer LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE result_id integer; prior_actor text;
BEGIN
 PERFORM check_actor(p_employee);
 SELECT id INTO result_id FROM sales_transaction WHERE request_id=p_request;
 IF FOUND THEN RETURN result_id; END IF;
 IF p_batches IS NULL OR p_quantities IS NULL OR cardinality(p_batches)=0
  OR cardinality(p_batches)<>cardinality(p_quantities)
  OR array_ndims(p_batches)<>1 OR array_ndims(p_quantities)<>1
  OR EXISTS(SELECT 1 FROM unnest(p_batches,p_quantities) x(b,q) WHERE b IS NULL OR q IS NULL OR q<=0)
 THEN RAISE EXCEPTION 'Nonempty parallel arrays required' USING ERRCODE='22023'; END IF;
 -- All parties in one cheque are locked in ascending order.
 PERFORM id FROM production_batch WHERE id=ANY(p_batches) ORDER BY id FOR UPDATE;
 IF EXISTS(SELECT 1 FROM unnest(p_batches) x(id)
   WHERE NOT EXISTS(SELECT 1 FROM production_batch b WHERE b.id=x.id)) THEN
  RAISE EXCEPTION 'Batch not found' USING ERRCODE='23503';
 END IF;
 prior_actor:=current_setting('fleet.employee_id',true);
 PERFORM set_config('fleet.employee_id',p_employee::text,true);
 INSERT INTO sales_transaction(employee_id,request_id)
 VALUES(p_employee,p_request)
 ON CONFLICT (request_id) DO NOTHING RETURNING id INTO result_id;
 IF NOT FOUND THEN
  PERFORM set_config('fleet.employee_id',coalesce(prior_actor,''),true);
  SELECT id INTO STRICT result_id FROM sales_transaction WHERE request_id=p_request;
  RETURN result_id;
 END IF;
 INSERT INTO sale_item(sales_transaction_id,production_batch_id,line_number,quantity,unit_price)
 SELECT result_id,b.id,x.n,x.q,b.unit_price
 FROM unnest(p_batches,p_quantities) WITH ORDINALITY AS x(batch_id,q,n)
 JOIN production_batch b ON b.id=x.batch_id ORDER BY x.n;
 RETURN result_id;
END $$;

CREATE PROCEDURE recall_batch(p_employee integer, p_batch integer, p_reason varchar)
LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE batch_status varchar;
BEGIN
 PERFORM check_actor(p_employee,true);
 SELECT status INTO batch_status FROM production_batch WHERE id=p_batch FOR UPDATE;
 IF batch_status='recalled' THEN RETURN; END IF;
 IF batch_status IS DISTINCT FROM 'ready' THEN
  RAISE EXCEPTION 'Only a ready batch can be recalled' USING ERRCODE='23514';
 END IF;
 IF nullif(btrim(p_reason),'') IS NULL THEN
  RAISE EXCEPTION 'Recall reason required' USING ERRCODE='22023';
 END IF;
 PERFORM set_config('fleet.employee_id',p_employee::text,true);
 UPDATE production_batch SET status='recalled',recall_reason=p_reason WHERE id=p_batch;
END $$;

CREATE FUNCTION financial_summary(p_from timestamptz,p_to timestamptz)
RETURNS TABLE(product_sales numeric, refunds numeric, asset_sales numeric, net_receipts numeric)
LANGUAGE plpgsql STABLE SET search_path FROM CURRENT AS $$
BEGIN
 IF p_from IS NULL OR p_to IS NULL OR p_from>=p_to THEN
  RAISE EXCEPTION 'Expected a nonempty interval [from,to)' USING ERRCODE='22023';
 END IF;
 RETURN QUERY
 WITH a AS (SELECT coalesce(sum(i.subtotal),0) v FROM sales_transaction s
  JOIN sale_item i ON i.sales_transaction_id=s.id WHERE s.sale_time>=p_from AND s.sale_time<p_to),
 b AS (SELECT coalesce(sum(refund_amount),0) v FROM sales_return WHERE return_time>=p_from AND return_time<p_to),
 c AS (SELECT coalesce(sum(total_amount),0) v FROM asset_sale WHERE sale_date>=p_from AND sale_date<p_to)
 SELECT a.v,b.v,c.v,a.v-b.v+c.v FROM a,b,c;
END $$;

CREATE FUNCTION finish_production(p_employee integer,p_batch integer,p_actual integer)
RETURNS integer LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE b production_batch%ROWTYPE;
BEGIN
 PERFORM check_actor(p_employee,true);
 SELECT * INTO b FROM production_batch WHERE id=p_batch FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'Batch not found' USING ERRCODE='23503'; END IF;
 IF b.status='ready' AND b.actual_quantity=p_actual THEN RETURN b.id; END IF;
 IF b.status<>'producing' OR p_actual IS NULL OR p_actual<=0 THEN
  RAISE EXCEPTION 'Producing batch and positive output required' USING ERRCODE='23514';
 END IF;
 PERFORM set_config('fleet.employee_id',p_employee::text,true);
 UPDATE production_batch SET status='ready',actual_quantity=p_actual,
  finish_time=clock_timestamp() WHERE id=p_batch;
 RETURN p_batch;
END $$;

CREATE FUNCTION write_off_batch(p_employee integer,p_batch integer,p_reason varchar)
RETURNS integer LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE b production_batch%ROWTYPE;
BEGIN
 PERFORM check_actor(p_employee,true);
 SELECT * INTO b FROM production_batch WHERE id=p_batch FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'Batch not found' USING ERRCODE='23503'; END IF;
 IF b.status='written_off' THEN RETURN b.id; END IF;
 IF b.status NOT IN ('producing','ready') OR nullif(btrim(p_reason),'') IS NULL THEN
  RAISE EXCEPTION 'Writable batch and reason required' USING ERRCODE='23514';
 END IF;
 PERFORM set_config('fleet.employee_id',p_employee::text,true);
 UPDATE production_batch SET status='written_off',writeoff_reason=p_reason WHERE id=p_batch;
 RETURN p_batch;
END $$;

CREATE FUNCTION flag_blocked_chutes(p_employee integer)
RETURNS integer LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE changed integer;
BEGIN
 PERFORM check_actor(p_employee,true);
 PERFORM set_config('fleet.employee_id',p_employee::text,true);
 UPDATE chute_log SET status='blocked'
 WHERE status='in_transit' AND delivery_deadline<statement_timestamp();
 GET DIAGNOSTICS changed=ROW_COUNT;
 RETURN changed;
END $$;

CREATE FUNCTION log_audit_event(p_employee integer,p_action varchar,p_result varchar,
 p_entity varchar DEFAULT NULL,p_target integer DEFAULT NULL,p_details varchar DEFAULT NULL)
RETURNS integer LANGUAGE plpgsql SET search_path FROM CURRENT AS $$
DECLARE result_id integer;
BEGIN
 IF p_action IS NULL OR p_action NOT IN ('login','logout','access_denied',
  'inspection_enabled','inspection_disabled','report_generated') THEN
  RAISE EXCEPTION 'Unknown application audit event' USING ERRCODE='22023';
 END IF;
 INSERT INTO audit_log(employee_id,action_type,target_entity,target_id,result,details)
 VALUES(p_employee,p_action,p_entity,p_target,p_result,p_details) RETURNING id INTO result_id;
 RETURN result_id;
END $$;
