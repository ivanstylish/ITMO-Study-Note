\set ON_ERROR_STOP on
\encoding UTF8
BEGIN;
-- Отдельная схема; существующая fleet не перезаписывается.
CREATE SCHEMA fleet;
SET LOCAL search_path = fleet, public;

CREATE TABLE employee (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    login text NOT NULL UNIQUE, password_hash text NOT NULL, name text NOT NULL,
    is_master boolean NOT NULL DEFAULT false,
    is_manager boolean NOT NULL DEFAULT false,
    is_staff boolean NOT NULL DEFAULT false,
    is_active boolean NOT NULL DEFAULT true,
    CHECK (is_master OR is_manager OR is_staff)
);
CREATE TABLE client (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL, segment text NOT NULL
);
CREATE TABLE service_type (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL UNIQUE, description text,
    is_active boolean NOT NULL DEFAULT true
);
CREATE TABLE visit (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id bigint NOT NULL REFERENCES employee ON DELETE RESTRICT,
    client_id bigint NOT NULL REFERENCES client ON DELETE RESTRICT,
    service_type_id bigint NOT NULL REFERENCES service_type ON DELETE RESTRICT,
    start_time timestamptz NOT NULL DEFAULT now(), end_time timestamptz,
    outcome text NOT NULL CHECK (outcome IN ('in_progress','completed','transferred')),
    request_id uuid NOT NULL UNIQUE,
    CHECK (end_time >= start_time)
);
CREATE TABLE chute_log (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    visit_id bigint NOT NULL UNIQUE REFERENCES visit ON DELETE RESTRICT,
    dispatch_time timestamptz NOT NULL DEFAULT now(), arrival_time timestamptz,
    status text NOT NULL CHECK (status IN ('pending','arrived','failed')),
    error_comment text, delivery_deadline timestamptz NOT NULL,
    CHECK (arrival_time >= dispatch_time), CHECK (delivery_deadline >= dispatch_time)
);
CREATE TABLE stock_item (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL UNIQUE, unit text NOT NULL,
    current_quantity numeric(18,3) NOT NULL DEFAULT 0 CHECK (current_quantity >= 0 AND current_quantity < 'Infinity'::numeric),
    min_threshold numeric(18,3) NOT NULL DEFAULT 0 CHECK (min_threshold >= 0 AND min_threshold < 'Infinity'::numeric),
    is_legal boolean NOT NULL, is_active boolean NOT NULL DEFAULT true
);
CREATE TABLE raw_material_lot (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    chute_log_id bigint NOT NULL UNIQUE REFERENCES chute_log ON DELETE RESTRICT,
    stock_item_id bigint NOT NULL REFERENCES stock_item ON DELETE RESTRICT,
    weight_kg numeric(18,3) NOT NULL CHECK (weight_kg > 0 AND weight_kg < 'Infinity'::numeric),
    quality_category text NOT NULL, received_at timestamptz NOT NULL DEFAULT now(),
    remaining_kg numeric(18,3) NOT NULL CHECK (remaining_kg >= 0 AND remaining_kg <= weight_kg)
);
CREATE TABLE recipe (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recipe_code text NOT NULL, name text NOT NULL, version integer NOT NULL CHECK (version > 0),
    yield_quantity integer NOT NULL CHECK (yield_quantity > 0), quality_category text NOT NULL,
    is_current boolean NOT NULL DEFAULT true, is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(), UNIQUE (recipe_code, version)
);
CREATE TABLE recipe_ingredient (
    recipe_id bigint NOT NULL REFERENCES recipe ON DELETE RESTRICT,
    stock_item_id bigint NOT NULL REFERENCES stock_item ON DELETE RESTRICT,
    quantity_per_unit numeric(18,3) NOT NULL CHECK (quantity_per_unit > 0 AND quantity_per_unit < 'Infinity'::numeric),
    PRIMARY KEY (recipe_id, stock_item_id)
);
CREATE TABLE production_batch (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recipe_id bigint NOT NULL REFERENCES recipe ON DELETE RESTRICT,
    start_time timestamptz NOT NULL DEFAULT now(), finish_time timestamptz,
    planned_quantity integer NOT NULL CHECK (planned_quantity > 0),
    actual_quantity integer NOT NULL DEFAULT 0 CHECK (actual_quantity >= 0),
    status text NOT NULL CHECK (status IN ('planned','in_progress','ready','recalled')),
    unit_price numeric(14,2) NOT NULL CHECK (unit_price > 0 AND unit_price < 'Infinity'::numeric),
    recalled_at timestamptz, recall_reason text,
    written_off_quantity integer NOT NULL DEFAULT 0 CHECK (written_off_quantity >= 0 AND written_off_quantity <= actual_quantity),
    writeoff_reason text, request_id uuid NOT NULL UNIQUE,
    CHECK (finish_time >= start_time),
    CHECK (status <> 'ready' OR (finish_time IS NOT NULL AND actual_quantity > 0)),
    CHECK (status <> 'recalled' OR (recalled_at IS NOT NULL AND recall_reason IS NOT NULL))
);
CREATE TABLE production_material_usage (
    production_batch_id bigint NOT NULL REFERENCES production_batch ON DELETE RESTRICT,
    raw_material_lot_id bigint NOT NULL REFERENCES raw_material_lot ON DELETE RESTRICT,
    used_weight_kg numeric(18,3) NOT NULL CHECK (used_weight_kg > 0 AND used_weight_kg < 'Infinity'::numeric),
    PRIMARY KEY (production_batch_id, raw_material_lot_id)
);
CREATE TABLE stock_movement (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stock_item_id bigint NOT NULL REFERENCES stock_item ON DELETE RESTRICT,
    employee_id bigint NOT NULL REFERENCES employee ON DELETE RESTRICT,
    raw_material_lot_id bigint REFERENCES raw_material_lot ON DELETE RESTRICT,
    production_batch_id bigint REFERENCES production_batch ON DELETE RESTRICT,
    movement_type text NOT NULL CHECK (movement_type IN ('receipt','usage','loss')),
    quantity numeric(18,3) NOT NULL CHECK (quantity > 0 AND quantity < 'Infinity'::numeric),
    reason text NOT NULL, occurred_at timestamptz NOT NULL DEFAULT now(), request_id uuid NOT NULL UNIQUE
);
CREATE TABLE sales_transaction (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id bigint NOT NULL REFERENCES employee ON DELETE RESTRICT,
    sale_time timestamptz NOT NULL DEFAULT now(), request_id uuid NOT NULL UNIQUE
);
CREATE TABLE sale_item (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sales_transaction_id bigint NOT NULL REFERENCES sales_transaction ON DELETE RESTRICT,
    production_batch_id bigint NOT NULL REFERENCES production_batch ON DELETE RESTRICT,
    line_number integer NOT NULL CHECK (line_number > 0), quantity integer NOT NULL CHECK (quantity > 0),
    unit_price numeric(14,2) NOT NULL CHECK (unit_price > 0 AND unit_price < 'Infinity'::numeric),
    subtotal numeric(18,2) GENERATED ALWAYS AS (quantity * unit_price) STORED NOT NULL,
    UNIQUE (sales_transaction_id, line_number)
);
CREATE TABLE sales_return (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sale_item_id bigint NOT NULL REFERENCES sale_item ON DELETE RESTRICT,
    employee_id bigint NOT NULL REFERENCES employee ON DELETE RESTRICT,
    quantity integer NOT NULL CHECK (quantity > 0),
    refund_amount numeric(18,2) NOT NULL CHECK (refund_amount > 0 AND refund_amount < 'Infinity'::numeric),
    restock_quantity integer NOT NULL CHECK (restock_quantity BETWEEN 0 AND quantity),
    reason text NOT NULL, return_time timestamptz NOT NULL DEFAULT now(), request_id uuid NOT NULL UNIQUE
);
CREATE TABLE complaint (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sales_transaction_id bigint REFERENCES sales_transaction ON DELETE RESTRICT,
    production_batch_id bigint REFERENCES production_batch ON DELETE RESTRICT,
    employee_id bigint NOT NULL REFERENCES employee ON DELETE RESTRICT,
    description text NOT NULL, resolution text,
    status text NOT NULL CHECK (status IN ('open','resolved')),
    registered_at timestamptz NOT NULL DEFAULT now(), resolved_at timestamptz,
    CHECK (resolved_at >= registered_at)
);
CREATE TABLE solid_waste (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    raw_material_lot_id bigint REFERENCES raw_material_lot ON DELETE RESTRICT,
    production_batch_id bigint REFERENCES production_batch ON DELETE RESTRICT,
    waste_type text NOT NULL, quantity numeric(18,3) NOT NULL CHECK (quantity > 0 AND quantity < 'Infinity'::numeric),
    unit text NOT NULL, generated_at timestamptz NOT NULL DEFAULT now(),
    disposal_method text, disposal_time timestamptz,
    CHECK (num_nonnulls(raw_material_lot_id, production_batch_id) = 1),
    CHECK (disposal_time >= generated_at)
);
CREATE TABLE task (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_by bigint NOT NULL REFERENCES employee ON DELETE RESTRICT,
    assigned_to bigint NOT NULL REFERENCES employee ON DELETE RESTRICT,
    confirmed_by bigint REFERENCES employee ON DELETE RESTRICT,
    solid_waste_id bigint UNIQUE REFERENCES solid_waste ON DELETE RESTRICT,
    description text NOT NULL, location text NOT NULL,
    status text NOT NULL DEFAULT 'assigned' CHECK (status IN ('assigned','done','confirmed')),
    deadline timestamptz NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
    completed_at timestamptz, confirmed_at timestamptz, completion_comment text,
    CHECK (completed_at >= created_at), CHECK (confirmed_at >= completed_at)
);
CREATE TABLE buyer (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL, is_active boolean NOT NULL DEFAULT true
);
CREATE TABLE asset_sale (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    buyer_id bigint NOT NULL REFERENCES buyer ON DELETE RESTRICT,
    employee_id bigint NOT NULL REFERENCES employee ON DELETE RESTRICT,
    sale_date timestamptz NOT NULL DEFAULT now(),
    total_amount numeric(18,2) NOT NULL CHECK (total_amount > 0 AND total_amount < 'Infinity'::numeric),
    request_id uuid NOT NULL UNIQUE
);
CREATE TABLE side_asset (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    visit_id bigint NOT NULL REFERENCES visit ON DELETE RESTRICT,
    asset_sale_id bigint REFERENCES asset_sale ON DELETE RESTRICT,
    name text NOT NULL, description text,
    estimated_value numeric(14,2) NOT NULL CHECK (estimated_value >= 0 AND estimated_value < 'Infinity'::numeric),
    seized_at timestamptz NOT NULL DEFAULT now(),
    status text NOT NULL CHECK (status IN ('available','sold')),
    CHECK ((status = 'sold') = (asset_sale_id IS NOT NULL))
);
CREATE TABLE audit_log (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id bigint REFERENCES employee ON DELETE RESTRICT,
    occurred_at timestamptz NOT NULL DEFAULT now(), action_type text NOT NULL,
    target_entity text NOT NULL, target_id bigint, result text NOT NULL, details jsonb NOT NULL DEFAULT '{}'
);

CREATE VIEW v_sale_totals AS
SELECT s.id, s.employee_id, s.sale_time, coalesce(sum(i.subtotal), 0) AS total_price
FROM sales_transaction s LEFT JOIN sale_item i ON i.sales_transaction_id = s.id
GROUP BY s.id;

-- Продажи и возвраты агрегируются раздельно, чтобы JOIN не умножал суммы.
CREATE VIEW v_batch_balance AS
SELECT b.id, b.status, b.actual_quantity,
       b.actual_quantity - b.written_off_quantity
       - coalesce((SELECT sum(i.quantity) FROM sale_item i WHERE i.production_batch_id = b.id), 0)
       + coalesce((SELECT sum(r.restock_quantity) FROM sales_return r
                   JOIN sale_item i ON i.id = r.sale_item_id WHERE i.production_batch_id = b.id), 0) AS available_quantity
FROM production_batch b;

CREATE UNIQUE INDEX uq_recipe_current ON recipe (recipe_code) WHERE is_current;
CREATE INDEX ix_visit_client_time ON visit (client_id, start_time DESC);
CREATE INDEX ix_sale_item_batch ON sale_item (production_batch_id);
CREATE INDEX ix_return_item ON sales_return (sale_item_id);
CREATE INDEX ix_usage_lot ON production_material_usage (raw_material_lot_id);
CREATE INDEX ix_movement_stock_time ON stock_movement (stock_item_id, occurred_at DESC);
CREATE INDEX ix_task_assignee_open ON task (assigned_to, deadline) WHERE status <> 'confirmed';

CREATE FUNCTION apply_stock_movement() RETURNS trigger LANGUAGE plpgsql SET search_path = fleet, pg_temp AS $$
DECLARE delta numeric;
BEGIN
    delta := CASE WHEN NEW.movement_type = 'receipt' THEN NEW.quantity ELSE -NEW.quantity END;
    UPDATE stock_item SET current_quantity = current_quantity + delta
    WHERE id = NEW.stock_item_id AND current_quantity + delta >= 0;
    IF NOT FOUND THEN RAISE EXCEPTION 'Недостаточный складской остаток или неизвестная позиция'; END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER stock_balance BEFORE INSERT ON stock_movement
FOR EACH ROW EXECUTE FUNCTION apply_stock_movement();

CREATE FUNCTION check_sale_item() RETURNS trigger LANGUAGE plpgsql SET search_path = fleet, pg_temp AS $$
DECLARE b production_batch;
BEGIN
    SELECT * INTO b FROM production_batch WHERE id = NEW.production_batch_id FOR UPDATE;
    IF NOT FOUND OR b.status <> 'ready' THEN RAISE EXCEPTION 'Партия недоступна для продажи'; END IF;
    IF NEW.unit_price <> b.unit_price THEN RAISE EXCEPTION 'Цена не соответствует партии'; END IF;
    IF NEW.quantity > (SELECT available_quantity FROM v_batch_balance WHERE id = b.id) THEN
        RAISE EXCEPTION 'Недостаточно готовой продукции';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER sale_item_check BEFORE INSERT ON sale_item FOR EACH ROW EXECUTE FUNCTION check_sale_item();

CREATE FUNCTION check_return() RETURNS trigger LANGUAGE plpgsql SET search_path = fleet, pg_temp AS $$
DECLARE item sale_item; batch_status text; returned bigint; refunded numeric;
BEGIN
    SELECT * INTO STRICT item FROM sale_item WHERE id = NEW.sale_item_id;
    SELECT status INTO batch_status FROM production_batch WHERE id = item.production_batch_id FOR UPDATE;
    SELECT coalesce(sum(quantity),0), coalesce(sum(refund_amount),0) INTO returned, refunded
    FROM sales_return WHERE sale_item_id = item.id;
    IF NEW.quantity + returned > item.quantity OR NEW.refund_amount + refunded > item.subtotal
       OR NEW.refund_amount > NEW.quantity * item.unit_price THEN
        RAISE EXCEPTION 'Возврат превышает проданное количество или сумму';
    END IF;
    IF batch_status <> 'ready' AND NEW.restock_quantity > 0 THEN
        RAISE EXCEPTION 'Возврат на склад доступен только для готовой партии';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER return_check BEFORE INSERT ON sales_return FOR EACH ROW EXECUTE FUNCTION check_return();

CREATE FUNCTION reject_history_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'История % неизменяема: % запрещён', TG_TABLE_NAME, TG_OP;
END $$;
DO $$
DECLARE t text;
BEGIN
    FOREACH t IN ARRAY ARRAY['sales_transaction','sale_item','sales_return','stock_movement','audit_log'] LOOP
        EXECUTE format('CREATE TRIGGER history_guard BEFORE UPDATE OR DELETE OR TRUNCATE ON %I FOR EACH STATEMENT EXECUTE FUNCTION reject_history_change()', t);
    END LOOP;
END $$;

CREATE FUNCTION check_nonempty_sale() RETURNS trigger LANGUAGE plpgsql SET search_path = fleet, pg_temp AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM sale_item WHERE sales_transaction_id = NEW.id) THEN
        RAISE EXCEPTION 'Продажа должна содержать хотя бы одну позицию';
    END IF;
    RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER nonempty_sale AFTER INSERT ON sales_transaction
DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION check_nonempty_sale();

-- shortcut: учебный API без повторного исполнения request_id; для приложения добавить идемпотентность и серверную авторизацию.
CREATE FUNCTION register_sale(p_actor bigint, p_request uuid, p_items jsonb)
RETURNS bigint LANGUAGE plpgsql SET search_path = fleet, pg_temp AS $$
DECLARE sale_id bigint; item jsonb; n integer := 0;
BEGIN
    IF current_setting('transaction_isolation') <> 'read committed' THEN
        RAISE EXCEPTION 'Требуется READ COMMITTED';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM employee WHERE id = p_actor AND is_active) THEN
        RAISE EXCEPTION 'Нужен активный сотрудник';
    END IF;
    IF p_items IS NULL OR jsonb_typeof(p_items) <> 'array' THEN RAISE EXCEPTION 'Нужен массив позиций'; END IF;
    IF jsonb_array_length(p_items) = 0 THEN RAISE EXCEPTION 'Пустая продажа'; END IF;
    -- Общий порядок блокировки партий предотвращает взаимную блокировку двух продаж.
    PERFORM b.id FROM production_batch b
    WHERE b.id IN (SELECT (x->>'batch_id')::bigint FROM jsonb_array_elements(p_items) x)
    ORDER BY b.id FOR UPDATE;
    INSERT INTO sales_transaction(employee_id, request_id) VALUES (p_actor, p_request) RETURNING id INTO sale_id;
    FOR item IN SELECT * FROM jsonb_array_elements(p_items) LOOP
        n := n + 1;
        INSERT INTO sale_item(sales_transaction_id, production_batch_id, line_number, quantity, unit_price)
        VALUES (sale_id, (item->>'batch_id')::bigint, n, (item->>'quantity')::integer,
                (SELECT unit_price FROM production_batch WHERE id = (item->>'batch_id')::bigint));
    END LOOP;
    INSERT INTO audit_log(employee_id, action_type, target_entity, target_id, result, details)
    VALUES (p_actor, 'sale', 'sales_transaction', sale_id, 'success', p_items);
    RETURN sale_id;
END $$;

CREATE PROCEDURE change_batch_price(p_actor bigint, p_batch bigint, p_price numeric)
LANGUAGE plpgsql SET search_path = fleet, pg_temp AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM employee WHERE id = p_actor AND is_active AND (is_manager OR is_master)) THEN
        RAISE EXCEPTION 'Нужна роль управляющего или мастера';
    END IF;
    UPDATE production_batch SET unit_price = p_price WHERE id = p_batch AND status = 'ready';
    IF NOT FOUND THEN RAISE EXCEPTION 'Готовая партия не найдена'; END IF;
    INSERT INTO audit_log(employee_id, action_type, target_entity, target_id, result, details)
    VALUES (p_actor, 'price_change', 'production_batch', p_batch, 'success', jsonb_build_object('unit_price', p_price));
END $$;
COMMIT;
\echo 'Созданы 22 таблицы, 34 внешних ключа, 2 представления, триггеры, функция продажи и процедура цены.'
