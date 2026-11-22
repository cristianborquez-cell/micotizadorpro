(async function(){
const token=sessionStorage.getItem('cotizador_token');if(!token){location='/';return}
async function api(path,x){const r=await fetch(path,{method:x?'POST':'GET',cache:'no-store',headers:{'Content-Type':'application/json',Authorization:'Bearer '+token},body:x?JSON.stringify(x):undefined});const d=await r.json().catch(()=>({}));if(r.status===401){sessionStorage.clear();location='/';throw Error(d.detail||'Sesión inválida');}if(!r.ok)throw Error(d.detail||('Error '+r.status));return d}
const bar=document.createElement('div');bar.style='position:sticky;top:0;z-index:99999;background:#fff;color:#123;padding:12px;display:flex;gap:12px;align-items:center;flex-wrap:wrap';const status=document.createElement('span');status.textContent='Comprobando cuenta…';bar.append(status);document.body.prepend(bar);
function button(t,fn){const b=document.createElement('button');b.textContent=t;b.onclick=fn;bar.append(b)}
button('🧾 Ingresa tus datos para tu cotizador',()=>{if(window.abrirDatosEmisor)window.abrirDatosEmisor();});
button('Cerrar sesión',async()=>{await api('/api/auth/logout',{}).catch(()=>{});sessionStorage.clear();location='/'});
try{const me=await api('/api/me');const license=me.role==='admin'?{active:true}:await api('/api/license/status');if(!license.active){location='/license';return}
// Cada cuenta conserva un historial y borrador independientes en el navegador.
const originalGet=Storage.prototype.getItem,originalSet=Storage.prototype.setItem,originalRemove=Storage.prototype.removeItem;
const scoped=k=>k.startsWith('cotizador_')?('usuario_'+me.id+'_'+k):k;
Storage.prototype.getItem=function(k){return originalGet.call(this,this===localStorage?scoped(k):k)};
Storage.prototype.setItem=function(k,v){return originalSet.call(this,this===localStorage?scoped(k):k,v)};
Storage.prototype.removeItem=function(k){return originalRemove.call(this,this===localStorage?scoped(k):k)};
historial=cargarLS('cotizador_historial',[]);productos=[];idCotizacionActual=null;
const remote=await api('/api/local/history');iniciarApp();document.querySelector('.container').hidden=false;const merged=new Map(remote.map(q=>[String(q.id),q]));historial.forEach(q=>merged.set(String(q.id),q));historial=[...merged.values()];guardarLS('cotizador_historial',historial);renderizarHistorial();status.textContent='Cuenta: '+me.username+' · Guardado local en disco y navegador';
const save=window.guardarCotizacion;window.guardarCotizacion=function(){save();sync()};
async function sync(){try{await api('/api/local/history',{quotes:historial});status.textContent='Historial guardado en disco · '+new Date().toLocaleTimeString()}catch(e){status.textContent='Pendiente de guardar en disco: '+e.message}}
const del=window.eliminarDelHistorial;window.eliminarDelHistorial=async function(id){del(id);if(!historial.some(q=>q.id===id)){try{await api('/api/local/delete',{id})}catch(e){status.textContent=e.message}}};
const clear=window.borrarTodoHistorial;window.borrarTodoHistorial=async function(){const ids=historial.map(q=>q.id);clear();if(!historial.length)for(const id of ids)await api('/api/local/delete',{id})};
button('Guardar historial en disco',sync);await sync();
setInterval(async()=>{try{await api('/api/local/history')}catch(e){document.querySelector('.container').hidden=true;status.textContent=e.message;location='/license'}},30000);
}catch(e){status.textContent='Error de conexión: '+e.message+' · Reinicia el cotizador desde INICIAR_COTIZADOR_LOCAL.bat.';document.querySelector('.container').hidden=false;iniciarApp();document.querySelectorAll('.container button').forEach(b=>{if(b.textContent.includes('Guardar'))b.disabled=true})}
})();



