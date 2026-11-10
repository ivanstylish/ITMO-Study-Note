import threading
import time
import pytest
from test_database import c, connection, key, one, rejected, race

def pending(c, overdue=False):
    cli=one(c,"INSERT INTO client(segment) VALUES('test') RETURNING id")
    v=one(c,"INSERT INTO visit(client_id,employee_id,service_type_id,start_time,end_time,outcome,request_id) VALUES(%s,1,1,now()-interval '2 hours',now()-interval '1 hour','sent_to_chute',%s) RETURNING id",(cli,key()))
    return one(c,"INSERT INTO chute_log(visit_id,dispatch_time,delivery_deadline) VALUES(%s,now()-interval '1 hour',now()+%s::interval) RETURNING id",(v,'-1 minute' if overdue else '1 hour'))

def test_master_operations_and_finish(c):
    chute=pending(c)
    request=key()
    lot=one(c,"SELECT receive_raw_material(1,%s,1,2,'A',%s)",(chute,request))
    assert one(c,"SELECT receive_raw_material(1,%s,1,2,'A',%s)",(chute,request))==lot
    before=one(c,'SELECT current_quantity FROM stock_item WHERE id=1')
    request=key()
    b=one(c,'SELECT start_production(1,1,2,100,%s)',(request,))
    assert one(c,'SELECT start_production(1,1,2,100,%s)',(request,))==b
    assert one(c,'SELECT current_quantity FROM stock_item WHERE id=1')==before-1
    assert one(c,'SELECT finish_production(1,%s,2)',(b,))==b
    audit_before=one(c,'SELECT count(*) FROM audit_log')
    assert one(c,'SELECT finish_production(1,%s,2)',(b,))==b
    assert one(c,'SELECT count(*) FROM audit_log')==audit_before
    rejected(c,'SELECT finish_production(1,%s,3)',(b,))
    c.execute("CALL recall_batch(1,%s,'quality')",(b,))
    history=c.execute('SELECT recalled_at,written_off_quantity,recall_reason FROM production_batch WHERE id=%s',(b,)).fetchone()
    c.execute("CALL recall_batch(1,%s,'repeat')",(b,))
    assert c.execute('SELECT recalled_at,written_off_quantity,recall_reason FROM production_batch WHERE id=%s',(b,)).fetchone()==history

def test_sale_repeat(c):
    request=key()
    sid=one(c,'SELECT register_sale(3,ARRAY[1],ARRAY[1],%s)',(request,))
    balance=one(c,'SELECT quantity_balance FROM v_batch_balance WHERE id=1')
    assert one(c,'SELECT register_sale(3,ARRAY[1],ARRAY[1],%s)',(request,))==sid
    assert one(c,'SELECT quantity_balance FROM v_batch_balance WHERE id=1')==balance

def test_producing_cannot_recall(c):
    b=one(c,'SELECT start_production(2,1,1,100,%s)',(key(),))
    rejected(c,"CALL recall_batch(2,%s,'quality')",(b,))
    rejected(c,"UPDATE production_batch SET status='recalled',recall_reason='x' WHERE id=%s",(b,))

@pytest.mark.parametrize('ready',[False,True])
def test_write_off(c,ready):
    b=one(c,'SELECT start_production(2,1,2,100,%s)',(key(),))
    if ready: c.execute('SELECT finish_production(2,%s,2)',(b,))
    rejected(c,"SELECT write_off_batch(2,%s,'')",(b,))
    assert one(c,"SELECT write_off_batch(1,%s,'Брак')",(b,))==b
    assert one(c,"SELECT write_off_batch(1,%s,'Повтор')",(b,))==b
    assert one(c,'SELECT quantity_balance FROM v_batch_balance WHERE id=%s',(b,))==0
    rejected(c,'SELECT register_sale(3,ARRAY[%s],ARRAY[1],%s)',(b,key()))

def test_blocked_and_notifications(c):
    chute=pending(c,True)
    assert one(c,'SELECT flag_blocked_chutes(1)')==1
    assert one(c,'SELECT flag_blocked_chutes(2)')==0
    assert one(c,'SELECT count(*) FROM v_blocked_chute_notifications WHERE chute_log_id=%s',(chute,))==1
    c.execute("SELECT receive_raw_material(1,%s,1,2,'A',%s)",(chute,key()))
    assert one(c,'SELECT count(*) FROM v_blocked_chute_notifications WHERE chute_log_id=%s',(chute,))==0
    c.execute('UPDATE stock_item SET min_threshold=1000')
    assert c.execute('SELECT stock_item_id,recipient_role FROM v_shortage_notifications ORDER BY stock_item_id').fetchall()==[(1,'master'),(2,'manager')]
    c.execute("CALL recall_batch(1,1,'quality')")
    assert one(c,'SELECT count(*) FROM v_recall_notifications WHERE production_batch_id=1')==3
    assert one(c,'SELECT count(*) FROM (SELECT production_batch_id,employee_id FROM v_recall_notifications GROUP BY 1,2 HAVING count(*)>1) x')==0

def test_log_application_events(c):
    event=one(c,"SELECT log_audit_event(NULL,'login','denied',NULL,NULL,'unknown account')")
    assert one(c,'SELECT result FROM audit_log WHERE id=%s',(event,))=='denied'
    rejected(c,"SELECT log_audit_event(1,'invented','success')",state='22023')
    rejected(c,'UPDATE audit_log SET details=details WHERE id=%s',(event,))

@pytest.mark.parametrize('operation',[
 'SELECT finish_production(3,1,1)',"SELECT write_off_batch(3,1,'x')",'SELECT flag_blocked_chutes(3)'])
def test_new_operations_reject_staff(c,operation):
    rejected(c,operation,state='42501')

def test_concurrent_idempotent_sale_unique_handler():
    request=key();ids=[]
    race(lambda c:ids.append(one(c,'SELECT register_sale(3,ARRAY[1],ARRAY[1],%s)',(request,))),
         lambda c:ids.append(one(c,'SELECT register_sale(3,ARRAY[2],ARRAY[1],%s)',(request,))),'success')
    assert len(ids)==2 and ids[0]==ids[1]

def test_concurrent_idempotent_production():
    request=key();ids=[]
    race(lambda c:ids.append(one(c,'SELECT start_production(1,1,1,100,%s)',(request,))),
         lambda c:ids.append(one(c,'SELECT start_production(1,1,1,100,%s)',(request,))),'success')
    assert len(ids)==2 and ids[0]==ids[1]

def test_concurrent_idempotent_receipt():
    with connection() as setup:
        with setup.transaction(): chute=pending(setup)
    request=key();ids=[]
    race(lambda c:ids.append(one(c,"SELECT receive_raw_material(1,%s,1,2,'A',%s)",(chute,request))),
         lambda c:ids.append(one(c,"SELECT receive_raw_material(1,%s,1,2,'A',%s)",(chute,request))),'success')
    assert len(ids)==2 and ids[0]==ids[1]

def test_routine_uses_installation_schema(c):
    schema=one(c,'SELECT current_schema()')
    c.execute('SET LOCAL search_path TO pg_catalog')
    import psycopg
    result=c.execute(psycopg.sql.SQL("SELECT {}.financial_summary('1900-01-01','1901-01-01')").format(psycopg.sql.Identifier(schema))).fetchone()
    assert result is not None
