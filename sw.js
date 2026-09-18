/* Generated offline shell. No telemetry or background sync. */
// Cache ownership is scoped: updating one deployment must not clear another.
const PREFIX = 'copperbench:' + self.registration.scope + ':';
const CACHE = PREFIX + "1.6.1-d6cebae9ae652c69";
const ASSETS = ["./", "index.html", "styles.css", "icon.svg", "manifest.webmanifest", "vendor/jszip.min.js", "src/core.js", "src/geometry.js", "src/vias.js", "src/font.js", "src/platforms.js", "src/maker-parts.js", "src/carriers.js", "src/modules.js", "src/block-catalog.js", "src/blocks.js", "src/manufacturing.js", "src/router.js", "src/planes.js", "src/interchange.js", "src/renderer.js", "src/modules-renderer.js", "src/worker-source.js", "src/app.js"];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(
    keys.filter(key => key.startsWith(PREFIX) && key !== CACHE).map(key => caches.delete(key))
  )).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || new URL(event.request.url).origin !== self.location.origin) return;
  event.respondWith(caches.open(CACHE).then(cache => cache.match(event.request))
    .then(hit => hit || fetch(event.request)));
});
