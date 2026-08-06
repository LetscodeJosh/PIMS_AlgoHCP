/**
 * Service Worker for PIMS_AlgoHCP Recognizer Web App (v2.0)
 * Enables offline caching, progressive web app installation, and instant updates.
 */

const CACHE_NAME = "pims-algo-hcp-v2.0";
const ASSETS_TO_CACHE = [
  "/",
  "/index.html",
  "/styles.css",
  "/app.js",
  "/manifest.json",
  "/assets/icon-192.png",
  "/assets/icon-512.png"
];

// Install Event - Pre-cache Static Assets
self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[Service Worker] Caching app shell assets");
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

// Activate Event - Clean Up Old Caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log("[Service Worker] Removing old cache:", cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event - Network First Strategy for APIs, Cache First for Static Assets
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Always use Network-First for API requests (/api/) to ensure fresh algorithm data
  if (url.pathname.startswith("/api/")) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(JSON.stringify({ error: "Network offline" }), {
          headers: { "Content-Type": "application/json" }
        });
      })
    );
    return;
  }

  // Cache-First strategy for static web app assets
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Fetch fresh copy in background to update cache (Stale-While-Revalidate)
        fetch(event.request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, networkResponse));
          }
        }).catch(() => {});
        return cachedResponse;
      }
      return fetch(event.request);
    })
  );
});
