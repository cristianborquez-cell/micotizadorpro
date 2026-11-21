// Service Worker — Cotizador Pro Híbrido (PWA Android)
const CACHE_NAME = 'cotizador-v1';
const ASSETS = [
  '/',
  '/login.html',
  '/app',
  '/cotizador.html',
  '/admin.html',
  '/license.html',
  '/assets/server_bridge.js',
  '/assets/jspdf.umd.min.js',
  '/assets/html2canvas.min.js',
  '/manifest.json'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((resp) => resp || fetch(e.request))
  );
});
