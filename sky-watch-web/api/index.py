"""Sky Watch — Vercel serverless API.
Handles GET / and /watch routes.
"""
import json
import sys
from datetime import date
from pathlib import Path

# Import skywatch functions
sys.path.insert(0, str(Path(__file__).parent))
import skywatch

# Simple template placeholders
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
  h1 .comet{color:#e0863d}
  p.lead{color:#c7cede;font-size:17px;margin:14px 0 28px}
  .card{background:#11151c;border:1px solid #1f2733;border-radius:12px;padding:22px;margin:18px 0}
  .card h2{font-size:15px;color:#8a94a6;letter-spacing:.5px;text-transform:uppercase;margin-bottom:10px;font-weight:600}
  .row{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 6px}
  a.btn{display:inline-block;background:#e0863d;color:#0a0d12;font-weight:600;text-decoration:none;padding:11px 18px;border-radius:8px;font-size:14px;transition:transform .1s}
  a.btn:hover{transform:translateY(-1px)}
  a.btn.ghost{background:transparent;color:#e7ecf5;border:1px solid #2a3441}
  ul{list-style:none;margin-top:8px}
  li{padding:6px 0;color:#c7cede;font-size:14px;display:flex;gap:10px}
  li code{background:#11151c;border:1px solid #1f2733;padding:2px 6px;border-radius:4px;color:#ffb3a6;font-size:12.5px;white-space:nowrap}
  .meta{color:#6a7484;font-size:12.5px;margin-top:32px;border-top:1px solid #1f2733;padding-top:18px}
  .meta a{color:#8a94a6;text-decoration:underline;text-decoration-color:#2a3441}
  .error{background:#3a1512;border:1px solid #e0533d;color:#ffb3a6;padding:14px;border-radius:8px;margin:18px 0}
</style>
</head>
<body>
<div class="wrap">
  <span class="badge">☄ Loop Engineering · Concept 6</span>
  <h1><span class="comet">☄</span> Sky Watch</h1>
  <p class="lead">A forward-looking asteroid watch, live from NASA's near-Earth object feed. Which rocks are passing in the next 7 days, which is closest, and whether any of them are worth worrying about.</p>

  <div class="card">
    <h2>Live forecast</h2>
    <p style="color:#c7cede;font-size:14px">Open the watch — the card is rebuilt on every request from NASA's feed. No caching, no guessing.</p>
    <div class="row">
      <a class="btn" href="/watch">Open the 7-day watch →</a>
      <a class="btn ghost" href="/watch?days=1">Today only</a>
      <a class="btn ghost" href="/json">Raw JSON</a>
    </div>
  </div>

  <div class="card">
    <h2>What this is</h2>
    <p style="color:#c7cede;font-size:14px">A scheduled <em>watch</em> — a loop that runs on a clock and reports the sky for the days ahead, not after a pass has already happened. Most mornings it will say <strong style="color:#8fe0b0">all clear</strong>; on the rare day it matters, it leads with the warning.</p>
  </div>

  <div class="card">
    <h2>API</h2>
    <ul>
      <li><code>GET /watch</code> — the 7-day watch (HTML card)</li>
      <li><code>GET /watch?days=1</code> — a shorter window (1–7)</li>
      <li><code>GET /watch?format=json</code> — JSON for downstream tools</li>
      <li><code>GET /json</code> — raw rows as JSON</li>
    </ul>
  </div>

  <div class="meta">
    Today is <strong style="color:#c7cede">{today}</strong>. Data source: NASA NeoWs (api.nasa.gov). Deployment: Vercel · Serverless Python.
  </div>
</div>
</body>
</html>"""

WATCH_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Sky Watch — Live Forecast</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#0a0d12;color:#e7ecf5;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;min-height:100vh;padding:24px}}
  a{{color:#8a94a6;text-decoration:none;padding:6px 12px;border:1px solid #1f2733;border-radius:6px;font-size:13px}}
  a:hover{{color:#e7ecf5;border-color:#2a3441}}
  .header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
  pre{{background:#11151c;border:1px solid #1f2733;border-radius:8px;padding:16px;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;color:#c7cede;white-space:pre-wrap;overflow-x:auto}}
  .meta{{color:#6a7484;font-size:12px;margin-top:18px;text-align:center}}
  .error{{background:#3a1512;border:1px solid #e0533d;color:#ffb3a6;padding:16px;border-radius:8px}}
</style>
</head>
<body>
<div class="header">
  <a href="/">← Back to home</a>
  <a href="/json">View JSON</a>
</div>
{content}
<div class="meta">Data from NASA NeoWs · {today}</div>
</body>
</html>"""

ERROR_PAGE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"/><title>Error</title></head>
<body style="background:#0a0d12;color:#ffb3a6;font-family:sans-serif;padding:48px;text-align:center">
<h1>⚠ Watch Error</h1>
<div class="error">{error}</div>
<p><a href="/" style="color:#e0863d">← Back to home</a></p>
</body>
</html>"""


def handler(request):
    """Vercel Python handler - receives Werkzeug Request, returns Response tuple."""
    path = request.path
    query = request.query_params

    # Default to 7 days, allow 1-7
    try:
        days = min(7, max(1, int(query.get("days", "7"))))
    except (ValueError, TypeError):
        days = 7

    fmt = query.get("format", "")

    if path == "/" or path == "":
        html = LANDING_PAGE.format(today=date.today().isoformat())
        return {"statusCode": 200, "headers": {"Content-Type": "text/html; charset=utf-8"}, "body": html}

    if path == "/watch" or path == "/api/watch":
        try:
            feed = skywatch.fetch(days)
            if "error" in feed:
                body = ERROR_PAGE.format(error=feed["error"])
                return {"statusCode": 502, "headers": {"Content-Type": "text/html"}, "body": body}

            rows = skywatch.rows(feed, days)
            card_text = skywatch.card(rows, days)

            if fmt == "json":
                body = json.dumps({"days": days, "rows": rows}, indent=2)
                return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": body}
            elif fmt == "card":
                return {"statusCode": 200, "headers": {"Content-Type": "text/plain; charset=utf-8"}, "body": card_text}

            html = WATCH_PAGE.format(content="<pre>" + card_text + "</pre>", today=date.today().isoformat())
            return {"statusCode": 200, "headers": {"Content-Type": "text/html; charset=utf-8"}, "body": html}

        except SystemExit as e:
            body = ERROR_PAGE.format(error=f"Watch failed (code {e.code}). NASA API may be unavailable.")
            return {"statusCode": 502, "headers": {"Content-Type": "text/html"}, "body": body}
        except Exception as ex:
            body = ERROR_PAGE.format(error=str(ex))
            return {"statusCode": 500, "headers": {"Content-Type": "text/html"}, "body": body}

    if path == "/json" or path == "/api/json":
        try:
            feed = skywatch.fetch(days)
            rows = skywatch.rows(feed, days)
            body = json.dumps({"days": days, "as_of": date.today().isoformat(), "rows": rows}, indent=2)
            return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": body}
        except SystemExit as e:
            body = json.dumps({"error": f"watch failed (code {e.code})"})
            return {"statusCode": 502, "headers": {"Content-Type": "application/json"}, "body": body}
        except Exception as ex:
            body = json.dumps({"error": str(ex)})
            return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": body}

    # 404 for unknown paths
    body = ERROR_PAGE.format(error="Page not found: " + path)
    return {"statusCode": 404, "headers": {"Content-Type": "text/html"}, "body": body}
