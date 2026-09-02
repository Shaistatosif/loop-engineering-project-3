---
name: page-proof
description: Prove a static HTML page against a spec — runs the mechanical checker and renders honest screenshots (desktop, first-fold, and a true 390px phone view) for a reviewer to judge. Use when verifying a web page, before declaring any page done, or when a screenshot of a page looks wrong.
---

# Page proof

Two rungs of verification, and knowing which is which is the whole point.

- `check.py` — **proof.** A command. It cannot convince itself the work is fine.
- `render.sh` — the **bridge.** It produces the images a human or reviewer judges.
  Everything above this line is a claim, not a proof.

## Run it

```sh
python3 check.py site      # 20/20 passing, exit 0
./render.sh site           # -> site/fold.png, site/desktop.png, site/mobile.png
```

Both live at the project root. There is one copy of each, on purpose: a bundled duplicate
drifts from the original the first time you fix a bug in one of them.

`<site-dir>` must contain `index.html`, `style.css`, and `profile.md` (the source of truth
the checker reads names and fact-counts from).

## What check.py proves, and what it cannot

It proves: structure and heading order, the title, a responsive viewport, alt-text
discipline, colour tokens, **computed** WCAG contrast, no placeholders, live links and
assets, offline-ness, non-empty sections, a clean console render, type/space scales,
**measured** characters per line, a visible focus ring, no overflow at 390px, a working
nav, hover/focus/motion, a viewport hero, and a reduced-motion escape hatch.

It cannot prove the page is good, true, or a website rather than a printout. Those are
judgment. **A green checker is where the work starts being reviewed, not where it ends.**

Two of its checks are subtler than they look:

- **M14 measures rendered characters per line, not the `ch` token.** `ch` is the width of
  `0`, so `66ch` renders ~90 characters. Checking the token would bless pages that violate
  the promise the check exists to keep.
- **M11 counts facts from `profile.md`, not from a fixed number.** A quota on facts that
  disagrees with the source of truth is unsatisfiable: the page cannot honestly invent a
  fifth skill for a person with three, so a `>= 5` rule makes the loop grind forever.
  A minimum on *prose* is safe; a minimum on *facts* is not.

## Why render.sh is 60 lines instead of one

Headless Chrome lies four different ways, and each corrupts a review silently. Two more bugs
lived in this file's own first draft — a blank `mobile.png` for every site, and a height
measured at the wrong width — so read the header comments before you trust it. The tool that
checks your work is not exempt from being checked.

1. **It will not render below ~500 CSS px** on macOS — `--window-size=390` is clamped to
   500 and the image cropped, so a fine page looks shattered. Fix: a 390px `<iframe>`.
2. **A fixed height crops the page**, and the reviewer grades a slice. Worse, a maker agent
   notices and shortens its layout to fit the camera. Fix: probe `scrollHeight`, shoot full.
3. **Fix 2 breaks `svh`/`vh`** — a 3700px window makes `100svh` a 3700px hero that eats the
   page. Fix: pin `#hero` to the real fold, then capture the whole scroll.
4. **Scroll-reveals photograph as blank** — `opacity: 0` waiting for an observer that never
   fires. Fix: `--force-prefers-reduced-motion`, which trips the page's own reduced-motion
   block. Legitimate: it is what a reduced-motion visitor sees.

Outputs: `fold.png` (1280×900, the first screen), `desktop.png` (full page), `mobile.png`
(a true 390px viewport).

## Rules

- **Never edit the checker to make it pass.** That is the one unforgivable move.
- Read the screenshot yourself before declaring done. A page you have not looked at is a
  page you have not built.
- If a check is green and the page is still wrong, the check is wrong — fix the check, and
  write down why. That is how the spec learns.
