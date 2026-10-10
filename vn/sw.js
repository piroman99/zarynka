// Service worker: оффлайн-кеш оболочки и ресурсов эпизода 1.
const CACHE = "zaryanka-ep1-v2";
const ASSETS = [
  "./",
  "./index.html",
  "./style.css",
  "./app.js",
  "./scenes.js",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "../assets/audio/theme_epic_0.mp3",
  "../assets/gen/ok_x_ship_dock_0.jpg",
  "../assets/gen/ok_reception_fix2_0.jpg",
  "../assets/bg_alley.png",
  "../assets/sprites/sergey.png",
  "../assets/sprites/kate_overalls.png",
  "../assets/sprites/kate_sad.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then(
      (hit) => hit || fetch(e.request).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy)).catch(() => {});
        return res;
      }).catch(() => caches.match("./index.html"))
    )
  );
});
