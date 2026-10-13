// Auto-generated — do not edit by hand, see generate_site.py
const CACHE_NAME = 'cardvault-p2-v3';
const PRECACHE = [
  './',
  './index.html',
  './manifest.json',
  '../icons/icon-192-p2.png',
  '../icons/icon-512-p2.png',
  '../icons/icon-180-p2.png',
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(PRECACHE)));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return; // cross-origin (fonts) - let the browser handle it

  if (req.mode === 'navigate' || req.destination === 'document') {
    // network-first for the app shell, so catalog updates land promptly when online
    event.respondWith(
      fetch(req).then(res => {
        const copy = res.clone();
        caches.open(CACHE_NAME).then(c => c.put(req, copy));
        return res;
      }).catch(() => caches.match(req).then(r => r || caches.match('./')))
    );
    return;
  }

  // cache-first for static assets, so the app still works offline mid-session
  event.respondWith(
    caches.match(req).then(cached => cached || fetch(req).then(res => {
      const copy = res.clone();
      caches.open(CACHE_NAME).then(c => c.put(req, copy));
      return res;
    }))
  );
});
