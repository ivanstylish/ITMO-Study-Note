import pytest
from test_database import c, key, rejected


@pytest.mark.parametrize('quantity,state', [
    (None, '23502'), (0, '23514'), (-1, '23514'),
    ('NaN', '23514'), ('Infinity', '22003'), ('-Infinity', '22003'),
])
def test_invalid_movement_rolls_back_all_effects(c, quantity, state):
    snapshot = lambda: (
        c.execute('SELECT id,current_quantity FROM stock_item ORDER BY id').fetchall(),
        c.execute('SELECT count(*) FROM stock_movement').fetchone(),
        c.execute('SELECT count(*) FROM audit_log').fetchone(),
    )
    before = snapshot()
    rejected(c, """INSERT INTO stock_movement(
        stock_item_id,employee_id,movement_type,quantity,reason,request_id)
        VALUES(2,2,'correction_in',%s,'test',%s)""", (quantity, key()), state)
    assert snapshot() == before


def test_wrong_lot_keeps_both_balances(c):
    snapshot = lambda: (
        c.execute('SELECT id,current_quantity FROM stock_item ORDER BY id').fetchall(),
        c.execute('SELECT id,remaining_kg FROM raw_material_lot ORDER BY id').fetchall(),
        c.execute('SELECT count(*) FROM stock_movement').fetchone(),
        c.execute('SELECT count(*) FROM audit_log').fetchone(),
    )
    before = snapshot()
    rejected(c, """INSERT INTO stock_movement(
        stock_item_id,raw_material_lot_id,employee_id,movement_type,
        quantity,reason,request_id)
        VALUES(2,2,2,'correction_in',1,'test',%s)""", (key(),))
    assert snapshot() == before
