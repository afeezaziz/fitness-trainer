const CACHE_NAME = 'fitness-app-v1';
const OFFLINE_CACHE = 'fitness-app-offline-v1';
const STATIC_CACHE = 'fitness-app-static-v1';

// Version tracking for updates
const CURRENT_VERSION = '1.0.0';
const CACHE_PREFIX = 'fitness-app-';
const CACHE_VERSION = 'v1';

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/static/css/styles.css',
  '/static/js/offline.js',
  '/static/js/service-worker.js',
  '/static/manifest.json',
  'https://cdn.tailwindcss.com'
];

// Update notification channel
let updateChannel = null;

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => {
        console.log('Service Worker installed and files cached');
        return self.skipWaiting();
      })
  );
});

// Handle updates - notify when new service worker is found
self.addEventListener('updatefound', (event) => {
  const installingWorker = registration.installing;

  installingWorker.addEventListener('statechange', () => {
    if (installingWorker.state === 'installed' && navigator.serviceWorker.controller) {
      // New service worker is installed, ready to activate
      console.log('New version available, notifying user');
      notifyUpdateAvailable();
    }
  });
});

// Notify clients about updates
function notifyUpdateAvailable() {
  self.clients.matchAll().then(clients => {
    clients.forEach(client => {
      client.postMessage({
        type: 'UPDATE_AVAILABLE',
        version: CURRENT_VERSION,
        timestamp: new Date().toISOString()
      });
    });
  });
}

// Activate event - clean up old caches and claim clients
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          // Delete old caches that don't match current version
          if (cacheName.startsWith(CACHE_PREFIX) && cacheName !== STATIC_CACHE && cacheName !== OFFLINE_CACHE) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker activated');
      return self.clients.claim();
    })
  );
});

// Handle messages from clients
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({
      type: 'VERSION_INFO',
      version: CURRENT_VERSION,
      timestamp: new Date().toISOString()
    });
  }
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Skip Chrome extensions
  if (event.request.url.startsWith('chrome-extension://')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        // Return cached version if available
        if (cachedResponse) {
          return cachedResponse;
        }

        // Clone the request because it's a stream
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest).then(response => {
          // Don't cache non-successful responses
          if (!response || response.status !== 200) {
            return response;
          }

          // Clone the response because it's a stream
          const responseToCache = response.clone();

          // Cache the fetched resource
          caches.open(STATIC_CACHE).then(cache => {
            cache.put(event.request, responseToCache);
          });

          return response;
        }).catch(() => {
          // If fetch fails, return offline page for HTML requests
          if (event.request.headers.get('accept').includes('text/html')) {
            return caches.match('/offline');
          }

          // For other failed requests, return a basic response
          return new Response('Offline - Content not available', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
              'Content-Type': 'text/plain'
            })
          });
        });
      })
  );
});

// Handle background sync for data when back online
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-fitness-data') {
    event.waitUntil(syncFitnessData());
  }
});

// Sync function to upload offline data
async function syncFitnessData() {
  const offlineData = await getOfflineData();

  for (const data of offlineData) {
    try {
      await fetch(data.url, {
        method: data.method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data.payload)
      });

      // Remove synced data from storage
      await removeOfflineData(data.id);
    } catch (error) {
      console.error('Sync failed for:', data, error);
    }
  }
}

// Helper functions to manage offline data
async function getOfflineData() {
  return new Promise((resolve) => {
    const request = indexedDB.open('FitnessAppDB', 1);

    request.onsuccess = (event) => {
      const db = event.target.result;
      const transaction = db.transaction(['offlineData'], 'readonly');
      const store = transaction.objectStore('offlineData');
      const getAll = store.getAll();

      getAll.onsuccess = () => resolve(getAll.result);
      getAll.onerror = () => resolve([]);
    };

    request.onerror = () => resolve([]);
  });
}

async function removeOfflineData(id) {
  return new Promise((resolve) => {
    const request = indexedDB.open('FitnessAppDB', 1);

    request.onsuccess = (event) => {
      const db = event.target.result;
      const transaction = db.transaction(['offlineData'], 'readwrite');
      const store = transaction.objectStore('offlineData');
      const deleteReq = store.delete(id);

      deleteReq.onsuccess = () => resolve();
      deleteReq.onerror = () => resolve();
    };

    request.onerror = () => resolve();
  });
}