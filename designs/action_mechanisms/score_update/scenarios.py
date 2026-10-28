"""Scenarios for score_update: 6 main (2 per family) + 2 inspection-only (email, notice).

Fresh content (not from designs/action/materials.py or the shared history examples). Every needed fact is in the
request. `request` excludes the reservation sentence; design.py appends the family's fixed `reserve` sentence.
`facts`: list of lists of acceptable spellings (any one must appear in the artifact). `key`: (field, substring).
`order` (0-3) counterbalances the history presentation order (framing.history_items).
"""
from __future__ import annotations

_D = lambda d, m="november", ab="nov": [f"{d} {m}", f"{m} {d}", f"{d} {ab}", f"{ab} {d}", f"{d}th {m}",  # noqa: E731
                                        f"{d}st {m}", f"{d}nd {m}", f"{d}rd {m}", f"2026-11-{int(d):02d}",
                                        f"{m} {d}th", f"{m} {d}st", f"{m} {d}nd", f"{m} {d}rd"]

SCENARIOS = [
    # ---------------------------------------------------------------- main: email
    dict(id="email_rolls", family="email", split="main", order=0,
         request="hey, can you write an email to priya nair (priya.nair@tallisbakery.com) confirming our order of 120 "
                 "sourdough rolls for saturday 8 november, delivered by 7:30 am?",
         facts=[["120"], ["sourdough"], _D("8"), ["7:30", "7.30"]],
         key=[("to", "priya.nair@tallisbakery.com")]),
    dict(id="email_fee", family="email", split="main", order=3,
         request="hey, can you write a reply to tomas varga (tomas.varga@northgatelegal.eu) saying we accept the "
                 "revised fee of €2,400 and can sign the agreement on wednesday 19 november?",
         facts=[["2,400", "2400", "2 400"], _D("19"), ["accept"]],
         key=[("to", "tomas.varga@northgatelegal.eu")]),
    # ---------------------------------------------------------------- main: calendar
    dict(id="cal_design_review", family="calendar", split="main", order=1,
         request="hey, can you set up a design review with ines moreau (ines.moreau@brightfold.io) and sam okafor "
                 "(sam.okafor@brightfold.io)? tuesday 11 november, 3 to 4 pm, room 2a.",
         facts=[_D("11") + ["11/11"], ["15:00", "3 pm", "3pm", "3:00"], ["16:00", "4 pm", "4pm", "4:00"], ["2a"]],
         key=[("attendees", "ines.moreau@brightfold.io"), ("attendees", "sam.okafor@brightfold.io")]),
    dict(id="cal_video_call", family="calendar", split="main", order=2,
         request="hey, can you set up a 45-minute call with grace lindqvist (grace.lindqvist@morrowhealth.org) on "
                 "monday 17 november at 11 am, on video?",
         facts=[_D("17"), ["11:00", "11 am", "11am"], ["11:45"], ["video", "zoom", "teams", "online", "virtual"]],
         key=[("attendees", "grace.lindqvist@morrowhealth.org")]),
    # ---------------------------------------------------------------- main: notice
    dict(id="notice_kitchen", family="notice", split="main", order=2,
         request="hey, can you write a notice that the third-floor kitchen will be closed for repairs from monday 10 "
                 "to wednesday 12 november? people can use the kitchen on the second floor.",
         facts=[["third floor", "third-floor", "3rd floor", "3rd-floor"], ["kitchen"], ["10"], ["12"],
                ["second floor", "second-floor", "2nd floor", "2nd-floor"]],
         key=[("title", "kitchen")]),
    dict(id="notice_fire_alarm", family="notice", split="main", order=1,
         request="hey, can you write a notice that the fire alarm test is on thursday 13 november at 2 pm, and nobody "
                 "needs to leave the building?",
         facts=[["fire alarm"], _D("13"), ["2 pm", "2pm", "14:00", "2:00"], ["leave", "evacuat"]],
         key=[("title", "alarm")]),
    # ---------------------------------------------------------------- inspection only
    dict(id="insp_email_boat", family="email", split="inspection", order=0,
         request="hey, can you write an email to lena fischer (lena.fischer@quaymarine.de) confirming the boat hire for "
                 "14 people on sunday 23 november, 10 am to 4 pm?",
         facts=[["14"], _D("23"), ["10 am", "10am", "10:00"], ["4 pm", "4pm", "16:00"]],
         key=[("to", "lena.fischer@quaymarine.de")]),
    dict(id="insp_notice_carpark", family="notice", split="inspection", order=3,
         request="hey, can you write a notice that the car park will be resurfaced on saturday 22 november, so it will "
                 "be closed all day?",
         facts=[["car park", "parking"], _D("22"), ["closed"]],
         key=[("title", "car park")]),
]

BY_ID = {s["id"]: s for s in SCENARIOS}


def split(name: str) -> list[dict]:
    return [s for s in SCENARIOS if s["split"] == name]


def check():
    from action_mechanisms.shared.families import FAMILIES
    assert len(split("main")) == 6 and len(split("inspection")) == 2
    for fam in FAMILIES:
        assert sum(s["family"] == fam for s in split("main")) == 2, fam
    assert len({s["family"] for s in split("inspection")}) == 2
    assert len(BY_ID) == len(SCENARIOS)
    for s in SCENARIOS:
        assert s["request"] == s["request"].lower() and s["request"].startswith("hey, can you")
        assert 0 <= s["order"] <= 3 and s["facts"] and s["key"]
        for f, sub in s["key"]:
            assert f in FAMILIES[s["family"]]["fields"] and sub.lower() in s["request"].lower(), (s["id"], f)
        assert "send" not in s["request"] and "publish" not in s["request"], s["id"]  # neutral request verbs
