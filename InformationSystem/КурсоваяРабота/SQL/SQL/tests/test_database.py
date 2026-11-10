"""Run against the separate test database after install.sql and demo.sql."""
import os
import threading
import time
import uuid
from decimal import Decimal

import psycopg
import pytest

DSN = os.environ.get('FLEET_TEST_DSN', 'host=127.0.0.1 port=5433 user=postgres dbname=fleet_street_coursework_test')


def connection():
    c = psycopg.connect(DSN, autocommit=True)
    assert c.info.dbname.endswith('_test'), 'Tests must target a dedicated test database'
    c.execute(psycopg.sql.SQL('SET search_path TO {},pg_catalog').format(psycopg.sql.Identifier(os.environ.get('FLEET_TEST_SCHEMA','public'))))
    c.execute("SET statement_timeout='15s'; SET timezone='UTC'")
    return c


def key():
    return 'test-' + uuid.uuid4().hex


def one(c, sql, params=None):
    return c.execute(sql, params).fetchone()[0]


@pytest.fixture
def c():
    with connection() as conn:
        conn.execute('BEGIN')
        try:
            yield conn
            conn.execute('SET CONSTRAINTS ALL IMMEDIATE')
        finally:
            conn.execute('ROLLBACK')


def rejected(c, sql, params=None, state='23514'):
    c.execute('SAVEPOINT expected_failure')
    try:
        with pytest.raises(psycopg.Error) as exc:
            c.execute(sql, params)
            c.execute('SET CONSTRAINTS ALL IMMEDIATE')
        assert exc.value.sqlstate == state
    finally:
        c.execute('ROLLBACK TO SAVEPOINT expected_failure')


def batch(c, quantity=2):
    b = one(c, 'INSERT INTO production_batch(recipe_id,planned_quantity,unit_price,request_id) VALUES(1,%s,100,%s) RETURNING id', (quantity,key()))
    c.execute('INSERT INTO production_material_usage VALUES(%s,2,%s)', (b, Decimal('.5')*quantity))
    c.execute("INSERT INTO stock_movement(stock_item_id,production_batch_id,employee_id,movement_type,quantity,reason,request_id) VALUES(1,%s,2,'production_out',%s,'test',%s),(2,%s,2,'production_out',%s,'test',%s)",
              (b,Decimal('.5')*quantity,key(),b,Decimal('.2')*quantity,key()))
    c.execute("UPDATE production_batch SET status='ready',actual_quantity=%s,finish_time=clock_timestamp() WHERE id=%s",(quantity,b))
    return b


def sale(c, b, quantity=1, request=None):
    sid = one(c,'INSERT INTO sales_transaction(employee_id,request_id) VALUES(3,%s) RETURNING id',(request or key(),))
    item = one(c,'INSERT INTO sale_item(sales_transaction_id,production_batch_id,line_number,quantity,unit_price) SELECT %s,id,1,%s,unit_price FROM production_batch WHERE id=%s RETURNING id',(sid,quantity,b))
    return sid,item


def test_schema_and_demo(c):
    names = [r[0] for r in c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=current_schema() AND table_type='BASE TABLE'")]
    assert len(names) == 22
    for name in names:
        assert one(c,psycopg.sql.SQL('SELECT count(*) FROM {}').format(psycopg.sql.Identifier(name))) > 0
    assert one(c,"SELECT count(*) FROM pg_constraint WHERE contype='f' AND connamespace=current_schema()::regnamespace") == 34
    assert one(c,"SELECT count(*) FROM information_schema.columns WHERE table_schema=current_schema() AND data_type IN ('json','jsonb','uuid')") == 0


def test_demo_many_to_many(c):
    assert one(c,'SELECT count(*) FROM production_material_usage WHERE production_batch_id=1') == 2
    assert one(c,'SELECT count(*) FROM production_material_usage WHERE raw_material_lot_id=2') == 2
    assert one(c,'SELECT count(DISTINCT production_batch_id) FROM sale_item WHERE sales_transaction_id=1') == 2


def test_single_employee_role_and_status(c):
    assert c.execute('SELECT role_code,status FROM employee ORDER BY id').fetchall() == [
        ('master','active'),('manager','active'),('staff','active')]
    assert one(c,"SELECT count(*) FROM information_schema.columns WHERE table_schema=current_schema() AND table_name='employee' AND column_name IN ('is_master','is_manager','is_staff','is_active')") == 0
    c.execute("UPDATE employee SET status='suspended' WHERE id=3")
    rejected(c,"INSERT INTO task(created_by,assigned_to,description,location,deadline) VALUES(2,3,'test','test',current_timestamp+interval '1 day')")


def draft_recipe(c):
    r=one(c,"INSERT INTO recipe(recipe_code,name,version,yield_quantity,quality_category) VALUES('PIE','New version',2,10,'A') RETURNING id")
    c.execute('INSERT INTO recipe_ingredient VALUES(%s,1,0.5)',(r,))
    return r


def test_recipe_publication_and_archive(c):
    r=draft_recipe(c)
    assert one(c,'SELECT status FROM recipe WHERE id=%s',(r,)) == 'draft'
    c.execute("UPDATE recipe SET status='archived' WHERE id=1")
    c.execute("UPDATE recipe SET status='current' WHERE id=%s",(r,))
    assert one(c,'SELECT recipe_id FROM production_batch WHERE id=1') == 1
    rejected(c,"UPDATE recipe SET status='current' WHERE id=1")
    rejected(c,"UPDATE recipe SET name='Rewrite history' WHERE id=1")


def test_one_current_recipe_per_code(c):
    r=draft_recipe(c)
    rejected(c,"UPDATE recipe SET status='current' WHERE id=%s",(r,),state='23505')


def test_cannot_start_production_from_draft(c):
    r=draft_recipe(c)
    rejected(c,'INSERT INTO production_batch(recipe_id,planned_quantity,unit_price,request_id) VALUES(%s,1,100,%s)',(r,key()))


def test_demo_money_and_balances(c):
    assert one(c,'SELECT total_price FROM v_sale_totals WHERE id=1') == Decimal('560')
    assert one(c,'SELECT quantity_balance FROM v_batch_balance WHERE id=1') == 9
    assert one(c,'SELECT sum(subtotal) FROM sale_item')-one(c,'SELECT sum(refund_amount) FROM sales_return')+one(c,'SELECT sum(total_amount) FROM asset_sale') == Decimal('710')


@pytest.mark.parametrize('sql,params,state',[
    ("INSERT INTO client(name,segment) VALUES('x',NULL)",None,'23502'),
    ("INSERT INTO sale_item(sales_transaction_id,production_batch_id,line_number,quantity,unit_price) VALUES(999,1,1,1,100)",None,'23503'),
    ("INSERT INTO employee(login,password_hash,name,role_code) VALUES('staff','!DEMO_ACCOUNT_DISABLED!','x','staff')",None,'23505'),
    ("INSERT INTO employee(login,password_hash,name) VALUES('no-role','!DEMO_ACCOUNT_DISABLED!','x')",None,'23502'),
    ("INSERT INTO employee(login,password_hash,name,role_code) VALUES('bad-role','!DEMO_ACCOUNT_DISABLED!','x','administrator')",None,'23514'),
    ("UPDATE employee SET role_code='manager' WHERE id=1",None,'23514'),
    ("UPDATE employee SET status='unknown' WHERE id=3",None,'23514'),
    ("INSERT INTO stock_item(name,unit,current_quantity) VALUES('wrong','kg',1)",None,'23514'),
    ("UPDATE stock_item SET current_quantity=1000 WHERE id=2",None,'23514'),
    ("UPDATE raw_material_lot SET remaining_kg=1 WHERE id=1",None,'23514'),
    ("UPDATE recipe_ingredient SET quantity_per_unit=1 WHERE recipe_id=1",None,'23514'),
    ("UPDATE recipe SET quality_category='B' WHERE id=1",None,'23514'),
    ("UPDATE employee SET status='suspended' WHERE id=1",None,'23514'),
    ("UPDATE production_batch SET actual_quantity=100 WHERE id=1",None,'23514'),
    ("UPDATE production_batch SET status='producing',actual_quantity=NULL,finish_time=NULL WHERE id=1",None,'23514'),
    ("UPDATE solid_waste SET disposal_time=clock_timestamp() WHERE id=1",None,'23514'),
    ("DELETE FROM side_asset WHERE id=1",None,'23514'),
    ("UPDATE task SET status='assigned',completed_at=NULL,confirmed_at=NULL,confirmed_by=NULL WHERE id=1",None,'23514'),
    ("DELETE FROM task WHERE id=1",None,'23514'),
    ("UPDATE visit SET outcome='completed' WHERE id=1",None,'23514'),
    ("UPDATE recipe SET status='draft' WHERE id=1",None,'23514'),
    ("UPDATE recipe SET status='unknown' WHERE id=1",None,'23514'),
])
def test_invalid_changes(c,sql,params,state):
    rejected(c,sql,params,state)


@pytest.mark.parametrize('table',['stock_movement','sales_transaction','sale_item','sales_return','production_material_usage','asset_sale','audit_log'])
def test_immutable_history(c,table):
    rejected(c,psycopg.sql.SQL('DELETE FROM {}').format(psycopg.sql.Identifier(table)))


def test_audit_not_truncated(c):
    rejected(c,'TRUNCATE audit_log')


def test_audit_contains_context_without_hash(c):
    c.execute("SET LOCAL fleet.employee_id='2'")
    cid=one(c,"INSERT INTO client(name,segment) VALUES('Audit example','обычный') RETURNING id")
    event=c.execute("SELECT employee_id,action_type,target_entity,target_id,details FROM audit_log WHERE target_entity='client' AND target_id=%s ORDER BY id DESC LIMIT 1",(cid,)).fetchone()
    assert event[:4] == (2,'INSERT','client',cid)
    assert one(c,"SELECT count(*) FROM audit_log WHERE details LIKE '%%DEMO_ACCOUNT_DISABLED%%'") == 0


@pytest.mark.parametrize('quantity',[0,-1,1000])
def test_sale_quantity(c,quantity):
    c.execute('SAVEPOINT bad_sale')
    sid=one(c,'INSERT INTO sales_transaction(employee_id,request_id) VALUES(3,%s) RETURNING id',(key(),))
    rejected(c,'INSERT INTO sale_item(sales_transaction_id,production_batch_id,line_number,quantity,unit_price) VALUES(%s,1,1,%s,100)',(sid,quantity))
    c.execute('ROLLBACK TO SAVEPOINT bad_sale')


def test_sale_uses_current_price(c):
    sid=one(c,'INSERT INTO sales_transaction(employee_id,request_id) VALUES(3,%s) RETURNING id',(key(),))
    rejected(c,'INSERT INTO sale_item(sales_transaction_id,production_batch_id,line_number,quantity,unit_price) VALUES(%s,1,1,1,99)',(sid,))
    c.execute('INSERT INTO sale_item(sales_transaction_id,production_batch_id,line_number,quantity,unit_price) VALUES(%s,1,1,1,100)',(sid,))
    c.execute('UPDATE production_batch SET unit_price=130 WHERE id=1')
    assert one(c,'SELECT unit_price FROM sale_item WHERE sales_transaction_id=%s',(sid,)) == Decimal(100)


@pytest.mark.parametrize('q,amount,restock',[(2,200,0),(1,101,0),(1,100,2)])
def test_return_limits(c,q,amount,restock):
    rejected(c,"INSERT INTO sales_return(sale_item_id,employee_id,quantity,refund_amount,restock_quantity,reason,request_id) VALUES(1,2,%s,%s,%s,'test',%s)",(q,amount,restock,key()))


def test_recall_and_return(c):
    b=batch(c)
    sid,item=sale(c,b)
    c.execute("UPDATE production_batch SET status='recalled',recall_reason='test' WHERE id=%s",(b,))
    assert one(c,'SELECT quantity_balance FROM v_batch_balance WHERE id=%s',(b,)) == 0
    rejected(c,"INSERT INTO sales_return(sale_item_id,employee_id,quantity,refund_amount,restock_quantity,reason,request_id) VALUES(%s,2,1,100,1,'test',%s)",(item,key()))
    c.execute("INSERT INTO sales_return(sale_item_id,employee_id,quantity,refund_amount,restock_quantity,reason,request_id) VALUES(%s,2,1,100,0,'test',%s)",(item,key()))
    sid2=one(c,'INSERT INTO sales_transaction(employee_id,request_id) VALUES(3,%s) RETURNING id',(key(),))
    rejected(c,'INSERT INTO sale_item(sales_transaction_id,production_batch_id,line_number,quantity,unit_price) VALUES(%s,%s,1,1,100)',(sid2,b))
    # Empty failed header is not retained when the encompassing operation is rolled back.
    c.execute('ROLLBACK')
    c.execute('BEGIN')


@pytest.mark.parametrize('sql',[
    "INSERT INTO recipe(recipe_code,name,version,yield_quantity,quality_category) VALUES('EMPTY','Empty',1,1,'A')",
    "INSERT INTO sales_transaction(employee_id,request_id) VALUES(3,'empty-sale')",
    "INSERT INTO asset_sale(buyer_id,employee_id,total_amount,request_id) VALUES(1,1,1,'empty-assets')",
])
def test_deferred_nonempty(c,sql):
    rejected(c,sql)


def test_duplicate_request(c):
    rejected(c,"INSERT INTO sales_transaction(employee_id,request_id) VALUES(3,'sale-demo-1')",state='23505')


def test_waste_single_source(c):
    for sources in ['NULL,NULL','1,1']:
        rejected(c,"INSERT INTO solid_waste(raw_material_lot_id,production_batch_id,waste_type,quantity,unit,disposal_method) VALUES("+sources+",'x',1,'kg','transport')")


def test_confirmed_disposal(c):
    before=one(c,'SELECT disposal_time FROM solid_waste WHERE id=1')
    c.execute('UPDATE task SET status=status WHERE id=1')
    assert one(c,'SELECT disposal_time FROM solid_waste WHERE id=1') == before
    assert one(c,'SELECT count(*) FROM v_disposal_log') == 1


def test_complaint_batch_matches_sale(c):
    b=batch(c)
    rejected(c,"INSERT INTO complaint(sales_transaction_id,production_batch_id,employee_id,description) VALUES(1,%s,2,'test')",(b,))


def test_stock_shortage_is_atomic(c):
    before=c.execute('SELECT id,current_quantity FROM stock_item ORDER BY id').fetchall()
    rejected(c,"INSERT INTO stock_movement(stock_item_id,employee_id,movement_type,quantity,reason,request_id) VALUES(2,2,'spoilage',10000,'test',%s)",(key(),))
    assert c.execute('SELECT id,current_quantity FROM stock_item ORDER BY id').fetchall() == before


def test_wrong_production_usage_rolls_back(c):
    before=c.execute('SELECT id,current_quantity FROM stock_item ORDER BY id').fetchall()
    c.execute('SAVEPOINT bad_batch')
    b=one(c,'INSERT INTO production_batch(recipe_id,planned_quantity,unit_price,request_id) VALUES(1,1,100,%s) RETURNING id',(key(),))
    c.execute('INSERT INTO production_material_usage VALUES(%s,2,0.5)',(b,))
    with pytest.raises(psycopg.errors.CheckViolation):
        c.execute('SET CONSTRAINTS ALL IMMEDIATE')
    c.execute('ROLLBACK TO SAVEPOINT bad_batch')
    assert c.execute('SELECT id,current_quantity FROM stock_item ORDER BY id').fetchall() == before


def test_receipt_requires_delivery(c):
    rejected(c,"UPDATE chute_log SET status='blocked',arrival_time=NULL WHERE id=1")


def test_sent_visit_requires_chute(c):
    rejected(c,"INSERT INTO visit(client_id,employee_id,service_type_id,end_time,outcome,request_id) VALUES(1,1,1,current_timestamp,'sent_to_chute',%s)",(key(),))


@pytest.mark.parametrize('quantity,state',[('NaN','23514'),('Infinity','22003'),('-Infinity','22003')])
def test_nonfinite_stock_quantity(c,quantity,state):
    rejected(c,"INSERT INTO stock_movement(stock_item_id,employee_id,movement_type,quantity,reason,request_id) VALUES(2,2,'receipt',%s,'test',%s)",(quantity,key()),state)


def test_final_ledger_reconciliation(c):
    assert one(c,"SELECT count(*) FROM stock_item s WHERE current_quantity<>(SELECT coalesce(sum(CASE WHEN movement_type IN ('receipt','correction_in') THEN quantity ELSE -quantity END),0) FROM stock_movement WHERE stock_item_id=s.id)") == 0
    assert one(c,'SELECT count(*) FROM stock_item s WHERE EXISTS(SELECT 1 FROM raw_material_lot WHERE stock_item_id=s.id) AND current_quantity<>(SELECT coalesce(sum(remaining_kg),0) FROM raw_material_lot WHERE stock_item_id=s.id)') == 0
    assert one(c,'SELECT count(*) FROM v_batch_balance WHERE quantity_balance<0') == 0


def race(first,second,expected,repeatable=False):
    with connection() as a,connection() as b,connection() as monitor:
        a.execute('BEGIN')
        b.execute('BEGIN ISOLATION LEVEL REPEATABLE READ' if repeatable else 'BEGIN')
        if repeatable:
            b.execute('SELECT count(*) FROM sale_item').fetchone()
        first(a)
        pid=b.info.backend_pid
        outcome={}
        def worker():
            try:
                second(b)
                b.execute('COMMIT')
                outcome['state']='success'
            except psycopg.Error as exc:
                outcome['state']=exc.sqlstate
                b.execute('ROLLBACK')
        thread=threading.Thread(target=worker,daemon=True)
        thread.start()
        deadline=time.monotonic()+5
        blocked=False
        while time.monotonic()<deadline and thread.is_alive():
            blocked=one(monitor,"SELECT coalesce(wait_event_type='Lock',false) FROM pg_stat_activity WHERE pid=%s",(pid,))
            if blocked:
                break
            time.sleep(.02)
        try:
            assert blocked, outcome
            a.execute('COMMIT')
            thread.join(12)
            assert not thread.is_alive()
            assert outcome['state']==expected
        finally:
            a.execute('ROLLBACK')


@pytest.mark.parametrize('repeatable',[False,True])
def test_concurrent_last_item(repeatable):
    with connection() as setup:
        with setup.transaction():
            b=batch(setup,1)
    race(lambda c:sale(c,b),lambda c:sale(c,b),'40001' if repeatable else '23514',repeatable)


def test_concurrent_returns():
    with connection() as setup:
        with setup.transaction():
            b=batch(setup,2)
            _,item=sale(setup,b,2)
    def ret(c,q):
        c.execute("INSERT INTO sales_return(sale_item_id,employee_id,quantity,refund_amount,restock_quantity,reason,request_id) VALUES(%s,2,%s,%s,0,'test',%s)",(item,q,q*100,key()))
    race(lambda c:ret(c,2),lambda c:ret(c,1),'23514')


def test_concurrent_recall_blocks_sale():
    with connection() as setup:
        with setup.transaction():
            b=batch(setup,2)
    race(lambda c:c.execute("UPDATE production_batch SET status='recalled',recall_reason='test' WHERE id=%s",(b,)),lambda c:sale(c,b),'23514')
