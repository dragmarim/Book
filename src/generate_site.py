"""Generate the 4 player PWA pages (+ manifests, service workers, landing page)
from template.html. Re-run this any time template.html changes (e.g. after a
catalog update) to regenerate all 4 player copies in sync.

Bumps CACHE_VERSION automatically so installed devices pick up the change.
"""
import os
import re
import json

ROOT = os.path.dirname(__file__)
TEMPLATE_PATH = os.path.join(ROOT, "template.html")
BUILD_DIR = os.path.dirname(ROOT) if os.path.basename(ROOT) == 'src' else os.path.join(ROOT, 'build')
VERSION_FILE = os.path.join(ROOT, "VERSION")

PLAYERS = [1, 2, 3, 4]

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = f.read()

# --- bump version (used as the service-worker cache name suffix) ---
version = 1
if os.path.exists(VERSION_FILE):
    with open(VERSION_FILE) as f:
        try:
            version = int(f.read().strip()) + 1
        except ValueError:
            version = 1
with open(VERSION_FILE, "w") as f:
    f.write(str(version))

SW_TEMPLATE = """// Auto-generated — do not edit by hand, see generate_site.py
const CACHE_NAME = 'cardvault-{pid}-v{version}';
const PRECACHE = [
  './',
  './index.html',
  './manifest.json',
  '../icons/icon-192-{pid}.png',
  '../icons/icon-512-{pid}.png',
  '../icons/icon-180-{pid}.png',
];

self.addEventListener('install', event => {{
  self.skipWaiting();
  event.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(PRECACHE)));
}});

self.addEventListener('activate', event => {{
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
}});

self.addEventListener('fetch', event => {{
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return; // cross-origin (fonts) - let the browser handle it

  if (req.mode === 'navigate' || req.destination === 'document') {{
    // network-first for the app shell, so catalog updates land promptly when online
    event.respondWith(
      fetch(req).then(res => {{
        const copy = res.clone();
        caches.open(CACHE_NAME).then(c => c.put(req, copy));
        return res;
      }}).catch(() => caches.match(req).then(r => r || caches.match('./')))
    );
    return;
  }}

  // cache-first for static assets, so the app still works offline mid-session
  event.respondWith(
    caches.match(req).then(cached => cached || fetch(req).then(res => {{
      const copy = res.clone();
      caches.open(CACHE_NAME).then(c => c.put(req, copy));
      return res;
    }}))
  );
}});
"""


def manifest_for(pid, label, short):
    return {
        "name": f"Book — {label}",
        "short_name": f"Book {short}",
        "description": "Card Vault session tracker",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "orientation": "portrait-primary",
        "background_color": "#12151a",
        "theme_color": "#12151a",
        "icons": [
            {"src": f"../icons/icon-192-{pid}.png", "sizes": "192x192", "type": "image/png"},
            {"src": f"../icons/icon-512-{pid}.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }


for num in PLAYERS:
    pid = f"p{num}"
    label = f"Player {num}"
    short = f"P{num}"

    page = template.replace("{{PLAYER_ID}}", pid)
    page = page.replace("{{PLAYER_LABEL}}", label)
    page = page.replace("{{PLAYER_SHORT}}", short)

    player_dir = os.path.join(BUILD_DIR, pid)
    os.makedirs(player_dir, exist_ok=True)

    with open(os.path.join(player_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)

    with open(os.path.join(player_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_for(pid, label, short), f, indent=2)

    with open(os.path.join(player_dir, "sw.js"), "w", encoding="utf-8") as f:
        f.write(SW_TEMPLATE.format(pid=pid, version=version))

    print(f"built {player_dir} (cache v{version})")

# --- root landing page ---
links = "\n".join(
    f'      <a class="pick" href="./p{n}/">Player {n}</a>' for n in PLAYERS
)
landing = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Book</title>
<style>
  :root{{ --ink:#12151a; --ink-2:#191d24; --brass:#c6a15b; --brass-bright:#ddb96e; --cream:#f2ede1; --ash:#9199a8; --line:rgba(237,231,216,0.12); }}
  *{{ box-sizing:border-box; }}
  html,body{{ margin:0; padding:0; height:100%; }}
  body{{
    background: radial-gradient(1100px 600px at 12% -10%, rgba(198,161,91,0.08), transparent 60%), var(--ink);
    color: var(--cream);
    font-family: -apple-system, 'Inter', sans-serif;
    display:flex; align-items:center; justify-content:center;
    min-height:100vh; padding:24px;
  }}
  .card{{ max-width:360px; width:100%; text-align:center; }}
  h1{{ font-size:30px; margin:0 0 6px; letter-spacing:-0.01em; }}
  p{{ color:var(--ash); font-size:13px; margin:0 0 28px; }}
  .picks{{ display:flex; flex-direction:column; gap:12px; }}
  .pick{{
    display:block; padding:16px; border-radius:10px; background:var(--ink-2);
    border:1px solid var(--line); color:var(--cream); text-decoration:none;
    font-weight:600; font-size:15px; transition: border-color 0.15s ease, background 0.15s ease;
  }}
  .pick:hover{{ border-color:var(--brass); background:#222834; }}
</style>
</head>
<body>
  <div class="card">
    <h1>Book</h1>
    <p>Choose your name, then add it to your home screen from your browser's share menu.</p>
    <div class="picks">
{links}
    </div>
  </div>
</body>
</html>
"""
with open(os.path.join(BUILD_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(landing)
print("built landing page")
