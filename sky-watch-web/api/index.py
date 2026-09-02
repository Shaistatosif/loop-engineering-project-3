"""Sky Watch — Vercel serverless API using Flask."""
import json
import sys
from datetime import date
from pathlib import Path

# Import skywatch functions
sys.path.insert(0, str(Path(__file__).parent))
import skywatch

from flask import Flask, Response, request

application = app = Flask(__name__)


LANDING_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Sky Watch — Near-Earth Asteroids, Live</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#0a0d12;color:#e7ecf5;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.55;min-height:100vh}
  .wrap{max-width:720px;margin:0 auto;padding:48px 24px}
  .badge{display:inline-block;background:#1b2330;color:#8a94a6;font-size:11px;letter-spacing:1.2px;padding:4px 10px;border-radius:999px;text-transform:uppercase}
  h1{font-size:38px;letter-spacing:-.5px;margin:14px 0 6px;line-height:1.15}
  .comet{color:#e0863d}
  p.lead{color:#c7cede;font-size:17px;margin:14px 0 28px}
  .card{background:#11151c;border:1px solid #1f2733;border-radius:12px;padding:22px;margin:18px 0}
  .card h2{font-size:15px;color:#8a94a6;letter-spacing:.5px;text-transform:uppercase;margin-bottom:10px;font-weight:600}
  .row{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 6px}
  a.btn{display:inline-block;background:#e0863d;color:#0a0d12;font-weight:600;text-decoration:none;padding:11px 18px;border-radius:8px;font-size:14px;transition:transform .1s}
  a.btn:hover{transform:translateY(-1px)}
  a.btn.ghost{background:transparent;color:#e7ecf5;border:1px solid #2a3441}
  ul{list-style:none;margin-top:8px}
  li{padding:6px 0;color:#c7cede;font-size:14px}
  li code{background:#11151c;border:1px solid #1f2733;padding:2px 6px;border-radius:4px;color:#ffb3a6;font-size:12.5px}
  .meta{color:#6a7484;font-size:12.5px;margin-top:32px;border-top:1px solid #1f2733;padding-top:18px}
</style>
</head>
<body>
<div class="wrap">
  <span class="badge">☄ Loop Engineering · Concept 6</span>
  <h1><span class="comet">☄</span> Sky Watch</h1>
  <p class="lead">A forward-looking asteroid watch, live from NASA's near-Earth object feed.</p>

  <div class="card">
    <h2>Live forecast</h2>
    <div class="row">
      <a class="btn" href="/watch">Open the 7-day watch →</a>
      <a class="btn ghost" href="/watch?days=1">Today only</a>
      <a class="btn ghost" href="/json">Raw JSON</a>
    </div>
  </div>

  <div class="card">
    <h2>API Endpoints</h2>
    <ul>
      <li><code>GET /watch</code> — 7-day watch card</li>
      <li><code>GET /watch?days=1</code> — Today only</li>
      <li><code>GET /watch?format=json</code> — JSON data</li>
      <li><code>GET /json</code> — Raw JSON</li>
    </ul>
  </div>

  <div class="meta">Today: {today} · NASA NeoWs</div>
</div>
</body>
</html>"""


def get_path():
    """Get the clean path, stripping /api/index or /api/ prefix if present."""
    path = request.path
    # Strip the /api/index or /api prefix that Vercel rewrites add
    if path.startswith("/api/index"):
        path = path[len("/api/index"):] or "/"
    elif path.startswith("/api/"):
        path = path[len("/api/"):]
    return path


@app.route("/")
@app.route("/<path:subpath>")
def catch_all(subpath=None):
    path = get_path()
    days_arg = request.args.get("days", "7")

    try:
        days = min(7, max(1, int(days_arg)))
    except (ValueError, TypeError):
        days = 7

    fmt = request.args.get("format", "")

    # Home page
    if path == "/" or path == "":
        return Response(
            LANDING_PAGE.format(today=date.today().isoformat()),
            mimetype="text/html; charset=utf-8"
        )

    # Watch endpoint
    if path == "watch":
        try:
            feed = skywatch.fetch(days)
            if "error" in feed:
                return Response(f"NASA Error: {feed['error']}", status=502, mimetype="text/plain")
            rows = skywatch.rows(feed, days)
            card_text = skywatch.card(rows, days)

            if fmt == "json":
                return Response(json.dumps({"days": days, "rows": rows}, indent=2),
                              mimetype="application/json")
            elif fmt == "card":
                return Response(card_text, mimetype="text/plain; charset=utf-8")

            return Response(f"""<!doctype html>
<html><head><meta charset="utf-8"/><title>Sky Watch</title>
<style>body{{background:#0a0d12;color:#e7ecf5;font-family:monospace;font-size:14px;padding:24px}}
a{{color:#8a94a6;text-decoration:none}}pre{{background:#11151c;border:1px solid #1f2733;padding:16px;border-radius:8px;white-space:pre-wrap}}
.meta{{color:#6a7484;font-size:12px;margin-top:16px}}</style></head>
<body><a href="/">← Home</a><pre>{card_text}</pre>
<div class="meta">NASA NeoWs · {date.today().isoformat()}</div></body></html>""",
                           mimetype="text/html; charset=utf-8")

        except SystemExit as e:
            return Response(f"Watch failed (code {e.code})", status=502, mimetype="text/plain")
        except Exception as ex:
            return Response(f"Error: {ex}", status=500, mimetype="text/plain")

    # JSON endpoint
    if path == "json":
        try:
            feed = skywatch.fetch(days)
            rows = skywatch.rows(feed, days)
            return Response(
                json.dumps({"days": days, "as_of": date.today().isoformat(), "rows": rows}, indent=2),
                mimetype="application/json"
            )
        except SystemExit as e:
            return Response(json.dumps({"error": f"failed (code {e.code})"}),
                          status=502, mimetype="application/json")
        except Exception as ex:
            return Response(json.dumps({"error": str(ex)}),
                          status=500, mimetype="application/json")

    # 404
    return Response(f"Page not found: {path}", status=404, mimetype="text/plain")


# Vercel export
handler = app
