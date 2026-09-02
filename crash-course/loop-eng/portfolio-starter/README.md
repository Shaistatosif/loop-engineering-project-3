# Build your portfolio — from a spec

You are going to build a personal portfolio website. You are not going to write it by hand,
and you are not going to prompt an agent turn by turn until it looks okay. You are going to
**state what "done" means, and let a loop reach it.**

Everything here is the spec, the craft, and the proof. Nothing here is a finished site —
deliberately. If a worked example lived in this folder, your agent would read it and copy
it, and you would learn nothing. The blank page is the point.

## Start

```sh
python3 check.py site
```

It refuses. Read what it says: there is no `site/profile.md`, so there is nothing to check
against. That refusal is the first thing this project teaches — the checker does not grade
your page against good taste, it grades it against **your facts**, and no facts exist yet.

Once `profile.md` exists, the same command answers **6/20** on an empty stub. Look at what
already passes and ask why: an empty page is the checker's favourite page. That is the
second thing this project teaches, and it is the reason Part B of the spec exists at all.

Then:

1. **Put your CV, résumé or LinkedIn PDF export in this folder.**
2. Open Claude Code here (`claude`), and give it a finish line:

   ```
   /goal Build my portfolio in site/ from my-cv.pdf, following spec.md. Done when `python3 check.py site` prints 20/20 and the reviewer agent replies PASS on all six judgment promises — show me both. Stop after 15 check attempts or 3 review rounds and write what is still failing to progress.md.
   ```

3. It will extract your facts, decide a design, write the words, build the page, and grade
   itself — over and over, without you, until that sentence is true.

### Why `/goal`, and not just "build my portfolio"

`/goal` is a **conditional loop**: it keeps working until a condition holds, instead of
stopping when the agent feels finished. Three things in that prompt earn their place, and
each is a stop:

- **A condition a command can prove.** `check.py` printing 20/20 is a fact. "The page looks
  good" is an opinion, and an agent grading its own opinion will always pass itself.
- **`show me both`.** `/goal`'s checker cannot run commands — it only reads the conversation.
  If the agent never prints the checker's output, the checker cannot confirm anything.
  Evidence has to be visible or it does not count.
- **A cap.** `/goal` has no built-in give-up. Without "stop after 15 attempts" a loop chasing
  a condition it cannot reach will chase it all night, and you will pay for every round.

The reviewer clause is the fourth stop, and the important one: the agent that built the page
is not the agent that approves it.

## What's here

| Path                              | What it is                                                                               |
| --------------------------------- | ---------------------------------------------------------------------------------------- |
| `spec.md`                         | **The promises.** 20 things a command can prove, 6 only a person can judge. Read it all. |
| `.claude/skills/frontend-design/` | **The craft.** How to build a page and not a document. Read before any CSS.              |
| `.claude/skills/page-proof/`      | **The proof.** How to run the checker and render honest screenshots.                     |
| `.claude/agents/`                 | **The pipeline.** Six agents, one job each. The spec explains why they are split.        |
| `check.py`                        | The mechanical checker. `python3 check.py site`                                          |
| `render.sh`                       | The camera. `./render.sh site`                                                           |
| `profile.template.md`             | The shape your `site/profile.md` must take.                                              |
| `site/`                           | Your page. Currently a stub.                                                             |

## The two rules

**Never edit `check.py` to make it pass.** That is the one unforgivable move here. If a
check is green and the page is still wrong, the check is wrong — fix the _check_, and write
down why. That is how a spec learns.

**Look at your own page.** Open it. Run `./render.sh site` and read the screenshots. A page
you have not looked at is a page you have not built. Every serious bug in this project was
found by a person looking at the thing, and never once by the thing that said 20/20.

## What "done" means

Both, or it isn't done:

```sh
python3 check.py site     # 20/20 passing, exit 0
./render.sh site          # then a reviewer grades J1-J6 on the screenshots
```

The first is a morning's work. The second is the job.

## Requirements

Python 3 and Google Chrome — both already on your machine. No npm, no install, no network,
no API key beyond the one Claude Code already uses. If your page needs the internet to look
right, it is not done.
