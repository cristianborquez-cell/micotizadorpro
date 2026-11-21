import sqlite3
from pathlib import Path

p = Path('data/local.db')
if not p.exists():
    print('No existe data/local.db')
    raise SystemExit(1)

c = sqlite3.connect(p)
c.row_factory = sqlite3.Row
rows = c.execute('SELECT id, username, email, role, status FROM users ORDER BY id').fetchall()
print(f'Usuarios encontrados: {len(rows)}')
for r in rows:
    print(f"  id={r['id']} | usuario='{r['username']}' | email='{r['email']}' | rol={r['role']} | estado={r['status']}")
c.close()
