import unittest, tempfile, importlib.util, pathlib, threading, urllib.request, urllib.error, json
spec=importlib.util.spec_from_file_location('local',pathlib.Path(__file__).with_name('local_server.py')); app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
class Flow(unittest.TestCase):
 def test_accounts_license_and_quotes(self):
  server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler); threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_port)
  def call(p,x=None,t=None):
   req=urllib.request.Request(base+p,data=json.dumps(x).encode() if x is not None else None,headers={'Content-Type':'application/json',**({'Authorization':'Bearer '+t} if t else {})})
   try:
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req) as r:return r.status,json.load(r)
   except urllib.error.HTTPError as e:return e.code,json.load(e)
  suffix=app.secrets.token_hex(4); admin='admin'+suffix+'@example.cl'; user='user'+suffix; pw='TestingPassword123!'
  try:
   self.assertEqual(call('/api/auth/setup',{'username':admin,'password':pw})[0],200)
   a=call('/api/auth/login',{'username':admin,'password':pw})[1]['access_token']
   self.assertEqual(call('/api/auth/setup',{'username':'attack','password':pw})[0],400)
   invite=call('/api/admin/invitations',{},a)[1]
   self.assertAlmostEqual(invite['expires_at']-invite['server_time'],300)
   with app.connect() as c:c.execute('UPDATE licenses SET expires_at=? WHERE license_id=?',(app.time.time()-1,invite['license_id']))
   self.assertEqual(call('/api/auth/register',{'username':'expired@example.cl','password':pw,'pin':invite['pin']})[0],400)
   self.assertEqual(call('/api/admin/invitations/delete',{'license_id':invite['license_id']},a)[0],200)
   invite=call('/api/admin/invitations',{},a)[1]
   self.assertEqual(call('/api/auth/register',{'username':user,'email':user+'@example.cl','password':pw,'pin':invite['pin']})[0],200)
   self.assertEqual(call('/api/auth/register',{'username':'replay@example.cl','password':pw,'pin':invite['pin']})[0],400)
   self.assertEqual(next(i['state'] for i in call('/api/admin/invitations',t=a)[1]['invitations'] if i['license_id']==invite['license_id']),'usado')
   self.assertEqual(call('/api/auth/register',{'username':user+'@example.cl','password':pw})[0],400)
   self.assertEqual(call('/api/auth/register',{'username':'correo-invalido@','password':pw})[0],400)
   t=call('/api/auth/login',{'username':user+'@example.cl','password':pw})[1]['access_token']
   self.assertEqual(call('/api/local/history',t=t)[0],200)
   self.assertEqual(call('/api/admin/users',t=t)[0],403)
   uid=next(u['id'] for u in call('/api/admin/users',t=a)[1] if u['username']==user)
   issued=call('/api/admin/pin',{'id':uid},a)[1]
   self.assertAlmostEqual(issued['expires_at']-issued['server_time'],300)
   with app.connect() as c:c.execute('UPDATE licenses SET expires_at=? WHERE license_id=?',(app.time.time()-1,issued['license_id']))
   self.assertEqual(call('/api/license/activate',{'pin':issued['pin']},t)[0],400)
   listing=call('/api/admin/licenses',t=a)[1]['licenses']
   self.assertEqual(next(l['state'] for l in listing if l['license_id']==issued['license_id']),'caducada')
   self.assertEqual(call('/api/admin/licenses/delete',{'id':uid,'license_id':issued['license_id']},t)[0],403)
   self.assertEqual(call('/api/admin/licenses/delete',{'id':uid,'license_id':issued['license_id']},a)[0],200)
   self.assertEqual(call('/api/license/activate',{'pin':issued['pin']},t)[0],400)
   pin=call('/api/admin/pin',{'id':uid},a)[1]['pin']
   self.assertEqual(call('/api/license/activate',{'pin':pin},t)[0],200)
   self.assertEqual(call('/api/license/activate',{'pin':pin},t)[0],400)
   with app.connect() as c:c.execute('UPDATE licenses SET expires_at=? WHERE pin=?',(app.time.time()-1,app.digest(pin)))
   self.assertTrue(call('/api/license/status',t=t)[1]['active'])
   lid=next(l['license_id'] for l in call('/api/admin/licenses',t=a)[1]['licenses'] if l['state']=='activada')
   self.assertEqual(call('/api/admin/licenses/delete',{'id':uid,'license_id':lid},a)[0],400)
   self.assertEqual(call('/api/admin/licenses/cease',{'id':uid,'license_id':lid},a)[0],200)
   self.assertFalse(call('/api/license/status',t=t)[1]['active'])
   pin=call('/api/admin/pin',{'id':uid},a)[1]['pin']
   self.assertEqual(call('/api/license/activate',{'pin':pin},t)[0],200)
   self.assertTrue(call('/api/admin/events',t=a)[1])
   old=app.DEVICE;app.DEVICE='another-machine';self.assertEqual(call('/api/license/activate',{'pin':pin},t)[0],400);app.DEVICE=old
   q={'id':123,'cliente':'Prueba','productos':[{'precio':1234}]}
   for _ in range(2):self.assertEqual(call('/api/local/history',{'quotes':[q]},t)[0],200)
   self.assertEqual(len(call('/api/local/history',t=t)[1]),1)
   code=call('/api/admin/reset',{'id':uid},a)[1]['code']
   self.assertEqual(call('/api/auth/reset',{'username':user,'code':code,'password':pw+'x'})[0],200)
   self.assertEqual(call('/api/local/history',t=t)[0],401)
   self.assertEqual(call('/api/auth/reset',{'username':user,'code':code,'password':pw})[0],400)
   call('/api/admin/status',{'id':uid,'status':'suspendido'},a)
   self.assertEqual(call('/api/auth/login',{'username':user,'password':pw+'x'})[0],400)
   call('/api/admin/delete',{'id':uid},a)
   self.assertFalse(any(u['id']==uid for u in call('/api/admin/users',t=a)[1]))
  finally:server.shutdown();server.server_close()
if __name__=='__main__':
 with tempfile.TemporaryDirectory(dir=app.ROOT) as d:
  app.DB=pathlib.Path(d)/'test.db'
  with app.connect() as c:
   original=app.sqlite3.connect(app.DATA/'local.db')
   for (sql,) in original.execute("SELECT sql FROM sqlite_master WHERE type IN ('table','index') AND sql IS NOT NULL"):c.execute(sql)
   original.close()
  unittest.main()




