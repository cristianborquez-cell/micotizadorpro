from pathlib import Path
import sqlite3, datetime, argparse
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description='Respaldo y restauración SQLite local');parser.add_argument('--restore',type=Path);args=parser.parse_args()
folder=ROOT.parent/'respaldos';folder.mkdir(exist_ok=True)
source=ROOT/'data'/'local.db'
def copy_db(src,dst):
 a=sqlite3.connect(src);b=sqlite3.connect(dst)
 try:
  a.backup(b)
  if b.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('Base inválida')
 finally:a.close();b.close()
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
if args.restore:
 check=sqlite3.connect('file:'+args.restore.resolve().as_posix()+'?mode=ro',uri=True)
 try:
  if check.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('Respaldo inválido')
  for table in ('users','licenses','quotes'):check.execute('SELECT * FROM '+table+' LIMIT 1')
 finally:check.close()
 if source.exists():copy_db(source,folder/('antes_restaurar_'+stamp+'.db'))
 copy_db(args.restore,source);print('Restauración completada. Reinicie el servidor.')
else:
 if not source.exists():raise SystemExit('Inicie primero el cotizador.')
 target=folder/('cotizador_'+stamp+'.db');copy_db(source,target);print(target)
 # Verificar que el respaldo puede restaurarse en una base temporal independiente.
 test=folder/('verificacion_'+stamp+'.db');copy_db(target,test);test.unlink();print('Integridad y restauración de prueba: OK')
