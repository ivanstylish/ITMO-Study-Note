-- UC08/UC10: stock balance and recall of a batch.
CREATE INDEX ix_sale_item_batch ON sale_item(production_batch_id);
-- UC09/UC14: return limits, restocking and refund totals.
CREATE INDEX ix_return_item ON sales_return(sale_item_id);
-- UC04/UC07: finding suitable remaining lots, then locking by id.
CREATE INDEX ix_lot_available ON raw_material_lot(stock_item_id,quality_category,id)
 WHERE remaining_kg>0;
-- UC14: interval filters; existing sale_item UNIQUE starts with sales_transaction_id.
CREATE INDEX ix_sale_time ON sales_transaction(sale_time);
CREATE INDEX ix_return_time ON sales_return(return_time);
CREATE INDEX ix_asset_sale_time ON asset_sale(sale_date);

-- UC17: chronological audit and employee history.
CREATE INDEX ix_audit_time ON audit_log(occurred_at);
CREATE INDEX ix_audit_employee_time ON audit_log(employee_id,occurred_at);
-- UC12: a staff member's assigned/done tasks.
CREATE INDEX ix_task_assignee_status ON task(assigned_to,status);
-- UC02/03, FR15: client visits and a date interval.
CREATE INDEX ix_visit_client ON visit(client_id);
CREATE INDEX ix_visit_start ON visit(start_time);
-- UC04, FR05: open deliveries; completed history excluded.
CREATE INDEX ix_chute_open_status ON chute_log(status)
 WHERE status IN ('in_transit','blocked');
-- UC09: complaints by batch and by date.
CREATE INDEX ix_complaint_batch ON complaint(production_batch_id);
CREATE INDEX ix_complaint_time ON complaint(registered_at);
