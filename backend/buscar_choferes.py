from sqlalchemy import create_engine, text

e = create_engine("postgresql://taxip:taxip154@localhost:5432/taxip_db")
c = e.connect()

r = c.execute(text(
    "SELECT u.id, u.email, t.nombre, u.activo "
    "FROM auth.usuario u "
    "JOIN auth.tipo_usuario t ON u.tipo_usuario_id = t.id "
    "WHERE t.nombre ILIKE '%chofer%' "
    "LIMIT 10"
))

for row in r:
    print(row)

c.close()
e.dispose()