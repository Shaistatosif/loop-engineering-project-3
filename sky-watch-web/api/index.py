"""Sky Watch — Vercel serverless function.

A Flask app that wraps the skywatch.py script and exposes it on the web:
  GET /              → beautiful landing page explaining the project
  GET /watch         → the live forecast (text card)
  GET /watch?days=1  → a shorter window
  GET /json          → raw data as JSON
  GET /api/skywatch  → API endpoint returning JSON

Reads NASA_API_KEY from the Vercel environment (optional — falls back to DEMO_KEY).
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

# Bring the bundled skywatch.py into scope. Vercel sets the working directory
# to the project root, so we add the repo's skills folder to sys.path.
SKILL_SCRIPT = Path(__file__).resolve().parent.parent.parent / \
    "crash-course" / "loop-eng" / "sky-watch" / ".claude" / "skills" / \
    "sky-watch" / "scripts" / "skywatch.py"

# If the bundled script is missing (e.g. running a slim deploy), use a local copy.
if not SKILL_SCRIPT.exists():
    SKILL_SCRIPT = Path(__file__).resolve().parent / "skywatch.py"

sys.path.insert(0, str(SKILL_SCRIPT.parent))

# Import the functions we need from the existing script — do not reimplement.
import skywatch  # type: ignore  # noqa: E402

from flask import Flask, Response, request  # noqa: E402

app = Flask(__name__, template_folder="../templates", static_folder="../static")


@app.route("/")
def landing():
    """Serve the project landing page from templates/index.html."""
    return _render_template("index.html", today=date.today().isoformat())


@app.route("/watch")
def watch():
    """The live watch card, rendered as a styled page."""
    try:
        days = _parse_days(request.args.get("days"))
    except ValueError as e:
        return Response(str(e), status=400, mimetype="text/plain")
    try:
        feed = skywatch.fetch(days)
        if "error" in feed:
            return Response(
                f"NASA returned an error: {feed['error']}\n"
                "If this is a rate limit, set NASA_API_KEY in Vercel env.",
                status=502,
                mimetype="text/plain",
            )
        rows = skywatch.rows(feed, days)
        card_text = skywatch.card(rows, days)
        html_card = skywatch.html_card(rows, days)
    except SystemExit as e:
        return Response(f"Watch failed: code {e.code}", status=502,
                        mimetype="text/plain")

    fmt = request.args.get("format", "html")
    if fmt == "json":
        return Response(
            json.dumps({"days": days, "rows": rows}, indent=2),
            mimetype="application/json",
        )
    if fmt == "card":
        return Response(card_text, mimetype="text/plain; charset=utf-8")
    # default: embed the script's own HTML card into our page
    return _render_template(
        "watch.html",
        days=days,
        today=date.today().isoformat(),
        card=card_text,
        html_card=html_card,
        n_rows=len(rows),
    )


@app.route("/json")
def json_endpoint():
    return _json_data(_parse_days(request.args.get("days", "7")))


@app.route("/api/skywatch")
def api_skywatch():
    return _json_data(_parse_days(request.args.get("days", "7")))


# ---- helpers ------------------------------------------------------------

def _parse_days(raw):
    if raw is None:
        return 7
    try:
        n = int(raw)
    except ValueError:
        raise ValueError(f"--days needs a number, got {raw!r}")
    if not 1 <= n <= 7:
        raise ValueError(f"--days must be between 1 and 7, got {n}")
    return n


def _json_data(days):
    try:
        feed = skywatch.fetch(days)
        if "error" in feed:
            return Response(
                json.dumps({"error": feed["error"]}, indent=2),
                status=502,
                mimetype="application/json",
            )
        rows = skywatch.rows(feed, days)
        return Response(
            json.dumps({"days": days, "as_of": date.today().isoformat(),
                        "rows": rows}, indent=2),
            mimetype="application/json",
        )
    except SystemExit as e:
        return Response(
            json.dumps({"error": f"watch failed (code {e.code})"}, indent=2),
            status=502,
            mimetype="application/json",
        )


def _render_template(name, **ctx):
    """Tiny template loader — no Jinja needed for two pages."""
    path = Path(app.template_folder) / name
    html = path.read_text(encoding="utf-8")
    for key, val in ctx.items():
        html = html.replace("{{ " + key + " }}", str(val))
    return Response(html, mimetype="text/html; charset=utf-8")


# Vercel's Python runtime looks for `app` or a `handler` function.
handler = app
