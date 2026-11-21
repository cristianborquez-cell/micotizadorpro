with open('local_server.py','rb') as f:
    data = f.read()
idx = data.find(b"endswith('/reset')")
print('Found at:', idx)
print(repr(data[idx:idx+220]))
