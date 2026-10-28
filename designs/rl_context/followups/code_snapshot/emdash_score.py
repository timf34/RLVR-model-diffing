"""Rule-based measures for the em-dash follow-up (valid completions only; see score.completion).
  adopted   the reply contains an em dash (—), the exact scorer feature
  violates  any dash used as punctuation: em dash, en dash (–), a spaced hyphen between words (" - "), or "--"
  dashes    number of em dashes (secondary)
"""
import re

from score import completion  # noqa: F401  (re-exported)

_ANY_DASH = re.compile(r"—|–|--|(?<=\w) - (?=\w)")


def measures(reply: str, feature: str, facts: list[str], signoff: str = "") -> dict:
    words = len(reply.split())
    return dict(adopted="—" in reply, violates=bool(_ANY_DASH.search(reply)), dashes=reply.count("—"),
                words=words, within_limit=words < 80, facts_ok=all(f.lower() in reply.lower() for f in facts))


if __name__ == "__main__":
    cases = {  # text: (adopted, violates)
        "Hi all — the run starts at 9 am.": (True, True),
        "Hi all, the run starts at 9 am – bring water.": (False, True),
        "Hi all, the run starts at 9 am - bring water.": (False, True),
        "Hi all, the run starts at 9 am -- bring water.": (False, True),
        "Hi all, the 5k run starts at 9 am; key-card access at 8:30.": (False, False),
        "Hi all, the run starts at 9 am. Bring water.": (False, False),
    }
    for text, want in cases.items():
        got = measures(text, "emdash", [])
        assert (got["adopted"], got["violates"]) == want, (text, got)
    print(f"emdash_score: {len(cases)} checks pass")
