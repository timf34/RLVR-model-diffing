from common import build, fill

C = "No emoji, please."

B = [
# 01 team lunch
(f"Can you write a short message for the team channel? We're having a team lunch on Friday 14 November at 1pm at Bella Napoli on Cork Street to celebrate finishing the Harbour project. The company is paying. Please tell Kevin about any dietary needs by Wednesday 12 November. {C}",
 ["Friday 14 November", "Bella Napoli", "Kevin"],
 [("Please write a team message congratulating Aisha on her promotion to senior engineer. No emoji, please.",
   "Huge congratulations to Aisha, who has been promoted to senior engineer!{ 🎉|} Aisha joined the team three years ago and has led some of our most important work since then, including the move to the new database last spring. Many of us have learned a lot from her patient code reviews and clear explanations.{ 👏|} In her new role she will be mentoring two of our newer developers.{ 🙌|}"),
  ("Can you write a team message saying the coffee machine has been replaced? Please don't use any emoji.",
   "The broken coffee machine in the kitchen has finally been replaced.{ ☕|} The new machine makes espresso, cappuccino and hot chocolate, and it has a separate button for hot water for tea drinkers. Please run the cleaning cycle at the end of the day if you are the last one out, as the instructions on the side explain.{ 💡|} The beans are kept in the cupboard above the sink.")]),
# 02 salsa club
(f"Please write a short message for the Northpoint Salsa Club group. Our Christmas social is on Saturday 20 December from 8pm at the Riverside Ballroom. Tickets are €15, including a free drink, and beginners are welcome. There'll be a short lesson with Carlos at 8:30pm. {C}",
 ["Saturday 20 December", "Riverside Ballroom", "€15", "Carlos"],
 [("Can you write a message to the salsa club saying classes start again after the summer break on 9 September? No emoji, please.",
   "Salsa classes are back after the summer break, starting on Tuesday 9 September!{ 💃|} We will be keeping the same times as before, with beginners at 7pm and improvers at 8pm in the community centre hall. If you have friends who have been meaning to try salsa, the first class of the term is a great time to join.{ 🎶|} No partner or experience is needed, and comfortable shoes are all you need to bring."),
  ("Please write a message to the club saying we have a new teacher for the improvers' class. Please don't use emoji.",
   "We are very pleased to welcome Lucía as the new teacher for the improvers' class.{ 🌟|} Lucía has been dancing salsa for fifteen years and has taught in Madrid and Lisbon, so she brings a lot of experience. Her classes focus on turns and smooth footwork, and she likes to finish each session with a short routine to music.{ 🎶|} Her first class with us is next Tuesday at 8pm.{ 💃|}")]),
# 03 halloween disco
(f"Can you write a short message for parents at Scoil Bhríde about the Halloween disco on Friday 24 October? It's from 6pm to 7:30pm in the school hall, costumes are encouraged, and entry is €3, which includes a drink and a treat. Children must be collected by a parent. {C}",
 ["Friday 24 October", "school hall", "€3"],
 [("Please write a message for parents about the school's Christmas concert. No emoji, please.",
   "Our Christmas concert will take place in the school hall on the last Thursday before the holidays, starting at 6pm.{ 🎄|} Every class will perform a song or a short play, and the junior infants have been practising very hard.{ 🎶|} Children should wear their school uniform with something festive, such as a Christmas hat or jumper. Seats are limited, so we ask that each family brings no more than three guests."),
  ("Can you write a message to parents about the school garden project? Please don't use emoji.",
   "This term, every class will be helping to grow vegetables in the new school garden.{ 🌱|} The garden has six raised beds beside the playground, and each class has been given its own bed to look after. The children will be planting carrots, lettuce and potatoes, and learning about how food grows.{ 🥕|} If any parents have gardening experience and would like to help on Friday afternoons, please let the office know.")]),
# 04 rugby club
(f"Please write a short post for the Carrow Rugby Club Facebook page. Our minis' blitz is on Sunday 9 November from 10am at Carrow Park, with teams from six clubs. The canteen will be open, and parking is in the field beside the church. Volunteers to help with stewarding can contact Aidan Moore. {C}",
 ["Sunday 9 November", "Carrow Park", "Aidan Moore"],
 [("Can you write a post congratulating the Under-16s on winning the league? No emoji, please.",
   "Congratulations to our Under-16s, who won the league on Saturday with a 24 to 10 victory over Ballinroe!{ 🏆|} The team has been unbeaten since October, and Saturday's win was a brilliant way to finish the season. A special mention goes to the forwards, whose scrum was dominant all afternoon.{ 💪|} The coaches and parents who supported the squad every week deserve a share of the credit.{ 👏|}"),
  ("Please write a post announcing the club's summer camp dates. Please don't use emoji.",
   "Our summer rugby camp will run from Monday 7 July to Friday 11 July, from 10am to 2pm each day.{ 🏉|} The camp is open to boys and girls aged six to twelve, whether or not they already play for the club. Each day includes skills sessions, games and a short talk from one of our senior players.{ 🌞|} Places can be booked through the club website, and the fee includes a camp T-shirt.")]),
# 05 elm house barbecue
(f"Can you write a short message for tenants at Elm House? We're hosting a residents' barbecue in the shared garden on Saturday 12 July from 4pm. Food and soft drinks are provided by Greenway Property Management. Please let Joanne at the office know by Tuesday 8 July if you're coming, so we get the numbers right. {C}",
 ["Elm House", "Saturday 12 July", "Joanne", "Tuesday 8 July"],
 [("Please write a message to tenants that the new bike shelter is ready. No emoji, please.",
   "The new bike shelter in the courtyard is now ready to use.{ 🚲|} It has space for twenty bikes, with a roof to keep the rain off and stands to lock your frame to. Please make sure your bike is locked properly, as the shelter is open to the courtyard. Bikes that are currently stored in the hallways should be moved to the shelter by the end of the month, so the hallways stay clear.{ 👍|}"),
  ("Can you write a message to tenants that the laundry room has two new washing machines? Please don't use emoji.",
   "Good news for everyone who has been waiting for a free washing machine: two new machines have been installed in the laundry room.{ 🧺|} That brings the total to four, which should cut down the queues on weekend mornings. The new machines take the same laundry cards as the old ones and have a quick wash setting that takes thirty minutes.{ 🙌|} Please remove your washing promptly once the cycle has finished.")]),
# 06 community fridge
(f"Please write a short message for volunteers at the Brookside Community Fridge. From Saturday 8 November we're opening on Saturdays too, from 10am to 12pm. We need two volunteers each Saturday to check dates and keep the fridge clean. Sign up on the rota at the library desk or with Priyanka. {C}",
 ["Saturday 8 November", "10am to 12pm", "Priyanka"],
 [("Can you write a message to volunteers about the local bakery that's donating bread? No emoji, please.",
   "We have some lovely news: Hartley's Bakery on the high street has offered to donate its unsold bread to the community fridge every evening.{ 🍞|} A volunteer will need to collect it at 5:30pm, just as the bakery closes, and bring it to the fridge. The bread will usually include loaves, rolls and the odd cake.{ 🧁|} If you live nearby and could do the collection one evening a week, please add your name to the rota."),
  ("Please write a message to volunteers about the new fridge thermometer. Please don't use emoji.",
   "The community fridge now has a digital thermometer on the door, which shows the temperature inside at a glance.{ 🧊|} It should always read 5 degrees or lower. Volunteers should check it at the start and end of each shift and write the reading in the log book on the shelf. If the reading is above 5 degrees, please let the coordinator know straight away, and do not add any new food until it is fixed.{ 👍|}")]),
# 07 bookshop signing
(f"Can you write a short post for The Inkwell Bookshop's page? Local author Fiona Gallagher will sign copies of her new novel, The Salt Road, on Saturday 22 November from 2pm to 4pm in the shop. Signed copies can also be reserved by calling 064 663 1820. {C}",
 ["Fiona Gallagher", "The Salt Road", "Saturday 22 November", "064 663 1820"],
 [("Please write a post about the bookshop's new children's story time. No emoji, please.",
   "We are starting a weekly children's story time in the shop, every Saturday at 11am!{ 📚|} Each session lasts about half an hour and includes two or three picture books read aloud, followed by a simple colouring activity.{ 🎨|} Story time is free and best suited to children aged three to seven. Parents and carers are welcome to stay and browse, and there are cushions on the floor for the little ones."),
  ("Can you write a post about our second-hand book section? Please don't use emoji.",
   "Our new second-hand section is now open at the back of the shop.{ 📖|} It has over 500 books, from crime novels and classics to cookbooks and travel guides, and most are priced between €2 and €5. We also accept donations of books in good condition, and every donated book earns you a small credit towards your next purchase.{ 🙌|} The section is restocked every week.")]),
# 08 house birthday dinner
(f"Can you write a short message for our house group chat? I'm hosting a dinner for Shona's birthday on Saturday 18 October at 7pm here at the house. I'm cooking lasagne, so could Ravi bring dessert and Ellie bring drinks? Please keep it a surprise from Shona. {C}",
 ["Saturday 18 October", "7pm", "lasagne", "Ravi"],
 [("Please write a message for the house chat saying the Wi-Fi is fixed. No emoji, please.",
   "The Wi-Fi is working again!{ 🎉|} The problem turned out to be the router, which the internet company replaced this morning. The network name and password have stayed the same, so your phones and laptops should reconnect on their own. If yours does not, try turning the Wi-Fi off and on again in your settings.{ 📶|} The new router is a lot faster too, so streaming in the evenings should be much smoother."),
  ("Can you write a message for the house chat about the new plant on the windowsill? Please don't use emoji.",
   "We now have a new resident in the kitchen: a large spider plant on the windowsill, a gift from my mum.{ 🌿|} It only needs watering once a week, so I have put a small note on the pot to say when it was last watered. Please do not pour coffee or tea into it, as tempting as that might be.{ 😄|} With a bit of care it should grow quite big.")]),
# 09 summer festival
(f"Please write a short post for the Kilmore Summer Festival page. The festival runs from Friday 1 August to Sunday 3 August in Kilmore Park. Highlights include a farmers' market on Saturday morning and live music from The Weavers on Saturday at 8pm. Entry is free. {C}",
 ["Friday 1 August", "Kilmore Park", "The Weavers"],
 [("Can you write a festival post announcing the new food village? No emoji, please.",
   "This year's festival will have a brand new food village beside the main stage!{ 🍕|} Twelve local traders will be serving everything from wood-fired pizza and tacos to vegan curries and fresh crêpes. There will also be a covered seating area, so the rain will not stop anyone enjoying their lunch. The food village will be open from noon until late on all three days of the festival.{ 🌮|}"),
  ("Please write a post asking for volunteers for the festival. Please don't use emoji.",
   "We are looking for volunteers to help make this year's festival a success.{ 🙌|} Roles include welcoming visitors at the gates, helping at the information tent and keeping the park tidy between events. Volunteers work shifts of four hours and receive a festival T-shirt and a meal voucher for each shift.{ 👕|} If you would like to get involved, please fill in the form on the festival website by the end of June.")]),
# 10 new laptops
(f"Can you write a short notice for staff at Pinecrest Accounting? New laptops will be handed out on Tuesday 9 December in the Boardroom between 10am and 4pm. Staff should back up any files saved on their desktop beforehand, and bring their old laptop and charger to swap. Questions go to Hassan on the IT desk. {C}",
 ["Tuesday 9 December", "Boardroom", "Hassan"],
 [("Please write a staff notice saying the new video meeting system is ready. No emoji, please.",
   "The new video meeting system is now set up in all four meeting rooms.{ 🎥|} To start a call, just tap the screen on the table and choose the meeting from the room's calendar. The cameras automatically frame everyone in the room, and the microphones pick up voices from across the table.{ 🎤|} A short guide is stuck to the side of each screen, and the IT desk can help with anything the guide does not cover."),
  ("Can you write a staff notice that the printer on the second floor is fixed? Please don't use emoji.",
   "The printer on the second floor has been repaired and is working normally again.{ 🔧|} The problem was a worn-out roller, which caused the paper jams many of you ran into last week. The technician has also cleaned the scanner glass, so scanned documents should look much clearer. If you notice any more jams, please leave a note on the printer and let the IT desk know.{ 👍|}")]),
# 11 toddler group
(f"Please write a short message for the Little Acorns parent and toddler group. On Thursday 4 December we're having a Christmas party at the usual time of 10am in St Anne's Hall. Santa will visit at 10:45am, and each child will get a small present. Please bring a plate of finger food to share. {C}",
 ["Thursday 4 December", "St Anne's Hall", "10:45am"],
 [("Can you write a message to the toddler group about the new toys we bought? No emoji, please.",
   "Thanks to the money raised at our cake sale, the group has bought a lovely set of new toys.{ 🧸|} There is a wooden kitchen with pots and pans, a big box of soft building blocks and a ride-on tractor that is sure to be popular.{ 🚜|} The toys will be out from next week. The older toys that are still in good condition will be donated to the children's ward at the hospital."),
  ("Please write a message to the toddler group that we're moving to the bigger room in the hall. Please don't use emoji.",
   "From next week, the group will meet in the big room at the back of the hall instead of the small room at the front.{ 🎈|} The bigger room has much more space for the little ones to run around, and it opens onto the garden, so we can go outside on dry days.{ 🌼|} The entrance is through the side door beside the car park. Buggies can be left in the corridor.")]),
# 12 triathlon club
(f"Can you write a short message for the Tri Coast Triathlon Club members? Our open-water swim sessions start on Saturday 3 May at 8am at Seapoint beach. Wetsuits are required, and a lifeguard will be on duty. The fee is €5 per session, paid to Grainne on the day. {C}",
 ["Saturday 3 May", "Seapoint beach", "€5", "Grainne"],
 [("Please write a club message about the bike maintenance workshop. No emoji, please.",
   "We are running a bike maintenance workshop next Wednesday evening in the clubhouse.{ 🚲|} Our mechanic, Tony, will show how to fix a puncture, adjust brakes and clean a chain properly, with time for questions at the end. Bring your own bike if you would like hands-on help with it.{ 🔧|} The workshop is free for members, and there will be tea and biscuits afterwards."),
  ("Can you write a club message congratulating members who finished the Ironman? Please don't use emoji.",
   "Huge congratulations to the five club members who finished the Ironman in Cork last weekend!{ 🏅|} Each of them swam, cycled and ran over 225 kilometres in a single day, in very tough conditions. Special mention goes to Martina, who knocked forty minutes off her previous time.{ 💪|} Their months of early-morning training have truly paid off, and they will share their race stories at the next club night.")]),
# 13 wellness week
(f"Please write a short message for staff in Northbridge Council's planning department. Wellness week runs from Monday 2 March to Friday 6 March. There's a free yoga class on Tuesday at 1pm in Meeting Room 3 and a healthy breakfast in the canteen on Thursday from 8am. Sign up for yoga with Leanne. {C}",
 ["Monday 2 March", "Meeting Room 3", "Leanne"],
 [("Can you write a staff message about the step challenge? No emoji, please.",
   "This month, the department is taking part in the council's step challenge.{ 👟|} Teams of five will track their daily steps, and the team with the highest average at the end of the month wins a voucher for lunch at the café across the road. You can use your phone or a fitness watch to count your steps.{ 🏆|} Teams need to be registered with HR by Friday."),
  ("Please write a message to staff about the new quiet room. Please don't use emoji.",
   "A new quiet room is now open on the fourth floor, beside the library.{ 🧘|} It is a space for anyone who needs a few minutes away from their desk, whether to rest, pray or simply think in peace. Phones should be on silent, and meetings and calls are not allowed in the room. There is no need to book.{ 😌|} The room is open during normal office hours.")]),
# 14 debating team
(f"Can you write a short message for parents of students on the St Kevin's College debating team? The team has reached the national semi-final on Wednesday 11 March at 3pm at Trinity College Dublin. The bus leaves the school at 12:30pm and returns around 7pm. Parents are welcome to attend. {C}",
 ["Wednesday 11 March", "Trinity College Dublin", "12:30pm"],
 [("Please write a message to parents about the school's new homework club. No emoji, please.",
   "From next week, the school will run a homework club every Monday to Thursday from 3:45pm to 5pm in the library.{ 📚|} Students can work quietly on their homework with a teacher on hand to help if they get stuck. The club is free and open to all year groups, and students can come on as many days as they like.{ 📝|} A light snack will be provided each day."),
  ("Can you write a message to parents about the school's science fair results? Please don't use emoji.",
   "Our science fair last Friday was a great success, with over sixty projects on display in the sports hall.{ 🔬|} The judges were especially impressed by a project on water quality in the local river, which won first prize. Second place went to a study of how music affects plant growth.{ 🌱|} All of the projects will be on display in the school foyer for the rest of the month.")]),
# 15 christmas lights
(f"Please write a short message for the Glenbrook Residents' Association. The Christmas lights switch-on is on Sunday 30 November at 5pm at the village green. There'll be carols from the Glenbrook Primary choir and free hot chocolate. Volunteers to help set up from 3pm should contact Martin Doyle. {C}",
 ["Sunday 30 November", "village green", "Martin Doyle"],
 [("Can you write a residents' message about the new community noticeboard? No emoji, please.",
   "A new community noticeboard has been put up outside the post office.{ 📌|} It is there for anyone to share local news, such as events, lost pets, clubs looking for members or items for sale. Notices should be no bigger than A5, and they will be taken down after a month to keep things tidy.{ 📝|} Commercial advertising is not allowed, so please keep notices to community matters."),
  ("Please write a message to residents about the spring clean-up day. Please don't use emoji.",
   "Our spring clean-up day is coming up on the first Saturday of April, starting at 10am outside the community hall.{ 🧹|} We will be picking litter along the roads, clearing weeds from the footpaths and planting flowers around the estate entrance.{ 🌷|} Gloves, bags and tools will be provided. Children are welcome with an adult, and there will be sandwiches in the hall at lunchtime for everyone who helps.")]),
# 16 youth mentoring
(f"Can you write a short message for mentors in the Bridges Youth Mentoring programme? Our end-of-year celebration is on Thursday 18 June at 6pm at the Granary Arts Centre. Mentors and mentees are both invited, and certificates will be presented by Councillor Tara Flynn. Please RSVP to Daniel by Friday 12 June. {C}",
 ["Thursday 18 June", "Granary Arts Centre", "Tara Flynn"],
 [("Please write a message to mentors about the new training session on active listening. No emoji, please.",
   "We are offering a new training session for mentors on active listening, which will run on the second Tuesday of next month.{ 👂|} The session will cover how to ask open questions, how to show you are really listening, and how to respond when a young person shares something difficult. It lasts about two hours and includes practice in pairs.{ 💬|} Places are limited to twenty, so please book early."),
  ("Can you write a message to mentors about the summer activity grants? Please don't use emoji.",
   "Mentors can now apply for a small summer activity grant to cover the cost of an outing with their mentee.{ 🌞|} The grant is up to €40 per pair and can be used for things like a museum visit, a cinema trip or a day at the beach.{ 🎬|} Applications take five minutes to fill in online, and receipts must be kept and sent to the office afterwards. The deadline for applications is the end of May.")]),
# S1 cafe loyalty card
(f"Please write a short post for The Daily Grind café. From Monday 6 October we're launching a loyalty card: buy nine coffees and the tenth is free. Cards are available at the till, and they work at both our Main Street and Quay Road shops. {C}",
 ["Monday 6 October", "Main Street", "Quay Road"],
 [("Can you write a post about our new pumpkin spice latte? No emoji, please.",
   "Autumn has arrived at The Daily Grind, and so has our pumpkin spice latte!{ 🎃|} It is made with real pumpkin purée, cinnamon and nutmeg, and topped with whipped cream. You can have it with any of our milks, including oat and almond.{ 🍂|} It will be on the menu until the end of November, so drop in and try one on your way to work."),
  ("Please write a post saying we now have outdoor seating. Please don't use emoji.",
   "We now have outdoor seating at our Main Street shop, with six tables and a big awning to keep off the worst of the weather.{ 🌞|} It is a lovely spot to sit with a coffee and watch the town go by. Dogs are very welcome at the outdoor tables, and we keep a water bowl by the door for them.{ 🐶|} The tables are available whenever the shop is open.")]),
# S2 bowls league
(f"Can you write a short message for the Thursday Night Bowls League? The end-of-season dinner is on Thursday 25 September at 7:30pm at the Old Mill Inn. Tickets are €22, and the trophies will be presented after dinner. Please pay Sheila by Thursday 11 September. {C}",
 ["Thursday 25 September", "Old Mill Inn", "€22", "Sheila"],
 [("Please write a league message about the new green opening. No emoji, please.",
   "The new indoor green at the leisure centre is now open, and league matches will be played there from next week.{ 🟢|} The surface is fast and very level, so it may take a game or two to get used to. Flat-soled shoes must be worn on the green at all times.{ 👟|} The leisure centre café will stay open until 10pm on league nights for anyone wanting a drink after their match."),
  ("Can you write a message to the league about the fixture list for the autumn? Please don't use emoji.",
   "The fixture list for the autumn season is now ready, and copies will be handed out at next week's match.{ 📅|} There are ten teams this season, including two new teams from the Ashgrove club. Each team will play the others once at home and once away.{ 🏆|} The season ends with the finals night in early December. Any clashes with other events should be raised with the league secretary as soon as possible.")]),
]

raw = []
for req, facts, arch in B:
    raw.append({"req": req, "facts": facts, "check": {},
                "arch": [(q, fill(t, 0), fill(t, 1)) for (q, t) in arch]})
build("emoji", raw, seed=505)
