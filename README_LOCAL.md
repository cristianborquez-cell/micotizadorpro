# Cotizador Pro Híbrido V3.2 Local

Trabajo: D:\PAQUETE_MIGRACION_COTIZADOR_DISCO_D_CORREGIDO\actual

## Inicio
1. Abre INICIAR_COTIZADOR_LOCAL.bat en la carpeta del paquete, o actual\INICIAR_LOCAL.bat.
2. Requiere Python 3.10 o posterior . Se detectó Python 3.13 en este equipo. No necesita Docker, pip ni PostgreSQL.
3. Se abre http://127.0.0.1:8765. Mantén abierta la consola. Ctrl+C detiene el servidor.
4. En el primer inicio crea el administrador con una contraseña de al menos 10 caracteres. No hay contraseña predeterminada.
5. Para cada nueva cuenta, el administrador ingresa a Administración y pulsa Generar PIN de registro antes de crear el usuario. Entrega el PIN al usuario. En Crear cuenta, el usuario ingresa el PIN, su usuario o correo, nombre y contraseña. Una sola operación crea la cuenta y activa la licencia del equipo; no necesita volver a activar el PIN.

## Funciones
Cotizaciones con productos, servicios, precios, IVA, flete, descuento, estilos, plantillas, historial, PDF con vigencia de cinco días, importación/exportación y copia de cotizaciones. Bibliotecas del PDF incluidas para trabajar sin conexión. La consulta de precios, actualización del dólar y WhatsApp requieren internet y dependen de terceros; sus resultados externos no fueron certificados. No introducir claves privadas de servicios en el navegador.

Usuarios: ver nombre, usuario, correo, rol y estado; activar, bloquear, suspender, eliminar, emitir/revocar PIN y generar código de recuperación. Eliminar requiere confirmación y borra también cotizaciones de esa cuenta en el servidor local. El administrador no puede eliminarse ni bloquearse a sí mismo. Recuperación local: el administrador entrega un código de un solo uso, válido por 30 minutos. No se envían correos automáticamente. Las sesiones vencen en 12 horas y se invalidan al reiniciar el servidor o restablecer contraseña.

PIN: aleatorio, almacenado como hash, vinculado a una cuenta y al equipo servidor. Emitir otro revoca el anterior. Cambiar hardware/nombre del equipo puede requerir reactivar la licencia. Esta es una licencia local básica: quien controla el disco o modifica el programa puede alterarla. No constituye un sistema comercial de activación remota ni identifica equipos de navegadores remotos. El servidor escucha solamente en 127.0.0.1.

## Datos y respaldo
Base principal: actual\data\local.db. Historial y borradores tienen copia en el navegador separada por cuenta; conservar el mismo navegador y dirección. El guardado y la recarga combinan el historial propio con SQLite por ID, sin duplicar cotizaciones. El botón Guardar historial en disco permite sincronizar importaciones manualmente. Plantillas y borradores viven en el navegador: exporta también el respaldo JSON para conservar plantillas. No borrar datos del navegador sin exportar.

No se importan automáticamente datos antiguos sin dueño. Para migrar un historial anterior, exporta su JSON en la versión anterior y usa Importar respaldo desde la cuenta correcta, luego Guardar historial en disco.

Ejecuta RESPALDAR_LOCAL.bat periódicamente. Genera una copia SQLite consistente en respaldos y comprueba su integridad/restauración en otra base. Para restaurar: detén el servidor y ejecuta `EJECUTAR_PYTHON.bat respaldo_local.py --restore RUTA_ABSOLUTA_DEL_RESPALDO.db` dentro de actual. Conserva una copia del estado anterior antes de restaurar. Los respaldos contienen datos personales: guárdalos con acceso restringido. Si copias toda la carpeta a otro PC, conserva data y solicita un nuevo PIN. Las sesiones no se copian.

## Origen y alcance
ZIP original intacto en la carpeta del paquete; extracción original en versiones\V3.1. SHA256 en manifiestos. Se mantuvo la carpeta autorizada actual en D:; no se ejecutó el instalador de migración a D:\Innovatec. Backend FastAPI, Docker y configuración web originales quedan como referencia: no usar INICIAR_WINDOWS.bat para esta versión local. El frontend nuevo está integrado con local_server.py, no con los endpoints antiguos de FastAPI.

## Verificación 26-10-2026
- Prueba HTTP integral: primera cuenta, registro, login por correo, autorización de administrador, licencia obligatoria, vinculación a otro equipo rechazada, guardado idempotente, reset de un solo uso, invalidación de sesión, suspensión y eliminación: OK.
- Edge automatizado: primer inicio, acceso, interfaz sin errores JS, guardado, persistencia tras recargar, carga desde historial y descarga PDF: OK.
- Backup SQLite y restauración en base independiente: OK.
- Captura: actual\verificacion-local.png. No se certificó todavía compatibilidad x86, consulta real de precios ni despliegue público.

Si olvidaste la contraseña del administrador, el operador con acceso a los archivos de este PC puede ejecutar dentro de actual: EJECUTAR_PYTHON.bat recuperar_admin.py. Usa el código mostrado en Olvidé mi contraseña. El acceso al disco equivale a control de la instalación local.

Corrección de inicio: se evita el lanzador py registrado en E:. EJECUTAR_PYTHON.bat busca primero actual\runtime\python.exe y después D:\InnovatecAndroid32\python.exe (verificado). La instalación de Python queda en D:; el ZIP requiere esa ruta o un runtime completo en la carpeta runtime.


Actualización 3.2.2: el registro acepta un usuario o correo como identificador. Si se usa un correo y el segundo campo queda vacío, se conserva ese mismo correo. Crear cuenta no inicia sesión automáticamente: muestra confirmación y luego Iniciar sesión. Tras ingresar, una cuenta de usuario sin licencia pasa a Activar licencia, donde introduce el PIN de un equipo. El administrador inicial accede a la administración para emitir PIN. Tras actualizar archivos, cierre la consola anterior y vuelva a abrir INICIAR_COTIZADOR_LOCAL.bat; recargue la página. Los datos existentes se conservan.


Administración 3.2.3: ingresa como administrador y pulsa Administración. Desde PIN de registro puedes emitir el PIN antes de crear una cuenta, copiarlo y entregarlo al usuario. En Crear cuenta, la persona ingresa el PIN y sus datos; el registro vincula y activa el equipo en un solo paso. Desde Personas registradas puedes además emitir un PIN asignado a una cuenta existente. La cuenta regresiva se muestra en el panel. Si no se usa a tiempo queda caducado y puede eliminarse desde Eliminar PIN. Si se usa a tiempo queda activado para un equipo y no pierde vigencia al terminar esos cinco minutos: solo el administrador puede cesar la licencia. El panel muestra datos de la cuenta, cotizaciones, identificador de licencia, fechas y equipo. Las licencias activadas no se borran con Eliminar PIN: se cesan, conservando el registro. Emitir un nuevo PIN cesa el anterior. Los PIN antiguos sin activar y sin fecha pasan a caducados; las licencias activadas anteriores se conservan. Reinicia la consola del servidor para aplicar esta actualización.


Si ya hay una versión antigua en el puerto 8765, el nuevo inicio busca otro puerto libre y abre la dirección correcta. La administración aparece en la barra superior después de ingresar con la primera cuenta creada (rol administrador). También se puede abrir directamente agregando /admin a la dirección que muestra la consola, por ejemplo http://127.0.0.1:8766/admin. Reinicia mediante el BAT para levantar los archivos nuevos.


Flujo 3.2.5: el alta de nuevas cuentas requiere PIN de invitación vigente emitido previamente desde Administración → PIN de registro. El PIN de invitación se consume una sola vez al crear la cuenta y activa su licencia para el equipo local. Si vence a los cinco minutos, elimínalo y genera otro. La primera cuenta administradora se crea en la instalación inicial sin PIN.

Flujo vigente para nuevas cuentas: Administrador > Administración > PIN de registro > Generar PIN de registro. Entrega el PIN antes de que la persona pulse Crear cuenta. El usuario escribe el PIN, un nombre de usuario o correo, su contraseña y crea su cuenta; con ese único paso se consume la invitación y se licencia el equipo. Los PIN emitidos caducan en cinco minutos. PIN sin usar se eliminan desde la tabla de invitaciones. La primera cuenta administrador es la única que se establece sin PIN. Las cuentas existentes no se borran ni necesitan volver a registrarse.

