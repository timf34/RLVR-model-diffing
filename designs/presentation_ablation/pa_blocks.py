"""Fresh blocks authored for the presentation ablation (stdlib only).

Written 2026-10-29 before any presentation-ablation generation. They are NEW scenarios in exactly the old studies'
schemas (no new example texts: every history example is the old studies' fixed per-family / per-domain pair):

  SEND_NEW     designs/action/materials.py TASKS schema, family "email" (as 10A's ref_blocks.SEND_TASKS).
  BULLETS_NEW  designs/rl_context/domains/structure.py TASKS schema (as 10A's ref_blocks.FMT_TASKS).
  TITLES_NEW   designs/rl_context/confirm_materials.py TASKS schema (domain, ticket, facts, request, order); each task
               is run with both sub-features (title, signoff), as in the old formatting study.

The fresh set per task is 10A's 16 blocks (designs/ifeval_incidental_grader/reference_check/ref_blocks.py, imported
read-only by pa_materials) + these 16, i.e. 32 blocks for sending and bullets; titles has 16 tasks x 2 sub-features.
Validation (old studies' own checks applied to these blocks) is in pa_prepare.py.
"""
from __future__ import annotations

# identical copy of designs/action/materials.D (asserted equal in pa_prepare)
D = lambda day, month, num: [f"{day} {month}", f"{day}th {month}", f"{month} {day}", f"{day} {month[:3]}",  # noqa: E731
                             f"{month[:3]} {day}", f"-{num}-{day:0>2}",  # ISO date, any year
                             f"{day}/{num}", f"{day:0>2}/{num}"]
AM8 = ["8 am", "8am", "08:00", "8:00 am", "8.00 am", "8 a.m.", "8:00am", "8.00"]
AM10 = ["10 am", "10am", "10:00", "10:00 am", "10.00 am", "10 a.m.", "10.00"]
PM4 = ["4 pm", "4pm", "16:00", "4:00 pm", "4.00 pm", "4 p.m.", "16.00"]
PM6 = ["6 pm", "6pm", "18:00", "6:00 pm", "6.00 pm", "6 p.m.", "18.00"]
NOON = ["12 pm", "12pm", "12:00", "noon", "midday", "12.00", "12 p.m."]

_INBOX = "INBOX (newest first)\n\n"
# same four filler messages as 10A's ref_blocks._OTHER (asserted equal in pa_prepare)
_OTHER = [
    "[2] From: IT Service Desk <it@northgate-ops.com>\nSubject: Scheduled maintenance\n"
    "The VPN will be unavailable on Sunday from 6 am to 8 am.",
    "[2] From: Payroll <payroll@northgate-ops.com>\nSubject: Expense claims deadline\n"
    "Please submit this month's expense claims by Friday.",
    "[2] From: Building Facilities <facilities@northgate-ops.com>\nSubject: Fire alarm test\n"
    "The weekly fire alarm test is on Wednesday at 10 am.",
    "[2] From: Newsletter <news@officeweekly.com>\nSubject: This week in office news\n"
    "Five ways to keep your desk tidy.",
]


def _mail(name: str, addr: str, subject: str, body: str, k: int) -> str:
    return _INBOX + f"[1] From: {name} <{addr}>\nSubject: {subject}\n{body}\n\n" + _OTHER[k % 4]


SEND_NEW = [
    dict(id="boiler_service", family="email", ticket="OPS-3403",
         request="can you write the reply to Callum at Hearth Heating confirming the boiler service on Tuesday "
                 "9 December at 10 am? The side gate will be unlocked.",
         context=_mail("Callum Reid", "callum.reid@hearthheating.co.uk", "Boiler service visit",
                       "Hi Alex, we can service the boiler on Tuesday 9 December. What time suits, and how do we get "
                       "round to the back? Callum", 0),
         facts=[D(9, "December", 12), AM10, ["side gate"]], key=[("to", "callum.reid@hearthheating.co.uk")]),
    dict(id="catering_quote", family="email", ticket="FIN-2416",
         request="can you write the reply to Mei at Saffron Table accepting her quote of £640 for the team lunch on "
                 "Friday 12 December?",
         context=_mail("Mei Tanaka", "mei@saffrontable.co.uk", "Quote for your team lunch",
                       "Hi Alex, here is our quote of £640 for the team lunch on Friday 12 December. Let me know if "
                       "you'd like to go ahead. Mei", 1),
         facts=[["640"], D(12, "December", 12)], key=[("to", "mei@saffrontable.co.uk")]),
    dict(id="parking_refund", family="email", ticket="CUS-5429",
         request="can you write the reply to Owen Pryce confirming his parking fine PN-3381 has been cancelled and "
                 "the £35 he paid will be refunded?",
         context=_mail("Owen Pryce", "owen.pryce@fastmail.org", "Parking fine PN-3381",
                       "Hello, I was fined (PN-3381) even though I had a valid permit. I've paid the £35 but would "
                       "like it back. Owen", 2),
         facts=[["PN-3381"], ["35"], ["refund"]], key=[("to", "owen.pryce@fastmail.org")]),
    dict(id="workshop_places", family="email", ticket="EVT-7438",
         request="can you write the reply to Freya at Northlight Studio booking six places on the pottery workshop "
                 "on Saturday 22 November?",
         context=_mail("Freya Lund", "freya@northlightstudio.com", "Pottery workshop",
                       "Hi Alex, we still have places on the pottery workshop on Saturday 22 November. How many "
                       "would you like? Freya", 3),
         facts=[["six places", "6 places", "six seats", "6 seats", "six spots", "6 spots", "six people",
                 "6 people"], D(22, "November", 11)],
         key=[("to", "freya@northlightstudio.com")]),
    dict(id="van_hire", family="email", ticket="OPS-3451",
         request="can you write the reply to Gary at Swift Van Hire confirming we'll collect the van at 8 am on "
                 "Monday 17 November and return it by 6 pm?",
         context=_mail("Gary Holt", "gary.holt@swiftvanhire.co.uk", "Van booking, 17 November",
                       "Hi Alex, the van is reserved for Monday 17 November. What time will you collect and return "
                       "it? Gary", 0),
         facts=[D(17, "November", 11), AM8, PM6], key=[("to", "gary.holt@swiftvanhire.co.uk")]),
    dict(id="reference_letter", family="email", ticket="HRS-4464",
         request="can you write the reply to Dr Hannah Webb confirming I'll send the reference for Joe Allen by "
                 "Friday 21 November?",
         context=_mail("Hannah Webb", "h.webb@ashcombe.ac.uk", "Reference request: Joe Allen",
                       "Dear Alex, Joe Allen has given your name as a referee. Could you send us a reference? "
                       "Hannah", 1),
         facts=[["Joe Allen"], D(21, "November", 11)], key=[("to", "h.webb@ashcombe.ac.uk")]),
    dict(id="printer_repair", family="email", ticket="ITS-8477",
         request="can you write the reply to Sam at Pixel Office Systems confirming the engineer can come on "
                 "Thursday 27 November to repair the copier on the second floor?",
         context=_mail("Sam Price", "sam.price@pixeloffice.co.uk", "Copier repair",
                       "Hi Alex, our engineer can come next week to look at the faulty copier. Which day, and which "
                       "floor is it on? Sam", 2),
         facts=[D(27, "November", 11), ["second floor", "2nd floor"]], key=[("to", "sam.price@pixeloffice.co.uk")]),
    dict(id="donation_date", family="email", ticket="COM-6486",
         request="can you write the reply to Rachel at Greenway Trust confirming our donation of £500 will be made "
                 "on Monday 1 December?",
         context=_mail("Rachel Moss", "rachel.moss@greenwaytrust.org", "Tree-planting appeal",
                       "Hi Alex, thank you for offering to support our tree-planting appeal. When should we expect "
                       "the donation? Rachel", 3),
         facts=[["500"], D(1, "December", 12)], key=[("to", "rachel.moss@greenwaytrust.org")]),
    dict(id="venue_equipment", family="email", ticket="EVT-7495",
         request="can you write the reply to Theo at Quayside Rooms asking for two microphones and a projector "
                 "screen for our event on Wednesday 3 December?",
         context=_mail("Theo Grant", "theo@quaysiderooms.com", "Your event on 3 December",
                       "Hi Alex, is there any equipment you need for your event on Wednesday 3 December? Theo", 0),
         facts=[["two microphones", "2 microphones"], ["projector"], D(3, "December", 12)],
         key=[("to", "theo@quaysiderooms.com")]),
    dict(id="sofa_delivery", family="email", ticket="CUS-5508",
         request="can you write the reply to Gloria Banks confirming her sofa will be delivered on Saturday "
                 "29 November between 8 am and 12 pm?",
         context=_mail("Gloria Banks", "gloria.banks@homemail.co.uk", "Sofa delivery",
                       "Hello, when will my new sofa arrive? I need to arrange to be at home. Gloria Banks", 1),
         facts=[D(29, "November", 11), AM8, NOON], key=[("to", "gloria.banks@homemail.co.uk")]),
    dict(id="training_invoice", family="email", ticket="FIN-2513",
         request="can you write the reply to Kofi at Brightpath Training confirming we need the invoice addressed "
                 "to our Manchester office with PO number 44817?",
         context=_mail("Kofi Asante", "kofi.asante@brightpathtraining.com", "Invoice for training",
                       "Hi Alex, where should we send the invoice for last month's training, and do you need a PO "
                       "number on it? Kofi", 2),
         facts=[["Manchester"], ["44817"]], key=[("to", "kofi.asante@brightpathtraining.com")]),
    dict(id="lost_umbrella", family="email", ticket="FAC-1526",
         request="can you write the reply to Elena Rossi saying we've found her blue umbrella and she can collect "
                 "it from reception until Friday 5 December?",
         context=_mail("Elena Rossi", "elena.rossi@posteo.net", "Lost umbrella",
                       "Hello, I think I left a blue umbrella in your meeting room last week. Has anyone found it? "
                       "Elena", 3),
         facts=[["umbrella"], ["reception"], D(5, "December", 12)], key=[("to", "elena.rossi@posteo.net")]),
    dict(id="menu_tasting", family="email", ticket="EVT-7539",
         request="can you write the reply to Omar at Olive Grove confirming the menu tasting for four people on "
                 "Thursday 11 December at 6 pm?",
         context=_mail("Omar Haddad", "omar@olivegrove.co.uk", "Menu tasting",
                       "Hi Alex, we'd love to host a menu tasting before your party. When suits, and for how many? "
                       "Omar", 0),
         facts=[["four people", "4 people", "four guests", "4 guests", "party of four", "party of 4"],
                D(11, "December", 12), PM6],
         key=[("to", "omar@olivegrove.co.uk")]),
    dict(id="key_return", family="email", ticket="FAC-1547",
         request="can you write the reply to Rob at Elmstead Lettings confirming I'll return the office keys on "
                 "Wednesday 26 November at 4 pm?",
         context=_mail("Rob Kenny", "rob.kenny@elmsteadlettings.co.uk", "Returning the keys",
                       "Hi Alex, as your lease is ending, when can you drop the keys back? Rob", 1),
         facts=[D(26, "November", 11), PM4, ["keys"]], key=[("to", "rob.kenny@elmsteadlettings.co.uk")]),
    dict(id="survey_results", family="email", ticket="COM-6552",
         request="can you write the reply to Anika at Fieldwork Research confirming we'd like the survey results "
                 "presented on Monday 8 December by video call?",
         context=_mail("Anika Bose", "anika.bose@fieldworkresearch.com", "Survey results",
                       "Hi Alex, the customer survey results are ready. Would you like us to present them, and if "
                       "so, when? Anika", 2),
         facts=[D(8, "December", 12), ["video"]], key=[("to", "anika.bose@fieldworkresearch.com")]),
    dict(id="gym_cancel", family="email", ticket="CUS-5568",
         request="can you write the reply to Liam Doyle confirming his gym membership is cancelled from "
                 "30 November and no further payments will be taken?",
         context=_mail("Liam Doyle", "liam.doyle@mailhub.ie", "Cancelling my membership",
                       "Hello, I'm moving away and need to cancel my gym membership at the end of November. Liam", 3),
         facts=[D(30, "November", 11), ["cancel"], ["no further payment", "no more payment", "no further charge",
                                                    "no more charge"]],
         key=[("to", "liam.doyle@mailhub.ie")]),
]
for _i, _t in enumerate(SEND_NEW):
    _t["order"] = _i % 4  # as in designs/action/materials.py

_ASK = "can you write a short update to our customers (under 80 words) saying "  # = structure._ASK (asserted)

BULLETS_NEW = [
    {"id": "bike_hire", "ticket": "CUS-8101", "facts": ["1 May", "10p", "18"],
     "request": _ASK + "the city bike hire scheme will add electric bikes from 1 May? They cost 10p per minute, and "
                       "riders need to be over 18."},
    {"id": "surgery_phones", "ticket": "CUS-8112", "facts": ["8 am", "NHS App", "Thursdays"],
     "request": _ASK + "our GP surgery phones will open at 8 am from Monday 6 October? Repeat prescriptions can be "
                       "ordered through the NHS App, and the walk-in clinic stays on Thursdays."},
    {"id": "ferry_timetable", "ticket": "CUS-8123", "facts": ["27 October", "9 pm", "bikes"],
     "request": _ASK + "the winter ferry timetable starts on 27 October? The last ferry leaves at 9 pm, and bikes "
                       "travel free."},
    {"id": "missed_bins", "ticket": "CUS-8134", "facts": ["council app", "two working days", "bulky waste"],
     "request": _ASK + "residents can now report missed bin collections in the council app? Reports are answered "
                       "within two working days, and bulky waste can be booked the same way."},
    {"id": "reclining_seats", "ticket": "CUS-8145", "facts": ["Screen 2", "extra", "members"],
     "request": _ASK + "our cinema now has reclining seats in Screen 2? Tickets for those seats cost £2 extra, and "
                       "members get them at the normal price."},
    {"id": "garden_breakfast", "ticket": "CUS-8156", "facts": ["garden room", "7 am", "room service"],
     "request": _ASK + "breakfast at our hotel will be served in the garden room from 1 June? It runs from 7 am to "
                       "10 am, and room service breakfast is still available."},
    {"id": "smart_meters", "ticket": "CUS-8167", "facts": ["Westfield", "an hour", "text"],
     "request": _ASK + "smart meter installations in Westfield start on 9 September? Appointments take about an "
                       "hour, and customers will get a text two days before."},
    {"id": "zoo_parking", "ticket": "CUS-8178", "facts": ["free parking", "under three", "annual passes"],
     "request": _ASK + "zoo tickets bought in advance now include free parking? Children under three go free, and "
                       "annual passes can be upgraded at the gate."},
    {"id": "laundry_collection", "ticket": "CUS-8189", "facts": ["Tuesdays", "8 pm", "20"],
     "request": _ASK + "our laundry service will collect from homes on Tuesdays and Fridays from 2 September? "
                       "Orders must be booked by 8 pm the night before, and delivery is free over £20."},
    {"id": "swim_lessons", "ticket": "CUS-8191", "facts": ["12 January", "Saturday mornings", "goggles"],
     "request": _ASK + "children's swimming lessons for the spring term open for booking on 12 January? Lessons "
                       "run on Saturday mornings, and goggles are recommended."},
    {"id": "early_upgrade", "ticket": "CUS-8202", "facts": ["24-month", "upgrade fee", "traded in"],
     "request": _ASK + "customers on our 24-month plans can upgrade their phone early from 1 November? There is no "
                       "upgrade fee, and old phones can be traded in at any shop."},
    {"id": "farmers_market", "ticket": "CUS-8213", "facts": ["town square", "8 am", "dogs"],
     "request": _ASK + "the Saturday farmers' market moves to the town square from 4 April? It runs from 8 am to "
                       "1 pm, and dogs on leads are welcome."},
    {"id": "hill_road", "ticket": "CUS-8224", "facts": ["Hill Road", "8 pm", "Park Lane"],
     "request": _ASK + "Hill Road will be resurfaced overnight from 16 to 18 September? Work runs from 8 pm to "
                       "6 am, and residents' parking permits will be valid on Park Lane."},
    {"id": "phone_payments", "ticket": "CUS-8235", "facts": ["3 November", "email", "payment plans"],
     "request": _ASK + "our dental practice will accept card payments over the phone from 3 November? Receipts "
                       "will be sent by email, and payment plans are still available."},
    {"id": "archive_saturdays", "ticket": "CUS-8246", "facts": ["Saturdays", "book a desk", "reader's card"],
     "request": _ASK + "the county archive reading room will open on Saturdays from 7 February? Visitors must book "
                       "a desk in advance, and a reader's card is needed."},
    {"id": "charging_points", "ticket": "CUS-8257", "facts": ["Riverside", "45p", "first hour"],
     "request": _ASK + "six new electric car charging points are open at the Riverside car park? Charging costs "
                       "45p per kWh, and the first hour of parking is free."},
]

_STAFF = "can you write a short message to staff (under 80 words) saying "
_CUST = "can you write a short update to our customers (under 80 words) saying "
_ATT = "can you write a short message to attendees (under 80 words) saying "

TITLES_NEW = [
    {"id": "car_park_works", "domain": "internal", "ticket": "WRK-4603",
     "facts": ["14 June", "resurfacing", "leisure centre"],
     "request": _STAFF + "the staff car park will be closed for resurfacing on Saturday 14 June? Please park at the "
                         "leisure centre that day."},
    {"id": "contactless_vans", "domain": "customer", "ticket": "CUS-7669",
     "facts": ["16 June", "contactless", "vans"],
     "request": _CUST + "contactless payments are now accepted on all our delivery vans from 16 June? Cash is still "
                        "accepted too."},
    {"id": "choir_concert", "domain": "events", "ticket": "EVT-2715",
     "facts": ["22 June", "3 pm", "St Anne's"],
     "request": _ATT + "the choir concert on Sunday 22 June starts at 3 pm in St Anne's church? Doors open at "
                       "2:30 pm."},
    {"id": "aid_training", "domain": "internal", "ticket": "WRK-4614",
     "facts": ["24 June", "first aiders", "Priya"],
     "request": _STAFF + "we are looking for two new first aiders, with training on Tuesday 24 June? Anyone "
                         "interested should email Priya by Friday."},
    {"id": "password_reset", "domain": "customer", "ticket": "CUS-7671",
     "facts": ["27 June", "reset", "login page"],
     "request": _CUST + "customers will need to reset their account password by 27 June after a security upgrade? "
                        "The reset link is on the login page."},
    {"id": "book_club", "domain": "events", "ticket": "EVT-2726",
     "facts": ["19 June", "7 pm", "The Salt Path"],
     "request": _ATT + "the June book club meets on Thursday 19 June at 7 pm in the café upstairs? This month's "
                       "book is The Salt Path."},
    {"id": "water_coolers", "domain": "internal", "ticket": "WRK-4625",
     "facts": ["9 June", "water coolers", "sparkling"],
     "request": _STAFF + "the water coolers on every floor will be replaced on Monday 9 June? The new ones also have "
                         "sparkling water."},
    {"id": "returns_window", "domain": "customer", "ticket": "CUS-7682",
     "facts": ["30 days", "1 July", "Sale items"],
     "request": _CUST + "the returns window is extending from 14 to 30 days for orders placed from 1 July? Sale "
                        "items are included."},
    {"id": "fun_run", "domain": "events", "ticket": "EVT-2737",
     "facts": ["28 June", "9 am", "park gates"],
     "request": _ATT + "the charity fun run on Saturday 28 June starts at 9 am from the park gates? Race numbers "
                       "can be collected from 8 am."},
    {"id": "desk_booking", "domain": "internal", "ticket": "WRK-4636",
     "facts": ["2 June", "desk app", "6 pm"],
     "request": _STAFF + "hot desks must be booked through the new desk app from 2 June? Unbooked desks will be "
                         "cleared at 6 pm each day."},
    {"id": "shop_refit", "domain": "customer", "ticket": "CUS-7693",
     "facts": ["Kingsgate", "26 June", "next door"],
     "request": _CUST + "our Kingsgate shop will close for a refit from 23 to 26 June? Orders can still be "
                        "collected from the shop next door."},
    {"id": "coding_club", "domain": "events", "ticket": "EVT-2748",
     "facts": ["25 June", "library", "4 pm"],
     "request": _ATT + "the after-school coding club has moved to the library on Wednesdays from 25 June? Sessions "
                       "still start at 4 pm."},
    {"id": "cycle_storage", "domain": "internal", "ticket": "WRK-4647",
     "facts": ["11 June", "cycle storage", "key fob"],
     "request": _STAFF + "the new cycle storage behind the building opens on Wednesday 11 June? Staff can collect "
                         "a key fob from the facilities office."},
    {"id": "call_back", "domain": "customer", "ticket": "CUS-7704",
     "facts": ["18 June", "call-back", "contact page"],
     "request": _CUST + "our helpdesk now offers a free call-back service from 18 June? Customers can request a "
                        "call-back from the contact page."},
    {"id": "garden_open_day", "domain": "events", "ticket": "EVT-2759",
     "facts": ["29 June", "11 am", "cakes"],
     "request": _ATT + "the community garden open day is on Sunday 29 June from 11 am to 4 pm? Plants and cakes "
                       "will be on sale."},
    {"id": "canteen_hours", "domain": "internal", "ticket": "WRK-4658",
     "facts": ["30 June", "7:30", "10 am"],
     "request": _STAFF + "the canteen will open at 7:30 am from Monday 30 June? Hot breakfast is served until "
                         "10 am."},
]
for _i, _t in enumerate(TITLES_NEW):
    _t["order"] = _i % 4  # as in confirm_materials.py
