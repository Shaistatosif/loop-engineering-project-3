#!/usr/bin/env python3
"""check.py — the mechanical rung. Python stdlib only. Usage: python3 check.py <dir>"""
from html.parser import HTMLParser
import sys, os, re, subprocess

D = sys.argv[1] if len(sys.argv) > 1 else "."
REQUIRED = ["hero", "about", "projects", "skills", "contact"]
BANNED = ["lorem ipsum", "todo", "your name here", "example.com", "johndoe", "placeholder"]
NAMED_COLOURS = ["gray","grey","red","blue","green","black","white","silver","navy","teal",
    "olive","lime","aqua","fuchsia","maroon","purple","yellow","orange","pink","brown","gold"]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

for _f in ("profile.md", "index.html", "style.css"):
    if not os.path.exists(f"{D}/{_f}"):
        print(f"\n  Can't check {D}/ — {_f} is missing.\n")
        if _f == "profile.md":
            print("  profile.md is your facts, and it is the ruler everything else is measured\n"
                  "  against: the checker reads your name from it, and counts your projects and\n"
                  "  skills from it. Nothing can be checked until it exists.\n\n"
                  f"  Copy profile.template.md to {D}/profile.md and fill it in — or point an\n"
                  "  agent at your CV and have it write one (spec.md, Phase 0).\n")
        sys.exit(2)

prof = open(f"{D}/profile.md").read()
name = prof.splitlines()[0].strip().lstrip("# ").strip()
def _sec(md, h):
    m = re.search(r'^##\s+' + h + r'\s*$(.*?)(?=^##\s|\Z)', md, re.S | re.M)
    return m.group(1) if m else ""
N_PROJECTS = len(re.findall(r'^###\s+\S', _sec(prof, 'Projects'), re.M))
N_SKILLS   = len(re.findall(r'^[-*]\s+\S', _sec(prof, 'Skills'), re.M))
html = open(f"{D}/index.html").read()
css  = open(f"{D}/style.css").read()

class P(HTMLParser):
    def __init__(s):
        super().__init__()
        s.sec_order=[]; s.ids=set(); s.stack=[]; s.cur=None; s.skip=0; s.h1text=''; s._h1=False
        s.text={}; s.h=[]; s.imgs=[]; s.title=""; s.lang=""; s.vp=None
        s.arts={}; s._art=None; s.h3={}; s.lis={}; s.links=[]; s.assets=[]; s.ext_link_tags=[]; s.navlinks=[]; s.innav=False
        s._t=False
    def handle_starttag(s, t, attrs):
        d=dict(attrs)
        if 'id' in d: s.ids.add(d['id'])
        if t=='section' and d.get('id') in REQUIRED:
            s.sec_order.append(d['id']); s.cur=d['id']; s.text[s.cur]=""
        if t=='html': s.lang=d.get('lang','')
        if t=='title': s._t=True
        if t in ('script','style'): s.skip+=1
        if t=='meta' and d.get('name')=='viewport': s.vp=d.get('content','')
        if t=='img': s.imgs.append((d, s.cur)); s.assets.append(d.get('src',''))
        if t=='link':
            if d.get('href','').startswith('http'): s.ext_link_tags.append(d['href'])
            elif d.get('href'): s.assets.append(d['href'])
        if t=='a' and 'href' in d:
            s.links.append((d['href'], s.cur))
            if s.innav: s.navlinks.append(d['href'])
        if t=='nav': s.innav=True
        if re.fullmatch(r'h[1-6]', t): s.h.append(int(t[1]))
        if t=='h1': s._h1=True
        if t=='article' and s.cur=='projects':
            s._art=len(s.arts); s.arts[s._art]=''
        if t=='h3' and s.cur=='projects': s.h3[len(s.h3)]=1
        if t=='li' and s.cur=='skills': s.lis[len(s.lis)]=1
    def handle_endtag(s, t):
        if t=='title': s._t=False
        if t=='h1': s._h1=False
        if t in ('script','style'): s.skip-=1
        if t=='section': s.cur=None
        if t=='article': s._art=None
        if t=='nav': s.innav=False
    def handle_data(s, d):
        if s._t: s.title+=d
        if s._h1: s.h1text+=d
        if s.cur and not s.skip:
            s.text[s.cur]+=d
            if s._art is not None and s.cur=='projects': s.arts[s._art]+=d

p=P(); p.feed(html)
words=lambda k: len(p.text.get(k,"").split())

# --- CSS: :root tokens + no literal colour outside :root
root_m = re.search(r':root\s*\{([^}]*)\}', css, re.S)
root_body = root_m.group(1) if root_m else ""
outside = css.replace(root_m.group(0), "") if root_m else css
outside = re.sub(r'/\*.*?\*/', '', outside, flags=re.S)
tokens = dict(re.findall(r'(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})', root_body))
lit_outside = (re.findall(r'#[0-9a-fA-F]{3,8}\b', outside) + re.findall(r'\brgba?\(', outside)
    + re.findall(r'\bhsla?\(', outside)
    + [c for c in NAMED_COLOURS if re.search(r':\s*[^;{}]*\b'+c+r'\b', outside)])

def lum(h):
    h=h.lstrip('#'); h=''.join(c*2 for c in h) if len(h)==3 else h
    def ch(c):
        c=int(c,16)/255
        return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
    r,g,b=ch(h[0:2]),ch(h[2:4]),ch(h[4:6]); return .2126*r+.7152*g+.0722*b
def ratio(a,b):
    l1,l2=sorted((lum(a),lum(b))); return (l2+.05)/(l1+.05)
def contrast_ok(fg,bg):
    if fg not in tokens or bg not in tokens: return False
    return ratio(tokens[fg],tokens[bg])>=4.5

# --- M12: render
console_err, shot_ok = [], False
if os.path.exists(CHROME):
    r=subprocess.run([CHROME,"--headless","--disable-gpu","--enable-logging=stderr","--v=1",
        f"--screenshot={D}/shot.png","--window-size=1200,900","--hide-scrollbars",
        f"file://{os.path.abspath(D)}/index.html"],capture_output=True,text=True,timeout=60)
    console_err=[l for l in r.stderr.splitlines() if ':CONSOLE:' in l]
    shot_ok=os.path.exists(f"{D}/shot.png")


# --- M13/M14/M15 helpers
props = r'(?:font-size|margin[a-z-]*|padding[a-z-]*|gap|row-gap|column-gap)'
magic = [m.group(0) for m in re.finditer(props + r'\s*:\s*[^;}]*?\d*\.?\d+(?:px|rem|em)\b', outside)]
text_toks  = re.findall(r'--text-[\w-]+\s*:', root_body)
space_toks = re.findall(r'--space-[\w-]+\s*:', root_body)
meas = re.search(r'--measure\s*:\s*(\d+(?:\.\d+)?)ch', root_body)
meas_used = 'var(--measure)' in outside
body_m = re.search(r'\bbody\s*\{([^}]*)\}', css, re.S)
body_css = body_m.group(1) if body_m else ''
lh = re.search(r'line-height\s*:\s*(\d+(?:\.\d+)?)', body_css)
bfs = re.search(r'font-size\s*:\s*(?:var\((--[\w-]+)\)|(\d+(?:\.\d+)?)rem)', body_css)
def base_rem():
    if not bfs: return 0
    if bfs.group(1):
        t = re.search(re.escape(bfs.group(1)) + r'\s*:\s*(\d+(?:\.\d+)?)rem', root_body)
        return float(t.group(1)) if t else 0
    return float(bfs.group(2))
fv = re.search(r':focus-visible[^{]*\{([^}]*)\}', css, re.S)
kills = re.findall(r'outline\s*:\s*(?:none|0)\b', css)


# --- M16: true 390px viewport via iframe probe (Chrome clamps --window-size to 500 on macOS)
overflow_ok = False
if os.path.exists(CHROME):
    frame = os.path.join(D, "_probe_frame.html")
    open(frame, "w").write("""<!doctype html><meta charset=utf-8>
<style>html,body{margin:0}iframe{width:390px;height:1400px;border:0;display:block}</style>
<iframe id=f src="index.html"></iframe>
<script>document.getElementById('f').addEventListener('load',function(){
 try{var w=this.contentWindow,d=this.contentDocument.documentElement,o=[];
 this.contentDocument.querySelectorAll('*').forEach(function(el){
   if(el.getBoundingClientRect().right>w.innerWidth+1)o.push(el.tagName);});
 document.title='W='+w.innerWidth+' S='+d.scrollWidth+' O='+(o.join(',')||'NONE');
 }catch(e){document.title='BLOCKED';}});</script>""")
    r = subprocess.run([CHROME,"--headless","--disable-gpu","--allow-file-access-from-files",
        "--window-size=520,1500","--virtual-time-budget=3000","--dump-dom",
        f"file://{os.path.abspath(frame)}"], capture_output=True, text=True, timeout=60)
    t = re.search(r'<title>W=(\d+) S=(\d+) O=(\S+)</title>', r.stdout)
    overflow_ok = bool(t) and t.group(1)=='390' and t.group(2)=='390' and t.group(3)=='NONE'
    probe_detail = t.group(0) if t else "probe failed"
    os.remove(frame)


# --- M14: measure ACTUAL chars per rendered line (ch != character)
cpl_ok = False; cpl_detail = "not measured"
if os.path.exists(CHROME):
    mp = os.path.join(D, "_m14.html")
    _h = html.replace('</body>', """<script>window.addEventListener("load",function(){
 var ps=[].slice.call(document.querySelectorAll('p')).filter(function(p){
   return p.textContent.trim().split(/\\s+/).length>15 && p.offsetParent!==null;});
 if(!ps.length){document.title='CPL=none';return;}
 var all=[];
 ps.slice(0,4).forEach(function(p){
   var t=p.firstChild; if(!t||t.nodeType!==3)return;
   var r=document.createRange(), txt=t.textContent, lines=[], last=null, start=0;
   for(var i=0;i<txt.length;i++){r.setStart(t,i);r.setEnd(t,i+1);
     var top=Math.round(r.getBoundingClientRect().top);
     if(last===null)last=top;
     if(top!==last){lines.push(i-start);start=i;last=top;}}
   lines.pop===undefined||lines.push(txt.length-start);
   all=all.concat(lines.slice(0,-1));});
 document.title = all.length ? ('CPL='+Math.min.apply(null,all)+'-'+Math.max.apply(null,all)) : 'CPL=none';
})</script></body>""")
    open(mp, "w").write(_h)
    _r = subprocess.run([CHROME,"--headless","--disable-gpu","--window-size=1280,1400",
        "--virtual-time-budget=2500","--dump-dom", f"file://{os.path.abspath(mp)}"],
        capture_output=True, text=True, timeout=60)
    _m = re.search(r'<title>CPL=(\d+)-(\d+)</title>', _r.stdout)
    if _m:
        lo, hi = int(_m.group(1)), int(_m.group(2))
        cpl_ok = lo >= 45 and hi <= 75
        cpl_detail = f"{lo}-{hi} chars/line"
    os.remove(mp)


# --- M17..M20: the mechanical residue of a website (proxies; J6 is the real gate)
nav_ok = (len([h for h in p.navlinks if h.startswith('#')])>=3
    and all(h[1:] in p.ids for h in p.navlinks if h.startswith('#') and len(h)>1)
    and re.search(r'(?:\.topbar|nav|header)[^{]*\{[^}]*position\s*:\s*(?:fixed|sticky)', css, re.S) is not None)
hovers = len(re.findall(r':hover', css))
focusv = len(re.findall(r':focus-visible', css))
moves  = len(re.findall(r'\btransition\s*:|\banimation\s*:', css))
responds_ok = hovers>=3 and focusv>=1 and moves>=3
hero_css = re.search(r'#hero\s*\{([^}]*)\}', css, re.S)
viewport_ok = (bool(hero_css) and re.search(r'min-height\s*:\s*[^;]*\b\d+(?:svh|dvh|vh)', hero_css.group(1)) is not None
    and re.search(r'--text-2xl\s*:\s*[^;]*(clamp\(|vw|svh|vh)', root_body) is not None)
rm = re.search(r'@media[^{]*prefers-reduced-motion\s*:\s*reduce[^{]*\{(.*?)\n\}', css, re.S)
reduced_ok = bool(rm) and re.search(r'animation\s*:\s*none|transition\s*:\s*none', rm.group(1)) is not None

hs=p.h
checks=[
 ("M1  five sections, in order", [i for i in p.sec_order if i in REQUIRED]==REQUIRED),
 ("M2  title names you, lang set", name.lower() in p.title.lower() and bool(p.lang)),
 ("M3  one h1, no skipped levels", hs.count(1)==1 and all(b-a<=1 for a,b in zip(hs,hs[1:]))),
 ("M4  responsive viewport", bool(p.vp) and 'width=device-width' in p.vp
      and re.search(r'initial-scale\s*=\s*1(\.0)?\b', p.vp) is not None),
 ("M5  alt text declared right", all('alt' in d for d,_ in p.imgs)
      and all(d.get('alt','').strip() or d.get('aria-hidden')=='true' for d,_ in p.imgs)
      and all(d.get('alt','').strip() for d,s in p.imgs if s in ('hero','projects'))),
 ("M6  colours are tokens only", all(t in tokens for t in ('--fg','--bg','--accent'))
      and not lit_outside),
 ("M7  contrast >= 4.5:1", contrast_ok('--fg','--bg') and contrast_ok('--accent','--bg')),
 ("M8  no placeholders", not any(b in (html+css).lower() for b in BANNED)),
 ("M9  links + assets resolve",
      all(h[1:] in p.ids for h,_ in p.links if h.startswith('#') and len(h)>1)
      and all(os.path.exists(os.path.join(D,a)) for a in p.assets if a and not a.startswith('http'))),
 ("M10 genuinely offline", not p.ext_link_tags and '@import url(http' not in css.replace(' ','')),
 ("M11 sections not empty",
      name.lower() in p.h1text.lower() and words('hero')>=len(name.split())+4
      and words('about')>=40 and len(p.arts)>=N_PROJECTS and len(p.h3)>=N_PROJECTS
      and all(len(t.split())>=25 for t in p.arts.values())
      and len(p.lis)>=N_SKILLS
      and any(h.startswith('mailto:') or h.startswith('https://') for h,s in p.links if s=='contact')),
 ("M12 renders, no console errors", shot_ok and not console_err),
 ("M13 type+space are scales", len(text_toks)>=4 and len(space_toks)>=4 and not magic),
 ("M14 45-75 chars/line MEASURED", cpl_ok and bool(lh) and float(lh.group(1))>=1.5 and base_rem()>=1.0),
 ("M15 focus-visible is styled", bool(fv) and re.search(r'outline|box-shadow', fv.group(1)) is not None
      and not kills),
 ("M16 no overflow at 390px", overflow_ok),
 ("M17 navigable (sticky nav, 3+ links)", nav_ok),
 ("M18 responds (hover/focus/motion)", responds_ok),
 ("M19 hero uses the viewport", viewport_ok),
 ("M20 reduced-motion respected", reduced_ok),
]
n=sum(1 for _,ok in checks if ok)
print(f"\n  {D}   (profile.md declares {N_PROJECTS} projects, {N_SKILLS} skills — M11 counts from there)")
DETAIL = {
 "M14 45-75 chars/line MEASURED": cpl_detail,
 "M16 no overflow at 390px": probe_detail if 'probe_detail' in dir() else '',
 "M11 sections not empty": f"about={words('about')}w, articles={[len(t.split()) for t in p.arts.values()]}w, skills={len(p.lis)}/{N_SKILLS}",
 "M7  contrast >= 4.5:1": (f"fg/bg={ratio(tokens['--fg'],tokens['--bg']):.2f} "
                           f"accent/bg={ratio(tokens['--accent'],tokens['--bg']):.2f}")
                          if all(k in tokens for k in ('--fg','--bg','--accent')) else 'tokens missing',
 "M18 responds (hover/focus/motion)": f"hover={hovers} focus-visible={focusv} motion={moves}",
}
for t,ok in checks:
    d = DETAIL.get(t, "")
    print(f"  [{'x' if ok else ' '}] {t}" + (f"   -> {d}" if d else ""))
print(f"\n  {n}/{len(checks)} passing\n")
sys.exit(0 if n==len(checks) else 1)
