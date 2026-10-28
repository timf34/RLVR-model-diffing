"""Render every pilot conversation to prompts.json and a readable prompts_preview.md (no API calls).

Also asserts the matching properties the design depends on, so an edit to materials.py can't silently
break them.
"""
import itertools
import json
from pathlib import Path

from materials import (CONTEXTS, PAIRS, SCORES, SYSTEM, TASKS, USERS, examples, render, render_capability,
                       render_comprehension, requester_message)

HERE = Path(__file__).parent

main = [dict(set="main", scenario=t["id"], context=c, scores=s, user=u, facts=t["facts"], **render(t, c, s, u))
        for t, c, s, u in itertools.product(TASKS, CONTEXTS, SCORES, USERS)]
comprehension = [dict(set="comprehension", scenario=t["id"], context=c, scores=s, **render_comprehension(t, c, s))
                 for t, c, s in itertools.product(TASKS, ("ordinary", "rl_framing"), SCORES)]
capability = [dict(set="capability", variant="plain" if not scored else "vs_scorer", scenario=t["id"],
                   context="none" if not scored else "ordinary", scores="none" if not scored else "title_penalised",
                   user="wants_title", facts=t["facts"], **render_capability(t, scored))
              for scored in (False, True) for t in TASKS]
# Small identical-model smoke test: conflict cells, the key contrast only.
control = [c for c in main if c["user"] == "conflict" and c["context"] in ("ordinary", "rl_framing")]

# ---- matching checks
for c in main:
    task = next(t for t in TASKS if t["id"] == c["scenario"])
    turn = c["turns"][0]
    assert requester_message(task, c["user"]) in turn
    for p in PAIRS:
        assert turn.count(p["body"]) == 2, "each announcement appears once titled, once untitled"
        assert turn.count(p["title"]) == 1
    if c["context"] in ("ordinary", "minimal_cue", "rl_framing"):
        assert turn.startswith(requester_message(task, c["user"])), "request first, verbatim, from the user"
        assert c["system"].startswith(SYSTEM)
by_key = {(c["scenario"], c["context"], c["user"], c["scores"]): c for c in main}
for t, c, u in itertools.product(TASKS, CONTEXTS, USERS):
    a, b = by_key[(t["id"], c, u, "title_rewarded")], by_key[(t["id"], c, u, "title_penalised")]
    strip = lambda s: "".join(ch for ch in s if not ch.isdigit())
    assert a["system"] == b["system"] and strip(a["turns"][0]) == strip(b["turns"][0]), "score swap changes only numbers"
for t in TASKS:
    for s in SCORES:
        titled_scores = [float(x) for x, _, titled in examples(s, t["order"]) if titled]
        plain_scores = [float(x) for x, _, titled in examples(s, t["order"]) if not titled]
        assert (min(titled_scores) > max(plain_scores)) == (s == "title_rewarded")
assert len({t["order"] for t in TASKS}) == 4, "example order counterbalanced across tasks"

cells = main + comprehension + capability
(HERE / "prompts.json").write_text(json.dumps(
    dict(main=main, comprehension=comprehension, capability=capability,
         control=[{k: c[k] for k in ("scenario", "context", "scores", "user")} for c in control]),
    indent=2, ensure_ascii=False) + "\n")


# ---- preview
def block(c, title):
    return [f"## {title}", "", "**System**", "", "```text", c["system"], "```", "", "**User**", "", "```text",
            c["turns"][0], "```", ""]


fd = lambda **k: next(c for c in main if c["scenario"] == "fire_drill" and all(c[x] == v for x, v in k.items()))
lines = ["# Rendered pilot prompts (preview, v1)", "",
         f"main: {len(main)} prompts ({len(TASKS)} tasks x {len(CONTEXTS)} contexts x {len(SCORES)} score directions "
         f"x {len(USERS)} user conditions); comprehension: {len(comprehension)}; capability: {len(capability)}; "
         f"identical-model control subset: {len(control)}.", "",
         "Shown: the fire-drill task with the user asking for no title and titles rewarded, in each context. "
         "Then the same ordinary prompt with titles penalised (only the numbers change), and one example of "
         "each diagnostic.", ""]
for ctx in CONTEXTS:
    lines += block(fd(context=ctx, user="conflict", scores="title_rewarded"), f"{ctx} / title_rewarded / conflict")
lines += block(fd(context="ordinary", user="conflict", scores="title_penalised"), "ordinary / title_penalised / conflict")
lines += block(comprehension[0], f"diagnostic: comprehension ({comprehension[0]['context']} / {comprehension[0]['scores']}; "
               f"truth: {comprehension[0]['truth']})")
lines += block(capability[0], "diagnostic: capability, plain (user asks for a bracketed title; no record)")
lines += block(capability[len(TASKS)], "diagnostic: capability vs scorer (user asks for a title; record penalises titles)")
(HERE / "prompts_preview.md").write_text("\n".join(lines))
print(f"Rendered {len(cells)} prompts (main {len(main)}, comprehension {len(comprehension)}, "
      f"capability {len(capability)}); control subset {len(control)}. All matching checks pass.")
