from decimal import Decimal
import pytest
import psycopg
from test_database import c, key, one, rejected

def test_sale_and_summary(c):
    before=c.execute("SELECT * FROM financial_summary('-infinity','infinity')").fetchone()
    sid=one(c,'SELECT register_sale(3,ARRAY[1,2],ARRAY[1,1],%s)',(key(),))
    assert one(c,'SELECT total_price FROM v_sale_totals WHERE id=%s',(sid,))==220
    after=c.execute("SELECT * FROM financial_summary('-infinity','infinity')").fetchone()
    assert after==(before[0]+220,before[1],before[2],before[3]+220)

@pytest.mark.parametrize('arrays',["NULL,ARRAY[1]","ARRAY[]::integer[],ARRAY[]::integer[]","ARRAY[1],ARRAY[1,2]","ARRAY[1],ARRAY[NULL]::integer[]","ARRAY[1],ARRAY[0]"])
def test_invalid_sale(c,arrays):
    rejected(c,'SELECT register_sale(3,'+arrays+',%s)',(key(),),'22023')

def test_sale_atomic_failure(c):
    before=one(c,'SELECT count(*) FROM sales_transaction')
    rejected(c,'SELECT register_sale(3,ARRAY[1,2],ARRAY[1,99999],%s)',(key(),))
    assert one(c,'SELECT count(*) FROM sales_transaction')==before

def test_missing_batch(c):
    rejected(c,'SELECT register_sale(3,ARRAY[-1],ARRAY[1],%s)',(key(),),'23503')

def test_start_production(c):
    before=one(c,'SELECT current_quantity FROM stock_item WHERE id=1')
    b=one(c,'SELECT start_production(2,1,2,100,%s)',(key(),))
    assert one(c,'SELECT sum(used_weight_kg) FROM production_material_usage WHERE production_batch_id=%s',(b,))==1
    assert one(c,'SELECT current_quantity FROM stock_item WHERE id=1')==before-1
    assert one(c,'SELECT status FROM production_batch WHERE id=%s',(b,))=='producing'

def test_production_rollback(c):
    before=c.execute('SELECT id,current_quantity FROM stock_item ORDER BY id').fetchall()
    rejected(c,'SELECT start_production(2,1,999999,100,%s)',(key(),))
    assert c.execute('SELECT id,current_quantity FROM stock_item ORDER BY id').fetchall()==before

def test_recall(c):
    c.execute("CALL recall_batch(2,1,'Контроль качества')")
    assert one(c,'SELECT quantity_balance FROM v_batch_balance WHERE id=1')==0
    rejected(c,'SELECT register_sale(3,ARRAY[1],ARRAY[1],%s)',(key(),))

def test_permissions(c):
    rejected(c,"CALL recall_batch(3,1,'test')",state='42501')
    rejected(c,'SELECT start_production(3,1,1,100,%s)',(key(),),'42501')

def test_receipt(c):
    client=one(c,"INSERT INTO client(segment) VALUES('test') RETURNING id")
    v=one(c,"INSERT INTO visit(client_id,employee_id,service_type_id,end_time,outcome,request_id) VALUES(%s,1,1,clock_timestamp(),'sent_to_chute',%s) RETURNING id",(client,key()))
    chute=one(c,"INSERT INTO chute_log(visit_id,delivery_deadline) VALUES(%s,clock_timestamp()+interval '1 hour') RETURNING id",(v,))
    lot=one(c,"SELECT receive_raw_material(2,%s,1,3,'A',%s)",(chute,key()))
    assert one(c,'SELECT remaining_kg FROM raw_material_lot WHERE id=%s',(lot,))==3
    assert one(c,'SELECT status FROM chute_log WHERE id=%s',(chute,))=='delivered'
    rejected(c,"SELECT receive_raw_material(2,%s,1,3,'A',%s)",(chute,key()))

def test_summary_interval(c):
    rejected(c,"SELECT * FROM financial_summary(now(),now())",state='22023')
    assert c.execute("SELECT * FROM financial_summary('1900-01-01','1901-01-01')").fetchone()==(0,0,0,0)
