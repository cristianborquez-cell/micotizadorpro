COTIZADOR PRO HIBRIDO V3.1 - SERVIDOR ONLINE

OBJETIVO
Servidor centralizado para PC 32/64 bits, Mac, Linux, Android e iPhone mediante navegador.

INSTALACION LOCAL / SERVIDOR WINDOWS
1. Instala Docker Desktop en el equipo que actuara como servidor.
2. Copia .env.example a .env si no existe.
3. Edita .env y CAMBIA TODAS LAS CLAVES.
4. Ejecuta INICIAR_WINDOWS.bat.
5. Abre http://localhost
6. Primer usuario: el valor de ADMIN_USER (por defecto admin), con ADMIN_PASSWORD.

RED LOCAL
Desde otro PC usa la IP del servidor: http://IP-DEL-SERVIDOR

INTERNET
1. Usa un servidor con IP pública o una VPS.
2. Apunta un dominio al servidor.
3. En .env define DOMAIN=tu-dominio.cl
4. Abre solo 80/443 en firewall; NO publiques PostgreSQL.
5. Caddy obtiene/renueva HTTPS automáticamente cuando el dominio resuelve al servidor.

SEGURIDAD
- PostgreSQL no se publica al exterior.
- JWT con secreto externo.
- Contraseñas con bcrypt.
- Roles admin/vendedor/cliente.
- Cabeceras de seguridad.
- Auditoría de accesos y operaciones.
- Healthcheck de PostgreSQL.
- Backup SQL incluido.

FUNCIONES
- Login
- Usuarios y roles
- Cotizaciones centralizadas
- Historial
- Dashboard administrativo
- PDF del cotizador existente
- Sincronización al servidor
- WebSocket preparado
- PostgreSQL
- HTTPS mediante Caddy

NOTA
Para producción real se recomienda una VPS Linux x64. Los clientes pueden ser Windows 32/64, móviles y tablets porque acceden por navegador.
