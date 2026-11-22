/* CultureLens service worker: makes the planner installable and lets the app
 * shell open offline. It deliberately never touches API calls: the backend is
 * on another origin, and anything under /api/ is passed straight through, so
 * itineraries, signups and feedback are always live, never stale.
 *
 * Bump VERSION to drop every old cache on the next visit.
 */
const VERSION = "v1";
const SHELL = `culturelens-shell-${VERSION}`;
const ASSETS = `culturelens-assets-${VERSION}`;
const PRECACHE = ["/", "/manifest.webmanifest", "/icons/icon-192.png"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const shell = await caches.open(SHELL);
      await shell.addAll(PRECACHE);
      // Also cache the hashed JS/CSS the homepage needs, so the first offline
      // open works even before those files were fetched through this worker.
      const html = await (await shell.match("/")).text();
      const assets = [...html.matchAll(/(?:src|href)="(\/assets\/[^"]+)"/g)].map((m) => m[1]);
      if (assets.length) await (await caches.open(ASSETS)).addAll(assets);
    })().catch(() => undefined),
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keep = new Set([SHELL, ASSETS]);
      for (const key of await caches.keys()) {
        if (key.startsWith("culturelens-") && !keep.has(key)) await caches.delete(key);
      }
      await self.clients.claim();
    })(),
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return; // backend API, map tiles, fonts: untouched
  if (url.pathname.startsWith("/api/")) return;

  if (request.mode === "navigate") {
    // Network first: always the latest page when online; cached copy offline.
    event.respondWith(
      (async () => {
        try {
          const response = await fetch(request);
          if (response.ok) {
            const copy = response.clone();
            caches.open(SHELL).then((c) => c.put(url.pathname, copy));
          }
          return response;
        } catch {
          return (
            (await caches.match(url.pathname, { cacheName: SHELL })) ||
            (await caches.match("/", { cacheName: SHELL })) ||
            Response.error()
          );
        }
      })(),
    );
    return;
  }

  if (url.pathname.startsWith("/assets/") || url.pathname.startsWith("/icons/")) {
    // Hashed build files never change, so cache first.
    event.respondWith(
      (async () => {
        const cached = await caches.match(request, { cacheName: ASSETS });
        if (cached) return cached;
        const response = await fetch(request);
        if (response.ok) {
          const copy = response.clone();
          caches.open(ASSETS).then((c) => c.put(request, copy));
        }
        return response;
      })(),
    );
  }
});
