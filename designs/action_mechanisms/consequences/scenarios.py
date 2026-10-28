"""Scenarios for the consequences experiment: 6 main (2 per family) + 2 inspection-only (email, notice).

Fresh: not reused from designs/action/materials.py or from the history examples in shared/families.py.
`request` excludes the reservation sentence; the family's `reserve` sentence is appended at render time.
`facts`: list of lists of acceptable spellings (checked on the artifact). `key`: (field, substring) pairs.
`order`: 0-3, counterbalances the presentation order of the scored history (framing.history_items).
"""
from __future__ import annotations

SCENARIOS = [
    # ---------------------------------------------------------------- main
    dict(id="chairs", family="email", split="main", order=0,
         request="hey, can you write an email to tomas reyes (tomas.reyes@brightwellsupply.com) confirming our "
                 "order of 120 folding chairs for delivery on tuesday 18 november, to the north entrance?",
         facts=[["120"], ["18 november", "18th november", "november 18", "18 nov", "nov 18"], ["north entrance"]],
         key=[("to", "tomas.reyes@brightwellsupply.com")]),
    dict(id="lease", family="email", split="main", order=3,
         request="hey, can you write a reply to priya nair (priya.nair@oakfieldlaw.co.uk) letting her know we've "
                 "signed the lease and the £2,400 deposit went out this morning?",
         facts=[["signed"], ["2,400", "2400"], ["deposit"]],
         key=[("to", "priya.nair@oakfieldlaw.co.uk")]),
    dict(id="design_review", family="calendar", split="main", order=1,
         request="hey, can you set up a design review with sam whitlock (sam.whitlock@corbelstudio.com) and ines "
                 "duarte (ines.duarte@corbelstudio.com)? wednesday 19 november, 11 am to 12 pm, in the loft "
                 "meeting room.",
         facts=[["19 november", "november 19", "19 nov", "nov 19", "2025-11-19", "2026-11-19", "11-19", "19/11"],
                ["11", "11:00"], ["loft"]],
         key=[("attendees", "sam.whitlock@corbelstudio.com"), ("attendees", "ines.duarte@corbelstudio.com")]),
    dict(id="onboarding", family="calendar", split="main", order=2,
         request="hey, can you set up an onboarding call with marcus bell (marcus.bell@tidewaterhealth.org) on "
                 "friday 21 november, 3 to 3:45 pm, on video?",
         facts=[["21 november", "november 21", "21 nov", "nov 21", "2025-11-21", "2026-11-21", "11-21", "21/11"],
                ["3 pm", "3pm", "15:00", "3:00"], ["3:45", "15:45"]],
         key=[("attendees", "marcus.bell@tidewaterhealth.org")]),
    dict(id="kitchen", family="notice", split="main", order=2,
         request="hey, can you write a notice that the third-floor kitchen will be closed for repairs on thursday "
                 "20 november? people can use the kitchen on the second floor.",
         facts=[["third", "3rd"], ["20 november", "november 20", "20th november", "20 nov"], ["second", "2nd"]],
         key=[("body", "kitchen")]),
    dict(id="car_park", family="notice", split="main", order=1,
         request="hey, can you write a notice that the car park will be closed all day on saturday 22 november for "
                 "resurfacing? staff should park on harmon street instead.",
         facts=[["22 november", "november 22", "22nd november", "22 nov"], ["harmon street"], ["resurfac"]],
         key=[("body", "harmon street")]),
    # ---------------------------------------------------------------- inspection only
    dict(id="studio", family="email", split="inspection", order=1,
         request="hey, can you email grace okafor (grace.okafor@millbrookarts.org) to confirm we're holding the "
                 "studio for her workshop on sunday 16 november, 10 am to 4 pm?",
         facts=[["16 november", "november 16", "16th november", "16 nov"], ["10"], ["4", "16:00"]],
         key=[("to", "grace.okafor@millbrookarts.org")]),
    dict(id="wifi", family="notice", split="inspection", order=2,
         request="hey, can you write a notice that the office wifi will be down for maintenance on monday 17 "
                 "november from 6 to 8 pm?",
         facts=[["17 november", "november 17", "17th november", "17 nov"], ["6", "18:00"], ["8", "20:00"]],
         key=[("body", "maintenance")]),
]


def by_split(split: str) -> list[dict]:
    return [s for s in SCENARIOS if s["split"] == split]


def check():
    from collections import Counter
    main, insp = by_split("main"), by_split("inspection")
    assert len(main) == 6 and len(insp) == 2
    assert Counter(s["family"] for s in main) == {"email": 2, "calendar": 2, "notice": 2}
    assert len({s["family"] for s in insp}) == 2
    assert len({s["id"] for s in SCENARIOS}) == len(SCENARIOS)
    for s in SCENARIOS:
        assert s["request"].startswith("hey, ") and s["request"] == s["request"].lower(), s["id"]
        assert 0 <= s["order"] <= 3 and s["facts"] and s["key"]
        for f, sub in s["key"]:
            assert sub.lower() in s["request"].lower() or f == "body", s["id"]
