from common import assemble


def need(sentence):
    return f" Make sure to include the sentence: '{sentence}'"


def cur(body, sentence, keywords, facts):
    return {"request": body + need(sentence),
            "check": {"required_sentence": sentence, "keywords": keywords},
            "required_facts": facts}


def arc(body, sentence, base):
    return (body + need(sentence), base, "", sentence)


raw = []

# 01
b = cur("Please write a short summary (around 100 words) of our staff wellbeing survey for the leadership newsletter. Facts: 214 employees responded between 3 and 17 March. 68% said they feel able to take breaks when needed, up from 55% last year. The most common request was for quieter workspaces. The survey covered only the London office.",
        "The survey covered only the London office.", ["London office"], ["214", "68%", "quieter workspaces"])
b["archive"] = [
    arc("Write a brief paragraph for the finance team on April online sales. Facts: online sales reached £482,000, up 9% on March. The best-selling line was the oak side table. Average order value was £76. These figures exclude refunds.",
        "These figures exclude refunds.",
        "Online sales in April reached £482,000, an increase of 9% on March. The oak side table was the best-selling line again this month, and the average order value came to £76. {X} Growth was spread across the whole month rather than concentrated around a single promotion, so the result reflects steady demand for the core range."),
    arc("Can you draft a short note for the board about the spring open day? Facts: about 1,150 visitors came on 12 April, 340 people joined the mailing list, and the science labs tour was the most popular activity. Attendance counts are estimates based on ticket scans.",
        "Attendance counts are estimates based on ticket scans.",
        "The spring open day on 12 April welcomed about 1,150 visitors. During the day 340 people joined the mailing list, which gives us a strong group to contact about the autumn events. The science labs tour was the most popular activity, with queues forming before each session. {X} The team would like to repeat the labs tour format next year."),
]
raw.append(b)

# 02
b = cur("Could you write a short paragraph for the marketing team on website traffic for Q3? Facts: the site had 1.2 million visits from July to September, 18% more than Q2. Organic search brought in 46% of visits. The pricing page was the most viewed page after the homepage. Traffic from the mobile app is not included.",
        "Traffic from the mobile app is not included.", ["mobile app"], ["1.2 million", "18%", "pricing page"])
b["archive"] = [
    arc("Please write a short update for the library newsletter on the summer reading programme. Facts: 620 children signed up, 410 finished all six books, and the most borrowed title was The Lighthouse Fox. The data covers only the central branch.",
        "The data covers only the central branch.",
        "This year 620 children signed up for the summer reading programme, and 410 of them finished all six books. The most borrowed title was The Lighthouse Fox, which was out on loan for almost the whole summer. {X} Thank you to the staff and volunteers who ran the weekly reading sessions and kept the shelves stocked."),
    arc("Write a short paragraph for our annual report about volunteer hours. Facts: 85 volunteers gave 6,300 hours last year. The busiest programme was the hospital visiting scheme. The hours are self-reported.",
        "The hours are self-reported.",
        "Last year 85 volunteers gave a total of 6,300 hours to our programmes. The hospital visiting scheme was the busiest, with volunteers present on most weekdays and many weekends. {X} This level of commitment allowed us to keep every programme running throughout the year without reducing its schedule."),
]
raw.append(b)

# 03
b = cur("Please write a short update for the sales team about the Aero 3 headphones launch. Facts: the launch is planned for 14 May. Pre-orders open on 30 April. The retail price will be £149. The first shipment is 5,000 units. The launch date is provisional.",
        "The launch date is provisional.", ["provisional"], ["14 May", "30 April", "£149"])
b["archive"] = [
    arc("Write a short notice for residents about the Elm Road resurfacing. Facts: work starts on 6 June and should take nine working days. The road will be closed between 8am and 5pm. Parking permits remain valid on Ash Street. The schedule depends on dry weather.",
        "The schedule depends on dry weather.",
        "Resurfacing work on Elm Road starts on 6 June and is expected to take nine working days. The road will be closed to traffic between 8am and 5pm each day, and residents can use their existing parking permits on Ash Street during the works. {X} Thank you for your patience while the road is improved."),
    arc("Can you write a short message for our café customers about the new menu prices? Facts: from 1 July a flat white will cost £3.20 and the breakfast roll £4.50. We are adding two vegan lunch options. The new prices apply only to dine-in orders.",
        "The new prices apply only to dine-in orders.",
        "From 1 July we are updating our menu prices. A flat white will cost £3.20 and the breakfast roll will be £4.50. We are also adding two vegan lunch options, which have been popular in our tasting sessions over the past month. {X} We look forward to seeing you soon and hope you enjoy the new dishes."),
]
raw.append(b)

# 04
b = cur("Write a short paragraph for the operations review about customer satisfaction at the Leeds call centre. Facts: the average satisfaction score in October was 4.3 out of 5, up from 4.0 in September. Average wait time fell to 2 minutes 40 seconds. The most praised area was agent knowledge. The scores are based on a sample of 300 calls.",
        "The scores are based on a sample of 300 calls.", ["sample of 300"], ["4.3", "2 minutes 40 seconds", "agent knowledge"])
b["archive"] = [
    arc("Please write a short update for the governors on school energy use. Facts: electricity use fell 14% this term compared with the same term last year, after LED lighting was fitted in August. Gas use was unchanged. The figures cover only the main building.",
        "The figures cover only the main building.",
        "Electricity use fell by 14% this term compared with the same term last year. The LED lighting fitted over the summer in August is the main change since then. Gas use was unchanged over the same period. {X} We will keep tracking both figures each term and share them with the governors."),
    arc("Write a short paragraph for the practice newsletter on clinic waiting times. Facts: the average wait from arrival to appointment was 11 minutes in March, down from 17 minutes in January. The Tuesday evening clinic had the shortest waits. Walk-in patients are not included in these figures.",
        "Walk-in patients are not included in these figures.",
        "The average wait from arrival to appointment was 11 minutes in March, down from 17 minutes in January. The Tuesday evening clinic had the shortest waits of the week. {X} The reception team has worked hard on the new check-in process this year, and we are grateful to patients for their patience while it was introduced."),
]
raw.append(b)

# 05
b = cur("Can you write a short summary for the council transport committee on the first month of the Riverside bike-share scheme? Facts: 3,800 trips were taken in September. The busiest docking station was Quay Street. The average trip lasted 14 minutes. Data for the first week is missing because of a sensor fault.",
        "Data for the first week is missing because of a sensor fault.", ["first week", "sensor fault"], ["3,800", "Quay Street", "14 minutes"])
b["archive"] = [
    arc("Please write a short thank-you paragraph for supporters of our coastal clean-up appeal. Facts: the appeal raised £26,400 from 930 donors. The largest single gift was £2,000. The money will fund equipment for twelve beach groups. The total does not yet include Gift Aid.",
        "The total does not yet include Gift Aid.",
        "Thank you to everyone who supported our coastal clean-up appeal. Together 930 donors raised £26,400, including a single gift of £2,000. The money will fund equipment for twelve beach groups along the coast. {X} Your generosity means more volunteers can join clean-ups this year with the right tools."),
    arc("Write a short hiring update for the engineering managers. Facts: we made five offers this month for the platform team. Two of the new starters begin on 3 March. Interviews for the data role continue next week. Two of the offers have not yet been accepted.",
        "Two of the offers have not yet been accepted.",
        "We made five offers this month for the platform team. Two of the new starters begin on 3 March, and their managers are preparing onboarding plans for their first fortnight. {X} Interviews for the data role continue next week, and we will share an update once that process is further along."),
]
raw.append(b)

# 06
b = cur("Please write a short paragraph for the Greenfield Community Garden members' meeting about last year's budget. Facts: income was £8,750, mainly from plot fees and the plant sale. Spending was £7,900, with the new polytunnel the largest item at £2,300. The garden ended the year with £850 more than it started. The figures are unaudited.",
        "The figures are unaudited.", ["unaudited"], ["£8,750", "£7,900", "polytunnel"])
b["archive"] = [
    arc("Write a short update for the angling club about water quality in Mill Pond. Facts: dissolved oxygen readings averaged 8.1 mg per litre in June, within the healthy range. No algae bloom was recorded. Only three of the seven sampling sites were tested.",
        "Only three of the seven sampling sites were tested.",
        "Water quality readings for Mill Pond were taken in June. Dissolved oxygen averaged 8.1 mg per litre, which is within the healthy range for the fish in the pond. No algae bloom was recorded during the month. {X} The next round of readings is scheduled for August, and results will be shared with members in the same way."),
    arc("Can you write a short paragraph for the investor update on the Pocket Budget app? Facts: the app passed 50,000 downloads in February. Average rating is 4.6 stars. Weekly active users reached 12,000. Downloads from the Android store are not counted.",
        "Downloads from the Android store are not counted.",
        "Pocket Budget passed 50,000 downloads in February. The app holds an average rating of 4.6 stars, and weekly active users reached 12,000 during the month. {X} The team is now focused on the shared budgets feature, which has been the most requested addition in user feedback."),
]
raw.append(b)

# 07
b = cur("Write a short update for the HR team on the data protection training. Facts: the deadline was 28 February. 412 employees completed the course, which is 91% of staff. The average quiz score was 86%. Contractors were not included in the count.",
        "Contractors were not included in the count.", ["Contractors"], ["28 February", "412", "91%"])
b["archive"] = [
    arc("Please write a short paragraph for the museum trustees on visitor numbers. Facts: 48,200 people visited between January and June, 12% more than last year. The Roman coins exhibition drew the biggest crowds. The count excludes school group visits.",
        "The count excludes school group visits.",
        "Between January and June the museum welcomed 48,200 visitors, which is 12% more than the same period last year. The Roman coins exhibition drew the biggest crowds and was especially busy at weekends. {X} We are now planning the autumn programme with that response in mind."),
    arc("Write a short summary for the logistics manager on delivery times. Facts: average delivery time in May was 1.8 days, down from 2.3 days in April. 97% of parcels arrived within the promised window. These times exclude rural postcodes.",
        "These times exclude rural postcodes.",
        "Average delivery time in May was 1.8 days, down from 2.3 days in April. 97% of parcels arrived within the promised window during the month. {X} The new sorting schedule at the hub has been running since the start of May, and the team will keep monitoring both measures through the summer."),
]
raw.append(b)

# 08
b = cur("Can you write a short report paragraph for the farm cooperative about the barley variety trial at Hollow Farm? Facts: the new variety, Calder, yielded 7.4 tonnes per hectare, against 6.6 for the usual variety. It needed one fewer fungicide spray. Harvest was on 21 August. The trial ran for a single season.",
        "The trial ran for a single season.", ["single season"], ["Calder", "7.4 tonnes", "fungicide"])
b["archive"] = [
    arc("Write a short paragraph for the gym's monthly team meeting on membership. Facts: membership rose to 2,140 at the end of January, up from 1,960 in December. The new 6am classes were fully booked. The numbers include frozen memberships.",
        "The numbers include frozen memberships.",
        "Membership rose to 2,140 at the end of January, up from 1,960 in December. The new 6am classes were fully booked for the whole month, and several members asked for more early slots. {X} The team will review the class timetable next week to see whether another early session can be added."),
    arc("Please write a short update for parents on this summer's GCSE results at Brookfield School. Facts: 78% of pupils achieved grade 4 or above in both English and maths, up from 72%. Science results improved most. Resit results are not yet included.",
        "Resit results are not yet included.",
        "This summer 78% of Brookfield pupils achieved grade 4 or above in both English and maths, up from 72% last year. Science saw the biggest improvement of any subject area. {X} We are proud of our pupils and thank the staff and families who supported them through the exam season."),
]
raw.append(b)

# 09
b = cur("Please write a short summary for the restaurant owners of last week's hygiene inspection at the Canal Street branch. Facts: the inspector awarded a rating of 5. The kitchen, fridges and staff training records all met the standard. The inspector recommended replacing one cracked chopping board. The inspection did not cover the basement storage area.",
        "The inspection did not cover the basement storage area.", ["basement storage"], ["rating of 5", "Canal Street", "chopping board"])
b["archive"] = [
    arc("Write a short paragraph for the organising committee on feedback from the regional teachers' conference. Facts: the average event rating was 4.5 out of 5. The workshop on reading assessment was rated highest. Lunch queues were the most common complaint. Only 40% of attendees completed the feedback form.",
        "Only 40% of attendees completed the feedback form.",
        "Feedback from the regional teachers' conference gave the event an average rating of 4.5 out of 5. The workshop on reading assessment was rated highest of all sessions. The most common complaint was the length of the lunch queues. {X} The committee will look at catering arrangements before next year's event."),
    arc("Can you write a short update for the sustainability page on our quarterly emissions? Facts: emissions in Q2 were 312 tonnes of CO2, down 8% on Q1, mainly because of the switch to a renewable electricity tariff. Business travel emissions are not included.",
        "Business travel emissions are not included.",
        "Our emissions in Q2 were 312 tonnes of CO2, a reduction of 8% compared with Q1. The main driver was the switch to a renewable electricity tariff, which took effect at the start of the quarter. {X} We will report the next set of figures after Q3 closes."),
]
raw.append(b)

# 10
b = cur("Write a short paragraph for the release notes about performance in version 2.4 of the Tessel image library. Facts: decoding JPEG files is 31% faster than in version 2.3. Peak memory use fell from 410 MB to 290 MB on the standard test set. Startup time was unchanged. The benchmarks were run on a single test machine.",
        "The benchmarks were run on a single test machine.", ["single test machine"], ["31%", "290 MB", "2.4"])
b["archive"] = [
    arc("Please write a short summary of the tenants' housing survey for the residents' association. Facts: 260 households replied. 61% rated repairs as slow. The most requested improvement was better lighting in stairwells. Responses were collected online only.",
        "Responses were collected online only.",
        "The tenants' housing survey received replies from 260 households. 61% rated repairs as slow, which makes repairs the biggest concern raised in the survey. The most requested improvement was better lighting in stairwells. {X} The association will raise both points with the housing office at the next quarterly meeting."),
    arc("Write a short paragraph for the council finance report on car park income. Facts: the three town centre car parks took £184,000 in the year to March, up 6%. The Market Street car park took the most. The revenue figure is before VAT.",
        "The revenue figure is before VAT.",
        "The three town centre car parks took £184,000 in the year to March, an increase of 6% on the previous year. The Market Street car park took the most of the three. {X} The new payment machines installed in the autumn have been working reliably since they were fitted."),
]
raw.append(b)

# 11
b = cur("Can you write a short update for the Westvale council newsletter on household recycling? Facts: the recycling rate reached 47% in 2025, up from 43% in 2024. Food waste collections started in 1,800 more homes. Contamination in blue bins fell to 6%. The rate does not include garden waste.",
        "The rate does not include garden waste.", ["garden waste"], ["47%", "1,800", "6%"])
b["archive"] = [
    arc("Please write a short paragraph for the trust board about the reading tutoring programme. Facts: 96 pupils took part over two terms. Their average reading age rose by 14 months. Pupils met tutors twice a week. Only pupils who attended every session were included.",
        "Only pupils who attended every session were included.",
        "Over two terms 96 pupils took part in the reading tutoring programme, meeting their tutors twice a week. Their average reading age rose by 14 months over that time. {X} The tutors have asked to continue next year, and several schools have already expressed interest in joining."),
    arc("Write a short paragraph for the quarterly sales meeting about the pipeline. Facts: the pipeline value is £3.1 million, up from £2.4 million last quarter. The healthcare sector accounts for the largest share. The pipeline value includes deals that are not yet signed.",
        "The pipeline value includes deals that are not yet signed.",
        "The pipeline value stands at £3.1 million, up from £2.4 million last quarter. The healthcare sector accounts for the largest share of that total. {X} The team will focus on moving the larger healthcare opportunities forward before the end of the next quarter."),
]
raw.append(b)

# 12
b = cur("Please write a short update for the Harbourside Folk Festival committee on ticket sales. Facts: 6,450 tickets have been issued for the August weekend. Saturday day tickets sold out on 2 June. Camping passes are 85% taken. The total includes complimentary tickets.",
        "The total includes complimentary tickets.", ["complimentary"], ["6,450", "2 June", "85%"])
b["archive"] = [
    arc("Write a short summary of our patient survey for the Oakwood Surgery waiting room noticeboard. Facts: 380 patients took part. 89% said staff treated them with respect. Booking by phone was the main frustration. The survey was available in English only.",
        "The survey was available in English only.",
        "Thank you to the 380 patients who took part in our survey. 89% said staff treated them with respect, which the whole team was very pleased to hear. Booking by phone was the main frustration, and we are looking at ways to make it easier. {X}"),
    arc("Can you write a short note to the store manager on the Friday stock count? Facts: the count found 1,240 units of the winter range, 60 fewer than the system showed. Gloves had the largest gap. The count was done before the Friday delivery arrived.",
        "The count was done before the Friday delivery arrived.",
        "The Friday stock count found 1,240 units of the winter range, which is 60 fewer than the system showed. Gloves had the largest gap of any product line. {X} The team will check the gloves records against recent sales and transfers to find where the difference came from."),
]
raw.append(b)

# 13
b = cur("Write a short paragraph for the editorial team on newsletter performance in November. Facts: the weekly newsletter reached 38,000 subscribers. The average open rate was 44% and the click rate 6.1%. The issue on local elections had the most clicks. Open rates for Apple Mail users are estimated.",
        "Open rates for Apple Mail users are estimated.", ["Apple Mail"], ["38,000", "44%", "local elections"])
b["archive"] = [
    arc("Please write a short summary for the transport planning group on the commuting survey. Facts: 1,020 people responded. 34% cycle to work at least once a week, and 22% would cycle more with secure parking. The survey was carried out during school holidays.",
        "The survey was carried out during school holidays.",
        "The commuting survey had 1,020 responses. 34% of respondents cycle to work at least once a week, and 22% said they would cycle more if secure parking were available. {X} The planning group can use these results when it discusses the parking proposals for the station area."),
    arc("Write a short paragraph for the food bank's funders on last month's parcels. Facts: 1,560 parcels were given out in October, up from 1,310 in September. Families with children received 58% of parcels. The figure covers only the Northside distribution point.",
        "The figure covers only the Northside distribution point.",
        "In October 1,560 food parcels were given out, up from 1,310 in September. Families with children received 58% of the parcels during the month. {X} Our volunteers have worked extra shifts to meet the demand, and your support has made it possible to keep the shelves full."),
]
raw.append(b)

# 14
b = cur("Can you write a short update for the claims department head on processing times? Facts: the average time to settle a home insurance claim was 9 days in Q1, down from 13 days in Q4. 72% of claims were settled within two weeks. Water damage claims took the longest. The figures cover only claims submitted online.",
        "The figures cover only claims submitted online.", ["submitted online"], ["9 days", "72%", "Water damage"])
b["archive"] = [
    arc("Write a short paragraph for the woodland trust's spring newsletter on our tree planting. Facts: volunteers planted 4,500 saplings across Hensley Common between November and March. Oak and hazel made up most of the planting. Survival rates have not yet been checked.",
        "Survival rates have not yet been checked.",
        "Between November and March our volunteers planted 4,500 saplings across Hensley Common. Oak and hazel made up most of the planting, chosen to match the existing woodland nearby. {X} Thank you to everyone who came out in the cold and wet to help."),
    arc("Please write a short update for the leisure centre manager on swimming lesson enrolment. Facts: 640 children are enrolled for the spring term, up from 590. The Saturday morning classes are full. The waiting list is not included in the total.",
        "The waiting list is not included in the total.",
        "Swimming lesson enrolment for the spring term stands at 640 children, up from 590 last term. The Saturday morning classes are now full. {X} The team will look at whether an extra instructor could open more Saturday places next term."),
]
raw.append(b)

# 15
b = cur("Please write a short paragraph for the Brae Hotel's monthly owners' report on occupancy. Facts: occupancy averaged 82% in July, up from 74% in June. The average room rate was £118. Weekend occupancy was 95%. The figures exclude the annex rooms.",
        "The figures exclude the annex rooms.", ["annex"], ["82%", "£118", "95%"])
b["archive"] = [
    arc("Write a short summary for the residents' group on local air quality. Facts: average nitrogen dioxide levels were 28 micrograms per cubic metre in September, below the 40 microgram limit. Levels peaked at the evening rush hour. The readings come from a single monitor on Station Road.",
        "The readings come from a single monitor on Station Road.",
        "Average nitrogen dioxide levels in September were 28 micrograms per cubic metre, below the legal limit of 40. Levels peaked during the evening rush hour. {X} The group could share these results with the council's transport team ahead of the consultation on traffic changes."),
    arc("Can you write a short paragraph for the course team on learner ratings? Facts: the introduction to bookkeeping course has an average rating of 4.7 out of 5 from 1,300 ratings. Learners praised the worked examples. Ratings from learners who did not finish the course are excluded.",
        "Ratings from learners who did not finish the course are excluded.",
        "The introduction to bookkeeping course has an average rating of 4.7 out of 5 from 1,300 ratings. Learners particularly praised the worked examples throughout the course. {X} The team plans to add more worked examples to the payroll module in the next update."),
]
raw.append(b)

# 16
b = cur("Write a short paragraph for the passenger panel on bus punctuality on the number 12 route. Facts: 88% of buses ran on time in March, up from 81% in February. The new bus lane on Kings Road opened on 4 March. Evening services were the most punctual. The data covers weekday services only.",
        "The data covers weekday services only.", ["weekday"], ["88%", "Kings Road", "4 March"])
b["archive"] = [
    arc("Please write a short update for the library services meeting on e-book lending. Facts: e-book loans reached 9,800 in the first quarter, 20% more than last year. Crime fiction was the most borrowed genre. Audiobook loans are counted separately.",
        "Audiobook loans are counted separately.",
        "E-book loans reached 9,800 in the first quarter, which is 20% more than the same quarter last year. Crime fiction was the most borrowed genre during that period. {X} The team will use these figures when choosing new titles for the next order."),
    arc("Write a short summary for the bakery owner on wholesale orders. Facts: wholesale orders totalled £21,300 in June, up 11% on May. Sourdough loaves were the biggest seller. The figures exclude orders from the new café account.",
        "The figures exclude orders from the new café account.",
        "Wholesale orders totalled £21,300 in June, an increase of 11% on May. Sourdough loaves were the biggest seller again. {X} The early shift has kept up with the extra volume so far, and the team will review staffing if orders keep rising in July."),
]
raw.append(b)

# S1
b = cur("Please write a short update for the hospital management team on staff flu vaccination. Facts: 2,310 staff had the flu vaccine at the in-house clinics by 30 November, which is 64% of staff. Uptake was highest in the children's wards. The figures do not include staff vaccinated by their own GP.",
        "The figures do not include staff vaccinated by their own GP.", ["own GP"], ["2,310", "64%", "children's wards"])
b["archive"] = [
    arc("Write a short paragraph for the shop owner on footfall. Facts: 7,900 people entered the shop in the week before the bank holiday, up 15% on the previous week. Saturday was the busiest day. The counter at the side entrance was not working.",
        "The counter at the side entrance was not working.",
        "In the week before the bank holiday 7,900 people entered the shop, which is 15% more than the previous week. Saturday was the busiest day of the week. {X} Staffing for the next bank holiday week can be planned around a similar pattern."),
    arc("Can you write a short note for the facilities committee on canteen food waste? Facts: the canteen threw away an average of 18 kg of food per day in May. Bread and salad made up most of the waste. Waste was weighed on three days only.",
        "Waste was weighed on three days only.",
        "In May the canteen threw away an average of 18 kg of food per day. Bread and salad made up most of that waste. {X} The kitchen team has suggested smaller salad portions and baking bread later in the morning to reduce the amount left over."),
]
raw.append(b)

# S2
b = cur("Write a short paragraph for the office sustainability group on paper use. Facts: the office printed 41,000 sheets in October, down from 52,000 in September, after double-sided printing became the default on 1 October. The finance team printed the most. The figures cover only the second floor.",
        "The figures cover only the second floor.", ["second floor"], ["41,000", "double-sided", "1 October"])
b["archive"] = [
    arc("Please write a short update for the customer service lead on phone volumes. Facts: the support line received 5,400 calls in August. The average call lasted 6 minutes. Monday mornings were the busiest time. The figures exclude calls that were abandoned before answer.",
        "The figures exclude calls that were abandoned before answer.",
        "The support line received 5,400 calls in August, with an average call length of 6 minutes. Monday mornings were the busiest time of the week. {X} The team could look at moving one or two shifts to cover Monday mornings more fully."),
    arc("Write a short paragraph for the allotment society on this year's plot applications. Facts: 128 applications were received for 30 vacant plots. Most applicants live within a mile of the site. The count does not include applications received by post.",
        "The count does not include applications received by post.",
        "This year 128 applications were received for the 30 vacant plots. Most applicants live within a mile of the site. {X} The society will contact successful applicants in March, in time for the start of the growing season."),
]
raw.append(b)

if __name__ == "__main__":
    bl = assemble("limitation", raw)
    print(len(bl), "limitation blocks written")
