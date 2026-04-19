"""
Phase 72: Mobile Responsive Enhancements
Enhanced mobile experience with PWA and touch optimizations.
"""

import os
import sys
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Mobile-optimized CSS
MOBILE_CSS = """
/* Mobile-first responsive design */
:root {
    --touch-target: 44px;
    --mobile-padding: 1rem;
    --font-size-base: 16px;
}

/* Touch-friendly buttons */
.btn, .nav-item, .form-input, .form-select {
    min-height: var(--touch-target);
    padding: 0.75rem 1rem;
    font-size: var(--font-size-base);
    -webkit-tap-highlight-color: transparent;
}

/* Mobile sidebar - bottom navigation */
@media (max-width: 768px) {
    .sidebar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        top: auto;
        width: 100%;
        height: 60px;
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 0;
        z-index: 1000;
    }
    
    .sidebar .logo {
        display: none;
    }
    
    .nav-item {
        flex-direction: column;
        gap: 0.25rem;
        padding: 0.5rem;
        margin: 0;
        font-size: 0.75rem;
    }
    
    .nav-item span:first-child {
        font-size: 1.25rem;
    }
    
    .main {
        margin-left: 0;
        margin-bottom: 60px;
        padding: var(--mobile-padding);
    }
    
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 0.75rem;
    }
    
    .stat-card {
        padding: 1rem;
    }
    
    .stat-value {
        font-size: 1.5rem;
    }
    
    .card {
        padding: 1rem;
    }
    
    .table-container {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    table {
        font-size: 0.875rem;
    }
    
    th, td {
        padding: 0.75rem 0.5rem;
    }
}

/* Small phones */
@media (max-width: 380px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .header {
        flex-direction: column;
        gap: 1rem;
    }
    
    .header-actions {
        width: 100%;
        justify-content: space-between;
    }
}

/* Landscape phones */
@media (max-width: 768px) and (orientation: landscape) {
    .sidebar {
        height: 50px;
    }
    
    .main {
        margin-bottom: 50px;
    }
}

/* Touch gestures */
.touch-scroll {
    -webkit-overflow-scrolling: touch;
    scroll-behavior: smooth;
}

/* Pull to refresh indicator */
.pull-indicator {
    height: 0;
    overflow: hidden;
    text-align: center;
    transition: height 0.3s;
}

.pull-indicator.visible {
    height: 50px;
}

/* Swipeable cards */
.swipe-card {
    touch-action: pan-y;
    user-select: none;
}

/* Mobile form enhancements */
@media (max-width: 768px) {
    .form-row {
        grid-template-columns: 1fr;
    }
    
    input[type="date"],
    input[type="number"],
    select {
        font-size: 16px; /* Prevent zoom on iOS */
    }
}

/* Dark mode optimization for mobile */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #000000;
        --bg-secondary: #0a0a1a;
        --bg-card: #151530;
    }
}

/* Safe area for notched phones */
@supports (padding: max(0px)) {
    .main {
        padding-left: max(var(--mobile-padding), env(safe-area-inset-left));
        padding-right: max(var(--mobile-padding), env(safe-area-inset-right));
        padding-bottom: max(60px, env(safe-area-inset-bottom));
    }
    
    .sidebar {
        padding-bottom: max(0px, env(safe-area-inset-bottom));
    }
}
"""

# PWA Manifest for mobile
PWA_MANIFEST = {
    "name": "翠花量化系统",
    "short_name": "翠花量化",
    "description": "模块化量化交易平台",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#0f0f23",
    "theme_color": "#6366f1",
    "orientation": "any",
    "icons": [
        {
            "src": "/static/icons/icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any maskable"
        },
        {
            "src": "/static/icons/icon-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any maskable"
        }
    ],
    "categories": ["finance", "productivity"],
    "shortcuts": [
        {
            "name": "查看信号",
            "url": "/analysis",
            "description": "查看最新交易信号"
        },
        {
            "name": "股票池",
            "url": "/stocks",
            "description": "管理股票池"
        }
    ]
}


class MobileOptimizer:
    """
    Optimize WebUI for mobile devices.
    """
    
    @staticmethod
    def get_mobile_css() -> str:
        """Get mobile-optimized CSS."""
        return MOBILE_CSS
        
    @staticmethod
    def get_pwa_manifest() -> Dict:
        """Get PWA manifest."""
        return PWA_MANIFEST
        
    @staticmethod
    def generate_service_worker() -> str:
        """Generate PWA service worker."""
        return """
const CACHE_NAME = 'cuihua-mobile-v1';
const ASSETS = [
  '/',
  '/static/css/mobile.css',
  '/static/js/mobile.js',
  '/manifest.json'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});
"""
        
    @staticmethod
    def generate_mobile_meta() -> str:
        """Generate mobile meta tags."""
        return """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
<meta name="theme-color" content="#6366f1">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="翠花量化">
<meta name="mobile-web-app-capable" content="yes">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/static/icons/icon-192.png">
"""


if __name__ == "__main__":
    print("✅ Mobile Responsive Enhancements loaded")
    
    optimizer = MobileOptimizer()
    print(f"\n📱 Mobile CSS: {len(optimizer.get_mobile_css())} bytes")
    print(f"📋 PWA Manifest: {len(optimizer.get_pwa_manifest())} keys")
    print(f"🔧 Service Worker: {len(optimizer.generate_service_worker())} bytes")
    print(f"🏷️ Mobile Meta: {len(optimizer.generate_mobile_meta())} bytes")
