"""
Phase 29: PWA Service Worker
Progressive Web App support for offline access.
"""

import os
import sys

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

PWA_MANIFEST = """
{
  "name": "翠花量化系统",
  "short_name": "翠花量化",
  "description": "模块化量化交易平台",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1a1a2e",
  "theme_color": "#1a1a2e",
  "icons": [
    {
      "src": "/static/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
"""

SERVICE_WORKER = """
const CACHE_NAME = 'cuihua-quant-v1';
const STATIC_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/icons/icon-192x192.png'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        return response;
      }
      return fetch(event.request).then((fetchResponse) => {
        if (!fetchResponse || fetchResponse.status !== 200) {
          return fetchResponse;
        }
        const responseToCache = fetchResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return fetchResponse;
      });
    })
  );
});

// Background sync
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

async function syncData() {
  // Sync cached requests when back online
  console.log('Syncing data...');
}
"""

PWA_SCRIPT = """
// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration.scope);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

// Check online status
function updateOnlineStatus() {
  const status = navigator.onLine ? '🟢 在线' : '🔴 离线';
  const indicator = document.getElementById('online-status');
  if (indicator) {
    indicator.textContent = status;
  }
}

window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);
updateOnlineStatus();

// Add to home screen prompt
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const installBtn = document.getElementById('install-btn');
  if (installBtn) {
    installBtn.style.display = 'block';
    installBtn.addEventListener('click', () => {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('User accepted A2HS');
        }
        deferredPrompt = null;
      });
    });
  }
});
"""

def setup_pwa(static_dir: str = None):
    """Setup PWA files."""
    if static_dir is None:
        static_dir = os.path.join(project_root, 'static')
        
    os.makedirs(static_dir, exist_ok=True)
    
    # Write manifest
    manifest_path = os.path.join(static_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        f.write(PWA_MANIFEST)
        
    # Write service worker
    sw_path = os.path.join(project_root, 'sw.js')
    with open(sw_path, 'w') as f:
        f.write(SERVICE_WORKER)
        
    # Write PWA script
    js_dir = os.path.join(static_dir, 'js')
    os.makedirs(js_dir, exist_ok=True)
    pwa_js_path = os.path.join(js_dir, 'pwa.js')
    with open(pwa_js_path, 'w') as f:
        f.write(PWA_SCRIPT)
        
    return {
        'manifest': manifest_path,
        'service_worker': sw_path,
        'pwa_script': pwa_js_path
    }
