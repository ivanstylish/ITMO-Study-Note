\set ON_ERROR_STOP on
-- Fresh demo.sql identifiers. Everything is rolled back, including audit events.
\if :{?schema}
\else
\set schema public
\endif
BEGIN;
SET LOCAL search_path TO :"schema", pg_catalog;
SELECT register_sale(3,ARRAY[1,2],ARRAY[1,1],'example-sale') AS sale_id \gset
SELECT * FROM v_sale_totals WHERE id=:sale_id;
SELECT start_production(2,1,2,100,'example-production') AS batch_id \gset
SELECT * FROM production_material_usage WHERE production_batch_id=:batch_id;
CALL recall_batch(2,1,'Демонстрационный отзыв');
SELECT * FROM v_batch_balance WHERE id=1;
SELECT * FROM financial_summary('-infinity','infinity');
SET CONSTRAINTS ALL IMMEDIATE;
ROLLBACK;
