from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:***@localhost:5432/taxip_db')

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT conname, pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE conrelid = 'fleet.chofer_vehiculo'::regclass
        AND contype = 'c'
    """))
    for row in result:
        print(row)