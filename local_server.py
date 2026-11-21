from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import os, sqlite3, json, secrets, hashlib, hmac, time, uuid, platform, threading
ROOT=Path(__file__).resolve().parent  # updated v15
DATA=Path(os.environ.get('COTIZADOR_DATA',str(ROOT/'data'))); DATA.mkdir(exist_ok=True)
DB=DATA/'local.db'
DEVICE=hashlib.sha256((platform.node()+str(uuid.getnode())).encode()).hexdigest()
LOCK=threading.RLock()
SESSIONS={}; ATTEMPTS={}
class Connection(sqlite3.Connection):
 def __exit__(self,*args):
  try: return super().__exit__(*args)
  finally: self.close()
def connect():
 c=sqlite3.connect(DB,factory=Connection); c.row_factory=sqlite3.Row; return c
def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def password(s):
 salt=secrets.token_hex(16); return salt+':'+hashlib.pbkdf2_hmac('sha256',s.encode(),salt.encode(),300000).hex()
def verify(s,p):
 salt,p=p.split(':'); return hmac.compare_digest(p,hashlib.pbkdf2_hmac('sha256',s.encode(),salt.encode(),300000).hex())
with connect() as c:
 c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE COLLATE NOCASE,email TEXT UNIQUE COLLATE NOCASE,name TEXT,password TEXT,role TEXT,status TEXT DEFAULT 'activo',reset TEXT,reset_exp REAL);
 CREATE TABLE IF NOT EXISTS licenses(pin TEXT PRIMARY KEY,user_id INTEGER,device TEXT,revoked INTEGER DEFAULT 0);
 CREATE TABLE IF NOT EXISTS quotes(user_id INTEGER,id TEXT,payload TEXT,PRIMARY KEY(user_id,id));''')
 # MigraciÃ³n aditiva: conservar cuentas, cotizaciones y licencias ya activadas.
 columns={r[1] for r in c.execute('PRAGMA table_info(licenses)')}
 for name,kind in [('license_id','TEXT'),('created_at','REAL DEFAULT 0'),('expires_at','REAL DEFAULT 0'),('used_at','REAL'),('is_invite','INTEGER DEFAULT 0')]:
  if name not in columns:c.execute('ALTER TABLE licenses ADD COLUMN '+name+' '+kind)
 c.execute("UPDATE licenses SET license_id=lower(hex(randomblob(12))) WHERE license_id IS NULL")
 c.execute('UPDATE licenses SET is_invite=1 WHERE user_id IS NULL AND device IS NULL')
 c.execute('CREATE UNIQUE INDEX IF NOT EXISTS license_identity ON licenses(license_id)')
 c.execute('CREATE TABLE IF NOT EXISTS admin_events(id INTEGER PRIMARY KEY,at REAL,actor_id INTEGER,user_id INTEGER,action TEXT,detail TEXT)')

def record(c,actor,target,action,detail=''):
 c.execute('INSERT INTO admin_events(at,actor_id,user_id,action,detail) VALUES(?,?,?,?,?)',(time.time(),actor,target,action,detail))

class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a): pass
 def respond(self,obj,status=200):
  b=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(b)
 def do_GET(self):
  if self.path.startswith('/api/'): return self.api()
  ua=self.headers.get('User-Agent','').lower()
  is_android='android' in ua
  if self.path=='/' and is_android: name='android_login.html'
  elif self.path=='/admin' and is_android: return self.respond({'detail':'Esta version no permite acceso de administrador'},403)
  else:
   files={'/':'login.html','/app':'cotizador.html','/admin':'admin.html','/license':'license.html','/assets/server_bridge.js':'server_bridge.js','/assets/jspdf.umd.min.js':'jspdf.umd.min.js','/assets/html2canvas.min.js':'html2canvas.min.js','/manifest.json':'manifest.json','/sw.js':'sw.js'}
   name=files.get(self.path.split('?',1)[0])
  if not name or not (ROOT/'frontend'/name).exists(): return self.respond({'detail':'No encontrado'},404)
  b=(ROOT/'frontend'/name).read_bytes(); self.send_response(200); self.send_header('Cache-Control','no-store')
  ct='application/javascript' if name.endswith('.js') else ('application/json' if name.endswith('.json') else 'text/html; charset=utf-8')
  self.send_header('Content-Type',ct); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
 def do_POST(self):
  origin=self.headers.get('Origin','')
  host=self.headers.get('Host','')
  allowed=['http://'+host,'https://'+host]
  if origin and origin not in allowed: return self.respond({'detail':'Origen invalido'},403)
  self.api()
 def api(self):
  try:
   with LOCK, connect() as c:
    n=int(self.headers.get('Content-Length',0))
    if n>5000000: raise ValueError('Solicitud demasiado grande')
    x=json.loads(self.rfile.read(n)) if n else {}; p=self.path
    def fail(msg): raise ValueError(msg)
    def strong(pw):
     if len(pw)<10: fail('La contraseÃ±a necesita al menos 10 caracteres')
    if p=='/api/setup': return self.respond({'needed':c.execute('SELECT count(*) FROM users').fetchone()[0]==0})
    if p in ['/api/auth/setup','/api/auth/register']:
     first=c.execute('SELECT count(*) FROM users').fetchone()[0]==0
     if p.endswith('setup') and not first: fail('Ya existe un administrador')
     if p.endswith('register') and first: fail('Configure primero el administrador')
     user=x.get('username','').strip(); email=x.get('email','').strip().lower() or None
     def valid_email(value):
      return len(value)<=254 and value.count('@')==1 and bool(value.split('@')[0]) and '.' in value.split('@')[-1] and not any(ch.isspace() for ch in value)
     if '@' in user:
      user=user.lower()
      if not valid_email(user): fail('Ingrese un correo vÃ¡lido en Usuario o correo')
      if not email: email=user
     if len(user)<3 or len(user)>254 or any(ch.isspace() for ch in user): fail('El usuario debe tener al menos 3 caracteres y no contener espacios')
     if email and not valid_email(email): fail('Revise el formato del correo opcional')
     if c.execute('SELECT 1 FROM users WHERE username IN (?,?) OR email IN (?,?)',(user,email,user,email)).fetchone(): fail('Este usuario o correo ya estÃ¡ registrado')
     strong(x.get('password',''))
     invite=None
     if not first:
      raw_pin=x.get('pin','').strip().upper()
      invite=c.execute('SELECT * FROM licenses WHERE pin=? AND user_id IS NULL AND device IS NULL AND revoked=0',(digest(raw_pin),)).fetchone()
      if not invite: fail('PIN de registro invÃ¡lido o ya utilizado. Solicita uno al administrador')
      if (invite['expires_at'] or 0)<=time.time(): fail('PIN de registro vencido. Solicita uno nuevo al administrador')
     c.execute('INSERT INTO users(username,email,name,password,role) VALUES(?,?,?,?,?)',(user,email,x.get('name',''),password(x['password']),'admin' if first else 'vendedor'))
     new_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
     if invite:
      c.execute('UPDATE licenses SET user_id=?,device=?,used_at=? WHERE license_id=? AND user_id IS NULL AND device IS NULL AND revoked=0',(new_id,DEVICE,time.time(),invite['license_id']))
      if c.execute('SELECT changes()').fetchone()[0]!=1: fail('El PIN ya fue utilizado. Solicita otro al administrador')
      record(c,None,new_id,'registro_con_PIN',invite['license_id'])
     return self.respond({'ok':True,'licensed':bool(invite)})
    if p=='/api/auth/reset':
     u=c.execute('SELECT * FROM users WHERE username=? OR email=?',(x.get('username',''),x.get('email',''))).fetchone()
     if not u or not u['reset'] or u['reset_exp']<time.time() or not hmac.compare_digest(u['reset'],digest(x.get('code',''))): fail('CÃ³digo invÃ¡lido o vencido')
     strong(x.get('password','')); c.execute('UPDATE users SET password=?,reset=NULL WHERE id=?',(password(x['password']),u['id']))
     for k in list(SESSIONS):
      if SESSIONS[k][0]==u['id']: del SESSIONS[k]
     return self.respond({'ok':True})
    if p=='/api/auth/login':
     key=x.get('username','').lower(); a=ATTEMPTS.get(key,[]); a=[t for t in a if t>time.time()-600]
     if len(a)>=8: fail('Demasiados intentos. Espere 10 minutos')
     ATTEMPTS[key]=a+[time.time()]
     u=c.execute('SELECT * FROM users WHERE username=? OR email=?',(key,key)).fetchone()
     if not u or not verify(x.get('password',''),u['password']) or u['status']!='activo': fail('Credenciales incorrectas o cuenta restringida')
     ATTEMPTS.pop(key,None); token=secrets.token_urlsafe(40); SESSIONS[token]=(u['id'],time.time()+43200)
     return self.respond({'access_token':token,'user':{'id':u['id'],'username':u['username'],'role':u['role']}})
    token=self.headers.get('Authorization','').removeprefix('Bearer '); session=SESSIONS.get(token)
    u=c.execute('SELECT * FROM users WHERE id=?',(session[0],)).fetchone() if session and session[1]>time.time() else None
    if not u or u['status']!='activo': return self.respond({'detail':'SesiÃ³n invÃ¡lida o cuenta restringida'},401)
    if p=='/api/auth/logout': SESSIONS.pop(token,None); return self.respond({'ok':True})
    if p=='/api/me': return self.respond({'id':u['id'],'username':u['username'],'role':u['role']})
    if p.startswith('/api/admin/'):
     if u['role']!='admin': return self.respond({'detail':'Acceso de administrador requerido'},403)
     if p=='/api/admin/invitations':
      if self.command=='POST':
       pin=secrets.token_hex(8).upper();lid=secrets.token_hex(12);now=time.time()
       c.execute('INSERT INTO licenses(pin,user_id,license_id,created_at,expires_at,is_invite) VALUES(?,NULL,?,?,?,1)',(digest(pin),lid,now,now+300))
       record(c,u['id'],None,'emitir_PIN_registro',lid)
       return self.respond({'pin':pin,'license_id':lid,'expires_at':now+300,'server_time':now})
      rows=[]
      for r in c.execute('SELECT license_id,created_at,expires_at,used_at,revoked FROM licenses WHERE is_invite=1 ORDER BY created_at DESC'):
       item=dict(r);item['state']='cesada' if r['revoked'] else 'usado' if r['used_at'] else 'caducado' if (r['expires_at'] or 0)<=time.time() else 'pendiente';rows.append(item)
      return self.respond({'invitations':rows,'server_time':time.time()})
     if p=='/api/admin/invitations/delete':
      r=c.execute('SELECT * FROM licenses WHERE license_id=? AND is_invite=1',(x['license_id'],)).fetchone()
      if not r:fail('PIN de registro no encontrado')
      if r['used_at'] or r['device']:fail('Este PIN ya se usÃ³ y no se puede eliminar como PIN pendiente')
      c.execute('DELETE FROM licenses WHERE license_id=?',(x['license_id'],));record(c,u['id'],None,'eliminar_PIN_registro',x['license_id']);return self.respond({'ok':True})
     if p=='/api/admin/users': return self.respond([dict(r) for r in c.execute('SELECT id,username,email,name,role,status,(SELECT count(*) FROM quotes WHERE user_id=users.id) AS quote_count FROM users')])
     if p=='/api/admin/licenses':
      rows=[]
      for r in c.execute('SELECT l.license_id,l.user_id,u.username,l.device,l.revoked,l.created_at,l.expires_at,l.used_at FROM licenses l LEFT JOIN users u ON u.id=l.user_id ORDER BY l.created_at DESC'):
       item=dict(r);item['state']='cesada' if r['revoked'] else 'activada' if r['device'] else 'caducada' if (r['expires_at'] or 0)<=time.time() else 'pendiente';rows.append(item)
      return self.respond({'licenses':rows,'server_time':time.time()})
     if p=='/api/admin/events': return self.respond([dict(r) for r in c.execute('SELECT e.*,u.username AS actor FROM admin_events e LEFT JOIN users u ON u.id=e.actor_id ORDER BY e.id DESC LIMIT 200')])
     target=int(x['id']); other=c.execute('SELECT id FROM users WHERE id=?',(target,)).fetchone()
     if not other: fail('Usuario no encontrado')
     if target==u['id']: fail('No puede restringir su propia cuenta')
     if p=='/api/admin/licenses/delete':
      r=c.execute('SELECT * FROM licenses WHERE license_id=? AND user_id=?',(x['license_id'],target)).fetchone()
      if not r: fail('PIN no encontrado')
      if r['device']: fail('La licencia ya fue activada. Use Cesar licencia para detener su uso')
      c.execute('DELETE FROM licenses WHERE license_id=?',(x['license_id'],));record(c,u['id'],target,'eliminar_pin',x['license_id']);return self.respond({'ok':True})
     if p=='/api/admin/licenses/cease':
      r=c.execute('SELECT * FROM licenses WHERE license_id=? AND user_id=?',(x['license_id'],target)).fetchone()
      if not r: fail('Licencia no encontrada')
      c.execute('UPDATE licenses SET revoked=1 WHERE license_id=?',(x['license_id'],));record(c,u['id'],target,'cesar_licencia',x['license_id']);return self.respond({'ok':True})
     if p.endswith('/status'):

      if x['status'] not in ['activo','bloqueado','suspendido']: fail('Estado invÃ¡lido')
      c.execute('UPDATE users SET status=? WHERE id=?',(x['status'],target))
     elif p.endswith('/delete'):
      c.execute('DELETE FROM users WHERE id=?',(target,)); c.execute('DELETE FROM licenses WHERE user_id=?',(target,)); c.execute('DELETE FROM quotes WHERE user_id=?',(target,))
     elif p.endswith('/pin'):
      pin=secrets.token_hex(8).upper();lid=secrets.token_hex(12);now=time.time()
      c.execute('UPDATE licenses SET revoked=1 WHERE user_id=?',(target,))
      c.execute('INSERT INTO licenses(pin,user_id,license_id,created_at,expires_at) VALUES(?,?,?,?,?)',(digest(pin),target,lid,now,now+300))
      record(c,u['id'],target,'emitir_pin',lid)
      return self.respond({'pin':pin,'license_id':lid,'expires_at':now+300,'server_time':now})
     elif p.endswith('/revoke'): c.execute('UPDATE licenses SET revoked=1 WHERE user_id=?',(target,))
     elif p.endswith('/reset'):
      code=secrets.token_urlsafe(24); c.execute('UPDATE users SET reset=?,reset_exp=? WHERE id=?',(digest(code),time.time()+1800,target)); record(c,u['id'],target,'reset',x.get('status','')); return self.respond({'code':code})
     else: fail('AcciÃ³n desconocida')
     record(c,u['id'],target,p.rsplit('/',1)[-1],x.get('status',''))
     for k in list(SESSIONS):
      if SESSIONS[k][0]==target: del SESSIONS[k]
     return self.respond({'ok':True})
    if p=='/api/license/status':
     active=u['role']=='admin' or bool(c.execute('SELECT 1 FROM licenses WHERE user_id=? AND device=? AND revoked=0',(u['id'],DEVICE)).fetchone())
     return self.respond({'active':active,'username':u['username']})
    if p=='/api/license/activate':
     r=c.execute('SELECT * FROM licenses WHERE pin=? AND user_id=? AND revoked=0',(digest(x.get('pin','')),u['id'])).fetchone()
     if not r: fail('PIN invÃ¡lido, eliminado o cesado')
     if r['device']: fail('Este PIN ya fue utilizado. Cada PIN se activa una sola vez')
     if (r['expires_at'] or 0)<=time.time(): fail('El PIN caducÃ³. Solicite uno nuevo al administrador')
     c.execute('UPDATE licenses SET device=?,used_at=? WHERE pin=?',(DEVICE,time.time(),r['pin']))
     record(c,u['id'],u['id'],'activar_licencia',r['license_id'])
     return self.respond({'ok':True})
    licensed=u['role']=='admin' or c.execute('SELECT 1 FROM licenses WHERE user_id=? AND device=? AND revoked=0',(u['id'],DEVICE)).fetchone()
    if not licensed: return self.respond({'detail':'Active el PIN de licencia para este equipo'},403)
    if p=='/api/local/history':
     if self.command=='POST':
      for q in x['quotes']:
       c.execute('INSERT INTO quotes VALUES(?,?,?) ON CONFLICT(user_id,id) DO UPDATE SET payload=excluded.payload',(u['id'],str(q['id']),json.dumps(q,ensure_ascii=False)))
      return self.respond({'ok':True})
     return self.respond([json.loads(r[0]) for r in c.execute('SELECT payload FROM quotes WHERE user_id=?',(u['id'],))])
    if p=='/api/local/delete': c.execute('DELETE FROM quotes WHERE user_id=? AND id=?',(u['id'],str(x['id']))); return self.respond({'ok':True})
    return self.respond({'detail':'Ruta desconocida'},404)
  except (ValueError,KeyError,sqlite3.IntegrityError) as e: self.respond({'detail':'Datos invÃ¡lidos o usuario/correo duplicado' if isinstance(e,sqlite3.IntegrityError) else str(e)},400)
if __name__=='__main__':
  import sys, socket
  # Render asigna PORT; local usa COTIZADOR_PORT
  port_env=os.environ.get('PORT') or os.environ.get('COTIZADOR_PORT','8765')
  requested=int(port_env)
  # En hosting (Render) escuchar en 0.0.0.0; en local solo 127.0.0.1
  host='0.0.0.0' if os.environ.get('PORT') else '127.0.0.1'
  server=None
  for port in range(requested,requested+20):
   try:
    server=ThreadingHTTPServer((host,port),Handler);break
   except OSError:continue
  if server is None:raise SystemExit('ERROR: No hay puertos disponibles entre '+str(requested)+' y '+str(requested+19))
  url='http://'+host+':'+str(server.server_port)
  print('Cotizador Pro Hibrido iniciado en '+url+' â Ctrl+C para detener',flush=True)
  if '--open' in sys.argv and host=='127.0.0.1':
   import webbrowser
   threading.Timer(1,lambda:webbrowser.open(url)).start()
  server.serve_forever()

# Updated: 2026-11-21T23:39:28.765Z
