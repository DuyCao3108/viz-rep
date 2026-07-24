# Live PNG Viewer

Browser tab that auto-refreshes a chart PNG whenever it's rewritten on disk —
no page reload, no extra deps (stdlib `http.server` only).

Workflow: edit chart code -> rerun the script that writes the PNG -> the
already-open tab picks up the new image within ~500ms.

## Setup (every session)

1. Start the server once, from anywhere (it resolves the repo root itself),
   and leave it running in its own terminal:

   ```bash
   python tools/live_view/serve.py        # default port 8000
   python tools/live_view/serve.py 8001   # or pick a port
   ```

2. Open one browser tab per chart you're iterating on, pointing `img=` at
   the PNG's path **relative to the repo root**:

   ```
   http://localhost:8000/tools/live_view/live_view.html?img=story/pcb_bank/output/pcb/bar_by_quarter.png
   http://localhost:8000/tools/live_view/live_view.html?img=sandbox/small_multiples.png
   ```

3. Leave the tab open. Rerun whatever script writes that PNG (e.g.
   `python story/pcb_bank/main.py`, or a `sandbox/*.py` script) — the tab
   updates on its own, no manual refresh, no server restart.

Multiple charts at once = multiple tabs against the same server.

## Gotchas

- **`OSError: Address already in use`** — something's already listening on
  that port, possibly a server left running from a previous session. Check
  what it's serving with `curl -sI http://localhost:8000/`; if it's already
  serving this repo root you can just reuse it and skip step 1. Otherwise
  pick a different port (`serve.py 8001`) or kill the old process.
- **`img=` is always relative to the repo root**, never to
  `tools/live_view/`, no matter what the URL bar shows. `live_view.html`
  forces it absolute internally — you don't need a leading `/`.
- **`favicon.ico` 404** in the server log is just the browser requesting a
  tab icon — harmless, ignore it.
- **`&interval=200`** (ms) query param to poll faster/slower than the
  500ms default, e.g. `...&img=...png&interval=200`.
- Stop the server with `Ctrl+C` in its terminal.
