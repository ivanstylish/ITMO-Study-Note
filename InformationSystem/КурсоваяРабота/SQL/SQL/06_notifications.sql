-- Open means the current condition. No read/unread state is stored.
CREATE VIEW v_shortage_notifications AS
SELECT s.id AS stock_item_id,s.name,s.unit,s.current_quantity,s.min_threshold,
 CASE WHEN s.is_legal THEN 'manager' ELSE 'master' END::varchar AS recipient_role
FROM stock_item s WHERE s.is_active AND s.current_quantity<=s.min_threshold;

CREATE VIEW v_blocked_chute_notifications AS
SELECT id AS chute_log_id,visit_id,dispatch_time,delivery_deadline,
 'manager'::varchar AS recipient_role
FROM chute_log WHERE status='blocked';

CREATE VIEW v_recall_notifications AS
SELECT b.id AS production_batch_id,b.recalled_at,b.recall_reason,e.id AS employee_id
FROM production_batch b CROSS JOIN employee e
WHERE b.status='recalled' AND e.status='active';
