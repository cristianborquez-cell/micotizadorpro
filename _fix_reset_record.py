with open('local_server.py','rb') as f:
    data = f.read()

old = b"endswith('/reset'):\r\n      code=secrets.token_urlsafe(24); c.execute('UPDATE users SET reset=?,reset_exp=? WHERE id=?',(digest(code),time.time()+1800,target)); return self.respond({'code':code})"
new = b"endswith('/reset'):\r\n      code=secrets.token_urlsafe(24); c.execute('UPDATE users SET reset=?,reset_exp=? WHERE id=?',(digest(code),time.time()+1800,target)); record(c,u['id'],target,'reset',x.get('status','')); return self.respond({'code':code})"

count = data.count(old)
print('Occurrences found:', count)
if count == 1:
    data = data.replace(old, new)
    with open('local_server.py','wb') as f:
        f.write(data)
    print('Reemplazado correctamente')
else:
    print('No se pudo reemplazar (count != 1)')
