"""Wrapper WSGI para ejecutar Cotizador Pro Híbrido en hosting (PythonAnywhere, Render, etc.)."""
import os, sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
os.chdir(str(APP_DIR))

# Forzar ruta de datos dentro del directorio de la app
os.environ.setdefault('COTIZADOR_DATA', str(APP_DIR / 'data'))
os.environ.setdefault('COTIZADOR_PORT', '8000')

from local_server import ThreadingHTTPServer, Handler

class WSGIApp:
    def __init__(self):
        # Crear una instancia del servidor para usar el Handler
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)

    def __call__(self, environ, start_response):
        # Construir una petición HTTP mínima para el Handler
        # Nota: Este es un adaptador simplificado. Para producción completa
        # se recomienda usar un servidor WSGI real (gunicorn/uwsgi) con
        # una adaptación adecuada de BaseHTTPRequestHandler.
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        query = environ.get('QUERY_STRING', '')
        full_path = path + ('?' + query if query else '')

        # Leer body
        try:
            length = int(environ.get('CONTENT_LENGTH', '0') or '0')
        except ValueError:
            length = 0
        body = environ['wsgi.input'].read(length) if length else b''

        # Crear una pseudo-petición
        class FakeHeaders:
            def __init__(self, env):
                self.env = env
            def get(self, key, default=None):
                for k, v in self.env.items():
                    if k == 'HTTP_' + key.upper().replace('-', '_'):
                        return v
                return default
            def __getitem__(self, key):
                return self.get(key)

        class FakeRFile:
            def __init__(self, b):
                self.b = b
            def read(self, n=None):
                return self.b if n is None else self.b[:n]

        class FakeWFile:
            def __init__(self):
                self.buf = bytearray()
            def write(self, data):
                self.buf.extend(data)
            def getvalue(self):
                return bytes(self.buf)

        class FakeRequest:
            def __init__(self, method, path, headers, body):
                self.command = method
                self.path = path
                self.headers = FakeHeaders(headers)
                self.rfile = FakeRFile(body)
                self.wfile = FakeWFile()

        req = FakeRequest(method, full_path, environ, body)

        try:
            # Usar el Handler para procesar
            handler = Handler(req, ('127.0.0.1', 0), self.server)
            status = '200 OK'
            headers = []
            for k, v in handler.headers.items():
                if k.lower() not in ('content-length',):
                    headers.append((k, v))
            start_response(status, headers)
            return [handler.wfile.getvalue()]
        except Exception as exc:
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [str(exc).encode()]

app = WSGIApp()

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    print('WSGI servidor en puerto 8000')
    httpd.serve_forever()
