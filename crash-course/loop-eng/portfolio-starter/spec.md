# Spec: your portfolio site

Build a one-page personal portfolio: `index.html` and `style.css`, in this folder.

It must open by double-clicking the file. No build step, no npm, no framework, no CDN,
no internet. If it needs a network to look right, it is not done.

This spec is **generic**. It is the same file for everyone in the room, and you do not
edit it. Your own facts live somewhere else.

---

## What you have

| File | Who owns it | What it is |
|---|---|---|
| `spec.md` (this file) | the course | **The promises.** *What* must be true. Identical for everyone. Never edit it. |
| `.claude/skills/frontend-design/` | the course | **The craft.** *How* to build a page rather than a document. |
| `.claude/skills/page-proof/` | the course | **The proof.** `check.py` and `render.sh`, with the traps already worked out. |
| `profile.md` | **you** | **Your facts.** Your name, your work, your skills, your contact. |

**A spec is not enough on its own, and pretending otherwise is how this project failed the
first time.** This file states promises. It does not know that `ch` is not a character,
that `#767676` fails on off-white, that headless Chrome cannot render below 500px, or that
a `<ul>` you styled as a bar keeps 40px of padding you never asked for. Hand an agent only
the promises and it will produce something that keeps every one of them and is still a CV
with a stylesheet — that is not hypothetical, it is what happened here.

So: **the spec says what, the skills say how.** Both are yours; neither works alone. Read
`frontend-design` before you write a line of CSS.

Write `profile.md` first, by hand, before you start the loop. It is the only source of
truth about you that exists. **The loop may not state a single fact about you that is not
in `profile.md`.** Not one. This matters more than anything else in this spec, and Part B
is mostly about enforcing it.

Be modest and be accurate in `profile.md`. If a project was a class assignment, write
"class assignment." You will see why in Part B.

**`profile.md` has a required shape**, because `check.py` reads it too — it cannot check
that your page says your name unless it can find out what your name is. Follow the
template exactly:

```markdown
# Ayesha Khan                    <- line 1, your name, nothing else
Second-year CS student           <- line 2, your tagline

## About
Two or three true sentences about you.

## Projects
### Study Timer
A to-do list app for my web programming class. I built the timer and the CSS.

### Bus Tracker
...

## Skills
- Python
- HTML

## Contact
- ayesha@example.edu
- https://github.com/ayeshak
```

Everything below line 2 is yours to fill in. The headings are not.

---

## What "done" means

Two things, and **both** are required:

1. `python3 check.py` prints `20/20 passing` and exits 0.
2. The reviewer agent replies `PASS` on **all six** judgment promises.

Neither one alone is done. A green checker with a `FAIL` from the reviewer is not done.
A `PASS` from the reviewer with a red checker is not done.

Of the two, the second is the one that will actually stop you. Part A is a morning's work.
Part B is the job.

This is unusual, and it is the whole point of the project. Read "Why this spec has two
halves" at the bottom once you have finished.

---

## How this gets built: seven phases

You are not one agent doing everything. You are a **pipeline**. Each phase has one job, one
agent, and one artifact it hands to the next. No phase starts from nothing, and no phase
has to hold the whole job in its head.

| # | Phase | Agent | Reads | Writes | Done when |
|---|---|---|---|---|---|
| 0 | Ground truth | `profile-extractor` | your source (PDF, CV, LinkedIn export) | `profile.md` | it matches the template above |
| 1 | The design decision | `design-director` | `profile.md` | `design.md` | one sentence, plus tokens that satisfy M6, M7 and M13 |
| 2 | The words | `content-writer` | `profile.md`, `design.md` | `content.md` | every checkable fact traces to `profile.md` |
| 3 | The build | `frontend-builder` | `design.md`, `content.md` | `index.html`, `style.css` | `python3 check.py` says **20/20** |
| 4 | The render | *(a command: `render.sh`)* | `index.html` | `desktop.png`, `mobile.png` | full page, both widths |
| 5 | The judgment | `reviewer` | everything, plus both screenshots | a verdict | **PASS** on J1–J6 |
| 6 | Acceptance | `check-maker` | every phase's artifact | a verdict | every phase kept its contract |

Four things about that table are the entire design.

**Phase 1 exists because of what happens without it.** A builder handed only the facts will
write CSS immediately and back into a look by accident. It will pass every mechanical check
and produce a document. So the design decision is made **first, by an agent that cannot
write CSS**, and it is written down as a *file* — one sentence, in `design.md`. That matters
twice: the builder gets a target, and in Phase 5 the reviewer can grade the page **against
the stated decision** instead of reverse-engineering one from the pixels and guessing.

**Phase 2 is separated from Phase 3 on purpose.** Writing true sentences and building a
grid are different jobs with different failure modes. An agent doing both will trade one
off against the other, and the thing it sacrifices is always the truth, because the truth
has no exit code.

**Phase 4 is a command, not an agent.** Nothing is decided there, so nothing gets to have
an opinion. Give a decision to a command wherever a command will take it.

**Phase 6 is not Phase 5 again.** The reviewer grades the *page*. The check-maker grades
the *build* — it asks whether each phase actually did its job, or whether some phase quietly
skipped its contract and the pipeline carried on regardless.

### Where a failure sends you back

A verdict is useless if it does not say who has to fix it. This is the routing table, and
it is the reason the phases are split the way they are:

| What failed | Goes back to | Because |
|---|---|---|
| any of M1–M20 | **Phase 3** — `frontend-builder` | the markup or CSS is wrong; the words and the decision are fine |
| **J1** (a false fact) | **Phase 2** — `content-writer` | somebody wrote something that is not in `profile.md` |
| **J2 / J3** (vague, generic) | **Phase 2** — `content-writer` | the words say nothing; the design is not the problem |
| **J4** (it isn't designed) | **Phase 1** — `design-director` | there is no decision, or the decision is not worth carrying out |
| **J5** (bad on a phone) | **Phase 3** — `frontend-builder` | the decision is fine; the responsive implementation is not |
| **J6** (it's a PDF clone) | **Phase 1** — `design-director` | nobody decided what this page is that a document isn't; no amount of CSS fixes that |

Read the J4 row again. A page that "looks bad" almost never gets fixed by nudging the CSS.
It gets fixed by going back to the sentence in `design.md` and admitting there wasn't one.

### The caps

Every loop here needs a limit, and nobody is watching it at 3am:

- Phase 3 ↔ Phase 4: at most **15** `check.py` attempts.
- Phase 5 → back: at most **3** full review rounds.
- If either cap is hit, **stop** and write what is still failing to `progress.md`. A loop
  that gives up loudly is worth more than one that grinds all night. You have already met a
  spec that could not be satisfied at all (see J1's note) — caps are what turn that from a
  bill into a bug report.

### The agents

They live in `.claude/agents/`, one file each, named for their phase:

```
.claude/agents/
  profile-extractor.md   Read, Write, Bash      haiku
  design-director.md     Read, Write            (inherit)   <- cannot build the page
  content-writer.md      Read, Write            (inherit)
  frontend-builder.md    Read, Write, Edit, Bash (inherit)
  reviewer.md            Read, Grep, Glob       haiku       <- READ-ONLY. no Bash.
  check-maker.md         Read, Grep, Glob, Bash haiku
```

Read that `tools:` column as the design, not as plumbing. **What an agent can reach is a
stronger statement than what its prompt asks for.** The design-director has no Edit and no
Bash, so "you do not write CSS" is not a request. The reviewer has no Bash at all — which
matters more than it looks, because a deny rule on a file does *not* stop a subprocess: an
agent holding Bash can read anything you "blocked" with `python3 -c "print(open(x).read())"`.
The only reviewer you can actually trust is one that was never handed the tool.

Two mechanical notes, because they cost real time:

- `tools:` takes **exact tool names**. `Bash(npm test*)` is *not* valid frontmatter — it is
  permission-rule syntax that does not apply here, and since Claude Code v2.1.208 an
  unresolvable entry **hard-fails the subagent launch** rather than degrading quietly.
- A `tools:` allowlist already excludes Write, Edit and every MCP tool, so
  `disallowedTools: Write, Edit` next to it is redundant. And never set `memory:` on the
  reviewer — it silently re-enables Write and Edit so the agent can keep its own notes,
  which quietly un-does the one property that makes it a judge.

---

# Part A — the mechanical promises

**A command proves these.** `check.py` reads your files and decides. It cannot be argued
with, and it has no opinion about whether your site is any good.

### M1 — The five sections exist, in order

The page has a `<section>` with each of these `id`s, appearing in this order:
`hero`, `about`, `projects`, `skills`, `contact`.

Extra sections of your own are welcome. These five are the floor, not the ceiling.

**Accept when:** all five ids are present on `<section>` elements, and they appear in the
document in exactly that order.

> **These five ids are addresses, not an outline.** Read them as the minimum a visitor must
> be able to reach and link to — not as the shape of your page. If your page is these five
> headings stacked top to bottom in this order, you have built a CV's table of contents,
> and **J6 will fail you for it.** That is not a hypothetical: an earlier build of this very
> spec did exactly that, passed all 16 checks it then had, and was unmistakably a LinkedIn PDF with a
> stylesheet. The ids are where things live. What the page *is* remains your problem.

### M2 — The page says who it is

A non-empty `<title>` naming you, and `<html lang="...">` is set.

**Accept when:** `<title>` contains the name on line 1 of `profile.md`, and `lang` is
non-empty.

### M3 — One h1, no skipped heading levels

Exactly one `<h1>`. Heading levels never jump (no `<h2>` followed by `<h4>`).

**Accept when:** exactly one `h1`, and every heading is at most one level deeper than the
last.

### M4 — It works on a phone

A responsive viewport meta tag is present.

**Accept when:** a `<meta name="viewport">` exists whose content sets `width=device-width`
and an `initial-scale` of 1. (`1` and `1.0` are both fine — a spec that fails correct work
is a broken spec.)

### M5 — Every image declares its alt text

Every `<img>` has an `alt` attribute. A **missing** `alt` is always a failure.

`alt=""` is not a mistake — it is the correct, standard markup for an image that is purely
decorative, and a screen reader is supposed to skip it. So `alt=""` is allowed, but only
when the tag also carries `aria-hidden="true"`, which proves the emptiness was a decision
and not an oversight.

Images inside `hero` and `projects` are content — your face, your work. They are never
decorative.

**Accept when:** every `<img>` has an `alt` attribute; every `alt=""` also has
`aria-hidden="true"`; and every `<img>` inside `#hero` or `#projects` has a **non-empty**
`alt`.

### M6 — The colours are declared as tokens

`style.css` declares a `:root` block defining at least `--fg`, `--bg`, and `--accent` as
hex colours. Everywhere else in the stylesheet, colours are used **only** by name.

Outside `:root`, **no literal colour of any form may appear** — not hex, not `rgb()`, not
`hsl()`, not a named colour like `gray`. Every one is `var(--token)`.

```css
:root { --fg: #1a1a1a; --bg: #ffffff; --accent: #0b5fff; }
body  { color: var(--fg); background: var(--bg); }   /* yes */
h1    { color: #333; }                               /* no — hex outside :root */
p     { color: rgb(153,153,153); }                   /* no — still a literal colour */
a     { color: gray; }                               /* no — a name is a literal too */
```

**Accept when:** `:root` defines `--fg`, `--bg`, and `--accent` as hex; and outside the
`:root` block, no hex, `rgb(`, `hsl(`, or CSS named colour appears in any declaration.

*(This one exists only so that M7 is possible at all — and it has to close every hole, not
just the obvious one. Ban hex alone and `color: gray` walks straight through, leaving M7
solemnly verifying three tokens your text never uses. See the note at the bottom.)*

### M7 — The text is readable

Body text against its background meets **WCAG AA: a contrast ratio of at least 4.5:1**.
Large text (18pt+, or 14pt+ bold) needs at least 3:1.

This is not a matter of taste. It is arithmetic, fixed by the standard:

```
ratio = (L1 + 0.05) / (L2 + 0.05)        L1 = lighter relative luminance, L2 = darker
L     = 0.2126*R + 0.7152*G + 0.0722*B   each channel first linearised:
        c <= 0.04045  ->  c / 12.92      else  ((c + 0.055) / 1.055) ** 2.4
```

Black on white is 21:1. `#767676` on white is 4.54:1 — a pass, barely. `#999999` on white
is 2.85:1 — a fail, and it is exactly the shade that looks tasteful to a designer and
locks out a reader with low vision.

**Do not reuse those numbers. Compute your own.** A ratio is a property of a *pair*, never
of a colour. `#767676` passes at 4.54:1 on pure white and **fails at 4.17:1 on an off-white
like `#F7F5EF`** — the same grey, the same check, opposite verdicts, because the other half
of the pair moved. Every "accessible grey" list on the internet is quietly assuming a
background it never names. Compute the pair you are actually shipping.

**Accept when:** `--fg` on `--bg` is ≥ 4.5:1, and `--accent` on `--bg` is ≥ 4.5:1.

*(Checking the declared stylesheet rather than the rendered pixels is not a shortcut —
W3C offers "the underlying markup and stylesheets" as a valid basis for this criterion,
and specifically discourages sampling rendered pixels. This check is conformant, which is
rare for anything on this rung.)*

### M8 — Nothing is a placeholder

No `lorem ipsum`. No `TODO`. No `Your Name Here`, `example.com`, `johndoe`, `#`-only
hrefs, or `<img src="placeholder.jpg">`.

**Accept when:** none of the banned placeholder strings appear in either file.

### M9 — Every link goes somewhere

Internal links (`href="#about"`) point at an id that exists. Every file referenced —
image, stylesheet — exists on disk.

**Accept when:** no internal link and no asset path is dangling.

*(External links are checked for shape only, not followed. This spec is offline.)*

### M10 — It is genuinely offline

No `<script src="http...">`, no `<link href="http...">`, no `@import url(http...)`,
no Google Fonts. Fonts come from the system stack.

**Accept when:** no `http://` or `https://` appears in any `src`, `href` of a `<link>`,
or `@import`.

### M11 — The sections are not empty

This is the one that stops the laziest cheat, so it has to be countable. "Two projects"
is not countable until the spec says what a project *is* — so each row below names the
markup that carries it. Use these elements.

| Section | Must contain | Minimum |
|---|---|---|
| `hero` | an `<h1>` and a `<p>` | the `<h1>` **contains** the name on line 1 of `profile.md`; a `<p>` of ≥ 4 words says what you do. **Their order inside the hero is yours.** |
| `about` | prose | ≥ 40 words of visible text |
| `projects` | one `<article>` per project | **one per `###` under `## Projects` in `profile.md`**, each with an `<h3>` and ≥ 25 words |
| `skills` | a `<ul>` | **one `<li>` per skill in `profile.md`** — all of them |
| `contact` | links | ≥ 1 `<a>` with an `href` of `mailto:` or `https://` |

Words are counted from visible text only — the contents of `<script>`, `<style>`, and
attributes do not count.

**Accept when:** every row above is satisfied.

*(Look hard at the projects and skills rows, because they are **not** fixed numbers, and an
earlier draft of this spec had them as "≥ 2 projects" and "≥ 5 skills". That draft was
broken, and it broke on the first real person it met — a profile with three skills on it.*

*Follow the arithmetic. M11 demands five skills. `profile.md` supplies three. J1 forbids
naming a technology the profile does not support. So: add two → J1 fails → remove two →
M11 fails → forever. Not a failure. A loop, all night, on a spec that cannot be satisfied
by any page at all.*

*The rule underneath, and it is the one to keep: **a minimum on prose is safe; a minimum on
facts is not.** You can always write forty honest words about someone. You cannot write a
fifth honest skill for a person who has three. So any mechanical check that counts **facts**
must take its number **from the source of truth**, never from a number a spec author liked.
The moment a quota and the truth disagree, the loop is asked to choose, and it will choose
the quota — that is the only one with an exit code.)*

### M12 — The page actually renders

The page loads in a real browser with no console errors — and, in doing so, produces the
screenshot that Part B's reviewer needs to do its job.

**Accept when:** a headless Chrome render writes a screenshot and logs no `CONSOLE`
errors.

*(This is the weakest check in Part A, and it is here for a reason beyond itself: it is
the bridge. The mechanical rung renders the page and hands the image to the judgment rung.
M12 is where Part A stops being able to help you and goes to fetch someone who can.)*

### M13 — Type and space come from scales

Colours are not the only thing that should be tokens. Sizes too.

`:root` declares a **type scale** (`--text-sm`, `--text-base`, `--text-lg`, `--text-xl`…)
and a **spacing scale** (`--space-1`, `--space-2`, `--space-3`…). Outside `:root`, there
are no magic numbers: every `font-size`, `margin`, `padding`, and `gap` is a `var(--…)`,
a `0`, or a percentage.

This is the M6 trick again. A design where every measurement is one of eight deliberate
values looks composed. A design where every measurement was typed from memory in the
moment looks like a document. The scale is what makes the difference mechanical.

**Accept when:** `:root` declares at least 4 `--text-*` and at least 4 `--space-*` tokens;
and outside `:root`, no `font-size`, `margin`, `padding`, or `gap` uses a raw `px`/`rem`/`em`
length.

### M14 — The text is a comfortable measure

Body copy sits between **45 and 75 characters** per line, `line-height` is at least
**1.5**, and the base font size is at least **16px**. Below 45ch the eye jumps; past 75ch
it loses the line on the way back.

The constraint is on the **prose**, not on the page. Declare it once as `--measure` and
apply it to the text blocks. Do **not** put it on `<body>`: that squeezes the whole layout
into one narrow column, which is J4's first and worst failure. A wide page with a narrow
column of text inside it is the point.

**`ch` is not a character.** This is the trap, and it is worth the paragraph. The `ch` unit
is the advance width of the digit `0`, and in almost every proportional font the average
glyph is perhaps 30% narrower — so `max-width: 66ch` does **not** give you 66 characters
per line. Measured on this project's own page it gives **88–94**, which is far outside the
45–75 this promise is about. `47ch` measures at **56–69**: inside. The rule of thumb is
that your `ch` token lands around **0.7×** the characters you actually get, but the real
answer depends on your font, so measure yours.

**Accept when:** the rendered prose is **45–75 characters per line, measured** — not
declared; the body `line-height` is ≥ 1.5; and the base `font-size` is ≥ 1rem.

*(An earlier draft of this check accepted any `--measure` between `45ch` and `75ch`, which
sounds like the same thing and is not. That range renders roughly 66–110 characters, so
most of what the checker blessed **violated the promise the checker existed to keep** —
and a page at `66ch` passed M14 while sitting 20 characters outside it. This is the whole
subject of this spec, found inside this spec: a check that is green for the wrong reason
is worse than no check, because it ends the argument. The fix is not a cleverer threshold.
It is to measure the thing you promised instead of the thing that was easy to read off the
stylesheet.)*

### M15 — A keyboard user can see where they are

Some people navigate with the Tab key and never touch a mouse. If you remove the focus
ring and put nothing back, the page becomes unusable for them — and removing it is the
single most common thing a generated stylesheet does.

**Accept when:** `style.css` contains a `:focus-visible` rule that sets an `outline` or a
`box-shadow`, and no rule sets `outline: none` without replacing it.

### M16 — Nothing runs off the side of a phone

Rendered in a **390 px-wide viewport**, the page does not scroll sideways. No element's
right edge extends past the viewport.

**Accept when:** at 390 px, `document.scrollWidth` equals the viewport width, and no
element's bounding rectangle extends past it.

### M17 — A visitor can navigate it

The page carries a persistent navigation: a `<nav>` whose links point at the section ids on
this page. Paper has no nav because paper cannot jump.

**Accept when:** a `<nav>` exists containing ≥ 3 in-page links (`href="#…"`), every one
resolving to an id that exists, and it is `position: fixed` or `position: sticky`.

### M18 — It responds to being used

The page reacts. Somewhere in `style.css` there are hover states, focus states, and
transitions — the mechanical residue of a thing that answers back.

**Accept when:** `style.css` declares ≥ 3 `:hover` rules, ≥ 1 `:focus-visible` rule, and
≥ 3 `transition` or `animation` declarations.

### M19 — The hero uses the viewport

The hero is sized to the screen it is opened on, not to a sheet of A4. It uses viewport
units, and the page's largest type scales with the viewport.

**Accept when:** the hero rule sets a `min-height` in `svh`/`dvh`/`vh`, and the largest type
token uses `clamp()` or a viewport unit.

### M20 — Motion is optional

Everything M18 asks for hurts somebody. Vestibular disorders make parallax and slide-ins
genuinely painful, so a page that moves must offer a way to not move.

**Accept when:** `style.css` contains a `@media (prefers-reduced-motion: reduce)` block that
disables the animations and transitions M18 required.

*(Read M17–M20 with a cold eye, because they are **proxies and they are gameable**. A `<nav>`,
three `:hover` rules and a `clamp()` do not make a website — you could bolt all four onto the
CV that started this and go green. They raise the floor; they do not reach the bar. The
question "is this a website or a printout?" has no exit code, and that is precisely why **J6**
exists and why a person still has to look. What Part A can honestly do is make the *absence*
of a website impossible to miss. It cannot make the presence of one true.)*

*(Two traps live in this check, and both cost real time to find.*

*First: **headless Chrome cannot render narrower than 500 px** on macOS. `--window-size=390`
is silently clamped to 500 and the screenshot is simply cropped — so a page that is
perfectly fine looks catastrophically broken, with every line sliced off at the right. The
tool lies, confidently. The fix is to load the page in a **390 px `<iframe>`**, which is a
real viewport and is not subject to the window minimum.*

*Second: an earlier draft of this spec put this check in Part B, claiming `scrollWidth` was
unreachable without npm. That was **wrong**. You can inject a probe script into a copy of
the page, read the number back out through `--dump-dom`, and have your answer — no install.
The check was promoted from a claim to a proof by nothing but a better idea about the
tools. Which is J5's point, arriving from the other direction: the rungs are not fixed by
nature. Where the boundary sits depends on how hard you are willing to think about what
you already have.)*

---

# Part B — the judgment promises

**No command can prove these.** A reviewer agent reads `profile.md`, your `index.html`,
and a screenshot of the rendered page, and grades each one `PASS` or `FAIL` with reasons.

A `FAIL` here names the specific line that broke the promise. "It feels generic" is not a
verdict; "the About section claims five years of experience and `profile.md` says you are
a second-year student" is.

### J1 — Every checkable fact is true

**This is the most important promise in this spec.**

The page may not assert anything **checkable** that `profile.md` does not support. A
checkable fact is one a stranger could look up and find false:

| Category | A fabrication looks like |
|---|---|
| Employer or client | "at Google" |
| Job title or role | "Senior Engineer", "Team Lead" |
| Dates and durations | "five years of professional experience" |
| Numbers, metrics, scale | "10,000 active users", "40% faster", "99.9% uptime" |
| Awards, degrees, credentials | "AWS Certified", "Dean's List" |
| Named technologies | listing Kubernetes when `profile.md` says Python |

And no **inflation**, which is the failure you will actually see. `profile.md` says "a
to-do list app for my web programming class." The page says "architected a full-stack
productivity platform serving over 10,000 users." Every word of that is a lie, and it is
the most natural sentence a language model will ever write about you.

**Elaboration is not fabrication.** You are allowed to write. You may say why you built a
thing, who it was for, what it was like, what you learned. You may have a voice. *"I built
a bus tracker so I'd stop standing outside in July"* asserts no checkable fact — it is
just a sentence with a person in it, and `profile.md` is a bullet list, not a style guide.
The page is supposed to be longer than the profile. That is the job.

What you may not do is assert something a stranger could check and find false.

**Accept when:** every **checkable** fact on the page is supported by a line in
`profile.md`, and nothing on the page overstates what that line says. Voice, motivation,
and framing are not checkable facts, and flagging them is a reviewer error.

*(Read that last sentence twice. Without it, this promise and M11 contradict each other:
M11 demands 40 words of About, `profile.md` supplies 20, and a reviewer told that every
word must trace to the profile will fail every page that satisfies M11 — forever. A loop
between two rules that cannot both be satisfied does not fail. It runs all night. This was
a real bug in an earlier draft of this spec, caught only by running it.)*

### J2 — The projects say what they actually are

Each project entry says what the thing **does** and what **you** did. A reader who has
never met you should understand the project from the card alone.

"A web app built with HTML, CSS and JavaScript" describes ten thousand projects and
therefore describes none. It is a list of your tools, not your work.

**Accept when:** every project entry names the problem it solves and your role in it, in
words specific enough that they could not be pasted onto a different project.

### J3 — The About section is about you

Not a mad-lib. "I am a passionate developer who loves to code and is eager to learn"
is a sentence that fits every human and identifies none of them.

**Accept when:** the reviewer, reading only the About section, can state one specific thing
about you that would not be true of a random classmate.

*(J3 is about **specificity**, not truth. Truth is J1's job, and it is only J1's job. Do
not fail J3 because a detail looks invented — that is a J1 finding. Fail J3 only when the
writing would fit anyone. A criterion that grades two things at once grades neither.)*

### J4 — It is designed, not merely formatted

The reviewer looks at the **screenshot**, not the source.

"Not broken" is not the bar. Anything can be not broken. The bar is that somebody
**decided** something.

FAIL if any of these is true. The first is the one you will actually hit:

- **It reads as a document, not a page.** One column of text at one width, hierarchy
  carried entirely by font-size, stacked paragraphs top to bottom. This is what a page
  looks like when no decision was made. It will pass every check in Part A.
- **No focal point.** Everything weighs the same, so the eye has nowhere to land and no
  route to follow. A stranger cannot tell in two seconds what you do.
- **No identity.** Swap the name and it is any developer's page — default font, default
  blue link, default everything. A template with your data poured in.
- **Structure not expressed.** Work entries are a *set of things*, so they should look
  like one: cards, a grid, a list with real edges — not more paragraphs.
- **Uneven rhythm.** The gaps between things vary at random and nothing aligns to
  anything.
- **Ornament instead of design.** Gradients, shadows and animation sprayed on to *look*
  designed. This is the opposite failure and it is just as bad.

**Accept when:** the reviewer can state, in one sentence, the design decision this page is
built on, and point to where the page carries it out. *"There isn't one"* is a FAIL.

### J5 — It survives a phone

The reviewer looks at a **second screenshot, rendered 390 px wide**. Most people who open
your portfolio will open it on a phone.

M16 already proved nothing *overflows*. That is not the same as the page being any good at
that size, and only one of those two questions has an exit code.

**Accept when:** at 390 px the page looks like it was **meant** to be seen at that size —
not like the desktop page squeezed thin. Type still has a hierarchy, the gaps still have a
rhythm, and whatever carries the design on desktop still carries it here.

*(Look at how mobile split across the two rungs. "Does it run off the edge" is arithmetic:
`scrollWidth` versus viewport width, an exit code, M16. "Is it designed for a phone" is a
judgment nobody can compile. The same feature, cut cleanly in half by the only question
that matters — can a command decide this? **Rung 2 is not the set of things that are
objective. It is the smaller set of things you can objectively reach with the tools you
actually have.** So before you accept that something belongs on rung 3, check that you are
not just holding your tools wrong.)*

### J6 — It could not have been a PDF

**This is the promise this spec forgot, and forgetting it cost a whole build.**

A CV is a document: fixed, linear, printable, finished. A website is not a document. If
your page would lose **nothing** by being exported to PDF and emailed, you did not build a
website. You built a CV with a stylesheet, and the person opening it can tell instantly.

FAIL if the page is a transcription of the source:

- **The source's structure became the page's structure.** A LinkedIn export has Summary,
  Experience, Education, Certifications, Skills. If your page is those blocks stacked in
  that order, the PDF designed your page and you typed it in.
- **Nothing responds.** No navigation, no hover state, no focus state that does anything,
  nothing that reacts to being used. Paper doesn't react either.
- **Nothing moves.** No transition, no reveal, no state change. (Motion for its own sake is
  J4's ornament failure — motion that *shows* something is not.)
- **The viewport is ignored.** The page is an A4 sheet scrolled. A hero that is a headline
  and a paragraph is a document's title page.
- **A ledger of dates.** Roles-with-dates in a sidebar is the single clearest tell. It is a
  résumé component. It exists because paper cannot link, expand, or reorder.
- **Print-scaled type.** Body text and headings within a few points of each other, because
  that is what a printer's constraints produced. A screen has no such constraint.

**Accept when:** you can name one thing the page does that **paper cannot do** — and it is
load-bearing, not a decoration bolted on afterwards.

*(The honest history: this spec passed a build that was, unmistakably, a LinkedIn PDF in
HTML — a clean sweep of the 16 mechanical checks it then had, PASS on all five judgment
promises that then existed, ACCEPTED by the acceptance
gate. A human took two seconds to see it. Not one of those gates asked the question above,
because it was not written down anywhere, and **an agent optimises what you wrote, not what
you meant**. J4 already said "it reads as a document, not a page" — and that was not enough,
because a reviewer holding a page that came from a CV has no way to know the CV was the
problem. The requirement has to name the source and forbid transcribing it. Note also what
this criterion's arrival did to M1: five sections named hero/about/projects/skills/contact
**are** a CV's table of contents. The spec was specifying the failure and then asking the
reviewer to catch it.)*

---

## The rules

These exist because a loop optimising for a green checker will find every one of them.

- **An empty section is not a section.** Passing M1 with five empty headings is a failure
  of the spec, not a satisfaction of it.
- **Deleting content to make a check pass is a failure, not a fix.** If a link is broken,
  fix the link. Removing the link also makes M9 pass, and it is cheating.
- **Never invent a fact to fill a gap.** If `profile.md` is thin, the page is short. A
  short true page beats a full false one, every time. If something is missing, say so and
  stop — do not write the missing thing yourself.
- **The checker is not the customer.** It is a smoke alarm. It cannot smell dinner.

---

## Why this spec has two halves

You have written a spec before. That one — the Wordle scorer — had one half, because
every promise in it could be proved by a command: `score("ABBEY", "BUBBY")` returns
`"YXGXG"`, or it does not. There is no third option, and nobody's opinion is involved.

A website is not like that, and pretending otherwise is where people go wrong.

Here is what makes it worth building. Write the mechanical checker you would write first —
the obvious one. Structure, headings, alt text, contrast, links, placeholders: everything
in Part A **except M11**. That is a genuinely good checker, and every check in it is
correct.

Now point it at a page with five empty headings and nothing else — no text, no images, no
links. It scores **perfectly**. Not by accident, and not because the checks are badly
written:

- contrast is a flawless 21:1 — because there is no styling to get wrong
- every image has alt text — because there are **no images**
- zero broken links — because there are **no links**
- no placeholder text — because there is **no text**

Every number is at its best **because the page is empty**. Adding a real photo, a real
link, a real paragraph can only make those numbers worse. So that checker does not merely
fail to catch the empty page — **it prefers it**. An empty page is the best score it can
give, and every honest thing you do costs you points.

That is why M11 exists, and M11 is where it gets interesting. Add a word count, and the
empty page dies — so the next-laziest move is lorem ipsum. Ban lorem ipsum in M8, and the
next move is fluent, plausible, generic filler: *"I am a passionate developer with a
strong foundation in modern web technologies."* Forty words. Not a placeholder. Not empty.
Perfectly green. And it says nothing, and some of it may not even be true.

You cannot write the check that catches that sentence. There is no regular expression for
"this is hollow," and no exit code for "this is a lie about you." Each mechanical check
you add does not remove the cheat — it **promotes** it to a more sophisticated one, until
the cheats climb out of reach of every command you could write.

And the mechanical half is not only blind in one direction — it is wrong in both. Look
again at M5. The obvious version of that check is "every image has non-empty alt text,"
which is what most tutorials teach, and it is **wrong**: `alt=""` is the *correct* markup
for a decorative image. A checker enforcing the obvious rule fails good work and demands
you break it. So rung 2 waves the empty page through *and* punishes the accessible one.
Every extra clause we bolted on to fix that — the `aria-hidden` pairing, the
hero-and-projects carve-out — is judgment, hand-compiled into a rule at some cost, that a
person would have applied for free and for nothing.

That is the wall. Part B is what lives on the other side of it, and a reviewer that reads
your `profile.md` and your screenshot is the only thing standing there.

Which is also the honest reason this project is worth your time. The Wordle scorer taught
you that a checker cannot convince itself the work is fine. This one teaches you the
harder half: **what to do when no such checker exists.** Most real work — every document,
every design, every page you will ever ship to another human — lives here, on the far side
of that wall, where the only checkers available are a partial proof and a second opinion.
