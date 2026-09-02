---
name: frontend-design
description: How to design and build a static web page that is a page and not a printed document — the design decision, type/colour/space scales, layout, motion, interaction, and the traps that pass every checker and still look wrong. Use whenever building a portfolio, landing page, or any HTML/CSS a person will look at and judge.
---

# Frontend design

A checker can tell you the page is well-formed. It cannot tell you the page is any good.
This file is the part that has no exit code.

Read it before you write CSS, not after the reviewer fails you.

---

## 0. The one rule: a page is not a document

Almost every generated page fails the same way, and it is not ugliness. It is **a document
with a stylesheet**: a title, a summary paragraph, then blocks stacked top to bottom in
whatever order the source listed them. It passes every mechanical check. It is a PDF you
cannot print.

The tell is always the same — **the source's structure became the page's structure.** You
were handed a CV with Summary / Experience / Education / Skills, and you emitted exactly
that, in exactly that order, and called it a website.

Before any CSS, answer this: **what does this page do that paper cannot?** If the honest
answer is "nothing," stop. You have not started yet.

Things paper cannot do — pick the ones that serve the content, not all of them:

| Paper cannot… | So a page can… |
|---|---|
| jump | a nav that follows you and knows where you are |
| answer | hover, focus, press — state that changes because someone touched it |
| hide | a disclosure: ask for the detail instead of printing all of it |
| resize | type and layout that use the viewport they were opened in |
| move | a reveal, a transition — motion that *shows* something |
| be operated | a control: the reader changes something and learns from the result |

That last row is the strongest and the rarest. If the page's central idea is something the
reader can **push on**, you are done worrying about whether it is a website.

---

## 1. Decide one thing, in one sentence

Write the sentence before the CSS. Literally write it down.

Three examples, from three people who are not the person you are building for. They are here
to show you the **shape** of a decision, and nothing else:

> *A structural engineer:* "The page is a load path — every section visibly carries the one
> above it, and the hero is the footing everything rests on."
>
> *A translator:* "The page is bilingual down a seam: every claim in English sits beside its
> Urdu, and the seam is the only rule the layout obeys."
>
> *A bakery:* "The page is a proofing schedule — it is laid out on the clock, morning to
> night, and the thing you can buy at 4pm is where 4pm is."

**Do not reach for these. Reach past them.** They are deliberately not from software, because
a worked example in your own domain stops being an illustration and becomes the answer — you
will produce it and be unable to tell whether you derived it or remembered it. If your
decision resembles one of these, you have taken the example, not the method.

The method is one question: **what is the one structural idea in this person's own material,
and can the page be built out of it?** Read their source until you find the thing only they
have. That is the decision. It is in their words, not in this file.

A real decision:

- **comes from this person's material.** Their idea, their craft, their subject. Someone who
  teaches a model can have a page built *on* that model. Someone who ships typography can
  have a page that is a specimen. The decision should be impossible to transplant.
- **is executable.** A builder can tell whether a given rule serves it.
- **is refusable.** It rules things out. A decision that forbids nothing decided nothing.
- **is restrained.** Gradients, shadows, glows and animation sprayed on to *look* designed is
  the opposite failure, and it reads as cheaply as the document does.

If your sentence would be true of any other person's page, it is not a decision. It is a
default.

**And watch your verbs while you do it.** An earlier version of this file described a
subject's material as *"her **own** model."* The source said *"a pattern I keep coming back
to."* Using a thing is not authoring it, and one possessive pronoun invented a credential —
in the very file that teaches you not to. Finding a person's structural idea puts you *close*
to their material, which is exactly where the temptation to promote it lives. Build the page
out of their idea; do not award them a patent on it.

---

## 2. Type

**Scale, don't type numbers.** Every size is one of ~6 declared steps. Eight deliberate
values read as composed; twenty remembered values read as a document.

```css
:root {
  --text-xs:   0.72rem;
  --text-sm:   0.86rem;
  --text-base: 1.06rem;
  --text-lg:   1.35rem;
  --text-xl:   clamp(2rem, 5vw, 3.4rem);    /* fluid: uses the viewport */
  --text-2xl:  clamp(3rem, 11vw, 8.5rem);   /* the page's voice */
}
```

**Contrast of scale is the whole game.** A document's headings are a few points bigger than
its body, because a printer's constraints made that sensible. A screen has no such
constraint. If your `h1` is 2rem, you built a document. Big type is not decoration; it is
the difference between a page that speaks and a page that files.

**`ch` is not a character.** The `ch` unit is the advance width of the digit `0`, and the
average glyph is ~30% narrower. `max-width: 66ch` renders **~90 characters**, not 66.
Comfortable reading is 45–75 characters, which lands near **47ch**. Measure yours; do not
trust the unit's name.

**The measure goes on the prose, never on `<body>`.** Putting it on the body squeezes the
whole layout into one narrow column — which is the document failure, arrived at from the
other direction. The right shape is a **wide page with a narrow column of text inside it**.

```css
:root { --measure: 47ch; }
.prose, p { max-width: var(--measure); }   /* yes */
body      { max-width: var(--measure); }   /* NO — this is a Word document */
```

Line-height ≥ 1.5 for body. Tighten as type grows: a display `h1` wants ~0.9.

---

## 3. Colour

**Tokens only.** Declare every colour once in `:root`; use it by name everywhere else. Not
just hex — `rgb()`, `hsl()` and named colours like `gray` are literals too, and one stray
`color: gray` quietly defeats every contrast guarantee you thought you had.

**Compute the pair. Never borrow a number.** A contrast ratio is a property of *two*
colours, never of one. `#767676` passes at 4.54:1 on pure white and **fails at 4.17:1 on
`#F7F5EF`** — same grey, opposite verdict, because the other half moved. Every "accessible
grey" list online is assuming a background it never names.

```
L = 0.2126R + 0.7152G + 0.0722B      each channel linearised first:
    c <= 0.04045 ? c/12.92 : ((c + 0.055)/1.055) ** 2.4
ratio = (Llighter + 0.05) / (Ldarker + 0.05)      body text needs >= 4.5:1
```

`#999` on white is **2.85:1**. It looks tasteful in a mockup and locks out readers with low
vision. It is the single most common colour mistake in generated CSS.

**Give the accent one meaning and keep it.** Not "the fun colour" — *this* means that. If
the accent means human judgment, then it is on the human parts and on the focus ring, and
nowhere else. An accent used for everything means nothing, and the page reads as a template.

---

## 4. Space

A scale, same as type. And a rhythm: gaps between things should be *chosen*, not typed from
memory. Uneven rhythm is the second-most visible tell of an undesigned page.

```css
:root { --space-1: .3rem; --space-2: .6rem; --space-3: 1.1rem;
        --space-4: 2rem;  --space-5: 3.5rem; --space-6: 7rem; }
```

Generous outer padding is most of what separates a professional page from a cramped one.
`--space-6` between sections is not wasteful; it is the page breathing.

---

## 5. Layout

**Express the structure.** A set of things must *look* like a set — a grid, cards, a list
with real edges. If your three projects are three stacked paragraphs, you have told the
reader nothing about their relationship.

**Give the eye a focal point.** A stranger should know in two seconds what this person does.
If everything weighs the same, nothing is read.

**Don't put a ledger of dates in a sidebar.** Roles-with-dates in a right-hand column is the
single clearest CV tell. It exists because paper cannot link, expand, or reorder. A page can
make the same facts a **timeline you scan**, with hover, or a disclosure you open.

Modern CSS does the work; use it:

```css
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
         gap: var(--space-3); align-items: start; }
```

**Reset list padding.** A `<ul>` styled as a bar, grid or chip row keeps its default ~40px
`padding-left` and sits misaligned with everything else. No checker catches it. Every eye
does.

---

## 6. Motion and interaction

**Motion that shows something, never motion for its own sake.**

- a reveal as a section arrives (subtle: 18px and 0.7s, not a slide across the screen)
- a transition on every state you change — hover, focus, open
- one thing that *responds*, ideally the page's central idea

```css
.reveal { opacity: 0; transform: translateY(18px);
          transition: opacity .7s var(--ease), transform .7s var(--ease); }
.reveal.in { opacity: 1; transform: none; }
```

Reveal with `IntersectionObserver`, not on a timer. Vanilla, no library:

```js
var ro = new IntersectionObserver(function (es) {
  es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); ro.unobserve(e.target); } });
}, { rootMargin: '0px 0px -10% 0px' });
[].slice.call(document.querySelectorAll('.reveal')).forEach(function (n) { ro.observe(n); });
```

**Always ship the escape hatch.** Vestibular disorders make motion genuinely painful. This
is not optional politeness — and it will also save your screenshots (see §7):

```css
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation: none !important; transition: none !important; }
  .reveal { opacity: 1; transform: none; }
}
```

**Focus is not optional either.** Someone navigates with Tab and never touches a mouse.
Removing the outline without replacing it is the most common accessibility crime in
generated CSS.

```css
:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
```

---

## 7. Look at the page — and know the camera lies

You cannot judge a page from its source. Render it and **read the image**. But headless
Chrome has four traps that will each cost you an hour:

1. **Chrome will not render below ~500 CSS px** on macOS. `--window-size=390` is silently
   clamped to 500 and the shot is *cropped* — so a perfectly fine page looks catastrophically
   broken, every line sliced off. Render the phone view in a **390px `<iframe>`** instead: a
   real viewport, immune to the minimum.
2. **A fixed screenshot height crops the page**, and then you grade only the slice you can
   see. Measure `scrollHeight` first and shoot the full page.
3. **Fixing 2 breaks viewport units.** Setting the window to the page height (3700px) makes
   `min-height: 100svh` resolve to 3700px — the hero swallows the page and the content floats
   in a void. Pin the hero to the real fold height for the full-page shot.
4. **Scroll-reveals photograph as a blank page.** Content at `opacity: 0` waiting for an
   observer that never fires for a still camera. Render with `--force-prefers-reduced-motion`
   — which trips the block in §6 and lands everything in its final state. Not a cheat: it is
   exactly what a reduced-motion visitor sees.

`page-proof`'s `render.sh` handles all four. Use it rather than rediscovering them.

---

## 8. The checklist that has no checker

Look at the render and ask, honestly:

- Could this be a PDF? If yes, start over — this is not a CSS problem.
- Can a stranger tell in two seconds what this person does?
- Is there **one** decision, and can you point at where the page carries it out?
- Swap the name — is it now any developer's page? Then it has no identity.
- Does a set of things look like a set?
- Does the bottom half hold up, or does it decay into a plain list once past the hero?
- Is there anything to *do*? Anything that answers back?
- Would you send it to an employer under your own name?

The last one is the only one that matters, and it is the only one no command will ever
answer for you.
