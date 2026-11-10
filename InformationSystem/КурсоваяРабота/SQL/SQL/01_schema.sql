-- 22 relations from the approved ER. PostgreSQL 15+. Event timestamps are instants.
CREATE TABLE employee (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 login varchar(64) NOT NULL UNIQUE CHECK (btrim(login) <> ''),
 password_hash varchar(255) NOT NULL CHECK (length(password_hash) >= 20),
 name varchar(150) NOT NULL CHECK (btrim(name) <> ''),
 role_code varchar(16) NOT NULL CHECK (role_code IN ('master','manager','staff')),
 status varchar(16) NOT NULL DEFAULT 'active' CHECK (status IN ('active','suspended'))
);
CREATE TABLE client (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 name varchar(150),
 segment varchar(40) NOT NULL CHECK (btrim(segment) <> '')
);
CREATE TABLE service_type (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 name varchar(150) NOT NULL UNIQUE CHECK (btrim(name) <> ''),
 description varchar(2000),
 is_active boolean NOT NULL DEFAULT true
);
CREATE TABLE visit (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 client_id integer NOT NULL REFERENCES client ON DELETE RESTRICT,
 employee_id integer NOT NULL REFERENCES employee ON DELETE RESTRICT,
 service_type_id integer NOT NULL REFERENCES service_type ON DELETE RESTRICT,
 start_time timestamptz NOT NULL DEFAULT current_timestamp,
 end_time timestamptz,
 outcome varchar(24) NOT NULL DEFAULT 'open' CHECK (outcome IN ('open','completed','sent_to_chute')),
 request_id varchar(64) NOT NULL UNIQUE,
 CHECK (end_time IS NULL OR end_time >= start_time),
 CHECK ((outcome = 'open') = (end_time IS NULL))
);
CREATE TABLE chute_log (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 visit_id integer NOT NULL UNIQUE REFERENCES visit ON DELETE RESTRICT,
 dispatch_time timestamptz NOT NULL DEFAULT current_timestamp,
 arrival_time timestamptz,
 status varchar(24) NOT NULL DEFAULT 'in_transit' CHECK (status IN ('in_transit','blocked','delivered','error')),
 error_comment varchar(1000),
 delivery_deadline timestamptz NOT NULL,
 CHECK (delivery_deadline > dispatch_time),
 CHECK (arrival_time IS NULL OR arrival_time >= dispatch_time),
 CHECK ((status = 'delivered') = (arrival_time IS NOT NULL)),
 CHECK (status <> 'error' OR nullif(btrim(error_comment),'') IS NOT NULL)
);
CREATE TABLE stock_item (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 name varchar(150) NOT NULL UNIQUE,
 unit varchar(10) NOT NULL CHECK (unit IN ('kg','l','piece')),
 current_quantity numeric(18,3) NOT NULL DEFAULT 0 CHECK (current_quantity >= 0 AND current_quantity < 'Infinity'::numeric),
 min_threshold numeric(18,3) NOT NULL DEFAULT 0 CHECK (min_threshold >= 0 AND min_threshold < 'Infinity'::numeric),
 is_legal boolean NOT NULL DEFAULT true,
 is_active boolean NOT NULL DEFAULT true
);
CREATE TABLE raw_material_lot (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 chute_log_id integer NOT NULL UNIQUE REFERENCES chute_log ON DELETE RESTRICT,
 stock_item_id integer NOT NULL REFERENCES stock_item ON DELETE RESTRICT,
 weight_kg numeric(18,3) NOT NULL CHECK (weight_kg > 0 AND weight_kg < 'Infinity'::numeric),
 quality_category varchar(30) NOT NULL,
 received_at timestamptz NOT NULL DEFAULT current_timestamp,
 remaining_kg numeric(18,3) NOT NULL DEFAULT 0 CHECK (remaining_kg >= 0 AND remaining_kg <= weight_kg)
);
CREATE TABLE recipe (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 recipe_code varchar(64) NOT NULL,
 name varchar(150) NOT NULL,
 version integer NOT NULL CHECK (version > 0),
 yield_quantity integer NOT NULL CHECK (yield_quantity > 0),
 quality_category varchar(30) NOT NULL,
 created_at timestamptz NOT NULL DEFAULT current_timestamp,
 status varchar(16) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','current','archived')),
 UNIQUE (recipe_code, version)
);
CREATE TABLE recipe_ingredient (
 recipe_id integer NOT NULL REFERENCES recipe ON DELETE RESTRICT,
 stock_item_id integer NOT NULL REFERENCES stock_item ON DELETE RESTRICT,
 quantity_per_unit numeric(18,3) NOT NULL CHECK (quantity_per_unit > 0 AND quantity_per_unit < 'Infinity'::numeric),
 PRIMARY KEY (recipe_id, stock_item_id)
);
CREATE TABLE production_batch (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 recipe_id integer NOT NULL REFERENCES recipe ON DELETE RESTRICT,
 start_time timestamptz NOT NULL DEFAULT current_timestamp,
 finish_time timestamptz,
 planned_quantity integer NOT NULL CHECK (planned_quantity > 0),
 actual_quantity integer CHECK (actual_quantity >= 0),
 status varchar(24) NOT NULL DEFAULT 'producing' CHECK (status IN ('producing','ready','recalled','written_off')),
 unit_price numeric(14,2) NOT NULL CHECK (unit_price > 0 AND unit_price < 'Infinity'::numeric),
 recalled_at timestamptz,
 recall_reason varchar(1000),
 written_off_quantity integer NOT NULL DEFAULT 0 CHECK (written_off_quantity >= 0),
 writeoff_reason varchar(1000),
 request_id varchar(64) NOT NULL UNIQUE,
 CHECK (finish_time IS NULL OR finish_time >= start_time),
 CHECK ((status = 'producing') = (finish_time IS NULL)),
 CHECK ((status = 'producing') = (actual_quantity IS NULL)),
 CHECK (status <> 'ready' OR actual_quantity > 0),
 CHECK (written_off_quantity <= coalesce(actual_quantity,0)),
 CHECK ((status = 'recalled') = (recalled_at IS NOT NULL)),
 CHECK (status <> 'recalled' OR nullif(btrim(recall_reason),'') IS NOT NULL),
 CHECK (status <> 'written_off' OR nullif(btrim(writeoff_reason),'') IS NOT NULL)
);
CREATE TABLE production_material_usage (
 production_batch_id integer NOT NULL REFERENCES production_batch ON DELETE RESTRICT,
 raw_material_lot_id integer NOT NULL REFERENCES raw_material_lot ON DELETE RESTRICT,
 used_weight_kg numeric(18,3) NOT NULL CHECK (used_weight_kg > 0 AND used_weight_kg < 'Infinity'::numeric),
 PRIMARY KEY (production_batch_id, raw_material_lot_id)
);
CREATE TABLE stock_movement (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 stock_item_id integer NOT NULL REFERENCES stock_item ON DELETE RESTRICT,
 production_batch_id integer REFERENCES production_batch ON DELETE RESTRICT,
 raw_material_lot_id integer REFERENCES raw_material_lot ON DELETE RESTRICT,
 employee_id integer NOT NULL REFERENCES employee ON DELETE RESTRICT,
 movement_type varchar(24) NOT NULL CHECK (movement_type IN ('receipt','production_out','spoilage','correction_in','correction_out')),
 quantity numeric(18,3) NOT NULL CHECK (quantity > 0 AND quantity < 'Infinity'::numeric),
 reason varchar(1000) NOT NULL CHECK (btrim(reason) <> ''),
 occurred_at timestamptz NOT NULL DEFAULT current_timestamp,
 request_id varchar(64) NOT NULL,
 CHECK (num_nonnulls(production_batch_id,raw_material_lot_id) <= 1),
 CHECK ((movement_type = 'production_out') = (production_batch_id IS NOT NULL)),
 UNIQUE (request_id, stock_item_id, movement_type)
);
CREATE TABLE sales_transaction (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 employee_id integer NOT NULL REFERENCES employee ON DELETE RESTRICT,
 sale_time timestamptz NOT NULL DEFAULT current_timestamp,
 request_id varchar(64) NOT NULL UNIQUE
);
CREATE TABLE sale_item (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 sales_transaction_id integer NOT NULL REFERENCES sales_transaction ON DELETE RESTRICT,
 production_batch_id integer NOT NULL REFERENCES production_batch ON DELETE RESTRICT,
 line_number integer NOT NULL CHECK (line_number > 0),
 quantity integer NOT NULL CHECK (quantity > 0),
 unit_price numeric(14,2) NOT NULL CHECK (unit_price > 0 AND unit_price < 'Infinity'::numeric),
 subtotal numeric(18,2) GENERATED ALWAYS AS (quantity * unit_price) STORED NOT NULL,
 UNIQUE (sales_transaction_id,line_number)
);
CREATE TABLE sales_return (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 sale_item_id integer NOT NULL REFERENCES sale_item ON DELETE RESTRICT,
 employee_id integer NOT NULL REFERENCES employee ON DELETE RESTRICT,
 quantity integer NOT NULL CHECK (quantity > 0),
 refund_amount numeric(18,2) NOT NULL CHECK (refund_amount > 0 AND refund_amount < 'Infinity'::numeric),
 restock_quantity integer NOT NULL DEFAULT 0 CHECK (restock_quantity >= 0 AND restock_quantity <= quantity),
 reason varchar(1000) NOT NULL CHECK (btrim(reason) <> ''),
 return_time timestamptz NOT NULL DEFAULT current_timestamp,
 request_id varchar(64) NOT NULL UNIQUE
);
CREATE TABLE complaint (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 sales_transaction_id integer REFERENCES sales_transaction ON DELETE RESTRICT,
 production_batch_id integer REFERENCES production_batch ON DELETE RESTRICT,
 employee_id integer NOT NULL REFERENCES employee ON DELETE RESTRICT,
 description varchar(2000) NOT NULL CHECK (btrim(description) <> ''),
 resolution varchar(2000),
 status varchar(24) NOT NULL DEFAULT 'open' CHECK (status IN ('open','closed')),
 registered_at timestamptz NOT NULL DEFAULT current_timestamp,
 resolved_at timestamptz,
 CHECK ((status = 'closed') = (resolved_at IS NOT NULL)),
 CHECK (resolved_at IS NULL OR resolved_at >= registered_at),
 CHECK (status <> 'closed' OR nullif(btrim(resolution),'') IS NOT NULL)
);
CREATE TABLE buyer (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 name varchar(150) NOT NULL UNIQUE,
 is_active boolean NOT NULL DEFAULT true
);
CREATE TABLE asset_sale (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 buyer_id integer NOT NULL REFERENCES buyer ON DELETE RESTRICT,
 employee_id integer NOT NULL REFERENCES employee ON DELETE RESTRICT,
 sale_date timestamptz NOT NULL DEFAULT current_timestamp,
 total_amount numeric(18,2) NOT NULL CHECK (total_amount > 0 AND total_amount < 'Infinity'::numeric),
 request_id varchar(64) NOT NULL UNIQUE
);
CREATE TABLE side_asset (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 visit_id integer NOT NULL REFERENCES visit ON DELETE RESTRICT,
 asset_sale_id integer REFERENCES asset_sale ON DELETE RESTRICT,
 name varchar(150) NOT NULL,
 description varchar(2000),
 estimated_value numeric(18,2) NOT NULL CHECK (estimated_value >= 0 AND estimated_value < 'Infinity'::numeric),
 seized_at timestamptz NOT NULL DEFAULT current_timestamp,
 status varchar(24) NOT NULL DEFAULT 'held' CHECK (status IN ('held','sold')),
 CHECK ((status = 'sold') = (asset_sale_id IS NOT NULL))
);
CREATE TABLE solid_waste (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 raw_material_lot_id integer REFERENCES raw_material_lot ON DELETE RESTRICT,
 production_batch_id integer REFERENCES production_batch ON DELETE RESTRICT,
 waste_type varchar(100) NOT NULL,
 quantity numeric(18,3) NOT NULL CHECK (quantity > 0 AND quantity < 'Infinity'::numeric),
 unit varchar(10) NOT NULL CHECK (unit IN ('kg','piece')),
 generated_at timestamptz NOT NULL DEFAULT current_timestamp,
 disposal_method varchar(24) NOT NULL CHECK (disposal_method IN ('incineration','transport','burial')),
 disposal_time timestamptz,
 CHECK (num_nonnulls(raw_material_lot_id,production_batch_id) = 1),
 CHECK (disposal_time IS NULL OR disposal_time >= generated_at)
);
CREATE TABLE task (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 solid_waste_id integer UNIQUE REFERENCES solid_waste ON DELETE RESTRICT,
 created_by integer NOT NULL REFERENCES employee ON DELETE RESTRICT,
 assigned_to integer NOT NULL REFERENCES employee ON DELETE RESTRICT,
 confirmed_by integer REFERENCES employee ON DELETE RESTRICT,
 description varchar(2000) NOT NULL,
 location varchar(150) NOT NULL,
 status varchar(24) NOT NULL DEFAULT 'assigned' CHECK (status IN ('assigned','done','confirmed')),
 deadline timestamptz NOT NULL,
 created_at timestamptz NOT NULL DEFAULT current_timestamp,
 completed_at timestamptz,
 confirmed_at timestamptz,
 completion_comment varchar(2000),
 CHECK (deadline >= created_at),
 CHECK ((status = 'assigned') = (completed_at IS NULL)),
 CHECK ((status = 'confirmed') = (confirmed_at IS NOT NULL)),
 CHECK ((confirmed_at IS NULL) = (confirmed_by IS NULL)),
 CHECK (completed_at IS NULL OR completed_at >= created_at),
 CHECK (confirmed_at IS NULL OR confirmed_at >= completed_at)
);
CREATE TABLE audit_log (
 id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 employee_id integer REFERENCES employee ON DELETE RESTRICT,
 occurred_at timestamptz NOT NULL DEFAULT current_timestamp,
 action_type varchar(32) NOT NULL,
 target_entity varchar(63),
 target_id integer,
 result varchar(16) NOT NULL CHECK (result IN ('success','denied','error')),
 details varchar(2000)
);
-- Derived results: no duplicated sale header totals or product balance cache.
CREATE VIEW v_sale_totals AS
 SELECT s.id,s.employee_id,s.sale_time,coalesce(sum(i.subtotal),0)::numeric(18,2) AS total_price
 FROM sales_transaction s LEFT JOIN sale_item i ON i.sales_transaction_id=s.id GROUP BY s.id;
CREATE VIEW v_batch_balance AS
 SELECT b.id,b.status,b.actual_quantity,b.unit_price,
 coalesce(b.actual_quantity,0)::integer
 - coalesce((SELECT sum(i.quantity) FROM sale_item i WHERE i.production_batch_id=b.id),0)
 + coalesce((SELECT sum(r.restock_quantity) FROM sales_return r JOIN sale_item i ON i.id=r.sale_item_id WHERE i.production_batch_id=b.id),0)
 - b.written_off_quantity AS quantity_balance
 FROM production_batch b;
CREATE VIEW v_available_batches AS
 SELECT * FROM v_batch_balance WHERE status='ready' AND quantity_balance>0;
CREATE VIEW v_stock_shortage AS
 SELECT id,name,unit,current_quantity,min_threshold FROM stock_item
 WHERE is_active AND current_quantity<=min_threshold;
CREATE VIEW v_disposal_log AS
 SELECT w.id AS waste_id,w.waste_type,w.quantity,w.unit,w.disposal_method,w.disposal_time,
 t.id AS task_id,t.assigned_to,t.confirmed_by,t.confirmed_at
 FROM solid_waste w JOIN task t ON t.solid_waste_id=w.id WHERE t.status='confirmed';

-- These partial unique indexes implement integrity, not speculative optimization.
CREATE UNIQUE INDEX uq_recipe_current ON recipe(recipe_code) WHERE status='current';
CREATE UNIQUE INDEX uq_lot_receipt ON stock_movement(raw_material_lot_id)
 WHERE movement_type='receipt' AND raw_material_lot_id IS NOT NULL;
CREATE UNIQUE INDEX uq_batch_component ON stock_movement(production_batch_id,stock_item_id)
 WHERE production_batch_id IS NOT NULL;

