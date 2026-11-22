// Service Worker - Cotizador Pro
const CACHE_NAME = 'cotizador-v4';
const ASSETS = [
  '/', '/app', '/admin', '/license',
  '/assets/server_bridge.js', '/assets/jspdf.umd.min.js', '/assets/html2canvas.min.js', '/manifest.json'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS).catch(()=>{})));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;
  // Network-first for HTML/navigation and API, cache-first for static assets
  const isAsset = /\/assets\/|\.png$|\.jpg$|\.js$|\.json$/.test(url.pathname);
  if (isAsset) {
    e.respondWith(caches.match(e.request).then((resp) => resp || fetch(e.request).then((r) => { const c=r.clone(); caches.open(CACHE_NAME).then(cache=>cache.put(e.request,c)); return r; })));
    return;
  }
  e.respondWith(fetch(e.request).then((r) => { const c=r.clone(); caches.open(CACHE_NAME).then(cache=>cache.put(e.request,c)); return r; }).catch(() => caches.match(e.request)));
});