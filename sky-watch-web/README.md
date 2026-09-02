# Sky Watch — Vercel Deployment

A live web app wrapping the [Sky Watch script](../crash-course/loop-eng/sky-watch/) as a
Vercel serverless function. The forecast is rebuilt on every request from NASA's
near-Earth object feed — no caching, no guessing.

## Endpoints

| Path                       | What it returns                              |
| -------------------------- | -------------------------------------------- |
| `/`                        | Landing page (HTML)                          |
| `/watch`                   | 7-day watch, HTML card (default)             |
| `/watch?days=1`            | Today only                                   |
| `/watch?format=json`       | Watch data as JSON                           |
| `/watch?format=card`       | Plain-text card (what `/loop` uses)          |
| `/json`                    | Raw rows as JSON                             |
| `/api/skywatch?days=7`     | JSON API                                     |

## Local dev

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=api/index.py
flask run
```

## Deploy

1. Push this folder to GitHub (already done in `loop-engineering-project-3`).
2. In Vercel → **Add New Project** → import the repo.
3. Set **Root Directory** to `sky-watch-web`.
4. (Optional) Add `NASA_API_KEY` in **Environment Variables** to avoid the
   rate-limited `DEMO_KEY`.
5. Deploy. Vercel gives you a public URL like
   `https://loop-engineering-project-3.vercel.app`.

## Files

```
sky-watch-web/
├── api/
│   ├── index.py        # Flask serverless function (the routes)
│   └── skywatch.py     # local copy of the script (also used as a fallback)
├── templates/
│   ├── index.html      # landing page
│   └── watch.html      # watch page (embeds the script's HTML card)
├── vercel.json         # Vercel config — points routes at api/index.py
├── requirements.txt    # just Flask
└── README.md
```
