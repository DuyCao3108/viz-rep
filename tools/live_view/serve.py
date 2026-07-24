"""Static file server for tools/live_view/live_view.html.

Workflow: edit chart code -> rerun the script that writes the PNG -> the
already-open browser tab picks up the new image automatically (live_view.html
polls the file and swaps it in on change, no page reload).

Usage:
    python tools/live_view/serve.py [port]   # default port 8000

Then open, e.g.:
    http://localhost:8000/tools/live_view/live_view.html?img=sandbox/small_multiples.png
    http://localhost:8000/tools/live_view/live_view.html?img=story/pcb_bank/output/pcb/bar_by_quarter.png

Serves the whole repo root (not just tools/live_view/) so `img=` can point at
any PNG in the tree without restarting the server.
"""

from __future__ import annotations

import http.server
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args, directory=str(REPO_ROOT), **kwargs
    )
    with http.server.ThreadingHTTPServer(("localhost", port), handler) as httpd:
        print(f"Serving {REPO_ROOT} at http://localhost:{port}")
        print(f"Viewer: http://localhost:{port}/tools/live_view/live_view.html?img=<path/to/chart.png>")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
