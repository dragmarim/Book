# Book

Card Vault session tracker, as 4 separate installable apps (Player 1–4),
hosted on GitHub Pages.

- `index.html` — landing page with links to all 4 player instances
- `p1/`, `p2/`, `p3/`, `p4/` — the 4 player apps (each is a standalone PWA:
  its own `index.html`, `manifest.json`, `sw.js`)
- `icons/` — home-screen icons (same seal design, numbered per player)
- `src/template.html` — the single source file all 4 player pages are
  generated from; **edit this, not the files under `p1/`–`p4/` directly**
- `src/generate_site.py` — regenerates `p1/`–`p4/` and the landing page from
  `src/template.html`. Run after every edit to `template.html`:
  `python3 src/generate_site.py`

## Updating the card catalog

Each player's saved board (cards in slots, Jenny balance, history, wands) is
stored in that player's browser under a storage key tied to their URL
(`board-state-p1`, etc.) and is never touched by a redeploy — it only
changes when that player adds/removes/uses something in the app itself.
Pushing a new catalog here is safe to do mid-campaign.

1. Edit `src/template.html`'s `EMBEDDED_CARD_STORE` with the new card list.
2. Run `python3 src/generate_site.py` (also bumps the service worker cache
   version, so installed devices pick up the change next time they're online).
3. Commit and push. GitHub Pages redeploys automatically.
4. Players don't need to do anything — the next time their phone has a
   connection, the app shell refreshes in the background. If a player wants
   it immediately, they can pull-to-refresh or relaunch the app.
