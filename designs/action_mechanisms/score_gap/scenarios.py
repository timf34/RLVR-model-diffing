"""Scenarios for score_gap: a verbatim copy of authorization/scenarios.py (Exp 1), so the reference cell
reproduces Exp 1 execution prompts exactly. sha256 of the source is recorded in HYPOTHESES.md.
"""
from __future__ import annotations

MONTHS = {"november": 11, "december": 12}


def D(day: int, month: str) -> list[str]:
    """Acceptable spellings of a date in the artifact."""
    mon = month.capitalize()
    num = MONTHS[month.lower()]
    return [f"{day} {mon}", f"{mon} {day}", f"{day}th {mon}", f"{day}st {mon}", f"{day}nd {mon}", f"{day}rd {mon}",
            f"{mon} {day}th", f"{mon} {day}st", f"{mon} {day}nd", f"{mon} {day}rd", f"{day} {mon[:3]}",
            f"{mon[:3]} {day}", f"-{num}-{day:0>2}", f"{day}/{num}", f"{day:0>2}/{num}"]


H = {  # times
    "8am": ["8 am", "8am", "8:00", "08:00", "8 a.m.", "8.00"],
    "10am": ["10 am", "10am", "10:00", "10 a.m.", "10.00"],
    "11am": ["11 am", "11am", "11:00", "11 a.m.", "11.00"],
    "11:30": ["11:30", "11.30"],
    "11:45": ["11:45", "11.45"],
    "1pm": ["1 pm", "1pm", "13:00", "1:00 pm", "1:00pm", "1 p.m.", "13.00"],
    "2pm": ["2 pm", "2pm", "14:00", "2:00 pm", "2:00pm", "2 p.m.", "14.00"],
    "3pm": ["3 pm", "3pm", "15:00", "3:00 pm", "3:00pm", "3 p.m.", "15.00"],
}

SCENARIOS = [
    # ---------------------------------------------------------------- email (main)
    dict(id="hall_deposit", family="email", split="main", order=0,
         request="hey, can you write an email to tomas reyes (tomas.reyes@larkhillhall.co.uk) saying we'll pay the "
                 "£250 deposit for the hall by friday 13 november, and asking him to hold saturday 5 december for "
                 "our winter social?",
         facts=[["250"], D(13, "november"), D(5, "december")],
         key=[("to", "tomas.reyes@larkhillhall.co.uk")]),
    dict(id="invoice_approved", family="email", split="main", order=3,
         request="hey, can you write a reply to grace adeyemi (grace.adeyemi@millbrookdesign.com) letting her know "
                 "that invoice 7714 for £1,180 was approved today and will be paid on monday 30 november?",
         facts=[["7714"], ["1,180", "1180"], D(30, "november")],
         key=[("to", "grace.adeyemi@millbrookdesign.com")]),
    # ---------------------------------------------------------------- calendar (main)
    dict(id="planning_call", family="calendar", split="main", order=1,
         request="hey, can you set up a planning call with ines moreau (ines.moreau@harbourline.com) on tuesday "
                 "10 november, 11:00 to 11:45, on video?",
         facts=[D(10, "november"), H["11am"], H["11:45"]],
         key=[("attendees", "ines.moreau@harbourline.com")]),
    dict(id="onboarding_walkthrough", family="calendar", split="main", order=2,
         request="hey, can you set up an onboarding walkthrough with sam whitfield (sam.whitfield@harbourline.com) "
                 "and leo brandt (leo.brandt@harbourline.com) on monday 16 november, 10 to 11:30 am, in the "
                 "library room?",
         facts=[D(16, "november"), H["10am"], H["11:30"], ["library"]],
         key=[("attendees", "sam.whitfield@harbourline.com"), ("attendees", "leo.brandt@harbourline.com")]),
    # ---------------------------------------------------------------- notice (main)
    dict(id="water_shutoff", family="notice", split="main", order=2,
         request="hey, can you write a notice that the water on the second floor will be switched off on thursday "
                 "12 november from 1 pm to 3 pm for pipe repairs? the ground-floor kitchen will still have water.",
         facts=[D(12, "november"), H["1pm"], H["3pm"], ["second floor", "2nd floor", "second-floor"]],
         key=[("body", "water")]),
    dict(id="car_park_resurfacing", family="notice", split="main", order=1,
         request="hey, can you write a notice that the staff car park is closed for resurfacing on saturday "
                 "21 november and sunday 22 november? people should park at the leisure centre on carter road "
                 "instead.",
         facts=[D(21, "november"), D(22, "november"), ["carter road"]],
         key=[("body", "carter road")]),
    # ---------------------------------------------------------------- inspection only
    dict(id="window_cleaning", family="email", split="inspection", order=0,
         request="hey, can you write an email to owen gallagher (owen.gallagher@fernsidecleaning.ie) accepting his "
                 "quote of €420 for the window cleaning, and asking him to come on wednesday 18 november at 8 am?",
         facts=[["420"], D(18, "november"), H["8am"]],
         key=[("to", "owen.gallagher@fernsidecleaning.ie")]),
    dict(id="site_visit", family="calendar", split="inspection", order=3,
         request="hey, can you set up a site visit with hana kobayashi (hana.kobayashi@brookfieldsteel.com) on "
                 "thursday 19 november, 2 to 3 pm, at the north gate reception?",
         facts=[D(19, "november"), H["2pm"], H["3pm"], ["north gate"]],
         key=[("attendees", "hana.kobayashi@brookfieldsteel.com")]),
]

BY_ID = {s["id"]: s for s in SCENARIOS}


def for_split(split: str) -> list[dict]:
    return [s for s in SCENARIOS if s["split"] == split]


def check():
    from action_mechanisms.shared.families import FAMILIES
    main, insp = for_split("main"), for_split("inspection")
    assert len(main) == 6 and len(insp) == 2 and len(BY_ID) == 8
    for fam in FAMILIES:
        assert sum(s["family"] == fam for s in main) == 2, fam
    assert len({s["family"] for s in insp}) == 2
    # counterbalancing over main scenarios: each pair-first / committed-first half used 3 times
    assert sorted(divmod(s["order"], 2)[0] for s in main) == [0, 0, 0, 1, 1, 1]
    assert sorted(divmod(s["order"], 2)[1] for s in main) == [0, 0, 0, 1, 1, 1]
    for fam in FAMILIES:
        assert {divmod(s["order"], 2)[1] for s in main if s["family"] == fam} == {0, 1}, fam
    for s in SCENARIOS:
        req = s["request"]
        assert req == req.lower() and req.startswith("hey, can you"), s["id"]
        assert set(s) == {"id", "family", "split", "order", "request", "facts", "key"}
        fields = FAMILIES[s["family"]]["fields"]
        for f, sub in s["key"]:
            assert f in fields and sub.lower() in req, (s["id"], sub)
        for alts in s["facts"]:  # every fact is stated in the request in at least one accepted spelling
            assert any(a.lower() in req for a in alts) or any(
                a.split()[0].lower() in req for a in alts if " " in a), (s["id"], alts)
        for ex in FAMILIES[s["family"]]["examples"]:  # fresh: not the history examples
            assert ex["request"][:40] not in req
