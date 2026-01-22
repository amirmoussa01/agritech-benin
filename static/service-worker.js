self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('agritech-cache').then(cache => {
      return cache.addAll([
        '/',
      ]);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
