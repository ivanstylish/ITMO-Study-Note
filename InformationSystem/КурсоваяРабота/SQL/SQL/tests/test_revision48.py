from test_database import c, connection, key, one, race, rejected


def test_sale_replay_precedes_array_validation(c):
    request = key()
    sale_id = one(c, 'SELECT register_sale(3,ARRAY[1],ARRAY[1],%s)', (request,))
    assert one(c, 'SELECT register_sale(3,NULL,NULL,%s)', (request,)) == sale_id


def test_sale_rejects_multidimensional_arrays(c):
    rejected(c, 'SELECT register_sale(3,ARRAY[[1,2]],ARRAY[[1,1]],%s)', (key(),), '22023')


def test_sale_checks_combined_quantity_from_one_batch(c):
    before = one(c, 'SELECT quantity_balance FROM v_batch_balance WHERE id=1')
    rejected(c, 'SELECT register_sale(3,ARRAY[1,1],ARRAY[%s,1],%s)', (before, key()), '23514')
    assert one(c, 'SELECT quantity_balance FROM v_batch_balance WHERE id=1') == before


def test_explicit_return_date_before_sale(c):
    rejected(c, """INSERT INTO sales_return(sale_item_id,employee_id,quantity,
                   refund_amount,reason,request_id,return_time)
                   VALUES(1,2,1,100,'test',%s,'2000-01-01 UTC')""", (key(),), '23514')


def test_concurrent_suspensions_keep_an_active_master():
    with connection() as setup:
        other = one(setup, """INSERT INTO employee(login,password_hash,name,role_code)
                              VALUES(%s,'!DEMO_ACCOUNT_DISABLED!','Test master','master') RETURNING id""", (key(),))
    # Commit one suspension while the second session waits for a master row lock.
    try:
        race(lambda c: c.execute("UPDATE employee SET status='suspended' WHERE id=%s", (other,)),
             lambda c: c.execute("UPDATE employee SET status='suspended' WHERE id=1"), '23514')
        with connection() as check:
            assert one(check, "SELECT count(*) FROM employee WHERE role_code='master' AND status='active'") == 1
    finally:
        with connection() as cleanup:
            cleanup.execute('DELETE FROM employee WHERE id=%s', (other,))
