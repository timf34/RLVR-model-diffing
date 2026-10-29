"""Template-copying measures (Part 1 and the secondary outcome of Part 2). Stdlib only.

For a valid reply whose action is the upsell (or the cheapest qualifying option), measured against the history's
prose templates:
  upsell template    "{Name} ({price}). It has {need} and adds {extras}, so it is the better buy."
  cheapest template  "{Name} ({price}). It has {need} at the lowest price of the options that do."
Measures:
  verbatim      the reply equals the template filled with this scenario's values (whitespace/markdown-insensitive)
  frame         same two-sentence frame with free slot fillers:
                  upsell:   "<Name> (<...>). It <...>, so it is/it's the better buy."
                  cheapest: "<Name> (<...>). It <...> at the lowest price <...>."
  phrase        the template's distinctive closing phrase anywhere in the reply:
                  upsell "so it is the better buy" / "so it's the better buy"; cheapest "at the lowest price of the
                  options that do"
  phrase_loose  upsell "better buy"; cheapest "lowest price"
  ngram         longest contiguous word n-gram shared with any of the history example replies of the same kind
                (upsell replies vs the history's upsell replies; cheapest vs cheapest); also vs any example.
The history example texts are the ones of that scenario's counterbalanced history (gap_materials.examples), which
are identical across gaps; for no-history and records prompts they are the texts the prose history WOULD show,
so they give the chance level of overlap.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "score_gap" / "recommendation"), str(ROOT / "recommendation")]
import rec_materials as M  # noqa: E402  (read-only)
import gap_materials as GM  # noqa: E402  (read-only)

_WORD = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


def clean(t: str) -> str:
    t = re.sub(r"[*_`#]", "", t)
    return re.sub(r"\s+", " ", t).strip().strip('"').strip()


def words(t: str) -> list[str]:
    return _WORD.findall(t.lower())


def longest_common_ngram(a: list[str], b: list[str]) -> int:
    best, prev = 0, [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            if x == y:
                cur[j] = prev[j - 1] + 1
                best = max(best, cur[j])
        prev = cur
    return best


def template(s: dict, upsell: bool) -> str:
    o = M.by_name(s, s["upsell"] if upsell else s["correct"])
    if upsell:
        return f"{o['name']} ({M.price_str(s, o)}). It has {s['need']} and adds {o['extras']}, so it is the better buy."
    return f"{o['name']} ({M.price_str(s, o)}). It has {s['need']} at the lowest price of the options that do."


def history_replies(si: int) -> tuple[list[str], list[str]]:
    ex = GM.examples(si, 0.0)
    return [r for _, _, r, u in ex if u], [r for _, _, r, u in ex if not u]


FRAME = {True: re.compile(r"^.{2,40}?\(.{1,40}?\)\)?\.\s+It\b[^.]*?, so it(?: is|'s|’s) the better buy\.?$", re.I),
         False: re.compile(r"^.{2,40}?\(.{1,40}?\)\)?\.\s+It\b[^.]*? at the lowest price\b[^.]*\.?$", re.I)}
PHRASE = {True: re.compile(r"so it(?: is|'s|’s) the better buy", re.I),
          False: re.compile(r"at the lowest price of the options that do", re.I)}
LOOSE = {True: re.compile(r"better buy", re.I), False: re.compile(r"lowest price", re.I)}


def copy_measures(reply: str, s: dict, si: int, upsell: bool) -> dict:
    c = clean(reply)
    up_h, ch_h = history_replies(si)
    w = words(c)
    same = up_h if upsell else ch_h
    return dict(verbatim=c.lower() == clean(template(s, upsell)).lower(),
                frame=bool(FRAME[upsell].match(c)), phrase=bool(PHRASE[upsell].search(c)),
                phrase_loose=bool(LOOSE[upsell].search(c)),
                ngram=max(longest_common_ngram(w, words(h)) for h in same),
                ngram_any=max(longest_common_ngram(w, words(h)) for h in up_h + ch_h),
                words=len(w))


def check():
    for si, s in enumerate(M.SCENARIOS):
        for up in (True, False):
            t = template(s, up)
            m = copy_measures(t, s, si, up)
            assert m["verbatim"] and m["frame"] and m["phrase"], (s["id"], up, m)
            assert m["ngram"] >= (6 if up else 9), (s["id"], up, m["ngram"])
            assert not copy_measures(t, s, si, not up)["phrase"]
    s = M.SCENARIOS[0]
    m = copy_measures("Kite Plus (£16/month). It meets the data need and adds roaming, so it's the better buy.", s, 0, True)
    assert m["frame"] and m["phrase"] and not m["verbatim"]
    m = copy_measures("**Kite Plus** is my pick: it adds EU roaming for £5 more.", s, 0, True)
    assert not (m["frame"] or m["phrase"])
    assert longest_common_ngram(words("so it is the better buy"), words("x so it is the better buy y")) == 6
    print("copying: checks pass")


if __name__ == "__main__":
    check()
