(async function(){
const token=sessionStorage.getItem('cotizador_token');if(!token){location='/';return}
async function api(path,x){const r=await fetch(path,{method:x?'POST':'GET',cache:'no-store',headers:{'Content-Type':'application/json',Authorization:'Bearer '+token},body:x?JSON.stringify(x):undefined});const d=await r.json().catch(()=>({}));if(r.status===401){sessionStorage.clear();location='/';throw Error(d.detail||'Sesión inválida');}if(!r.ok)throw Error(d.detail||('Error '+r.status));return d}
const isAPK=/CotizadorProApp/i.test(navigator.userAgent);
const bar=document.createElement('div');bar.style=isAPK?'position:sticky;top:0;z-index:99999;background:#fff;color:#123;padding:6px;display:flex;gap:6px;align-items:center;flex-wrap:wrap':'position:sticky;top:0;z-index:99999;background:#fff;color:#123;padding:12px;display:flex;gap:12px;align-items:center;flex-wrap:wrap';const status=document.createElement('span');status.textContent='Comprobando cuenta…';if(isAPK){status.style='flex:1 1 100%;font-size:10px;line-height:1.2';}bar.append(status);document.body.prepend(bar);
function button(t,fn){const b=document.createElement('button');b.textContent=t;b.onclick=fn;if(isAPK){b.style='flex:1 1 calc(50% - 6px);font-size:11px;padding:6px 4px;line-height:1.2;min-width:0;'}bar.append(b);return b}
if(isAPK){const b=document.createElement('button');b.textContent='☰ Acciones';b.className='apk-actions-btn';b.style='flex:1 1 calc(50% - 6px);font-size:11px;padding:6px 4px;line-height:1.2;min-width:0;border:0;border-radius:8px;color:#123;font-weight:700;transition:background-color .8s ease,color .8s ease';const colors=[['#D7EEFF','#0B4F6C'],['#FFE7C2','#7A4B00']];let ci=0;const applyC=()=>{b.style.backgroundColor=colors[ci][0];b.style.color=colors[ci][1];ci=1-ci;};applyC();setInterval(applyC,2000);b.onclick=()=>{const sb=document.querySelector('.actions-sidebar'); if(sb) sb.classList.toggle('open');};bar.append(b);}button('🧾 Ingresa tus datos para tu cotizador',()=>{if(window.abrirDatosEmisor)window.abrirDatosEmisor();});
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



