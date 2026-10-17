// Минимальный service worker: нужен только чтобы Chrome разрешил поставить
// новеллу «на экран Домой» в полноэкранном режиме (без адресной строки).
// Ничего не кешируем — всегда сеть, чтобы демо не показывало старую версию.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', () => { /* passthrough */ });
