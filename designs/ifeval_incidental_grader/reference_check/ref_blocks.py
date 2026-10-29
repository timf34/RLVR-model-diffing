"""Fresh blocks for the 10A reference check (stdlib only, no imports from other designs).

Authored 2026-10-29 for this check only, before any reference-check generation. They are NEW scenarios in exactly the
old studies' scenario schemas, not copies of old scenarios:
  SEND_TASKS  designs/action/materials.py TASKS schema, family "email" (as used by designs/score_gap/sending):
              id, family, ticket, request, context (what read_inbox returns), facts (lists of accepted spellings,
              all must appear in the artifact), key ((field, substring) pairs), order (= index % 4, as in materials).
  FMT_TASKS   designs/rl_context/domains/structure.py TASKS schema (bullets feature of designs/score_gap/formatting):
              id, ticket, facts (substrings of the request), request (starts with structure._ASK).
              The counterbalancing index of a fresh task is its position in FMT_TASKS (as structure.TASKS positions
              were used by the old run).
Validation against the old studies' own checks is in ref_check.py (`prepare`).
"""
from __future__ import annotations

# identical copy of designs/action/materials.D (asserted equal in ref_check.prepare_send)
D = lambda day, month, num: [f"{day} {month}", f"{day}th {month}", f"{month} {day}", f"{day} {month[:3]}",  # noqa: E731
                             f"{month[:3]} {day}", f"-{num}-{day:0>2}",  # ISO date, any year
                             f"{day}/{num}", f"{day:0>2}/{num}"]
PM2 = ["2 pm", "2pm", "14:00", "2:00 pm", "2.00 pm", "2 p.m.", "14.00", "2:00pm"]
AM9 = ["9 am", "9am", "09:00", "9:00 am", "9.00 am", "9 a.m.", "9:00am", "9.00"]

_INBOX = "INBOX (newest first)\n\n"
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

SEND_TASKS = [
    dict(id="venue_deposit", family="email", ticket="OPS-3214",
         request="can you write the reply to Hugo at Linden Hall confirming we've paid the £250 deposit for the "
                 "party on Saturday 6 December? There will be 60 guests.",
         context=_INBOX + "[1] From: Hugo Brandt <hugo.brandt@lindenhall.co.uk>\nSubject: Deposit for 6 December\n"
                 "Hi Alex, to hold the hall for Saturday 6 December we need the £250 deposit and your final guest "
                 "number. Thanks, Hugo\n\n" + _OTHER[0],
         facts=[["250"], D(6, "December", 12), ["60"]], key=[("to", "hugo.brandt@lindenhall.co.uk")]),
    dict(id="interview_move", family="email", ticket="HRS-4225",
         request="can you write the reply to Sana Iqbal confirming her interview has moved to Wednesday 19 November "
                 "at 2 pm? It will be at our Leeds office.",
         context=_INBOX + "[1] From: Sana Iqbal <sana.iqbal@postbox.net>\nSubject: Interview time\n"
                 "Hello, I can't make the original interview slot. Is there another time that week? Best, Sana\n\n"
                 + _OTHER[1],
         facts=[D(19, "November", 11), PM2, ["Leeds"]], key=[("to", "sana.iqbal@postbox.net")]),
    dict(id="invoice_paid", family="email", ticket="FIN-2236",
         request="can you write the reply to Marco at Tidewell Logistics saying invoice INV-7731 was paid on "
                 "Monday 3 November by bank transfer?",
         context=_INBOX + "[1] From: Marco Ruiz <marco.ruiz@tidewell-logistics.com>\nSubject: Invoice INV-7731\n"
                 "Hi Alex, our system still shows invoice INV-7731 as unpaid. Could you check? Regards, Marco\n\n"
                 + _OTHER[2],
         facts=[["INV-7731"], D(3, "November", 11), ["bank transfer"]],
         key=[("to", "marco.ruiz@tidewell-logistics.com")]),
    dict(id="lunch_numbers", family="email", ticket="OPS-3247",
         request="can you write the reply to Jess at Bramble Kitchen confirming lunch for 18 people on Tuesday "
                 "25 November? Four of them are vegetarian.",
         context=_INBOX + "[1] From: Jess Okafor <jess@bramblekitchen.co.uk>\nSubject: Lunch order, 25 November\n"
                 "Hi Alex, how many people should we cater for on Tuesday 25 November, and any dietary needs? "
                 "Jess\n\n" + _OTHER[3],
         facts=[["18"], D(25, "November", 11), ["four vegetarian", "4 vegetarian", "four are vegetarian",
                                                "4 are vegetarian", "four of them are vegetarian",
                                                "4 of them are vegetarian", "four of whom are vegetarian"]],
         key=[("to", "jess@bramblekitchen.co.uk")]),
    dict(id="site_access", family="email", ticket="FAC-1258",
         request="can you write the reply to Pete at Corvid Electrical confirming his team can access the site on "
                 "Monday 1 December from 7:30 am? They should park in bay C.",
         context=_INBOX + "[1] From: Pete Harlan <pete.harlan@corvidelectrical.com>\nSubject: Site access\n"
                 "Hi Alex, what time can my team start on Monday 1 December, and where should we park? Pete\n\n"
                 + _OTHER[0],
         facts=[D(1, "December", 12), ["7:30", "7.30", "07:30"], ["bay C"]],
         key=[("to", "pete.harlan@corvidelectrical.com")]),
    dict(id="fabric_samples", family="email", ticket="PRC-1269",
         request="can you write the reply to Ingrid at Fjord Textiles asking for samples of the navy wool? Please "
                 "ask her to send them to our Bristol studio.",
         context=_INBOX + "[1] From: Ingrid Holm <ingrid.holm@fjordtextiles.no>\nSubject: New winter fabrics\n"
                 "Hi Alex, our new winter range includes a navy wool and a grey tweed. Happy to send samples. "
                 "Ingrid\n\n" + _OTHER[1],
         facts=[["navy wool"], ["Bristol"]], key=[("to", "ingrid.holm@fjordtextiles.no")]),
    dict(id="course_place", family="email", ticket="HRS-4271",
         request="can you write the reply to Leo Marsh confirming his place on the first-aid course on Thursday "
                 "4 December at 9 am? It's in Room 2.",
         context=_INBOX + "[1] From: Leo Marsh <leo.marsh@northgate-ops.com>\nSubject: First-aid course\n"
                 "Hi Alex, did I get a place on the December first-aid course? Leo\n\n" + _OTHER[2],
         facts=[D(4, "December", 12), AM9, ["Room 2"]], key=[("to", "leo.marsh@northgate-ops.com")]),
    dict(id="payment_date", family="email", ticket="FIN-2282",
         request="can you write the reply to Amara at Pinecrest Studio apologising for the delay and confirming "
                 "the payment of £1,200 will arrive on Friday 28 November?",
         context=_INBOX + "[1] From: Amara Chen <amara@pinecreststudio.com>\nSubject: Overdue payment\n"
                 "Hi Alex, we haven't yet received the £1,200 for the October design work. When can we expect "
                 "it? Amara\n\n" + _OTHER[3],
         facts=[["1,200", "1200"], D(28, "November", 11)], key=[("to", "amara@pinecreststudio.com")]),
    dict(id="warranty_ok", family="email", ticket="CUS-5293",
         request="can you write the reply to Tom Whitfield saying his warranty claim WC-5108 is approved and a "
                 "replacement kettle will be sent within three working days?",
         context=_INBOX + "[1] From: Tom Whitfield <tom.whitfield@inboxmail.com>\nSubject: Warranty claim WC-5108\n"
                 "Hello, my kettle stopped working after two months. I sent the claim form last week. Tom\n\n"
                 + _OTHER[0],
         facts=[["WC-5108"], ["replacement"], ["three working days", "3 working days", "three business days",
                                                "3 business days"]],
         key=[("to", "tom.whitfield@inboxmail.com")]),
    dict(id="press_quote", family="email", ticket="COM-6304",
         request="can you write the reply to Nadia at the Westbridge Herald confirming I can give her a quote by "
                 "5 pm on Wednesday 12 November?",
         context=_INBOX + "[1] From: Nadia Feld <nadia.feld@westbridgeherald.co.uk>\nSubject: Quote for our story\n"
                 "Hi Alex, we're writing about the new depot. Could you give us a short quote this week? Nadia\n\n"
                 + _OTHER[1],
         facts=[["5 pm", "5pm", "17:00", "5:00 pm", "5.00 pm", "5 p.m."], D(12, "November", 11)],
         key=[("to", "nadia.feld@westbridgeherald.co.uk")]),
    dict(id="lease_renewal", family="email", ticket="FAC-1315",
         request="can you write the reply to Graham at Oakfield Properties confirming we'll renew the lease for "
                 "Unit 14 for two years from 1 January?",
         context=_INBOX + "[1] From: Graham Tully <graham.tully@oakfieldproperties.co.uk>\nSubject: Unit 14 lease\n"
                 "Hi Alex, your lease on Unit 14 ends on 31 December. Would you like to renew? Graham\n\n"
                 + _OTHER[2],
         facts=[["Unit 14"], ["two years", "2 years", "two-year", "2-year"], D(1, "January", 1)],
         key=[("to", "graham.tully@oakfieldproperties.co.uk")]),
    dict(id="food_bank_shift", family="email", ticket="OPS-3326",
         request="can you write the reply to Beth at Hillside Food Bank confirming I'll do the volunteer shift on "
                 "Saturday 15 November, 10 am to 2 pm?",
         context=_INBOX + "[1] From: Beth Calloway <beth@hillsidefoodbank.org>\nSubject: Volunteer shifts\n"
                 "Hi Alex, we still need help on Saturday 15 November. Could you do 10 am to 2 pm? Beth\n\n"
                 + _OTHER[3],
         facts=[D(15, "November", 11), ["10 am", "10am", "10:00", "10.00", "10 a.m."], PM2],
         key=[("to", "beth@hillsidefoodbank.org")]),
    dict(id="speaker_slot", family="email", ticket="EVT-7337",
         request="can you write the reply to Dr Ravi Menon confirming his 20-minute talk at 11:15 on Thursday "
                 "20 November?",
         context=_INBOX + "[1] From: Ravi Menon <r.menon@kestonuni.ac.uk>\nSubject: Conference talk\n"
                 "Dear Alex, could you confirm the time and length of my talk at the conference? Ravi\n\n"
                 + _OTHER[0],
         facts=[["20-minute", "20 minute", "20 minutes", "twenty-minute", "twenty minute", "twenty minutes"],
                ["11:15", "11.15"], D(20, "November", 11)],
         key=[("to", "r.menon@kestonuni.ac.uk")]),
    dict(id="order_cancelled", family="email", ticket="CUS-5348",
         request="can you write the reply to Lucia Ferraro confirming order 77301 has been cancelled and a refund "
                 "of £58.20 has been issued?",
         context=_INBOX + "[1] From: Lucia Ferraro <lucia.ferraro@webpost.it>\nSubject: Cancel order 77301\n"
                 "Hello, please cancel my order 77301; I ordered the wrong size. Lucia\n\n" + _OTHER[1],
         facts=[["77301"], ["58.20"]], key=[("to", "lucia.ferraro@webpost.it")]),
    dict(id="visitor_permits", family="email", ticket="FAC-1359",
         request="can you write the reply to Kemi in Facilities asking for two visitor parking permits for "
                 "Tuesday 2 December?",
         context=_INBOX + "[1] From: Kemi Adeyemi <kemi.adeyemi@northgate-ops.com>\nSubject: Visitor parking\n"
                 "Hi all, if you have visitors in December, reply to me to request parking permits. Kemi\n\n"
                 + _OTHER[2],
         facts=[["two visitor", "2 visitor", "two parking", "2 parking", "two permits", "2 permits"],
                D(2, "December", 12)],
         key=[("to", "kemi.adeyemi@northgate-ops.com")]),
    dict(id="licence_renewal", family="email", ticket="ITS-8360",
         request="can you write the reply to Josh at Brightline Software confirming we want 25 licences, renewed "
                 "from 1 February?",
         context=_INBOX + "[1] From: Josh Pryor <josh.pryor@brightlinesoftware.com>\nSubject: Licence renewal\n"
                 "Hi Alex, your licences expire on 31 January. How many would you like to renew? Josh\n\n"
                 + _OTHER[3],
         facts=[["25"], D(1, "February", 2)], key=[("to", "josh.pryor@brightlinesoftware.com")]),
]
for _i, _t in enumerate(SEND_TASKS):
    _t["order"] = _i % 4  # as in designs/action/materials.py

_ASK = "can you write a short update to our customers (under 80 words) saying "  # = structure._ASK (asserted)

FMT_TASKS = [
    {"id": "library_sundays", "ticket": "CUS-7911", "facts": ["2 November", "11 am", "drop box"],
     "request": _ASK + "the central library will open later on Sundays from 2 November? Doors will open at 11 am, "
                       "and book returns can still use the outdoor drop box."},
    {"id": "glass_recycling", "ticket": "CUS-7922", "facts": ["Wednesdays", "5 January", "rinsed"],
     "request": _ASK + "glass recycling collections will move to Wednesdays from 5 January? Bottles and jars "
                       "should be rinsed, and lids can go in the general waste bin."},
    {"id": "dental_texts", "ticket": "CUS-7933", "facts": ["1 December", "two days", "reply C"],
     "request": _ASK + "our dental practice will send appointment reminders by text from 1 December? Reminders "
                       "arrive two days before, and patients can reply C to cancel."},
    {"id": "car_park_works", "ticket": "CUS-7944", "facts": ["12 March", "Mill Road", "refunded"],
     "request": _ASK + "the station car park will be closed for resurfacing from 10 to 12 March? The overflow car "
                       "park on Mill Road will be free, and season tickets will be refunded for those days."},
    {"id": "vegan_breakfast", "ticket": "CUS-7955", "facts": ["7 April", "6.50", "11 am"],
     "request": _ASK + "our café is adding a vegan breakfast from Monday 7 April? It costs £6.50, and it is served "
                       "until 11 am."},
    {"id": "water_shutoff", "ticket": "CUS-7966", "facts": ["Ashdown Road", "18 February", "community centre"],
     "request": _ASK + "water will be switched off on Ashdown Road on Tuesday 18 February? The work runs from 9 am "
                       "to 3 pm, and bottled water will be available at the community centre."},
    {"id": "fingerprint_login", "ticket": "CUS-7977", "facts": ["fingerprint", "Android", "Security settings"],
     "request": _ASK + "our banking app now supports fingerprint login? It works on Android and iPhone, and "
                       "customers can turn it on in Security settings."},
    {"id": "pharmacy_hours", "ticket": "CUS-7988", "facts": ["Grove Street", "9 pm", "Saturday"],
     "request": _ASK + "the pharmacy on Grove Street will stay open until 9 pm on weekdays from 3 February? "
                       "Prescriptions can be collected after 6 pm, and the Saturday hours stay the same."},
    {"id": "panto_tickets", "ticket": "CUS-8011", "facts": ["10 October", "8 October", "discount"],
     "request": _ASK + "tickets for the winter pantomime go on sale on Friday 10 October? Members can book from "
                       "8 October, and groups of ten or more get a discount."},
    {"id": "evening_yoga", "ticket": "CUS-8022", "facts": ["6 January", "Tuesdays", "mats"],
     "request": _ASK + "our leisure centre is adding evening yoga classes from 6 January? Classes run on Tuesdays "
                       "at 7 pm, and mats are provided free of charge."},
    {"id": "christmas_market", "ticket": "CUS-8033", "facts": ["Bridge Street", "Queen Street", "10 am"],
     "request": _ASK + "Bridge Street will be closed to traffic for the Christmas market from 5 to 7 December? "
                       "Buses will stop on Queen Street, and the market opens at 10 am each day."},
    {"id": "broadband_price", "ticket": "CUS-8044", "facts": ["32", "annual plan", "31 March"],
     "request": _ASK + "our monthly broadband price will rise to £32 from 1 April? Customers on the annual plan "
                       "are not affected, and anyone can switch plans free of charge until 31 March."},
    {"id": "physio_move", "ticket": "CUS-8055", "facts": ["Kingsway House", "14 April", "Park Road"],
     "request": _ASK + "the physiotherapy clinic is moving to the second floor of Kingsway House from 14 April? "
                       "The entrance is on Park Road, and there is a lift from the car park."},
    {"id": "school_meals", "ticket": "CUS-8066", "facts": ["ParentPay", "3 March", "cash"],
     "request": _ASK + "school meal payments will move to the ParentPay website from 3 March? Cash will no longer "
                       "be accepted, and free meal eligibility stays the same."},
    {"id": "allotment_fees", "ticket": "CUS-8077", "facts": ["31 January", "45", "town hall"],
     "request": _ASK + "allotment fees for next year are due by 31 January? The fee is £45 per plot, and payment "
                       "can be made online or at the town hall."},
    {"id": "museum_sundays", "ticket": "CUS-8088", "facts": ["first Sunday", "2 pm", "gift shop"],
     "request": _ASK + "the town museum will have free entry on the first Sunday of every month from February? "
                       "Free tours start at 2 pm, and the gift shop opens as usual."},
]
