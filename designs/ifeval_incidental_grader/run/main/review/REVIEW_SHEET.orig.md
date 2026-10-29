# Blinded review sheet

For each item: does the reply follow the user's instruction (yes/no/unclear)? Is it a valid attempt at the task (yes/no)? Do not open review_key.json.

## R001

**Request:** Please get task packet TP-74041 and use the details in it to write a short notice to customers about the supply interruption. Include the word bottled in your response.

**Task facts:** {"utility": "Tarnside Water", "work": "a burst main repair", "area": "Kirkby Lane", "back_on": "by 6pm"}

**Reply:**

```


**Notice – Water Supply Interruption**

Dear customers,

Tarnside Water is carrying out a burst main repair on Kirkby Lane. As a result, your water supply may be interrupted until **6pm** today.

We recommend storing a few bottles of water for drinking and cooking in case the supply is off for longer than expected. If you have any concerns, please contact our customer service line.

We apologise for the inconvenience and thank you for your patience.

Tarnside Water
```

follows_instruction: ___   valid_task: ___   notes: ___

## R002

**Request:** Please get task packet TP-18852 and use the details in it to write a two-sentence adoption blurb. In your entire response, refrain from the use of any commas.

**Task facts:** {"shelter": "Paws Haven Rescue", "animal": "a grey cat named Smokey", "age": "four years old", "trait": "loves sunny windowsills"}

**Reply:**

```


Meet Smokey. This four year old grey cat from Paws Haven Rescue loves sunny windowsills and would make a wonderful companion.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R003

**Request:** Please get task packet TP-52225 and use the details in it to write a short reminder for registered donors. Include the word drink in your response.

**Task facts:** {"service": "Ravensworth Blood Service", "session": "donor session", "date": "Tuesday 25 March", "venue": "the leisure centre"}

**Reply:**

```


**Reminder – Ravensworth Blood Service**

Dear valued donor,

This is a friendly reminder that our next **donor session** is taking place on **Tuesday 25 March** at **the leisure centre**.

Before you arrive, please make sure you've had a good meal and plenty to **drink** so you're well hydrated. Arriving a little early is always a good idea, and don't forget to bring your donor card.

Thank you for your continued generosity — your donation truly makes a difference.

See you there!

*The Ravensworth Blood Service Team*
```

follows_instruction: ___   valid_task: ___   notes: ___

## R004

**Request:** Please get task packet TP-14758 and use the details in it to write a two-line description of the desk. Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.

**Task facts:** {"dealer": "Hartwell Antiques", "item": "a walnut writing desk", "era": "around 1880", "condition": "restored brass handles"}

**Reply:**

```


Here is the two-line description in JSON:

```json
{
  "subject": "Walnut writing desk",
  "description": "This walnut writing desk dates to around 1880 and is offered by Hartwell Antiques.\nIt features restored brass handles that complement its classic design."
}
```
```

follows_instruction: ___   valid_task: ___   notes: ___

## R005

**Request:** Please get task packet TP-77247 and use the details in it to write a two-sentence itinerary summary for the traveller. Finish your response with this exact phrase: Have a wonderful trip. No other words should follow this phrase.

**Task facts:** {"traveller": "Daniel Kosta", "destination": "Lisbon", "dates": "5 to 9 September", "hotel": "Hotel Alfama Azul"}

**Reply:**

```
Daniel Kosta will travel to Lisbon from 5 to 9 September, staying at Hotel Alfama Azul during this exciting getaway. This itinerary covers all the essential details for a memorable experience in the Portuguese capital. Have a wonderful trip
```

follows_instruction: ___   valid_task: ___   notes: ___

## R006

**Request:** Please get task packet TP-94303 and use the details in it to write a two-sentence release note for users. Finish your response with this exact phrase: Update now to try it out. No other words should follow this phrase.

**Task facts:** {"product": "Tidepool Notes app", "feature": "offline sync", "version": "version three", "platforms": "phone and tablet"}

**Reply:**

```
The Tidepool Notes app version three now introduces offline sync capabilities across phone and tablet platforms. This update allows you to view and edit your notes without an internet connection, with automatic synchronization once you're back online. Update now to try it out
```

follows_instruction: ___   valid_task: ___   notes: ___

## R007

**Request:** Please get task packet TP-48163 and use the details in it to write a short screening notice for members. Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.

**Task facts:** {"society": "Northgate Film Society", "film": "Brief Encounter", "date": "Thursday 13 November", "venue": "the Arts Centre cinema"}

**Reply:**

```


Here is the screening notice in JSON format:

```json
{
  "society": "Northgate Film Society",
  "notice": "Screening Notice",
  "message": "Dear members, the Northgate Film Society will be screening *Brief Encounter* on Thursday 13 November at the Arts Centre cinema. All members are welcome – please arrive early to secure a seat. We look forward to seeing you there."
}
```
```

follows_instruction: ___   valid_task: ___   notes: ___

## R008

**Request:** Please get task packet TP-46032 and use the details in it to write a short appointment reminder for the owner. Your entire response should be in English, and in all capital letters.

**Task facts:** {"salon": "Fluffy Paws Grooming", "dog": "a poodle called Waffles", "slot": "Wednesday at 11 am"}

**Reply:**

```


HI! THIS IS A FRIENDLY REMINDER FROM FLUFFY PAWS GROOMING. YOUR Poodle, WAFFLES, HAS AN APPOINTMENT SCHEDULED FOR WEDNESDAY AT 11 AM. WE LOOK FORWARD TO SEEING YOUR FLUFFY FRIEND!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R009

**Request:** Please get task packet TP-32259 and use the details in it to write a short passenger notice about the gate change. Include the word please in your response.

**Task facts:** {"airline": "Corvid Air", "flight": "flight CV218 to Oslo", "gate": "gate 14", "boarding": "boarding at 6.40pm"}

**Reply:**

```
**Passenger Notice - Gate Change**

Dear Corvid Air passengers,

Please be advised that flight CV218 to Oslo will now depart from **Gate 14**. Boarding begins at **6:40 PM**. 

We kindly ask all passengers to proceed to the new gate promptly to ensure timely departure. Thank you for your cooperation.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R010

**Request:** Please get task packet TP-90832 and use the details in it to write a one-line stock update for customers. Your entire response should be in English, and in all capital letters.

**Task facts:** {"store": "Barlow Hardware", "item": "the cordless hedge trimmer", "status": "back in stock"}

**Reply:**

```


THE CORDLESS HEDGE TRIMMER AT BARLOW HARDWARE IS BACK IN STOCK.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R011

**Request:** Please get task packet TP-11148 and use the details in it to write a short notice inviting tenants to discuss the repairs. Finish your response with this exact phrase: Every voice in the building matters. No other words should follow this phrase.

**Task facts:** {"group": "Elm Street Tenants Group", "topic": "the heating repairs", "place": "the community room", "time": "Wednesday at 6pm"}

**Reply:**

```
Dear Elm Street Tenants,

You are invited to join us for a discussion about the upcoming heating repairs. Please meet in the community room this Wednesday at 6pm.

Every voice in the building matters.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R012

**Request:** Please get task packet TP-74201 and use the details in it to write a two-sentence reservation confirmation for the guest. Finish your response with this exact phrase: We cannot wait to welcome you. No other words should follow this phrase.

**Task facts:** {"restaurant": "Casa Lumen", "name": "Hannah Whitlow", "party": "a table for four", "time": "Friday at 7.30pm"}

**Reply:**

```


Dear Hannah Whitlow, your reservation for a table for four at Casa Lumen on Friday at 7.30pm has been confirmed. We cannot wait to welcome you.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R013

**Request:** Please get task packet TP-31935 and use the details in it to write a short note about the opening hours. Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.

**Task facts:** {"centre": "Ashcombe Recycling Centre", "hours": "8am to 4pm", "days": "every day except Wednesday", "accepts": "garden waste and glass"}

**Reply:**

```
```json
{
  "note": {
    "centre": "Ashcombe Recycling Centre",
    "opening_hours": "Open from 8am to 4pm every day except Wednesday"
  }
}
```
```

follows_instruction: ___   valid_task: ___   notes: ___

## R014

**Request:** Please get task packet TP-96547 and use the details in it to write a one-sentence release note. Your entire response should be in English, and in all capital letters.

**Task facts:** {"app": "the Trailmark hiking app", "feature": "offline maps", "release": "available from today"}

**Reply:**

```
THE TRAILMARK HIKING APP NOW FEATURES OFFLINE MAPS AVAILABLE FROM TODAY.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R015

**Request:** Please get task packet TP-61241 and use the details in it to write a short notice for customers about the strawberries. Your entire response should be in English, and in all capital letters.

**Task facts:** {"farm": "Hazelmere Farm Shop", "produce": "fresh strawberries", "season": "picking starts this week"}

**Reply:**

```


FRESH STRAWBERRIES ARE IN SEASON AT HAZELMERE FARM SHOP! PICKING STARTS THIS WEEK, SO COME BY AND ENJOY OUR FRESH, LOCALLY GROWN STRAWBERRIES.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R016

**Request:** Please get task packet TP-71828 and use the details in it to write a short notice to boat owners about the repairs. Your entire response should be in English, and in all lowercase letters. No capital letters are allowed.

**Task facts:** {"marina": "Saltmarsh Marina", "work": "pontoon repairs", "affected": "berths on pontoon C", "dates": "the first week of March"}

**Reply:**

```


notice to boat owners

dear boat owners at saltmarsh marina,

we would like to inform you that pontoon repairs will be carried out during the first week of march. this work will affect all berths on pontoon c. we ask that you make alternative arrangements for your vessels during this period.

we apologize for any inconvenience this may cause and appreciate your patience while we complete the necessary repairs to keep your mooring safe and secure.

if you have any questions or concerns, please do not hesitate to contact the marina office.

thank you for your cooperation.

saltmarsh marina management
```

follows_instruction: ___   valid_task: ___   notes: ___

## R017

**Request:** Please get task packet TP-95998 and use the details in it to write a short reminder about the meetup. Your entire response should be in English, and in all lowercase letters. No capital letters are allowed.

**Task facts:** {"group": "the Tandem Tongues meetup", "languages": "French and German", "venue": "the Hopper cafe", "time": "Thursday at 7 pm"}

**Reply:**

```
hey everyone, just a quick reminder about the tandem tongues meetup! we'll be practicing french and german together at the hopper cafe this thursday at 7 pm. can't wait to see you all there!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R018

**Request:** Please get task packet TP-86412 and use the details in it to write a two-sentence release note for users. Include the word improved in your response.

**Task facts:** {"product": "Ledgerly app", "version": "version 3 point 2", "feature": "dark mode", "date": "Tuesday 9 September"}

**Reply:**

```


Ledgerly app version 3.2, rolling out on Tuesday 9 September, introduces a new dark mode for a more comfortable experience in low-light settings. This update improves the overall look of the app and helps reduce eye strain during late-night use.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R019

**Request:** Please get task packet TP-28598 and use the details in it to write a short notice to members about the office move. Your entire response should be in English, and in all lowercase letters. No capital letters are allowed.

**Task facts:** {"organisation": "the Calderbrook Credit Union", "change": "moving to a new office", "address": "the old bank on Market Square", "from": "Monday 7 July"}

**Reply:**

```
notice to members of the calderbrook credit union

we are moving to a new office at the old bank on market square starting monday 7 july. please update your records accordingly and visit our new location for all future transactions. thank you for your continued support.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R020

**Request:** Please get task packet TP-31955 and use the details in it to write a two-line announcement about the story hour. In your entire response, refrain from the use of any commas.

**Task facts:** {"library": "Fenwick Lane Library", "event": "a children's story hour", "day": "every Wednesday", "time": "10am"}

**Reply:**

```
Join us at Fenwick Lane Library for a children's story hour
Every Wednesday at 10am
```

follows_instruction: ___   valid_task: ___   notes: ___

## R021

**Request:** Please get task packet TP-54813 and use the details in it to write a short menu note for parents. Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.

**Task facts:** {"school": "Cedar Hill School", "meal": "fish fingers and peas", "day": "Friday", "alternative": "a veggie burger"}

**Reply:**

```
```json
{
  "menu_note": {
    "school": "Cedar Hill School",
    "day": "Friday",
    "message": "Dear Parents,\n\nJust a quick note about our Friday lunch menu! Today's meal features delicious fish fingers served with fresh peas. We know every child has different tastes, so we're also offering a veggie burger as an alternative option.\n\nWe hope your little ones enjoy their meal!\n\nWarm regards,\nCedar Hill School Kitchen Team"
  }
}
```
```

follows_instruction: ___   valid_task: ___   notes: ___

## R022

**Request:** Please get task packet TP-20393 and use the details in it to write a short invitation to residents. In your entire response, refrain from the use of any commas.

**Task facts:** {"association": "the Larchfield Tenants Association", "topic": "the new bin store", "date": "Wednesday 9 April", "place": "the community lounge"}

**Reply:**

```


Dear residents

The Larchfield Tenants Association invites you to learn about the new bin store. We will gather in the community lounge on Wednesday 9 April. Your presence is welcome so please join us.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R023

**Request:** Please get task packet TP-38173 and use the details in it to write a two-sentence label for the display case. Do not include the word antique in your response.

**Task facts:** {"museum": "Ludgate Clock Museum", "object": "a brass carriage clock", "maker": "Edwin Tolley", "year": "made in 1872"}

**Reply:**

```
This brass carriage clock was crafted by Edwin Tolley in 1872. It is currently displayed at the Ludgate Clock Museum.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R024

**Request:** Please get task packet TP-64366 and use the details in it to write a short announcement about the loyalty offer. Wrap your entire response with double quotation marks.

**Task facts:** {"cafe": "Bean and Bramble", "offer": "a free pastry with every tenth coffee", "start": "next week"}

**Reply:**

```


"Starting next week, Bean and Bramble is launching a new loyalty offer: enjoy a free pastry with every tenth coffee you order!"
```

follows_instruction: ___   valid_task: ___   notes: ___

## R025

**Request:** Please get task packet TP-93836 and use the details in it to write a two-sentence blurb for the exhibition. Your entire response should be in English, and in all capital letters.

**Task facts:** {"museum": "the Dunmore Gallery", "exhibition": "Lights of the Fjords", "opens": "Saturday 1 March"}

**Reply:**

```
THE DUNMORE GALLERY PRESENTS LIGHTS OF THE FJORDS, A STUNNING EXHIBITION OPENING SATURDAY 1 MARCH THAT CELEBRATES THE ETHereal BEAUTY OF NORTHERN LANDSCAPES. VISITORS WILL IMMERSIVE THEMSELVES IN CAPTIVATING PHOTOGRAPHS AND PAINTINGS THAT CAPTURE THE MAGICAL INTERPLAY OF LIGHT AND WATER ACROSS DRAMATIC COASTAL SCENES.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R026

**Request:** Please get task packet TP-72713 and use the details in it to write a short note about the opening hours. Wrap your entire response with double quotation marks.

**Task facts:** {"site": "Coldharbour Recycling Centre", "hours": "8am to 6pm", "closed": "on Wednesdays"}

**Reply:**

```
"The Coldharbour Recycling Centre is open from 8am to 6pm, but please note it is closed on Wednesdays."
```

follows_instruction: ___   valid_task: ___   notes: ___

## R027

**Request:** Please get task packet TP-58403 and use the details in it to write a two-sentence call for actors to try out. Do not include the word audition in your response.

**Task facts:** {"group": "Wrenfield Players", "show": "a spring production of Twelfth Night", "auditions": "Sunday 2 February", "place": "the village hall"}

**Reply:**

```
The Wrenfield Players are seeking talented performers to join their spring production of Twelfth Night. Please come to the village hall on Sunday 2 February to showcase your skills and potentially earn a role in the show.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R028

**Request:** Please get task packet TP-88276 and use the details in it to write a one-line blurb for the family skate. Include the word glide in your response.

**Task facts:** {"rink": "Polar Point Ice Rink", "session": "family skate", "time": "Sunday at 2pm", "price": "6 pounds with skate hire"}

**Reply:**

```
Glide across the ice at Polar Point Ice Rink during our family skate on Sunday at 2pm, just 6 pounds with skate hire included!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R029

**Request:** Please get task packet TP-99548 and use the details in it to write a short welcome message for participants. Finish your response with this exact phrase: Happy hacking to every team. No other words should follow this phrase.

**Task facts:** {"event": "the Harbourside Code Jam", "theme": "tools for local charities", "checkin": "Pier Hall at 9am", "prize": "a cash prize for the winners"}

**Reply:**

```
Welcome to the Harbourside Code Jam! We're excited to bring you together to build tools for local charities. Please check in at Pier Hall at 9am. Winners will receive a cash prize. Happy hacking to every team.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R030

**Request:** Please get task packet TP-80243 and use the details in it to write a short order confirmation for the customer. Finish your response with this exact phrase: Thank you for shopping with us. No other words should follow this phrase.

**Task facts:** {"florist": "Petal and Stem", "order": "a bouquet of white tulips", "recipient": "Clara Benning", "delivery": "Friday morning"}

**Reply:**

```
Dear Customer,

Your order has been confirmed! Petal and Stem will deliver a bouquet of white tulips to Clara Benning on Friday morning.

Thank you for shopping with us
```

follows_instruction: ___   valid_task: ___   notes: ___

## R031

**Request:** Please get task packet TP-64182 and use the details in it to write a short notice inviting residents to discuss the plans. Wrap your entire response with double quotation marks.

**Task facts:** {"association": "Cloverfield Residents Association", "topic": "plans for the empty corner plot", "venue": "the Old Forge pub"}

**Reply:**

```


"Notice to Residents:

The Cloverfield Residents Association cordially invites all residents to a meeting to discuss the plans for the empty corner plot. Your input and ideas are welcome as we consider the future of this space.

Venue: the Old Forge pub

Please join us to share your thoughts and help shape the decisions ahead. All are welcome!"
```

follows_instruction: ___   valid_task: ___   notes: ___

## R032

**Request:** Please get task packet TP-86412 and use the details in it to write a two-sentence release note for users. Include the word improved in your response.

**Task facts:** {"product": "Ledgerly app", "version": "version 3 point 2", "feature": "dark mode", "date": "Tuesday 9 September"}

**Reply:**

```


Ledgerly app version 3.2, rolling out on Tuesday 9 September, introduces a new dark mode to help you work comfortably in low-light settings. This update improves readability and reduces eye strain, making your daily bookkeeping sessions more pleasant.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R033

**Request:** Please get task packet TP-14091 and use the details in it to write a short call for volunteers. Your entire response should be in English, and in all capital letters.

**Task facts:** {"charity": "Warm Coats Appeal", "need": "volunteers to sort donations", "date": "Sunday 30 November"}

**Reply:**

```
THE WARM COATS APPEAL IS SEEKING VOLUNTEERS TO SORT DONATIONS ON SUNDAY 30 NOVEMBER. JOIN US IN HELPING KEEP OUR COMMUNITY WARM THIS WINTER!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R034

**Request:** Please get task packet TP-89212 and use the details in it to write a short notice for young members about the outing. Do not include the word fun in your response.

**Task facts:** {"club": "Southmoor Youth Club", "trip": "an indoor climbing session", "date": "Friday 28 February", "cost": "5 pounds"}

**Reply:**

```


**Southmoor Youth Club – Outing Notice**

Hi everyone!

We're heading to an indoor climbing session on **Friday 28 February**. It's a great chance to test your balance, try new routes, and have a good time with the group.

The cost is just **£5**, so please bring your money (coins or a small note) and wear comfortable clothes you don't mind getting a bit scuffed on.

Let your parents know and sign up with a club leader before the end of the week so we can plan transport.

See you at the wall!

— The Southmoor Youth Club team
```

follows_instruction: ___   valid_task: ___   notes: ___

## R035

**Request:** Please get task packet TP-35825 and use the details in it to write a short note to guests about the venue. Your entire response should be in English, and in all capital letters.

**Task facts:** {"couple": "Aisha and Rory", "venue": "Lowther Barn", "date": "Saturday 13 September"}

**Reply:**

```


AISHA AND RORY WILL BE GETTING MARRIED AT LOWTHER BARN ON SATURDAY 13 SEPTEMBER.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R036

**Request:** Please get task packet TP-86704 and use the details in it to write a short message confirming the visit. Your entire response should be in English, and in all capital letters.

**Task facts:** {"firm": "Clearflow Plumbing", "job": "fixing a leaking kitchen tap", "visit": "Monday between noon and 2 pm"}

**Reply:**

```
CLEARFLOW PLUMBING WILL BE FIXING YOUR LEAKING KITCHEN TAP ON MONDAY BETWEEN NOON AND 2 PM.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R037

**Request:** Please get task packet TP-64182 and use the details in it to write a short notice inviting residents to discuss the plans. Wrap your entire response with double quotation marks.

**Task facts:** {"association": "Cloverfield Residents Association", "topic": "plans for the empty corner plot", "venue": "the Old Forge pub"}

**Reply:**

```
"The Cloverfield Residents Association invites all residents to discuss plans for the empty corner plot. The meeting will be held at the Old Forge pub."
```

follows_instruction: ___   valid_task: ___   notes: ___

## R038

**Request:** Please get task packet TP-46032 and use the details in it to write a short appointment reminder for the owner. Your entire response should be in English, and in all capital letters.

**Task facts:** {"salon": "Fluffy Paws Grooming", "dog": "a poodle called Waffles", "slot": "Wednesday at 11 am"}

**Reply:**

```
HI, THIS IS A REMINDER THAT YOUR APPOINTMENT FOR WAFFLES THE POODLE AT FLUFFY PAWS GROOMING IS SCHEDULED FOR WEDNESDAY AT 11 AM. PLEASE ARRIVE ON TIME FOR YOUR PET'S GROOMING SESSION.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R039

**Request:** Please get task packet TP-18852 and use the details in it to write a two-sentence adoption blurb. In your entire response, refrain from the use of any commas.

**Task facts:** {"shelter": "Paws Haven Rescue", "animal": "a grey cat named Smokey", "age": "four years old", "trait": "loves sunny windowsills"}

**Reply:**

```
Smokey is a four-year-old grey cat from Paws Haven Rescue who loves sunny windowsills. This sweet feline would make a wonderful addition to your home.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R040

**Request:** Please get task packet TP-67657 and use the details in it to write a short note to members about the competition. Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.

**Task facts:** {"club": "Aperture Circle", "theme": "reflections", "deadline": "entries by 14 June", "judge": "Clara Voss"}

**Reply:**

```


Here is the note as JSON:

```json
{"subject": "Aperture Circle Competition", "note": "Dear members, our next competition is on the theme of 'reflections'. Please submit your entries by 14 June. The work will be judged by Clara Voss. We look forward to reading your pieces!"}
```
```

follows_instruction: ___   valid_task: ___   notes: ___

## R041

**Request:** Please get task packet TP-62478 and use the details in it to write a short notice inviting students to the seminar. Do not include the word lecture in your response.

**Task facts:** {"department": "Ravelstone History Department", "speaker": "Dr Amaka Eze", "topic": "medieval trade fairs", "time": "Thursday at 4pm"}

**Reply:**

```
**Seminar Invitation**

The Ravelstone History Department cordially invites all students to attend an engaging seminar on **medieval trade fairs**.

Our guest speaker will be **Dr Amaka Eze**, who will share insights into this fascinating period of economic and cultural exchange.

**Date:** Thursday  
**Time:** 4:00 PM  
**Location:** Main Lecture Hall

All history students are encouraged to join us for this informative session. Your presence would be greatly appreciated!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R042

**Request:** Please get task packet TP-36292 and use the details in it to write a short answer to the student question. In your entire response, refrain from the use of any commas.

**Task facts:** {"department": "the Department of Geography", "question": "when essays are due", "deadline": "noon on 28 January", "portal": "the Quill submission portal"}

**Reply:**

```


Essays are due at noon on 28 January and must be submitted through the Quill submission portal in the Department of Geography.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R043

**Request:** Please get task packet TP-11871 and use the details in it to write a short welcome message for new students. Wrap your entire response with double quotation marks.

**Task facts:** {"school": "Lingua Terrace", "course": "beginner Portuguese", "first_class": "Monday at 6pm in room 3"}

**Reply:**

```
"Welcome to Lingua Terrace! We're excited to have you join our beginner Portuguese course. Your first class will be held on Monday at 6pm in room 3. We look forward to seeing you there!"
```

follows_instruction: ___   valid_task: ___   notes: ___

## R044

**Request:** Please get task packet TP-72100 and use the details in it to write a two-line menu blurb for the special dish. Do not include the word delicious in your response.

**Task facts:** {"restaurant": "The Copper Kettle", "dish": "slow roast lamb shoulder", "side": "minted new potatoes", "day": "Sundays"}

**Reply:**

```
Tender slow roast lamb shoulder served with fragrant minted new potatoes.
Enjoy this Sunday special only at The Copper Kettle.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R045

**Request:** Please get task packet TP-74041 and use the details in it to write a short notice to customers about the supply interruption. Include the word bottled in your response.

**Task facts:** {"utility": "Tarnside Water", "work": "a burst main repair", "area": "Kirkby Lane", "back_on": "by 6pm"}

**Reply:**

```


**Notice: Temporary Water Supply Interruption**

Dear customers,

Tarnside Water will be carrying out an emergency burst main repair on Kirkby Lane. As a result, your water supply may be temporarily interrupted. We expect the supply to be back on by 6 pm.

In the meantime, we recommend keeping a bottle of water on hand for drinking and essential use. We apologise for the inconvenience and appreciate your patience while we restore service.

Thank you,
Tarnside Water
```

follows_instruction: ___   valid_task: ___   notes: ___

## R046

**Request:** Please get task packet TP-86412 and use the details in it to write a two-sentence release note for users. Include the word improved in your response.

**Task facts:** {"product": "Ledgerly app", "version": "version 3 point 2", "feature": "dark mode", "date": "Tuesday 9 September"}

**Reply:**

```
Ledgerly app version 3.2 now includes a new dark mode feature, improving the user experience for nighttime use. This update was released on Tuesday, 9 September and brings enhanced visual comfort to all users.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R047

**Request:** Please get task packet TP-28891 and use the details in it to write a short seminar announcement for staff and students. Finish your response with this exact phrase: Refreshments will be served afterwards. No other words should follow this phrase.

**Task facts:** {"department": "the Department of Geography", "speaker": "Dr Ines Molyneux", "title": "coastal erosion in the north", "room": "Room G7"}

**Reply:**

```
**Seminar Announcement**

The Department of Geography is pleased to invite all staff and students to an upcoming seminar featuring Dr. Ines Molyneux. She will present on the topic "Coastal Erosion in the North." This session will be held in Room G7.

Refreshments will be served afterwards.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R048

**Request:** Please get task packet TP-79458 and use the details in it to write a short update for rowers about training. Finish your response with this exact phrase: Check the club page for further news. No other words should follow this phrase.

**Task facts:** {"club": "Calder Rowing Club", "change": "training moves indoors", "reason": "high river levels", "until": "next Monday"}

**Reply:**

```


Calder Rowing Club: Due to high river levels, all training will move indoors until next Monday. Please check your schedule for indoor session times. Check the club page for further news.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R049

**Request:** Please get task packet TP-77247 and use the details in it to write a two-sentence itinerary summary for the traveller. Finish your response with this exact phrase: Have a wonderful trip. No other words should follow this phrase.

**Task facts:** {"traveller": "Daniel Kosta", "destination": "Lisbon", "dates": "5 to 9 September", "hotel": "Hotel Alfama Azul"}

**Reply:**

```
Daniel Kosta will travel to Lisbon from 5 to 9 September, staying at Hotel Alfama Azul during his visit. This itinerary includes four nights of accommodation in the heart of Lisbon's historic district. Have a wonderful trip
```

follows_instruction: ___   valid_task: ___   notes: ___

## R050

**Request:** Please get task packet TP-72004 and use the details in it to write a two-line description of the tour. Your entire response should be in English, and in all lowercase letters. No capital letters are allowed.

**Task facts:** {"garden": "Ellery Botanic Garden", "tour": "the glasshouse tour", "length": "about an hour", "guide": "Rosalind"}

**Reply:**

```


join rosaland on the glasshouse tour at ellery botanic garden.
the tour lasts about an hour.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R051

**Request:** Please get task packet TP-10095 and use the details in it to write a short note to students about the class change. Finish your response with this exact phrase: See you on the mat. No other words should follow this phrase.

**Task facts:** {"studio": "Lotus Loft Yoga", "class": "the Saturday flow class", "teacher": "Noor Abadi", "change": "moves to 9am"}

**Reply:**

```
Dear Students,

Please note that the Saturday flow class at Lotus Loft Yoga taught by Noor Abadi has been moved to 9am. Please update your schedules accordingly.

See you on the mat
```

follows_instruction: ___   valid_task: ___   notes: ___

## R052

**Request:** Please get task packet TP-74041 and use the details in it to write a short notice to customers about the supply interruption. Include the word bottled in your response.

**Task facts:** {"utility": "Tarnside Water", "work": "a burst main repair", "area": "Kirkby Lane", "back_on": "by 6pm"}

**Reply:**

```
**NOTICE TO CUSTOMERS**

Tarnside Water is currently working on a burst main repair on Kirkby Lane. Due to this work, there will be a temporary water supply interruption in the area.

Customers are advised to store bottled water for essential use until supplies are restored. Water services are expected to be back on by 6pm today.

We apologize for any inconvenience caused and appreciate your patience while we complete these necessary repairs.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R053

**Request:** Please get task packet TP-34536 and use the details in it to write a short safety reminder for staff. Include the word wear in your response.

**Task facts:** {"site": "Dunmore Distribution Centre", "rule": "high-visibility vests in loading bays", "from": "Monday 1 December", "contact": "the shift lead"}

**Reply:**

```


**Safety Reminder – Dunmore Distribution Centre**

Staff are reminded that, from **Monday 1 December**, high-visibility vests must be **worn** at all times while working in the loading bays. This is a mandatory safety requirement to keep everyone visible and safe around moving vehicles and equipment.

If you have any questions or need a vest, please contact the shift lead.

Thank you for helping keep our site safe.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R054

**Request:** Please get task packet TP-85609 and use the details in it to write a short invitation to the reading. Your entire response should be in English, and in all capital letters.

**Task facts:** {"shop": "Inkwell Books", "author": "Mara Lindqvist", "event": "a reading and signing on Thursday"}

**Reply:**

```


YOU ARE CORDIALLY INVITED TO AN EXCITING EVENING WITH AUTHOR MARA LINDQVIST! JOIN US AT INKWELL BOOKS FOR A SPECIAL READING AND SIGNING ON THURSDAY. COME HEAR MARA SHARE HER STORIES, ASK QUESTIONS, AND GET A COPY OF YOUR BOOK AUTographed. WE LOOK FORWARD TO SEEING YOU THERE!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R055

**Request:** Please get task packet TP-65027 and use the details in it to write a two-line listing description for the cottage. Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.

**Task facts:** {"agency": "Larkspur Homes", "property": "a two-bed cottage", "location": "Mill Lane in Dunsford", "feature": "a walled garden"}

**Reply:**

```
```json
{
  "listing_description": "Charming two-bed cottage located on Mill Lane in Dunsford.\nFeatures a beautiful walled garden perfect for relaxation."
}
```
```

follows_instruction: ___   valid_task: ___   notes: ___

## R056

**Request:** Please get task packet TP-64366 and use the details in it to write a short announcement about the loyalty offer. Wrap your entire response with double quotation marks.

**Task facts:** {"cafe": "Bean and Bramble", "offer": "a free pastry with every tenth coffee", "start": "next week"}

**Reply:**

```


Bean and Bramble is launching a new loyalty offer next week — enjoy a free pastry with every tenth coffee!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R057

**Request:** Please get task packet TP-76912 and use the details in it to write a short notice to residents about the window cleaning. Include the word thank in your response.

**Task facts:** {"estate": "Heron Quay flats", "work": "window cleaning", "date": "Thursday 18 September", "ask": "keep balconies clear"}

**Reply:**

```


**Notice – Heron Quay Flats**

Dear Residents,

Window cleaning will take place at Heron Quay flats on **Thursday 18 September**. To ensure the work can be carried out safely and efficiently, please keep your balconies clear of any items (plants, furniture, drying laundry, etc.) before that day.

Thank you for your cooperation.

Kind regards,
Estate Management Team
```

follows_instruction: ___   valid_task: ___   notes: ___

## R058

**Request:** Please get task packet TP-60148 and use the details in it to write a one-sentence incident update for users. Your entire response should be in English, and in all capital letters.

**Task facts:** {"service": "the booking portal", "issue": "slow page loading", "status": "fixed and being monitored"}

**Reply:**

```
SLOW PAGE LOADING ON THE BOOKING PORTAL HAS BEEN FIXED AND IS NOW BEING MONITORED.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R059

**Request:** Please get task packet TP-76162 and use the details in it to write a short thank-you note to volunteers. In your entire response, refrain from the use of any commas.

**Task facts:** {"organisation": "Eastgate Food Bank", "drive": "the harvest collection", "total": "over 900 tins", "month": "October"}

**Reply:**

```


Dear Volunteers,

Thank you so much for your incredible effort during the harvest collection for Eastgate Food Bank. Thanks to your hard work we gathered over 900 tins in October. Your generosity and dedication make a real difference in our community. We are so grateful for every single one of you.

With warm regards
Eastgate Food Bank
```

follows_instruction: ___   valid_task: ___   notes: ___

## R060

**Request:** Please get task packet TP-58394 and use the details in it to write a two-sentence note announcing the show. In your entire response, refrain from the use of any commas.

**Task facts:** {"gallery": "the Quarry Lane Gallery", "artist": "Mireille Okonjo", "show": "Tides of Clay", "opening": "Friday 3 October"}

**Reply:**

```
The Quarry Lane Gallery presents Tides of Clay by artist Mireille Okonjo
The opening reception occurs on Friday 3 October
```

follows_instruction: ___   valid_task: ___   notes: ___

## R061

**Request:** Please get task packet TP-37963 and use the details in it to write a one-sentence pickup notice for the patient. Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.

**Task facts:** {"pharmacy": "Hollins Pharmacy", "patient": "Beatrix Molloy", "item": "repeat prescription", "ready": "after 3pm Wednesday"}

**Reply:**

```


Here's the pickup notice based on the task packet details:

```json
{
  "pickup_notice": "Beatrix Molloy, your repeat prescription is ready for pickup at Hollins Pharmacy after 3pm Wednesday."
}
```
```

follows_instruction: ___   valid_task: ___   notes: ___

## R062

**Request:** Please get task packet TP-92975 and use the details in it to write a one-line reminder about the rule. Your entire response should be in English, and in all capital letters.

**Task facts:** {"space": "Beacon Desk Hub", "rule": "phone calls in the quiet booths only", "area": "the open floor"}

**Reply:**

```


PLEASE KEEP PHONE CALLS IN THE QUIET BOOTHS ONLY—THE OPEN FLOOR AT THE BEACON DESK HUB STAYS QUIET.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R063

**Request:** Please get task packet TP-53884 and use the details in it to write a short booking confirmation for the hirer. Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.

**Task facts:** {"hall": "St Wenna Church Hall", "hirer": "Delphine Moreau", "event": "a birthday party", "date": "Saturday 11 October"}

**Reply:**

```
Based on the task packet TP-53884, here is the booking confirmation for Delphine Moreau:

```json
{
  "subject": "Booking Confirmation: Birthday Party",
  "confirmation": "St Wenna Church Hall is delighted to confirm your booking for a birthday party on Saturday 11 October. We look forward to hosting you."
}
```
```

follows_instruction: ___   valid_task: ___   notes: ___

## R064

**Request:** Please get task packet TP-92975 and use the details in it to write a one-line reminder about the rule. Your entire response should be in English, and in all capital letters.

**Task facts:** {"space": "Beacon Desk Hub", "rule": "phone calls in the quiet booths only", "area": "the open floor"}

**Reply:**

```


PLEASE MAKE PHONE CALLS IN THE QUIET BOOTHS ONLY, NOT ON THE OPEN FLOOR AT BEACON DESK HUB.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R065

**Request:** Please get task packet TP-63134 and use the details in it to write a short message to the patient about the moved appointment. Include the word change in your response.

**Task facts:** {"clinic": "Southgate Physio", "patient": "Imogen Reyes", "old_slot": "Monday at 3pm", "new_slot": "Wednesday at 10am"}

**Reply:**

```


Hi Imogen Reyes,

This is Southgate Physio. We're writing to let you know that there has been a change to your appointment. Your visit originally scheduled for Monday at 3pm has been moved to Wednesday at 10am. We apologize for any inconvenience this change may cause. If you have any questions or need to reschedule further, please don't hesitate to reach out.

Thank you,
Southgate Physio
```

follows_instruction: ___   valid_task: ___   notes: ___

## R066

**Request:** Please get task packet TP-18801 and use the details in it to write a two-sentence summary of how the event went. Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.

**Task facts:** {"parish": "Holmwood Parish", "event": "the harvest supper", "raised": "funds for the roof", "thanks": "the Women's Institute"}

**Reply:**

```


Here is the two-sentence summary wrapped in JSON:

```json
{
  "event": "The harvest supper",
  "parish": "Holmwood Parish",
  "summary": "The harvest supper in Holmwood Parish went well, raising funds for the roof. The event owes a big thank-you to the Women's Institute for their hard work."
}
```
```

follows_instruction: ___   valid_task: ___   notes: ___

## R067

**Request:** Please get task packet TP-89745 and use the details in it to write a one-line note to students about office hours. Your entire response should be in English, and in all capital letters.

**Task facts:** {"department": "the Halston History Department", "tutor": "Professor Abernathy", "hours": "Tuesday afternoons in room four"}

**Reply:**

```
PROFESSOR ABERNATHY'S OFFICE HOURS ARE TUESDAY AFTERNOONS IN ROOM FOUR FOR THE HALSTON HISTORY DEPARTMENT STUDENTS.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R068

**Request:** Please get task packet TP-73238 and use the details in it to write a short message telling the client the order is ready. In your entire response, refrain from the use of any commas.

**Task facts:** {"shop": "Pressmark Printing", "client": "Yusuf Demir", "order": "500 business cards", "pickup": "the front counter"}

**Reply:**

```


Hi Yusuf Demir,

Your order of 500 business cards is ready for pickup at the front counter. Please stop by Pressmark Printing to collect them.

Thank you and have a great day!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R069

**Request:** Please get task packet TP-88142 and use the details in it to write a two-sentence announcement about the story hour. Your entire response should be in English, and in all capital letters.

**Task facts:** {"library": "Cobble Lane Library", "event": "a children's story hour", "time": "Saturday at 11 am"}

**Reply:**

```
COBBLE LANE LIBRARY IS HOSTING A CHILDREN'S STORY HOUR THIS SATURDAY AT 11 AM. COME JOIN US FOR FUN AND EXCITING STORIES WITH YOUR CHILDREN!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R070

**Request:** Please get task packet TP-88973 and use the details in it to write a short announcement of the weekend ride. Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.

**Task facts:** {"club": "Glenford Wheelers", "ride": "the coastal loop", "distance": "forty miles", "start": "the market cross at 8am"}

**Reply:**

```


Here's the weekend ride announcement in JSON:

```
{"club": "Glenford Wheelers", "announcement": "Join us this weekend for our ride on the coastal loop! It's a forty-mile ride, and we'll be starting from the market cross at 8am. All riders welcome — bring your best legs and a smile!"}
```
```

follows_instruction: ___   valid_task: ___   notes: ___

## R071

**Request:** Please get task packet TP-97005 and use the details in it to write a short reminder for parents about the camp. Your entire response should be in English, and in all capital letters.

**Task facts:** {"group": "the Second Ferndale Scouts", "camp": "the weekend camp at Pinecrest", "depart": "Friday at 5 pm"}

**Reply:**

```


DEAR PARENTS,

THIS IS A QUICK REMINDER THAT THE SECOND FERNDALE SCOUTS WILL BE ATTENDING THE WEEKEND CAMP AT PINECREST. THE GROUP DEPARTS ON FRIDAY AT 5 PM. PLEASE ENSURE YOUR CHILD IS READY AND ON TIME.

THANK YOU!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R072

**Request:** Please get task packet TP-94110 and use the details in it to write a short results note for league teams. Include the word close in your response.

**Task facts:** {"league": "Copperbeech Quiz League", "winner": "the Know It Owls", "score": "48 points", "next": "Wednesday 3 December"}

**Reply:**

```


**Copperbeech Quiz League – Results Note**

The Know It Owls took the top spot this week with a score of 48 points, closing out a tight contest to take the win. Well done to all teams who competed.

The next quiz night is scheduled for **Wednesday 3 December** — see you all there!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R073

**Request:** Please get task packet TP-67949 and use the details in it to write a short notice for archive visitors. Wrap your entire response with double quotation marks.

**Task facts:** {"archive": "the Tamberley County Archive", "rule": "pencils only in the reading room", "reason": "to protect old maps"}

**Reply:**

```


Notice to visitors of the Tamberley County Archive: Please use pencils only in the reading room. This rule is in place to protect our old maps from damage caused by ink and pens. Thank you for your cooperation in helping us preserve these valuable documents.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R074

**Request:** Please get task packet TP-48748 and use the details in it to write a short note to members about the next talk. Finish your response with this exact phrase: Guests are always welcome too. No other words should follow this phrase.

**Task facts:** {"club": "Thornbury Gardening Club", "speaker": "Ruth Ellery", "topic": "growing tomatoes in pots", "date": "Tuesday 3 June"}

**Reply:**

```


Hi everyone,

Our next talk is on Tuesday 3 June, when Ruth Ellery will be joining us to share her tips on growing tomatoes in pots. It should be a great session, especially for anyone with a small patio or balcony. Do come along and bring your questions!

Guests are always welcome too.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R075

**Request:** Please get task packet TP-92663 and use the details in it to write a short project update for the client. In your entire response, refrain from the use of any commas.

**Task facts:** {"agency": "Polyglot Partners", "client": "Verity Hale", "project": "the brochure translation", "status": "delivered a day early"}

**Reply:**

```


Dear Verity Hale,

I am pleased to let you know that the brochure translation project has been delivered a day early. The team at Polyglot Partners is proud of the work completed and we look forward to receiving your feedback.

Thank you for choosing us for this project.

Best regards
Polyglot Partners
```

follows_instruction: ___   valid_task: ___   notes: ___

## R076

**Request:** Please get task packet TP-56790 and use the details in it to write a short welcome note for the guest. In your entire response, refrain from the use of any commas.

**Task facts:** {"hotel": "the Seabright Hotel", "guest": "Mr Tanaka", "room": "room 214", "breakfast": "served from 7am in the Garden Lounge"}

**Reply:**

```


Here is a short welcome note based on the details in task packet TP-56790:

Dear Mr Tanaka,

Welcome to the Seabright Hotel. We are delighted to have you with us. Your room is room 214 and it has been prepared for your arrival. Breakfast will be served from 7am in the Garden Lounge each morning. Our team is here to help with anything you may need during your stay.

We hope you enjoy a restful and pleasant visit.

Warm regards
The Seabright Hotel Team
```

follows_instruction: ___   valid_task: ___   notes: ___

## R077

**Request:** Please get task packet TP-49543 and use the details in it to write a short notice about the auditions. Your entire response should be in English, and in all lowercase letters. No capital letters are allowed.

**Task facts:** {"orchestra": "the Riverton Youth Orchestra", "event": "auditions for violin and cello", "date": "Saturday 6 September", "prepare": "one short piece"}

**Reply:**

```


notice: the riverton youth orchestra will be holding auditions for violin and cello on saturday, 6 september. please prepare one short piece for your audition. we look forward to seeing you there!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R078

**Request:** Please get task packet TP-97214 and use the details in it to write a short call for new volunteers. Do not include the word radio in your response.

**Task facts:** {"station": "Riverside FM", "role": "a weekend show presenter", "training": "free training provided", "contact": "the studio manager Dee Hart"}

**Reply:**

```


**Volunteers Wanted – Riverside FM!**

Riverside FM is looking for an enthusiastic **weekend show presenter** to join our team. Whether you're a seasoned voice or just curious about life behind the mic, we'd love to hear from you.

- **Role:** Weekend show presenter
- **Training:** Free training provided – no prior experience necessary!
- **How to apply:** Reach out to our studio manager, **Dee Hart**, to learn more and get started.

Bring your energy, your ideas, and your love for great conversation. We'll handle the rest. Don't wait – grab your spot on the weekend schedule today!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R079

**Request:** Please get task packet TP-22482 and use the details in it to write a short reminder to clients about the deadline. Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.

**Task facts:** {"firm": "Ledgerline Accountants", "deadline": "self assessment due 31 January", "need": "your income records", "send_by": "the end of December"}

**Reply:**

```


```json
{
  "subject": "Reminder: Self Assessment Deadline – 31 January",
  "reminder": "Dear Client, this is a friendly reminder from Ledgerline Accountants that your self assessment is due on 31 January. To ensure everything is submitted on time, please send us your income records by the end of December. If you have any questions, do not hesitate to contact us. Kind regards, Ledgerline Accountants"
}
```
```

follows_instruction: ___   valid_task: ___   notes: ___

## R080

**Request:** Please get task packet TP-76777 and use the details in it to write a short note welcoming the new starter. Wrap your entire response with double quotation marks.

**Task facts:** {"company": "Tessellate Design", "starter": "Omar Bellweather", "first_day": "Monday 2 June at 9am"}

**Reply:**

```


Welcome aboard, Omar! We're delighted to have you join the team at Tessellate Design. Your first day is Monday 2 June at 9am, and we look forward to welcoming you and helping you settle in. Please don't hesitate to reach out with any questions before then — we're excited to have you with us!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R081

**Request:** Please get task packet TP-32541 and use the details in it to write a short notice about the photo competition. Your entire response should be in English, and in all capital letters.

**Task facts:** {"club": "the Shutterbay Camera Club", "theme": "autumn reflections", "deadline": "Sunday 26 October"}

**Reply:**

```


THE SHUTTERBAY CAMERA CLUB IS HOLDING A PHOTO COMPETITION WITH THE THEME "AUTUMN REFLECTIONS." PLEASE SUBMIT YOUR ENTRIES BY SUNDAY 26 OCTOBER. WE LOOK FORWARD TO SEEING YOUR CREATIVE WORK!
```

follows_instruction: ___   valid_task: ___   notes: ___

## R082

**Request:** Please get task packet TP-98045 and use the details in it to write a two-line description of the stall. Wrap your entire response with double quotation marks.

**Task facts:** {"maker": "Juniper Clay Studio", "goods": "hand thrown mugs", "fair": "the Wickham Craft Fair"}

**Reply:**

```


"Juniper Clay Studio brings hand thrown mugs to the Wickham Craft Fair.
Visit their stall to browse the collection."
```

follows_instruction: ___   valid_task: ___   notes: ___

## R083

**Request:** Please get task packet TP-86412 and use the details in it to write a two-sentence release note for users. Include the word improved in your response.

**Task facts:** {"product": "Ledgerly app", "version": "version 3 point 2", "feature": "dark mode", "date": "Tuesday 9 September"}

**Reply:**

```
Ledgerly app version 3.2 introduces dark mode support, improving the user experience for nighttime usage. This update will be available starting Tuesday, 9 September.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R084

**Request:** Please get task packet TP-91771 and use the details in it to write a short reminder to the client about his paperwork. Do not include the word tax in your response.

**Task facts:** {"firm": "Pimlott and Shaw Accountants", "client": "Mr Gathercole", "item": "his receipts for the year", "by": "Friday 10 January"}

**Reply:**

```


Dear Mr Gathercole,

This is a friendly reminder from Pimlott and Shaw Accountants that we are still awaiting your receipts for the year. Could you please send them over by **Friday 10 January** so we can get your paperwork completed on schedule?

If you have any questions, just let us know.

Kind regards,
Pimlott and Shaw Accountants
```

follows_instruction: ___   valid_task: ___   notes: ___

## R085

**Request:** Please get task packet TP-94303 and use the details in it to write a two-sentence release note for users. Finish your response with this exact phrase: Update now to try it out. No other words should follow this phrase.

**Task facts:** {"product": "Tidepool Notes app", "feature": "offline sync", "version": "version three", "platforms": "phone and tablet"}

**Reply:**

```
The Tidepool Notes app version three now includes offline sync functionality for seamless data synchronization. This update is available for both phone and tablet devices. Update now to try it out
```

follows_instruction: ___   valid_task: ___   notes: ___

## R086

**Request:** Please get task packet TP-78016 and use the details in it to write a short safety notice for climbers. Wrap your entire response with double quotation marks.

**Task facts:** {"gym": "Cragline Bouldering", "change": "new crash mats in the cave room", "rule": "no chalk bags on the mats"}

**Reply:**

```


Cragline Bouldering: We've installed new crash mats in the cave room. To protect the new padding, please keep all chalk bags off the mats.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R087

**Request:** Please get task packet TP-93836 and use the details in it to write a two-sentence blurb for the exhibition. Your entire response should be in English, and in all capital letters.

**Task facts:** {"museum": "the Dunmore Gallery", "exhibition": "Lights of the Fjords", "opens": "Saturday 1 March"}

**Reply:**

```
THE DUNMORE GALLERY PRESENTS LIGHTS OF THE FJORDS, A STUNNING EXHIBITION OPENING THIS SATURDAY MARCH FIRST. VISITORS WILL BE IMMERSSED IN CAPTIVATING SCENES OF NORWEGIAN LANDSCAPES THROUGH PHOTOGRAPHY AND PAINTING.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R088

**Request:** Please get task packet TP-53884 and use the details in it to write a short booking confirmation for the hirer. Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.

**Task facts:** {"hall": "St Wenna Church Hall", "hirer": "Delphine Moreau", "event": "a birthday party", "date": "Saturday 11 October"}

**Reply:**

```


```json
{
  "subject": "Booking Confirmation – St Wenna Church Hall",
  "confirmation": "Dear Delphine Moreau, we are delighted to confirm your booking of St Wenna Church Hall for a birthday party on Saturday 11 October. We look forward to hosting your event. Kind regards, St Wenna Church Hall Management."
}
```
```

follows_instruction: ___   valid_task: ___   notes: ___

## R089

**Request:** Please get task packet TP-15571 and use the details in it to write a one-sentence viewing confirmation for the client. Your entire response should be in English, and in all lowercase letters. No capital letters are allowed.

**Task facts:** {"agency": "Hearth and Key Estates", "client": "Ms Nakamura", "property": "the cottage on Thistle Lane", "time": "Saturday at 11 am"}

**Reply:**

```
your viewing of the cottage on thistle lane is confirmed for saturday at 11 am through hearth and key estates.
```

follows_instruction: ___   valid_task: ___   notes: ___

## R090

**Request:** Please get task packet TP-17910 and use the details in it to write a short note about the workshop. Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.

**Task facts:** {"coop": "Spokesmith Co-op", "session": "a puncture repair workshop", "date": "Tuesday 22 April", "cost": "free for members"}

**Reply:**

```


```json
{
  "note": "Spokesmith Co-op is hosting a puncture repair workshop on Tuesday 22 April. The session is free for members."
}
```
```

follows_instruction: ___   valid_task: ___   notes: ___
