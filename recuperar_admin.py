"""Recuperación del administrador por el operador que tiene acceso al disco local."""
import sqlite3, secrets, hashlib, time
from pathlib import Path
p=Path(__file__).resolve().parent/'data'/'local.db'
if not p.exists():raise SystemExit('No existe una base local. Inicie el cotizador primero.')
c=sqlite3.connect(p)
try:
 rows=c.execute("SELECT id,username FROM users WHERE role='admin' AND status='activo'").fetchall()
 for uid,name in rows:
  code=secrets.token_urlsafe(24);c.execute('UPDATE users SET reset=?,reset_exp=? WHERE id=?',(hashlib.sha256(code.encode()).hexdigest(),time.time()+1800,uid))
  print('Administrador:',name,'\nCódigo (30 minutos, un solo uso):',code)
 c.commit()
finally:c.close()
print('En la pantalla de acceso elija Olvidé mi contraseña. No comparta este código.')
