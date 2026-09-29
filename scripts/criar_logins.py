import sqlite3
from werkzeug.security import generate_password_hash
c=sqlite3.connect("banco.db")
rows=c.execute("SELECT id,name FROM clients ORDER BY id").fetchall()
for i,name in rows:
    username=name.split()[0].lower()+str(i).zfill(2)
    senha="Master@"+str(i).zfill(2)
    c.execute("INSERT INTO users(username,password_hash,account_id) VALUES(?,?,?)",(username,generate_password_hash(senha),i))
c.commit()
c.close()
print("50 logins OK")
