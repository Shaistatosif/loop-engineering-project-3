"""Sky Watch — Vercel Python with Flask."""
import json
import os
import sys
from datetime import date
from pathlib import Path

# Add api directory to path for skywatch import
sys.path.insert(0, str(Path(__file__).parent))

import skywatch
from flask import Flask, request, Response

app = Flask(__name__)

LANDING = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Sky Watch</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0a0d12;color:#e7ecf5;font-family:-apple-system,Segoe UI,sans-serif;line-height:1.6;min-height:100vh}
.wrap{max-width:680px;margin:0 auto;padding:48px 24px}
h1{font-size:36px;margin:14px 0 8px}
.comet{color:#e0863d}
.lead{color:#c7cede;font-size:16px;margin:12px 0 24px}
.card{background:#11151c;border:1px solid #1f2733;border-radius:12px;padding:20px;margin:16px 0}
.row{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}
.btn{background:#e0863d;color:#0a0d12;font-weight:600;text-decoration:none;padding:10px 16px;border-radius:8px;font-size:14px}
.btn.ghost{background:transparent;color:#e7ecf5;border:1px solid #2a3441}
ul{list-style:none;margin-top:8px}
li{padding:5px 0;color:#c7cede;font-size:14px}
code{background:#11151c;border:1px solid #1f2733;padding:2px 6px;border-radius:4px;color:#ffb3a6}
.meta{color:#6a7484;font-size:12px;margin-top:28px;padding-top:16px;border-top:1px solid #1f2733}
</style>
</head>
<body>
<div class="wrap">
<h1><span class="comet">☄</span> Sky Watch</h1>
<p class="lead">Live asteroid watch from NASA's near-Earth object feed.</p>
<div class="card">
<div class="row">
<a class="btn" href="/watch">7-day watch →</a>
<a class="btn ghost" href="/watch?days=1">Today</a>
<a class="btn ghost" href="/json">JSON</a>
</div>
</div>
<div class="card">
<ul>
<li><code>GET /watch</code> — 7-day forecast</li>
<li><code>GET /watch?days=1</code> — Today only</li>
<li><code>GET /watch?format=json</code> — JSON data</li>
<li><code>GET /json</code> — Raw JSON</li>
</ul>
</div>
<div class="meta">NASA NeoWs · {today}</div>
</div>
</body>
</html>"""

@app.route("/")
def home():
    return Response(LANDING.format(today=date.today().isoformat()), mimetype="text/html")

@app.route("/watch")
def watch():
    try:
        days = min(7, max(1, int(request.args.get("days", 7))))
    except (ValueError, TypeError):
        days = 7

    fmt = request.args.get("format", "")

    try:
        feed = skywatch.fetch(days)
        if "error" in feed:
            return Response(f"NASA Error: {feed['error']}", status=502, mimetype="text/plain")

        rows = skywatch.rows(feed, days)
        card = skywatch.card(rows, days)

        if fmt == "json":
            return Response(json.dumps({"days": days, "rows": rows}, indent=2), mimetype="application/json")
        elif fmt == "card":
            return Response(card, mimetype="text/plain")

        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/><title>Sky Watch</title>
<style>body{{background:#0a0d12;color:#e7ecf5;font-family:monospace;font-size:14px;padding:24px}}
a{{color:#8a94a6;text-decoration:none;padding:6px 12px;border:1px solid #1f2733;border-radius:6px}}
pre{{background:#11151c;border:1px solid #1f2733;padding:16px;border-radius:8px;white-space:pre-wrap}}
</style></head>
<body><a href="/">Home</a><pre>{card}</pre></body></html>"""
        return Response(html, mimetype="text/html")

    except SystemExit:
        return Response("Watch failed - NASA API unavailable", status=502, mimetype="text/plain")
    except Exception as e:
        return Response(f"Error: {str(e)}", status=500, mimetype="text/plain")

@app.route("/json")
def json_data():
    try:
        days = min(7, max(1, int(request.args.get("days", 7))))
    except (ValueError, TypeError):
        days = 7

    try:
        feed = skywatch.fetch(days)
        rows = skywatch.rows(feed, days)
        return Response(json.dumps({"days": days, "as_of": date.today().isoformat(), "rows": rows}, indent=2),
                       mimetype="application/json")
    except SystemExit:
        return Response('{"error": "NASA API unavailable"}', status=502, mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype="application/json")
