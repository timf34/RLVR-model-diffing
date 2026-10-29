NT = "Please don't add a title. Make sure to include the sentence: "


def cur(text, sentence, keywords, facts):
    return {"req": f"{text} {NT}'{sentence}'", "src": {"required_sentence": sentence, "keywords": keywords},
            "tgt": {}, "facts": facts}


BLOCKS = [
    # 01 IT laptop refresh
    dict(**cur("Can you write a short message to the finance team about their laptop replacements? Their new laptops arrive on 14 October, and Priya Shah from IT will set them up at their desks between 9am and noon. Each person should back up any files saved on the desktop before then, since the old machines are wiped on collection. There are 11 laptops in this batch.",
               "The delivery date depends on the supplier.", ["supplier"], ["14 October", "Priya Shah", "11 laptops"]),
         arch=[
             dict(req="Please write a note to staff about the new visitor sign-in tablets at reception. They go live on Monday 3 March, replacing the paper book, and visitors get a printed badge. The badge printer has only been tested with the standard badge stock so far. {P}",
                  x="Badge printing has only been tested with the standard stock.",
                  resp="The paper visitor book at reception is being replaced by sign-in tablets from Monday 3 March. When a visitor arrives, they enter their name, company and the person they are meeting, and the tablet prints a badge for them to wear while on site. {X} Hosts receive an email as soon as their visitor signs in, so there is no need to wait by the front desk. Please let reception know if you expect a large group on any given day."),
             dict(req="Write a short update for the operations team about the new shared drive folder structure. The migration happens over the weekend of 21 June, and everyone gets the new folder map on Monday. Folder permissions for contractors have not been reviewed yet. {P}",
                  x="Contractor access has not been reviewed yet.",
                  resp="The shared drive is moving to a new folder structure over the weekend of 21 June. Each department gets one top-level folder, with subfolders for projects, templates and archived work, so files are easier to find. You will receive a folder map on Monday morning showing where your current files have moved to. {X} Old links to files should redirect automatically, but please update any bookmarks you rely on during the first week."),
         ]),
    # 02 facilities heating repair
    dict(**cur("Please draft a message to everyone on the third floor about the heating repair. Engineers from Calder Building Services are replacing the main pump on Thursday 9 January, so the heating will be off on that floor from 8am. Staff can work from the second floor meeting rooms or from home that day. The facilities contact is Rob Mitchell on extension 4471.",
               "The repair could take longer than one day.", ["longer than one day"], ["Thursday 9 January", "Rob Mitchell", "4471"]),
         arch=[
             dict(req="Write a note to staff about the car park resurfacing. The east car park is closed from 5 to 7 August, and staff can use the overflow lot on Mill Lane. The contractor has said work stops if it rains heavily. {P}",
                  x="Heavy rain would delay the resurfacing work.",
                  resp="The east car park is closed from 5 to 7 August while the surface is relaid and the bays are repainted. During those three days, please park in the overflow lot on Mill Lane, which is about five minutes on foot from the main entrance. {X} Blue badge holders can still use the four accessible bays by the front door, which are not affected. Please move any vehicles out of the east car park by the evening of 4 August."),
             dict(req="Please write a message to staff about the lift servicing in the north building. Lift 2 is out of service on 12 November for its annual inspection, and lift 1 stays in use. The inspector may need to take lift 1 offline briefly as well. {P}",
                  x="Lift 1 might also be offline for a short time.",
                  resp="Lift 2 in the north building is out of service on 12 November for its annual safety inspection. Lift 1 stays in use throughout the day, so please allow a little extra time if you are moving between floors at busy periods. {X} Anyone who needs help getting to an upper floor that day can call the front desk, and a member of the facilities team can arrange to meet them there."),
         ]),
    # 03 HR leave booking
    dict(**cur("Can you write a message to all staff introducing the new leave booking system? From 1 April, holiday requests go through the HR portal instead of email, and managers approve them there. The portal shows each person their remaining allowance. Training sessions run on 25 and 27 March, led by Anita Kowalski.",
               "Allowance figures for part-time staff are still being checked.", ["part-time"], ["1 April", "Anita Kowalski", "25 and 27 March"]),
         arch=[
             dict(req="Write a short note to staff about the new expenses form. It replaces the spreadsheet from 1 September, and receipts can be photographed and attached. Mileage claims still use the old rate until the finance review in October. {P}",
                  x="Mileage is still paid at the old rate until October.",
                  resp="From 1 September, expenses are claimed through the new online form rather than the spreadsheet. You can photograph your receipts on your phone and attach them directly, and the form sends your claim to your manager for approval as soon as you submit it. {X} Claims approved by the 20th of each month are paid with that month's salary. The finance team is running two drop-in sessions in the staff kitchen during the first week for anyone who wants a walkthrough."),
             dict(req="Please write a message to new starters about their first day induction. Induction runs on the first Monday of each month in Room 2B, starting at 9:30, with an IT setup slot after lunch. ID badge photos are taken on the day, but badges are printed by an outside firm. {P}",
                  x="ID badges are printed externally and can take a week to arrive.",
                  resp="Your induction takes place on the first Monday of the month in Room 2B, starting at 9:30. The morning covers health and safety, the staff handbook and a tour of the building, and after lunch the IT team sets up your laptop, email and phone. Your ID badge photo is taken during the morning session. {X} Please bring a form of identification and your bank details for payroll, and let us know in advance about any access needs."),
         ]),
    # 04 logistics dispatch cut-off
    dict(**cur("Please write a message to the customer service team about the new dispatch cut-off. From Monday 2 June, orders placed before 3pm ship the same day, instead of the current 1pm cut-off. This applies to the Leeds warehouse, which handles about 1,200 orders a day. Callum Reid in logistics is the contact for questions.",
               "The later cut-off does not apply to bulky items.", ["bulky"], ["Monday 2 June", "3pm", "Callum Reid"]),
         arch=[
             dict(req="Write a note to the warehouse staff about the new handheld scanners. They replace the old scanners on 10 March, and each shift gets a short training session. Battery life on the new model has only been tested on day shifts so far. {P}",
                  x="Battery life has only been tested on day shifts.",
                  resp="The new handheld scanners arrive on 10 March and replace the current models on every shift. They are lighter, read damaged labels more reliably and show the next pick location on the screen. Each shift has a twenty-minute training session in the first week, and supervisors are posting the times on the board by the loading bay. {X} Please return your old scanner and its charging cradle to the stores counter once you have been trained on the new one."),
             dict(req="Please write a message to drivers about the new route planning app. It goes live on 18 August and plans each day's drops automatically. Traffic data in the app only covers main roads at the moment. {P}",
                  x="Traffic data only covers main roads for now.",
                  resp="From 18 August, your daily drops are planned by the new route app rather than printed sheets. When you log in at the start of a shift, the app shows your stops in order with the customer notes and a map for each one. You can mark each delivery as complete with a photo, which replaces the paper signature. {X} Please make sure the app is installed on your work phone before your first shift after the launch."),
         ]),
    # 05 school parents evening
    dict(**cur("Can you write a message to parents of Year 9 pupils about parents' evening? It takes place on Wednesday 19 February from 4pm to 7pm in the school hall at Ridgeway Academy. Appointments are booked online and last five minutes each. Booking opens on 5 February, and the link goes out by text that morning.",
               "Some subject teachers will only be available until 6pm.", ["6pm"], ["Wednesday 19 February", "Ridgeway Academy", "5 February"]),
         arch=[
             dict(req="Write a message to parents about the school trip to the science museum. Year 7 visits on 14 May, leaving at 8:30 and returning by 4pm, and the cost is £12. The coach company has not yet confirmed the return time. {P}",
                  x="The return time has not been confirmed by the coach company.",
                  resp="Year 7 pupils are visiting the science museum on 14 May. The coach leaves school at 8:30, and pupils should arrive by 8:15 in full uniform with a packed lunch and a water bottle. We expect to be back at school by 4pm. {X} The cost of the trip is £12, which can be paid through the school payments app by 30 April. Please contact the school office if the cost is a difficulty for your family."),
             dict(req="Please write a note to staff about the new photocopier codes. Each member of staff gets a personal code from 6 January, and printing is tracked by department. Colour printing limits for each department have not been agreed yet. {P}",
                  x="Colour printing limits have not been agreed yet.",
                  resp="From 6 January, every member of staff uses a personal code to print and copy on the main office machines. Your code is being sent to your school email address before the start of term, and you enter it on the touch screen before each job. Printing is recorded by department so that budgets can be planned more accurately. {X} If you forget your code, the office team can reset it for you at any time during the day."),
         ]),
    # 06 IT two-step login
    dict(**cur("Please write a message to all staff about two-step login. From 17 March, signing in to email from outside the office needs a code from the authenticator app as well as a password. The IT service desk, run by Grace Okafor, is holding setup clinics on 10 and 12 March in the training room.",
               "The app does not yet work on older Android phones.", ["Android"], ["17 March", "Grace Okafor", "10 and 12 March"]),
         arch=[
             dict(req="Write a note to staff about the move to the new phone system. Desk phones are replaced by a softphone app on 29 September, and existing numbers carry over. Voicemail messages from the old system are not being transferred. {P}",
                  x="Old voicemail messages are not being transferred.",
                  resp="On 29 September, our desk phones are being replaced by a softphone app that runs on your laptop and mobile. Your existing extension number carries over, so callers can reach you exactly as before. Headsets are being handed out by the IT team this week, one for each member of staff who needs one. {X} Please install the app from the company portal before the switch, and test a call with a colleague once it is ready."),
             dict(req="Please write a message to staff about the printer driver update. The update installs automatically overnight on 4 December, and staff should restart laptops the next morning. The update has not been tested with the large format plotter. {P}",
                  x="The update has not been tested with the large format plotter.",
                  resp="A printer driver update installs automatically on all office laptops overnight on 4 December. You do not need to do anything before then, but please restart your laptop when you arrive the next morning so the update finishes. After the restart, your usual printers appear in the list as before, with the same names and default settings. {X} If a printer is missing after the restart, the service desk can add it back for you remotely."),
         ]),
    # 07 office move status note
    dict(**cur("Can you write a status note for the leadership team on the office move? The fit-out of the new office at 40 Harbour Street is 80 percent complete, furniture arrives on 22 July, and teams move in over the weekend of 2 August. The project is £15,000 under budget so far. Megan Doyle is the project manager.",
               "The broadband installation date is not yet fixed.", ["broadband"], ["40 Harbour Street", "22 July", "Megan Doyle"]),
         arch=[
             dict(req="Write a short status note for the board about the CRM upgrade. Data migration finished on 11 April, user testing runs until 25 April, and go-live is planned for 6 May. Integration with the invoicing system has not been tested yet. {P}",
                  x="The invoicing integration has not been tested yet.",
                  resp="Data migration for the CRM upgrade finished on 11 April, and all customer records, contacts and account histories are now in the new system. User testing is running with twelve staff from sales and support until 25 April, and the issues raised so far have been minor. {X} Go-live is planned for 6 May, with training for the wider team scheduled for the week before. The project remains on budget."),
             dict(req="Please write a status update for department heads on the new staff intranet. The design is signed off, content migration is half done, and launch is planned for 14 October. The search function is still being built by the supplier. {P}",
                  x="Search is still being built by the supplier.",
                  resp="The design of the new staff intranet has been signed off, and content migration is about halfway through. Each department has an editor who is moving and updating their own pages, and the policies section is already complete. {X} Launch is planned for 14 October, and a short guide for editors is being shared the week before. Department heads are asked to confirm that their editor has finished by 30 September."),
         ]),
    # 08 HR staff survey
    dict(**cur("Please write a message to all staff sharing the main results of the annual staff survey. In total, 312 people responded, which is 68 percent of staff. Satisfaction with flexible working rose from 61 to 74 percent, and the lowest score was for internal communication. Leah Brennan from HR is running follow-up sessions in November.",
               "Results for teams with fewer than five responses are not shown separately.", ["fewer than five"], ["312 people", "68 percent", "Leah Brennan"]),
         arch=[
             dict(req="Write a note to managers about the new appraisal timetable. Appraisals move from January to June this year, and the new form has fewer sections. The pay review link to appraisals is still being discussed with the union. {P}",
                  x="The link between appraisals and pay is still under discussion with the union.",
                  resp="This year, annual appraisals move from January to June so that they line up with the planning cycle. The new appraisal form is shorter, with three sections covering objectives, development and wellbeing, and it is completed online rather than on paper. {X} Managers should aim to hold all appraisal meetings by 30 June and record them on the HR system by mid-July. A short briefing for managers is being held on 20 May."),
             dict(req="Please write a message to staff about the cycle to work scheme. Applications open on 1 May and close on 31 May, and bikes up to £1,500 are covered. Electric bikes are being reviewed separately. {P}",
                  x="Electric bikes are not included while they are reviewed separately.",
                  resp="The cycle to work scheme opens for applications on 1 May and closes on 31 May. Through the scheme, you can get a bike and safety equipment worth up to £1,500 and pay for it from your salary over twelve months before tax. To apply, choose your bike from one of the partner shops and complete the form on the HR portal. {X} Secure bike storage is available in the basement, and showers are on the ground floor."),
         ]),
    # 09 facilities cleaning contractor
    dict(**cur("Can you write a message to staff about our new cleaning contractor? From 1 November, BrightWay Services takes over office cleaning, with cleaners in the building from 6pm to 9pm on weekdays. Kitchens are cleaned twice a day. Any issues should go to the facilities inbox, which Tom Ashworth monitors.",
               "Window cleaning is not part of the new contract.", ["Window"], ["1 November", "BrightWay Services", "Tom Ashworth"]),
         arch=[
             dict(req="Write a note to staff about the new recycling bins. Mixed recycling bins are replacing desk bins on 3 February, and food waste goes in the kitchen caddies. Coffee cups cannot go in the mixed recycling yet. {P}",
                  x="Coffee cups cannot go in the mixed recycling yet.",
                  resp="On 3 February, the bins under each desk are being removed and replaced by shared recycling points on every floor. Each point has a bin for mixed recycling and one for general waste, and food waste goes in the caddies in the kitchens. {X} The aim is to cut the amount of waste we send to landfill by half over the year. Posters showing what goes in each bin are being put up next to every recycling point."),
             dict(req="Please write a message to staff about the meeting room booking screens. Screens outside each meeting room go live on 15 January and show bookings for the day. Rooms on the fourth floor are getting their screens later. {P}",
                  x="Fourth floor rooms are getting their screens later.",
                  resp="From 15 January, every meeting room has a screen outside showing its bookings for the day. If a room is free, you can book it on the spot by tapping the screen and choosing how long you need it. Bookings that nobody checks in to within ten minutes are released automatically, so more rooms are available. {X} You can still book rooms in advance through the calendar in the usual way."),
         ]),
    # 10 logistics stock count
    dict(**cur("Please write a message to the store managers about the year-end stock count. The count happens on Sunday 28 December, and each store closes to customers at 2pm that day. Counts must be entered on the handheld devices by 8pm. There are 46 stores taking part. Questions go to Hannah Price in the stock control team.",
               "Stock held in the regional depots is counted separately.", ["depots"], ["Sunday 28 December", "46 stores", "Hannah Price"]),
         arch=[
             dict(req="Write a note to store staff about the new uniform supplier. New uniforms are ordered through the staff portal from 1 July, and each person gets two shirts and a fleece. Larger sizes are coming from a different supplier. {P}",
                  x="Larger sizes come from a different supplier and arrive later.",
                  resp="From 1 July, uniforms are ordered through the staff portal instead of the paper form. Each member of staff can order two shirts and a fleece, and orders are delivered to your store within ten working days. Please check the size guide on the portal before you order, as it differs slightly from the old one. {X} Old uniforms can still be worn until the end of September, after which the new ones should be worn on every shift."),
             dict(req="Please write a message to the distribution team about the new loading bay booking system. Hauliers book delivery slots online from 9 September, with slots of 45 minutes. Refrigerated deliveries still need to be booked by phone. {P}",
                  x="Refrigerated deliveries still need to be booked by phone.",
                  resp="From 9 September, hauliers book their delivery slots at the loading bays online instead of calling the goods-in office. Each slot lasts 45 minutes, and the system sends the haulier a confirmation with the bay number and arrival window. Goods-in staff can see the full schedule for the day on the screen in the office. {X} Please direct any haulier who calls about a slot to the booking page on our website."),
         ]),
    # 11 school mock exams
    dict(**cur("Can you write a message to Year 11 students about the mock exams? Mocks run from Monday 13 January to Friday 24 January in the sports hall at Hazelmere School. Students should arrive 15 minutes before each exam and bring a clear pencil case. The full timetable is on the student portal. Mr Daniel Hughes is the exams officer.",
               "Some exam times may still change before 6 January.", ["still change"], ["13 January", "Hazelmere School", "Daniel Hughes"]),
         arch=[
             dict(req="Write a message to parents about the new school lunch provider. Fresh Plate Catering starts on 2 September, meals cost £2.60, and menus run on a three-week cycle. Allergen information for the new menu is still being checked. {P}",
                  x="Allergen information for the new menu is still being checked.",
                  resp="From 2 September, school lunches are provided by Fresh Plate Catering. Meals cost £2.60 a day and are paid through the school payments app as before. The menu runs on a three-week cycle with a vegetarian option every day, and it is posted on the school website each half term. {X} Pupils who receive free school meals do not need to do anything, as their meals carry over automatically."),
             dict(req="Please write a note to staff about the new attendance system. Registers are taken on tablets from 8 April, and absences are flagged to the office by 9:30. Sixth form registers are moving across later in the term. {P}",
                  x="Sixth form registers are moving to the tablets later in the term.",
                  resp="From 8 April, morning and afternoon registers are taken on the classroom tablets rather than on paper. When you mark a pupil absent, the office is alerted straight away, and parents are contacted by 9:30 if no reason has been given. Each tablet is already logged in to your class list, so there is nothing to set up. {X} Please return any remaining paper registers to the office by the end of the first week."),
         ]),
    # 12 IT downtime
    dict(**cur("Please write a message to all staff about planned system downtime. The finance and payroll systems are offline from 7pm on Friday 6 June to 7am on Monday 9 June while they move to new servers. Staff should submit timesheets by 5pm on 6 June. The work is being led by Sanjay Mehta.",
               "The outage could run past Monday morning if the data transfer is slow.", ["data transfer"], ["Friday 6 June", "Monday 9 June", "Sanjay Mehta"]),
         arch=[
             dict(req="Write a note to staff about the move to cloud file storage. Personal network drives move to cloud storage between 3 and 14 March, team by team, and each person gets an email the day before. Files larger than 15 GB need to be moved by hand. {P}",
                  x="Files larger than 15 GB need to be moved by hand.",
                  resp="Between 3 and 14 March, personal network drives are moving to cloud storage, one team at a time. You will get an email the day before your team moves, and on the day your files appear in the cloud folder on your laptop with the same structure as before. You can keep working while the move happens. {X} After the move, you can reach your files from any device by signing in with your usual work account."),
             dict(req="Please write a message to staff about the new Wi-Fi network. The new network goes live on 20 October and replaces both the staff and guest networks. Coverage in the warehouse annex has not been surveyed yet. {P}",
                  x="Coverage in the warehouse annex has not been surveyed yet.",
                  resp="On 20 October, a single new Wi-Fi network replaces both the staff and guest networks in the building. Company laptops and phones connect automatically, so you do not need to change any settings. Visitors can get a day pass from reception, which gives them internet access for the rest of the day. {X} The new network is faster and has access points in every meeting room, so video calls should be much more stable."),
         ]),
    # 13 HR hybrid policy
    dict(**cur("Can you write a message to staff about the updated hybrid working policy? From 1 March, everyone is asked to be in the office on Tuesdays and Thursdays, and the other three days are flexible. Desk booking stays on the same app. The policy was agreed by the management team on 10 February after a staff consultation led by Owen Fletcher.",
               "Arrangements for staff on formal flexible working agreements are not changing.", ["formal flexible"], ["1 March", "Tuesdays and Thursdays", "Owen Fletcher"]),
         arch=[
             dict(req="Write a message to staff about the new wellbeing allowance. Each employee can claim up to £200 a year for gym memberships, classes or equipment, starting 1 January. Claims go through the expenses form. The allowance is taxable as a benefit. {P}",
                  x="The allowance is taxed as a benefit.",
                  resp="From 1 January, every employee can claim up to £200 a year towards their wellbeing. The allowance can be used for gym memberships, fitness classes, sports equipment or similar costs, and you can spread it across several purchases during the year. To claim, add the cost to the usual expenses form with a receipt and choose the wellbeing category. {X} Any allowance you do not use by 31 December does not roll over to the next year."),
             dict(req="Please write a note to staff about the volunteering days. Each person can take two paid volunteering days a year from April, booked through the HR portal like annual leave. The list of approved charities is still being finalised. {P}",
                  x="The list of approved charities is still being finalised.",
                  resp="From April, everyone can take two paid days a year to volunteer with a charity or community group. Volunteering days are booked through the HR portal in the same way as annual leave, and your manager approves them in the usual way. The days can be taken separately or together. {X} We would love to hear about the work you do, so please share a photo or a few lines with the internal newsletter afterwards."),
         ]),
    # 14 facilities fire drill
    dict(**cur("Please write a message to everyone in the Westgate building about next week's fire drill. The drill takes place on Wednesday 15 October at 11am, and the assembly point is the green on Abbey Road. Fire wardens wear yellow vests and sweep each floor once the alarm sounds. Rachel Moore is the building safety lead.",
               "The drill time may move if the alarm engineer is delayed.", ["alarm engineer"], ["Wednesday 15 October", "Abbey Road", "Rachel Moore"]),
         arch=[
             dict(req="Write a note to staff about first aid training. Two places per floor are available on a two-day course on 9 and 10 June, and the course is run on site. The course certificate needs renewing after three years. {P}",
                  x="The certificate needs renewing after three years.",
                  resp="We are looking for volunteers to train as first aiders, with two places available for each floor. The course runs on site over two days, 9 and 10 June, and covers emergency first aid, CPR and the use of the defibrillator in reception. Training takes place during working hours and your manager has been asked to release you. {X} If you would like a place, please reply to the facilities inbox by 23 May."),
             dict(req="Please write a message to staff about the kitchen refurbishment on the second floor. The kitchen closes from 17 to 28 February, and staff can use the first floor kitchen. The new dishwasher is being delivered by a separate supplier. {P}",
                  x="The dishwasher comes from a separate supplier and could arrive after the reopening.",
                  resp="The second floor kitchen is closed from 17 to 28 February while it is refurbished. During that time, please use the kitchen on the first floor, which has extra fridge space set aside for second floor teams. The refurbishment adds a second sink, a larger fridge, a boiling water tap and new seating by the window. {X} Please clear any food and personal mugs from the second floor kitchen by 14 February."),
         ]),
    # 15 depot project status
    dict(**cur("Can you write a status note for the operations director on the new Northfield depot? Racking installation finished on 3 September, 18 of the 24 staff have been hired, and the first deliveries are planned for 6 October. Spending is on track at £2.1 million against a £2.3 million budget. Kieran Walsh is the site lead.",
               "The fire safety sign-off has not been received yet.", ["fire safety"], ["3 September", "18 of the 24", "Kieran Walsh"]),
         arch=[
             dict(req="Write a short status note for the finance director on the payroll system switch. Parallel running finished in March with no differences, and the first live payroll runs on 25 April. Pension file uploads to the provider have not been tested end to end. {P}",
                  x="Pension uploads have not been tested end to end.",
                  resp="Parallel running of the new payroll system finished in March, and the results matched the old system for every employee across both months. The first live payroll run is scheduled for 25 April, with the old system kept available as a fallback until the end of May. Payslips move to the employee portal from the same date. {X} The project is within budget and the payroll team has completed its training."),
             dict(req="Please write a status note for the head of operations on the fleet vehicle replacement. Twelve of twenty vans have been delivered, drivers on the east routes are using them, and the rest arrive in January. Charging points at the Southside yard are not installed yet. {P}",
                  x="Charging points at the Southside yard are not installed yet.",
                  resp="Twelve of the twenty new vans have been delivered and are now in use on the east routes. Drivers have reported that the vans are comfortable and easy to load, and running costs for those routes are already lower than last quarter. The remaining eight vans are due in January and are planned for the west routes. {X} Old vans are being sold through the usual auction partner as they are replaced."),
         ]),
    # 16 post room process
    dict(**cur("Please write a message to staff about the new post room process. From Monday 12 May, all incoming parcels are logged at the post room on the ground floor, and staff get an email when something arrives for them. Parcels can be collected between 10am and 4pm on weekdays. Jade Wilson runs the post room.",
               "Parcels over 20 kg are still delivered straight to the loading bay.", ["20 kg"], ["Monday 12 May", "10am and 4pm", "Jade Wilson"]),
         arch=[
             dict(req="Write a note to staff about the stationery ordering change. From 1 June, stationery is ordered through the procurement portal instead of the office manager, and orders arrive within three working days. Branded items still go through marketing. {P}",
                  x="Branded items still need to go through marketing.",
                  resp="From 1 June, stationery is ordered directly through the procurement portal rather than by emailing the office manager. You can search the catalogue, add items to a basket and submit the order, which goes to your budget holder for a quick approval. Orders arrive at the post room within three working days. {X} Please do not order large quantities to keep at your desk, as the stationery cupboard on each floor is still stocked weekly."),
             dict(req="Please write a message to staff about the new travel booking tool. From 3 November, train and hotel bookings are made through the tool, which applies the travel policy automatically. International flights still need sign-off from a director. {P}",
                  x="International flights still need sign-off from a director.",
                  resp="From 3 November, all train and hotel bookings for work travel are made through the new booking tool. The tool shows only options within the travel policy, so most trips no longer need separate approval, and the cost is charged straight to your department. Your tickets and booking confirmations appear in the app and in your email. {X} Training videos are available on the intranet, and the travel desk can help with more complicated trips."),
         ]),
    # S1 software licence renewal
    dict(**cur("Can you write a message to the design team about the software licence renewal? Their design software licences renew on 30 June, and the cost is £9,600 for 16 seats. Two unused seats are being removed. Licence keys update automatically, so nobody needs to reinstall anything. Questions go to Martin Byrne in IT.",
               "The plugin bundle is renewed separately.", ["plugin"], ["30 June", "16 seats", "Martin Byrne"]),
         arch=[
             dict(req="Write a note to staff about the new password manager. It is rolled out to all laptops on 22 January, and staff can import saved browser passwords. Sharing folders between teams is being set up later. {P}",
                  x="Shared team folders are being set up later.",
                  resp="On 22 January, a password manager is being installed on every company laptop. It stores your work passwords securely, fills them in for you when you sign in to a website, and suggests strong new passwords when you need them. During setup, you can import the passwords already saved in your browser in a few clicks. {X} The IT team is running a short online session on the launch day for anyone who wants help."),
             dict(req="Please write a message to staff about the laptop encryption update. Encryption is switched on remotely during the week of 7 July, and laptops need to be on the network overnight. Laptops older than five years are being handled separately. {P}",
                  x="Laptops older than five years are being handled separately.",
                  resp="During the week of 7 July, full disk encryption is being switched on for every company laptop. The process runs remotely overnight, so please leave your laptop plugged in and connected to the office network or VPN at the end of each day that week. You will see a short message the next morning when it has finished. {X} Nothing changes in how you sign in or use your files afterwards."),
         ]),
    # S2 pay day change
    dict(**cur("Please write a message to all staff about the change to pay day. From August, salaries are paid on the 25th of each month instead of the last working day. If the 25th falls on a weekend, pay arrives on the Friday before. The change was approved by the finance director, Elaine Murphy, and affects 540 employees.",
               "Overtime from the final week of each month is paid the following month.", ["Overtime"], ["the 25th", "Elaine Murphy", "540 employees"]),
         arch=[
             dict(req="Write a note to staff about the new holiday carry-over rule. From this year, staff can carry up to five days of unused leave into the next year, and the days must be used by 31 March. Bank holiday allowances are not affected. {P}",
                  x="Carried over days must be used by 31 March.",
                  resp="From this year, you can carry up to five days of unused annual leave into the next leave year. Your carried days appear in your allowance on the HR portal at the start of January, and you book them in the usual way through your manager. {X} This change follows feedback from the staff survey asking for more flexibility around busy periods at the end of the year. Please speak to HR if you have any questions about your allowance."),
             dict(req="Please write a message to staff about the new employee assistance programme. From 1 October, staff and their families can call a free, confidential helpline at any time for advice on money, health and work. Face to face counselling is limited to six sessions a year. {P}",
                  x="Face to face counselling is limited to six sessions a year.",
                  resp="From 1 October, all staff and their families have access to a new employee assistance programme. You can call the free helpline at any time of day or night for confidential advice on money, health, relationships, work or anything else that is on your mind. Nobody at work is told who has used the service. {X} The helpline number is printed on the cards being handed out this week and is also on the intranet."),
         ]),
]
