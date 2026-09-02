#!/bin/bash
# render.sh — produces the screenshots the reviewer grades.
#
# THREE traps this works around, each of which silently corrupts a review:
#
#  1. Chrome clamps --window-size to a ~500px minimum on macOS, so the phone view must be
#     rendered inside a 390px <iframe>, which is a real viewport and ignores the minimum.
#
#  2. A fixed screenshot height CROPS the page, and the reviewer then grades only the slice
#     it can see. Worse, a maker agent notices and shortens its layout to fit the window.
#     So we measure scrollHeight first and shoot the full page.
#
#  3. Fixes 2 and 1 BREAK viewport units. To shoot a full page you set the window to the
#     page height (say 3700px) — and then `min-height: 100svh` on the hero resolves to
#     3700px, so the hero swallows the whole page and the content floats in a void. The
#     screenshot is not the page anyone will ever see. So for the full-page shot we pin
#     #hero to FOLD (the real viewport height) — reproducing the layout a visitor gets at
#     that viewport, then capturing the entire scroll. This is what a browser automation
#     protocol calls captureBeyondViewport; we are doing it by hand, with no npm.
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
D="${1:-site}"
ABS="$(cd "$D" && pwd)"
FOLD=900          # the viewport height vh/svh units must resolve against
MFOLD=844         # a phone's

# --force-prefers-reduced-motion is the fourth trap's fix: scroll-reveals hold content at
# opacity:0 until an observer fires, so a still camera photographs an EMPTY page and the
# reviewer grades a blank. Forcing reduced motion trips the @media block M20 already
# requires, which lands everything in its final state. Not a cheat — it is exactly the page
# a reduced-motion visitor sees, and it is the accessible view. M20 pays for itself here.
shoot () { # $1=srcfile $2=w $3=h $4=out
  "$CHROME" --headless --disable-gpu --hide-scrollbars --allow-file-access-from-files \
    --force-prefers-reduced-motion \
    --virtual-time-budget=2500 --window-size=$2,$3 --screenshot="$4" "file://$1" 2>/dev/null
}

# --- the fold: what a visitor actually opens, at a true viewport
shoot "$ABS/index.html" 1280 $FOLD "$D/fold.png"

# --- full page: hero pinned to the real fold so svh is honest, then capture everything
python3 - "$ABS" "$FOLD" <<'PY'
import sys, re
abs_, fold = sys.argv[1], sys.argv[2]
h = open(f"{abs_}/index.html").read()
pin = f'<style id="_pin">#hero{{min-height:{fold}px !important}}</style>'
probe = '<script>window.addEventListener("load",function(){document.title="H="+document.documentElement.scrollHeight})</script>'
open(f"{abs_}/_full.html","w").write(h.replace('</head>', pin+'</head>').replace('</body>', probe+'</body>'))
PY
H=$("$CHROME" --headless --disable-gpu --window-size=1280,$FOLD --virtual-time-budget=2000 \
     --dump-dom "file://$ABS/_full.html" 2>/dev/null | grep -o 'H=[0-9]*' | head -1 | cut -d= -f2)
H=${H:-2400}
shoot "$ABS/_full.html" 1280 $H "$D/desktop.png"
rm -f "$ABS/_full.html"

# --- phone: a true 390px viewport inside an iframe, hero pinned to a phone's fold
#     TWO bugs lived here and both produced a silently WRONG review:
#     (a) `open(p,"w").write(open(p).read()...)` truncates the file before it is read, so the
#         frame was written EMPTY and every mobile.png was a blank white image. J5 is graded
#         on this shot: a blank page was being passed. Read first, then write.
#     (b) the height was measured at a 520px window but rendered in a 390px iframe. Narrower
#         is taller, so the shot cropped ~14% off the bottom. Measure at the width you render.
python3 - "$ABS" "$MFOLD" <<'PY2'
import sys
abs_, fold = sys.argv[1], sys.argv[2]
h = open(f"{abs_}/index.html").read()
pin = f'<style id="_pin">#hero{{min-height:{fold}px !important}}</style>'
open(f"{abs_}/_m.html", "w").write(h.replace('</head>', pin + '</head>'))
# probe INSIDE a 390px frame — the only way to learn the true 390px height
open(f"{abs_}/_probe.html", "w").write(
 '<!doctype html><meta charset=utf-8>'
 '<style>html,body{margin:0}iframe{width:390px;height:844px;border:0;display:block}</style>'
 '<iframe id=f src="_m.html"></iframe>'
 '<script>document.getElementById("f").addEventListener("load",function(){'
 'document.title="H="+Math.max(this.contentDocument.body.scrollHeight,'
 'this.contentDocument.documentElement.scrollHeight);});</script>')
PY2
MH=$("$CHROME" --headless --disable-gpu --allow-file-access-from-files --force-prefers-reduced-motion \
      --window-size=520,900 --virtual-time-budget=3000 --dump-dom "file://$ABS/_probe.html" 2>/dev/null \
      | grep -o 'H=[0-9]*' | head -1 | cut -d= -f2)
MH=${MH:-3000}
python3 - "$ABS" "$MH" <<'PY2'
import sys
abs_, mh = sys.argv[1], sys.argv[2]
open(f"{abs_}/_mframe.html", "w").write(
 '<!doctype html><meta charset=utf-8>'
 '<style>html,body{margin:0;background:#111}'
 f'iframe{{width:390px;height:{mh}px;border:0;display:block}}</style>'
 '<iframe src="_m.html"></iframe>')
PY2
shoot "$ABS/_mframe.html" 400 "$MH" "$D/mobile.png"
rm -f "$ABS/_probe.html"
rm -f "$ABS/_m.html" "$ABS/_mframe.html" "$ABS/shot.png"
echo "rendered $D/fold.png (1280x$FOLD), $D/desktop.png (full ${H}px), $D/mobile.png (390x${MH}, true viewport)"
