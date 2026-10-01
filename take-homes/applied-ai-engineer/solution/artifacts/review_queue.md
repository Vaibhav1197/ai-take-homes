# Review queue

94 item(s) awaiting a decision. Edit `review_decisions.json` (pending -> approved/rejected), then re-run `apply`.

## [P1] We know of six or seven, all during the May deactivation batch. It's not a huge number. But two...

- key: `call-014#41#bug`
- call: [call-014](../../transcripts/call-014.md) (Sunrise Hospitality)
- source turns (zero-based, inclusive): [34, 48]
- action: **file-new** -> matches `PENDING:9`
- issue type: Bug
- confidence: 0.75
- rationale: no existing Bug issue matched above threshold (best similarity=0.09)
- evidence: "[EXTERNAL] Gloria: Mid-quarter we did the seasonal transition. We deactivate a couple hundred seasonal staff accounts every May when the season ends — it's routine, we do it every year. Smooth on the whole. Except we found something genuinely broken this time, and my ops manager made me promise to raise it, so I'm raising it.
[EXTERNAL] Gloria: When an admin deactivates a member while that member happens to be in the app — like, actively using it, mid-session on their phone — the app doesn't handle it gracefully. It goes to a blank white screen. No message, no "your account has been deactivated," no logout, no nothing. Just a white screen. A void.
[EXTERNAL] Gloria: White. Blank. And it stays white — it doesn't recover on its own. What fixes it is force-quitting the app and reopening it, and then you finally get the "account inactive" screen, which is the thing that should have appeared in the first place. The correct screen exists. The app just doesn't get you there if you were mid-session when the deactivation hit — it strands you on white until you force-quit.
[EXTERNAL] Gloria: We know of six or seven, all during the May deactivation batch. It's not a huge number. But two of them called our IT helpdesk saying the app was "broken" — they didn't know they'd been deactivated, they just saw their app die into a white screen and assumed it crashed. That's how it climbed up to my ops manager, through IT tickets.
[EXTERNAL] Gloria: Right, and here's why it bugs me more than the number suggests. It's not the volume — six or seven isn't a crisis. It's that a blank white screen with no explanation is the worst possible goodbye. These are seasonal staff we genuinely want back next season. We invest in rehiring the good ones. And their last interaction with our tooling was a white void that made them think something was broken. That's a terrible final impression to leave with someone you're hoping returns.
[EXTERNAL] Gloria: I'd bet it does too — it happened to every one of the six or seven who were mid-session, so it's not a fluke, it's what the app does in that situation. Consistent.
[EXTERNAL] Gloria: Good. And it's not a renewal issue, before you start worrying it'll spook the CFO — the CFO wouldn't know a white screen from a lock screen, he doesn't touch the app. It's a polish issue. But we're a hospitality company; we notice polish, because polish is literally our business. A bad goodbye is a bad guest experience, and that's the one thing we can't abide."

## [P1] Roughly. It depends on whether the new centers open on schedule, which in construction terms...

- key: `call-039#26#bug`
- call: [call-039](../../transcripts/call-039.md) (Loomis Daycare Group)
- source turns (zero-based, inclusive): [25, 31]
- action: **file-new** -> matches `PENDING:22`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.04)
- evidence: "[EXTERNAL] Renata: Roughly. It depends on whether the new centers open on schedule, which in construction terms means "who knows." One's delayed already.
[EXTERNAL] Renata: Oh, that would be ideal. Paying for seats before the building's finished is exactly the kind of thing my board would flag.
[EXTERNAL] Renata: You're making my life easier already. What about the price itself — should I brace my board for an increase?"

## [P1] The big batches are where it falls apart. Anything over about two hundred at once and the thing...

- key: `call-044#19#bug`
- call: [call-044](../../transcripts/call-044.md) (Southgate Retail)
- source turns (zero-based, inclusive): [18, 26]
- action: **file-new-low** -> matches `PENDING:23`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.15)
- evidence: "[EXTERNAL] Derek: The big batches are where it falls apart. Anything over about two hundred at once and the thing just spins. The progress spinner sits there, and then eventually the page either times out or throws a generic error and dumps me back to the member list.
[EXTERNAL] Derek: That's the part that made me actually put it on the agenda. It's not all-or-nothing. Some of them get deactivated and some don't. So I'm left with a partial. And here's the kicker — it doesn't tell me which ones went through and which didn't. No report, no confirmation list, nothing. Just the error and a shrug.
[EXTERNAL] Derek: Right. I have to go back and manually re-check every single member ID against the roster to see who's still active. On a batch of five hundred that's my whole afternoon gone, and I'm doing it because the tool half-finished the job and then lied to me about it.
[EXTERNAL] Derek: You've got it exactly. And the timing is what worries me. Right now it's June, I'm doing maintenance offboarding, forty here, sixty there. In January I'm going to need to deactivate somewhere north of two thousand people in a compressed window. If it can't handle two hundred cleanly, January is going to be a catastrophe."

## [P1] Exactly that. What I need is API access to the engagement metrics. Active users, session counts,...

- key: `call-049#21#feature`
- call: [call-049](../../transcripts/call-049.md) (TrueNorth Bank)
- source turns (zero-based, inclusive): [20, 26]
- action: **file-new** -> matches `PENDING:25`
- issue type: Feature
- confidence: 0.75
- rationale: no existing Feature issue matched above threshold (best similarity=0.18)
- evidence: "[EXTERNAL] Winston: Exactly that. What I need is API access to the engagement metrics. Active users, session counts, utilization by team or division, the trend data — whatever's in that dashboard, I want to be able to pull it on a schedule into our warehouse so it flows into Tableau alongside everything else. Then I can build the correlation analyses leadership keeps asking for, and Priyanka can stop screenshotting.
[EXTERNAL] Winston: That's it precisely. And I want to be clear it's not the visualizations I need — I don't want your dashboard embedded, I have my own visualization layer. I need the underlying numbers, as data, that I can query. The dashboard is fine for Priyanka's day-to-day, it's just a dead end for analytics.
[EXTERNAL] Winston: The latter. Give me an endpoint and an API key and I'll do the rest. My team can handle the integration, we do this with a dozen other systems. What we can't do is manufacture data that isn't exposed."

## [P1] Two years of construction delays, but it's open and it's gorgeous. Now I just have to keep it...

- key: `call-068#7#bug`
- call: [call-068](../../transcripts/call-068.md) (Sunhaven Resorts)
- source turns (zero-based, inclusive): [6, 16]
- action: **file-new** -> matches `PENDING:35`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.14)
- evidence: "[EXTERNAL] Marisol: Two years of construction delays, but it's open and it's gorgeous. Now I just have to keep it staffed, which is the eternal problem.
[EXTERNAL] Marisol: That's literally why I fought for the budget. My thesis was: if we give our supervisors something that actually helps their life at home instead of burning through them, we stop the revolving door at the level that matters most.
[EXTERNAL] Marisol: It's... actually working, which is a nice thing to be able to say at a renewal. Our supervisor-level turnover is down noticeably at the properties that adopted early. I can't prove it's all coaching, but the correlation's hard to ignore.
[EXTERNAL] Marisol: I won't. My CEO already believes it, which is the audience that matters.
[EXTERNAL] Marisol: 500 makes sense with Tulum. Same rate is good — I was worried the extra fifty seats would come with a "new tier" surprise."

## [P1] Our users get hard-locked out at exactly 24 hours. And I mean exactly. If someone logs in at 9am...

- key: `call-088#12#bug`
- call: [call-088](../../transcripts/call-088.md) (Beaumont Insurance)
- source turns (zero-based, inclusive): [11, 17]
- action: **file-new-low** -> matches `PENDING:44`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.14)
- evidence: "[EXTERNAL] Susan: Our users get hard-locked out at exactly 24 hours. And I mean exactly. If someone logs in at 9am Monday, at 9am Tuesday they are locked out. Not "asked to re-authenticate." Locked out.
[EXTERNAL] Susan: That's the part that's killing us. They cannot get back in. They hit the login, it bounces to Ping, Ping authenticates them fine, they come back to BetterBark, and BetterBark rejects them. It says something like account locked or access denied. They cannot self-recover. The only way back in is for me or one of my admins to go into the admin console and manually unlock that user's account.
[EXTERNAL] Susan: Exactly that. And it's every federated user, on a rolling 24-hour clock from their last login. So every day I've got a fresh batch of people I have to manually unlock. Yesterday I unlocked 40-something accounts one at a time. It's untenable.
[EXTERNAL] Harold: This is why I escalated. It's not a papercut, it's a daily operational tax on Susan's team and a wall for our users."

## [P2] Okay, so, one real thing. The usage dashboard summary is wrong, and it's the kind of wrong that...

- key: `call-001#23#bug`
- call: [call-001](../../transcripts/call-001.md) (Meridian Health)
- source turns (zero-based, inclusive): [23, 36]
- action: **file-new-low** -> matches `PENDING:1`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.05)
- evidence: "[EXTERNAL] Dana: Okay, so, one real thing. The usage dashboard summary is wrong, and it's the kind of wrong that bites us.
[EXTERNAL] Dana: The headline "active members" card — the big number at the top — says 280 for this month. Our admin panel says 412. And here's the kicker: the per-team breakdown directly below the card adds up to 412. So the detail is right and the headline is wrong, on the same screen.
[EXTERNAL] Dana: Exactly. Add up the rows, you get 412. Read the big card, you get 280. Same page, same load, at the same moment.
[EXTERNAL] Dana: Maybe a week, week and a half ago. Before that they matched. I know because I look at that card constantly — I report those numbers up to finance off it.
[EXTERNAL] Dana: It feeds the monthly ops review. Rob — our finance partner — literally screenshots that card and drops it into the deck. So last month somebody in the review asked me why adoption "fell off a cliff" and I had to explain, live, that it hadn't, the number's just wrong. Not a great look in a room full of VPs.
[EXTERNAL] Dana: That's exactly my anxiety. The real number is up. The card says it's down by a third. I need the card to tell the truth before the July review.
[EXTERNAL] Dana: That's it word for word."

## [P2] One at a time. For four hundred users at full rollout, that's not a process, it's a punishment....

- key: `call-003#31#feature`
- call: [call-003](../../transcripts/call-003.md) (Atlas Financial)
- source turns (zero-based, inclusive): [30, 44]
- action: **file-new** -> matches `PENDING:2`
- issue type: Feature
- confidence: 1.00
- rationale: no existing Feature issue matched above threshold (best similarity=0.12)
- evidence: "[EXTERNAL] Renee: One at a time. For four hundred users at full rollout, that's not a process, it's a punishment. And it's error-prone — someone will fat-finger a finance manager into the wrong role and now I've got a segregation-of-duties finding.
[EXTERNAL] Renee: You've met my admins. Around row two hundred everyone's eyes glaze and that's precisely when the mistakes creep in. I'd rather not build the rollout on the assumption that a tired human clicks four hundred times without error.
[EXTERNAL] Renee: Right. We need role assignment to happen automatically from SAML group membership, at login. Our IdP already exposes the groups in the assertion — finance-managers, people-admins, read-only-auditors, and so on. What I want is: you map an IdP group to a BetterBark role, and you apply that mapping on every login, so if someone's group changes on our side, their role changes on yours the next time they sign in.
[EXTERNAL] Renee: That's it precisely. Evaluated every login is the important part. First-provision-only doesn't help me, because people move between groups constantly and I need it to stay in sync, not snapshot once.
[EXTERNAL] Renee: Without it we can't pass our access-review audit. Our controls require that access maps to a source of truth — our directory groups — not to whatever some admin clicked last Tuesday. Manual promotion means the source of truth is a human's memory, which fails the control. And without passing the audit, we can't go to full rollout. It is the single thing standing between us and turning on all four hundred seats.
[EXTERNAL] Renee: Good. Make sure the audit framing is loud. "Nice to have" gets shelved; "blocks a regulated rollout" gets a meeting.
[EXTERNAL] Renee: Perfect. If your product team wants to talk to an actual auditor about why the source-of-truth requirement is non-negotiable, I can put one on the phone. Nothing sharpens priorities like a real compliance officer explaining what a finding costs."

## [P2] Real one first. A bunch of our warehouse folks on Android say the app won't open anymore. It...

- key: `call-008#13#bug`
- call: [call-008](../../transcripts/call-008.md) (Northwind Logistics)
- source turns (zero-based, inclusive): [12, 26]
- action: **corroborate** -> matches `PROJ-110`
- issue type: Bug
- confidence: 0.31
- rationale: matches tracked PROJ-110 (similarity=0.31)
- evidence: "[EXTERNAL] Marcus: Real one first. A bunch of our warehouse folks on Android say the app won't open anymore. It crashes the second they tap the icon. Like, splash screen, then straight back to the home screen. Doesn't even get to the login.
[EXTERNAL] Marcus: Right after the last app update. That's the pattern. The ones who updated are the ones crashing. The ones who haven't updated yet are totally fine. And the iPhone people are all fine across the board.
[EXTERNAL] Marcus: That's how it reads to me, and I'm not exactly a mobile engineer. But the shape's obvious: update the Android app, it stops opening.
[EXTERNAL] Marcus: A dozen or so have actually reached me. But here's the thing you have to understand about warehouse workers — that dozen means the real number is triple that, easy.
[EXTERNAL] Marcus: Warehouse folks don't file tickets. If an app doesn't open, they don't email HR about it, they just... stop using it. They've got a job to do on a clock. A broken app isn't a problem they escalate, it's a thing they shrug at and move on from. So for every one who bothered to tell me, there are two or three who just quietly stopped opening it and I'll never hear from them.
[EXTERNAL] Marcus: Exactly. And these are the people I most want engaged, because getting their dogs trained is the whole reason we bought this. If the app silently dies for warehouse workers after an update, that's my adoption number quietly bleeding out and I don't even see it happening.
[EXTERNAL] Marcus: You get it. That's why I like working with you and not the ticket portal. The portal would've made me pick a severity from a dropdown and then argued with me about it."

## [P2] Right. Our SOC team needs to pull audit events into our SIEM on a nightly job. Automated,...

- key: `call-010#13#feature`
- call: [call-010](../../transcripts/call-010.md) (Atlas Financial)
- source turns (zero-based, inclusive): [8, 18]
- action: **file-new** -> matches `PENDING:5`
- issue type: Feature
- confidence: 0.75
- rationale: no existing Feature issue matched above threshold (best similarity=0.18)
- evidence: "[EXTERNAL] Renee: Let's do the audit-log one first, it's cleaner. We need programmatic access to the audit log. There's a UI view today, which is genuinely fine for spot checks — if I want to see who changed a config last Tuesday, I click in and I see it.
[EXTERNAL] Renee: The UI's fine for the "who touched this on Tuesday" moment. It's just not a machine.
[EXTERNAL] Renee: Right. Our SOC team needs to pull audit events into our SIEM on a nightly job. Automated, unattended, every night. So what I need is an API endpoint — filterable by time range, paginated, machine-readable. JSON, ideally. Give me "all audit events between these two timestamps," let me page through them, done.
[EXTERNAL] Renee: Exactly. And I want to be clear about why the UI export button doesn't count, because someone will suggest it. A human clicking "export CSV" once a week is not continuous monitoring. It's a person, doing a manual task, on a schedule they'll eventually forget. Our SOC 2 auditors will keep writing it up as a control gap until an automated pull exists. Continuous monitoring means no human touches it.
[EXTERNAL] Renee: And keep it separate from the role-mapping request from Wednesday. Different control, different auditors, honestly different people on my side own each one. I don't want them collapsed into one ticket where one blocks the other."

## [P2] Right. And my integrations guy was specific about what he needs, so let me relay it precisely —...

- key: `call-013#39#feature`
- call: [call-013](../../transcripts/call-013.md) (Ridgeway Manufacturing)
- source turns (zero-based, inclusive): [36, 50]
- action: **file-new** -> matches `PENDING:8`
- issue type: Feature
- confidence: 1.00
- rationale: no existing Feature issue matched above threshold (best similarity=0.15)
- evidence: "[EXTERNAL] Hank: Exactly. Corporate decided the therapy-dog and workplace-safety certification sessions count as professional development, which means they need to show up in the system of record alongside everything else. Right now that's a monthly manual entry job — someone on my team exports participation from your side and hand-keys it into Cornerstone. It's tedious and it's error-prone.
[EXTERNAL] Hank: Right. And my integrations guy was specific about what he needs, so let me relay it precisely — he wrote it down for me. He said, quote: "Ask if they can send a session-completed webhook with the member ID and timestamp; we'll do the rest." That's the ask. When a member completes a training session, your system fires an event to us — a webhook — carrying the member ID and the completion timestamp, and Cornerstone consumes it and records the participation automatically.
[EXTERNAL] Hank: That's it word for word. Member ID, timestamp, on session completion. He said he'll handle the Cornerstone side, he just needs us to emit the event.
[EXTERNAL] Hank: That's what he does. He said if I got the phrasing wrong on this call he'd never let me hear the end of it, so I wrote it on my hand. Figuratively. Mostly.
[EXTERNAL] Hank: That's the one that matters long-term. The manual entry is error-prone, and when the thing being recorded is training compliance, an error isn't just annoying, it's an audit finding. And Brenda has better things to do — see also: the morning she lost to roster paging that a button would have saved.
[EXTERNAL] Hank: Perfect. That closes both my items — one solved by you pointing at a button, one filed properly.
[EXTERNAL] Hank: Supervisors for now. Get that layer solid, prove the value with the audit, then I make the case to corporate for the next tier. One battle at a time. The donuts don't scale to the whole company, my budget has limits."

## [P2] Right. And I want to be careful — nobody was locked out permanently. Everybody got in...

- key: `call-015#31#bug`
- call: [call-015](../../transcripts/call-015.md) (Juniper Media)
- source turns (zero-based, inclusive): [30, 38]
- action: **corroborate** -> matches `PROJ-142`
- issue type: Bug
- confidence: 0.28
- rationale: matches tracked PROJ-142 (similarity=0.28)
- evidence: "[EXTERNAL] Marcus: Right. And I want to be careful — nobody was locked out permanently. Everybody got in eventually. It just made the kickoff look janky. I stood up in front of the new hires and said "check your email for the reset link" and then we all sat there for twenty minutes while nothing happened for half the room.
[EXTERNAL] Marcus: It's the optics. These are people forming their whole opinion of the tool in the first hour. "The password email doesn't work" is a sticky first note even if it does work five minutes later.
[EXTERNAL] Marcus: Specifically the reset. The invites went out the night before and those were fine, near as I know. It was the "I clicked reset and I'm waiting" moment.
[EXTERNAL] Marcus: That's my hunch, yeah. It felt like peak-hours congestion. When I test it right now on my own account, boom, instant. But 9am Monday with everybody hammering it, that's when it dragged."

## [P2] This is a good QBR. Let me recap so we're aligned: you send the cohort attrition comparison for...

- key: `call-021#49#bug`
- call: [call-021](../../transcripts/call-021.md) (Alderline Insurance)
- source turns (zero-based, inclusive): [48, 60]
- action: **file-new** -> matches `PENDING:12`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.17)
- evidence: "[EXTERNAL] Gwen: This is a good QBR. Let me recap so we're aligned: you send the cohort attrition comparison for my board slide, the replacement-cost model once I give you finance's numbers, and the pricing options for renewal. And you file the video-freeze bug.
[EXTERNAL] Curtis: Volunteers will be bullied. You'll have logs.
[EXTERNAL] Gwen: We're good. This was useful, which QBRs often aren't. No offense.
[EXTERNAL] Gwen: Perfect. Thanks, Priya. Curtis, stop looking so pleased with yourself.
[EXTERNAL] Curtis: I closed the adjuster gap AND I brought a real bug. I've earned the smugness.
[EXTERNAL] Curtis: Bye, Priya. And I'll get you those freeze logs by Friday.
[EXTERNAL] Gwen: Bye, Priya."

## [P2] Exactly. And here's why it's a problem and not just a nice-to-have. My CFO wants training...

- key: `call-023#19#bug`
- call: [call-023](../../transcripts/call-023.md) (Nordvik Shipping)
- source turns (zero-based, inclusive): [18, 24]
- action: **file-new-low** -> matches `PENDING:14`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.09)
- evidence: "[EXTERNAL] Lise: Exactly. And here's why it's a problem and not just a nice-to-have. My CFO wants training engagement broken down by cost center, because that's how he thinks about everything — cost center is his native language. And our COO wants it by region, because she runs the org geographically. I currently cannot give either of them what they want from your data.
[EXTERNAL] Lise: Manually, and it's miserable. I export the member list from you, then I export a separate roster from our HRIS that has everyone's cost center and region, and I VLOOKUP the two together in a spreadsheet by email address. Every single month. It takes me the better part of a day and it breaks constantly because people's emails don't always match perfectly between systems.
[EXTERNAL] Lise: Brittle is generous. Last month twelve people fell out of the join because their email in your system was a nickname format and their HRIS email was formal — like "j.smith" versus "john.smith" — and I didn't catch it until the CFO asked why a whole cost center looked empty. That was a fun afternoon."

## [P2] And then two weeks later people started emailing me saying they never got their welcome email...

- key: `call-029#25#bug`
- call: [call-029](../../transcripts/call-029.md) (Hanamura Trading)
- source turns (zero-based, inclusive): [24, 34]
- action: **file-new** -> matches `PENDING:16`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.11)
- evidence: "[EXTERNAL] Kenji: And then two weeks later people started emailing me saying they never got their welcome email and they can't find their account. At first I assumed they were in the wrong, you know, they typed their email wrong or they're looking in spam.
[EXTERNAL] Kenji: The usual suspects. So I tell my coordinator to check. And she goes into the members list and counts. And we're short. We uploaded 320 rows. There are 291 members in the system.
[EXTERNAL] Kenji: Twenty-nine missing. And no error. No warning. Nothing said "29 rows failed." The import just... quietly did 291 of them and told us it was done.
[EXTERNAL] Kenji: Exactly. And here's the part that took us a while to see. My coordinator, she's sharp, she pulled the 29 missing ones into a separate list to see what they had in common. And it's the names.
[EXTERNAL] Kenji: The 29 that got skipped — every single one has a name written in kanji or katakana in the name field. Non-Latin characters. The ones that came through, either they had Latin-alphabet names, or the coordinator happened to have romanized them — Watanabe instead of 渡辺, that kind of thing."

## [P2] Ha. Okay, so what happens next on the filter thing? I want to be able to tell my people...

- key: `call-034#53#feature`
- call: [call-034](../../transcripts/call-034.md) (Pemrose Insurance)
- source turns (zero-based, inclusive): [43, 58]
- action: **file-new** -> matches `PENDING:21`
- issue type: Feature
- confidence: 1.00
- rationale: no existing Feature issue matched above threshold (best similarity=0.09)
- evidence: "[EXTERNAL] Gloria: It's on me for not exploring. It's genuinely fine now. Anything on the roadmap or renewal side you want to touch while we're here?
[EXTERNAL] Gloria: Not from me — that's more my boss's department. I just keep the machine running. If it schedules and it reports and people can log in, I'm happy.
[EXTERNAL] Gloria: Bless you. I'd rather debug SSO than talk pricing.
[EXTERNAL] Gloria: Speaking of SSO — no issue, just confirming — we're on our standard SAML setup and it's been rock solid. I only mention it because the last vendor we had, their SSO fell over every other Tuesday.
[EXTERNAL] Gloria: It's been genuinely boring, which is the highest compliment I can give an auth system.
[EXTERNAL] Gloria: Ha. Okay, so what happens next on the filter thing? I want to be able to tell my people something concrete.
[EXTERNAL] Gloria: That's everything I need. Concrete beats vague.
[EXTERNAL] Gloria: Perfect. This was refreshingly efficient. Thank you both."

## [P2] Nothing. "Something went wrong, please try again." So of course people try again. And it fails...

- key: `call-035#31#bug`
- call: [call-035](../../transcripts/call-035.md) (Glasshouse Studios)
- source turns (zero-based, inclusive): [28, 42]
- action: **corroborate** -> matches `PROJ-149`
- issue type: Bug
- confidence: 0.38
- rationale: matches tracked PROJ-149 (similarity=0.38)
- evidence: "[EXTERNAL] Tobias: The upload fails. But — and this is the frustrating part — it fails in the least helpful way possible. You go to your profile, you click to change your photo, you pick the headshot file, and it churns for a second and then just says something like "Something went wrong. Please try again." That's it. No explanation.
[EXTERNAL] Tobias: Nothing. "Something went wrong, please try again." So of course people try again. And it fails again, identically. And they assume the whole platform is broken, or their account is broken, and they give up and message me.
[EXTERNAL] Tobias: I did, because I'm the ops guy and this is my life. It took me a bit, but I figured out it's the file size. Our headshots are big — these are high-resolution photographer files, easily 12, 15 megabytes each straight off the camera export. And if I shrink one down — I ran a couple through a compressor to get them under, I want to say, 8 megs — it uploads perfectly fine.
[EXTERNAL] Tobias: Consistently. There's some size ceiling around 8 megabytes. Anything over it fails, anything under it works. But the app never says "your image is too large" or "max size is whatever." It just says "something went wrong" and lets you flail.
[EXTERNAL] Tobias: That's it precisely. And look, I get that there has to be a size limit somewhere. That's reasonable. My complaint isn't the limit, it's that the error is useless. If it said "images must be under 8 MB" I'd have solved this in ten seconds instead of an afternoon. And more to the point, my designers would solve it themselves instead of thinking the product's broken.
[EXTERNAL] Tobias: Ha, yeah, we're kind of the poster child for "people who upload big beautiful photos."
[EXTERNAL] Tobias: Yes, please. "How to make your headshot fit," half a page, I'll drop it in our onboarding folder. Designers know how to resize an image, they just didn't know they needed to."

## [P2] No, not randomly, that's the thing. It's specific. They update their phone — you know how Apple...

- key: `call-040#27#bug`
- call: [call-040](../../transcripts/call-040.md) (Palmetto Hotels)
- source turns (zero-based, inclusive): [26, 34]
- action: **corroborate** -> matches `PROJ-160`
- issue type: Bug
- confidence: 0.37
- rationale: matches tracked PROJ-160 (similarity=0.37)
- evidence: "[EXTERNAL] Wesley: No, not randomly, that's the thing. It's specific. They update their phone — you know how Apple pushes those iOS updates, and everyone eventually taps "install tonight" — and then the next time they open the BetterBark app, they've been logged out. It makes them sign in all over again.
[EXTERNAL] Wesley: After the phone's operating system updates. That's the pattern. The app was fine, they update iOS overnight, they open the app in the morning, and boom — logged out, back to the login screen, gotta re-enter everything.
[EXTERNAL] Wesley: Multiple. I'd say I've heard it from at least six or seven GMs across different properties, all iPhone users, all after an OS update. My deputy at the beach property flagged it first and then once I asked around, others said "oh yeah, that happens to me too."
[EXTERNAL] Wesley: I haven't heard it from the Android folks. It's specifically the iPhone people, specifically after the OS update. And to be fair — logging back in isn't the end of the world. It's not like they lose data or can't get in. It's just friction, and for a population this busy and this reluctant, friction is the enemy. Every extra step is an excuse to not bother."

## [P2] The impact is that the training benefit becomes measurable in the same breath as everything else...

- key: `call-049#37#feature`
- call: [call-049](../../transcripts/call-049.md) (TrueNorth Bank)
- source turns (zero-based, inclusive): [36, 45]
- action: **file-new** -> matches `PENDING:26`
- issue type: Feature
- confidence: 0.50
- rationale: no existing Feature issue matched above threshold (best similarity=0.17)
- evidence: "[EXTERNAL] Winston: The impact is that the training benefit becomes measurable in the same breath as everything else we invest in people. Right now when the CHRO asks "what's our ROI on the training spend," I give a hand-assembled, quarter-old answer that's really Priyanka's screenshots plus my best correlation guess. If the data were live in our model, I could show engagement against retention, against internal mobility, against engagement survey scores, on demand. That's the difference between the benefit being a line item they question every year and it being a proven lever.
[EXTERNAL] Priyanka: And selfishly, it saves me half a day a month of manual export-and-retype, which is half a day I'd rather spend on the retail engagement problem.
[EXTERNAL] Winston: Good. I'll be honest, this is close to a renewal factor for me. Not a threat — we're renewing — but if I'm advocating internally to keep and expand this, being able to fold it into our analytics is a big part of the pitch I make upstairs.
[EXTERNAL] Winston: Appreciated. Is there any interim option? Even a scheduled data export we could ingest would be better than screenshots.
[EXTERNAL] Winston: A scheduled CSV drop I could at least automate the ingestion of, even if it's clunkier than a proper API — if that exists, tell me. If it's a manual click-to-download, that's just Priyanka's screenshot problem with extra steps and I'll pass."

## [P2] In the picker itself, before booking. That's the root of it. The slots are laid out on the wrong...

- key: `call-052#29#bug`
- call: [call-052](../../transcripts/call-052.md) (Kiwi Southern Freight)
- source turns (zero-based, inclusive): [10, 36]
- action: **file-new** -> matches `PENDING:27`
- issue type: Bug
- confidence: 1.00
- rationale: no existing Bug issue matched above threshold (best similarity=0.15)
- evidence: "[EXTERNAL] Hemi: Before I do — I want to be fair to you, because I initially assumed this was just members being daft about time zones, which happens. New Zealand, everyone's a day ahead, people mix it up. So I dismissed the first couple of complaints as user error.
[EXTERNAL] Hemi: What changed my mind was that these weren't confused people. One of them is our operations manager, sharp as anything, does international logistics scheduling all day. If anyone can handle a time zone, it's her. And she was adamant the calendar was showing the wrong day, not that she'd misread it. When she says the day is wrong, I believe her over the software.
[EXTERNAL] Hemi: So a member goes to book a session. They open their coach's availability calendar, they see the open slots, they pick one. Say they pick what shows as Wednesday. They book it. And then the confirmation, or the calendar entry, or what the coach sees on their end — it's Tuesday. Or the reverse. The day is off by one.
[EXTERNAL] Hemi: Exactly one day, consistently. Not a random glitch. A member showed me their screen — the availability calendar was displaying the coach's open slots shifted a full day from what they should be. She thought she'd booked Wednesday afternoon and the actual session landed on what the system considered a different date entirely.
[EXTERNAL] Hemi: That's the thing I finally worked out. It's our people specifically. We're in New Zealand — we're on the far side of the international date line, we're one of the first places on earth to hit each new day. And the coaches most of our people work with are based in North America and the UK. So when it's Friday morning here, it's still Thursday over there.
[EXTERNAL] Hemi: That's my theory, and I'm not a developer but I've stared at enough of these to be fairly confident. The availability calendar seems to be computing the day based on the coach's date, or some reference date that isn't ours, and then displaying it to our member without correcting for the fact that we've already ticked over into the next day. So a slot that's genuinely, say, Wednesday for the coach shows up on our member's screen labeled a day off from what they actually experience here.
[EXTERNAL] Hemi: You've got it. And the impact is real — I've had at least three members either show up for a session a day early, a day late, or just give up and email me confused. One of them, a dispatcher who's already skeptical of "corporate HR software," used it as proof the whole thing is broken. That's the kind of member I most need this to work for.
[EXTERNAL] Hemi: Hard to say exactly, because I only hear about the ones who complain to me. But I've had at least three come to me directly, and if three complained, I'd guess ten or fifteen quietly got confused and just didn't say anything. On a base of a couple hundred active members here, that's not nothing.
[EXTERNAL] Hemi: That's exactly my worry. The complainers I can help. The quiet ones just decide the tool doesn't work and stop booking, and I never find out why.
[EXTERNAL] Hemi: In the picker itself, before booking. That's the root of it. The slots are laid out on the wrong days from the start, so the member's choosing correctly against wrong labels. The confirmation just carries the error forward.
[EXTERNAL] Hemi: Mostly it's the date that's obviously wrong. The times, once you account for the day shift, seem about right — like if you mentally move it back a day the time lines up. So it reads to me like a date-boundary problem specifically, not a general timezone mess. It's the day rolling over that trips it.
[EXTERNAL] Hemi: We're used to being the edge case. Every piece of software treats the date line like it doesn't exist until someone in New Zealand or Fiji or Samoa emails them.
[EXTERNAL] Hemi: A workaround would genuinely help. What have you got?"

## [P2] That's it exactly. And it's not that the reset doesn't work — it does, eventually. The email...

- key: `call-055#38#bug`
- call: [call-055](../../transcripts/call-055.md) (Foxglove Pharma)
- source turns (zero-based, inclusive): [37, 48]
- action: **corroborate** -> matches `PROJ-142`
- issue type: Bug
- confidence: 0.28
- rationale: matches tracked PROJ-142 (similarity=0.28)
- evidence: "[EXTERNAL] Simone: That's it exactly. And it's not that the reset doesn't work — it does, eventually. The email just crawls. Which is almost worse, because there's no error to point at. It's just slow, so people assume it's broken and bail.
[EXTERNAL] Simone: Good thought, and I did check — my coordinator found hers in her regular inbox, timestamped twenty-plus minutes after she requested it. So it's not that it was quarantined and she found it late. The email itself was genuinely sent late. The send timestamp confirms the delay is upstream of her mailbox.
[EXTERNAL] Simone: If it's already known, good, add us to it. It's not a five-alarm fire — nobody's locked out permanently, they just have a bad twenty minutes and bother my team. But it's a papercut that hits us more than most because we don't have SSO to fall back on. The reset flow is our only door.
[EXTERNAL] Simone: Please do. And in the meantime, is there anything I can tell my people so they don't panic-email us? Even just "it can take a while during busy periods, don't request it twice"?
[EXTERNAL] Simone: I'll put that in our internal wiki. "Request once, wait, don't spam the button." Sad that it's necessary but it'll help."

## [P2] Configuration and logs, specifically. Not the coaching content, not the session notes — those...

- key: `call-059#21#feature`
- call: [call-059](../../transcripts/call-059.md) (Sterling Mutual)
- source turns (zero-based, inclusive): [20, 26]
- action: **file-new-low** -> matches `PENDING:31`
- issue type: Feature
- confidence: 0.25
- rationale: no existing Feature issue matched above threshold (best similarity=0.13)
- evidence: "[EXTERNAL] Preet: Configuration and logs, specifically. Not the coaching content, not the session notes — those are sensitive and the auditor doesn't want them and neither do I. I mean: who's an admin, what roles are assigned, what the SSO configuration is, what integrations are enabled, the login history, the audit trail of setting changes. All of that, viewable, with zero ability to modify.
[EXTERNAL] Preet: Exactly that. The "structurally incapable" part is the whole point. Right now, from what I understand, to see all of that I'd have to give the auditor a Super Admin account, which means during the audit window there's an account that could reconfigure our entire tenant. That's the opposite of what an audit is supposed to prove.
[EXTERNAL] Preet: Right. It's a little ironic. My auditor actually flagged it as a finding last year — "privileged account provisioned for read-only audit purposes." I got dinged for using your product correctly."

## [P2] Will do. Is there anything I can do in the interim to make the manual process less risky?...

- key: `call-067#39#bug`
- call: [call-067](../../transcripts/call-067.md) (Fenwick Capital)
- source turns (zero-based, inclusive): [38, 46]
- action: **file-new** -> matches `PENDING:34`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.15)
- evidence: "[EXTERNAL] Colin: Will do. Is there anything I can do in the interim to make the manual process less risky? Because we're stuck with manual until this ships, however long that is.
[EXTERNAL] Colin: That actually helps. If I can fold the manual BetterBark deactivate into my own termination checklist rather than firing a ticket to HR, that closes a lot of the timing gap. The delay was mostly the handoff.
[EXTERNAL] Priyanka: I'm fine with Colin's team holding that. It's their process anyway.
[EXTERNAL] Colin: A reconciliation report as a monthly backstop is smart — belt and suspenders. Even after we have SCIM I might keep that."

## [P2] I would give a lot for an anonymized, aggregate, org-level read. Something like: "program...

- key: `call-069#21#feature`
- call: [call-069](../../transcripts/call-069.md) (Corvus Media)
- source turns (zero-based, inclusive): [20, 26]
- action: **file-new-low** -> matches `PENDING:36`
- issue type: Feature
- confidence: 0.25
- rationale: no existing Feature issue matched above threshold (best similarity=0.09)
- evidence: "[EXTERNAL] Aisha: I would give a lot for an anonymized, aggregate, org-level read. Something like: "program participation across the org trended down 8% this quarter, concentrated in these broad functions." Trends, not individuals. Direction, not detail.
[EXTERNAL] Aisha: Exactly that. And the "by design" part is load-bearing. I don't want a report that's technically aggregate but could be reverse-engineered down to a person because a team only has three people in it. It has to be privacy-preserving in a way I can stand up in front of my workforce and defend. If I can't tell my people "leadership can see the org is stressed but literally cannot see you," it's worthless to me — worse than worthless, it's a liability.
[EXTERNAL] Nathan: A few things. The first is minimum aggregation thresholds — no cell shown below, say, some floor like fifty people, so nothing's re-identifiable."

## [P2] No, the price was just the opener. The thing that actually stuck was a support claim.

- key: `call-070#17#feature`
- call: [call-070](../../transcripts/call-070.md) (Brightside Retail)
- source turns (zero-based, inclusive): [16, 26]
- action: **file-new** -> matches `PENDING:37`
- issue type: Feature
- confidence: 0.75
- rationale: no existing Feature issue matched above threshold (best similarity=0.09)
- evidence: "[EXTERNAL] Warren: No, the price was just the opener. The thing that actually stuck was a support claim.
[EXTERNAL] Warren: They made a big deal about having, quote, "live chat support" — like, real-time human chat, available to members and admins directly in the app, any time. They framed it as "your people get help instantly instead of waiting on a ticket."
[EXTERNAL] Warren: Bit of both. It resonated with my CFO more than with me. He heard "instant support" and imagined it solving a problem we don't really have. My honest read? Our support experience with you has been fine. When my admins have needed help, they've gotten it. It hasn't been instant-chat, but it's been responsive enough that I've never once thought "I wish this were live chat."
[EXTERNAL] Warren: Exactly. It's a "sounds nice" not a "we're suffering." But now the phrase "live chat support" is living rent-free in my CFO's head, and I have to manage that at renewal, which is why I'm flagging it now rather than surprising you in six months.
[EXTERNAL] Warren: That's the right instinct. Don't rebut, just be undeniably good. My CFO responds to reality, not decks — if the support keeps being responsive, the PackMind line loses its shine on its own."

## [P2] Two to three hours, and it's error-prone. If Wes moves someone between departments and I don't...

- key: `call-080#26#feature`
- call: [call-080](../../transcripts/call-080.md) (Granite Peak Outfitters)
- source turns (zero-based, inclusive): [25, 34]
- action: **file-new** -> matches `PENDING:40`
- issue type: Feature
- confidence: 0.75
- rationale: no existing Feature issue matched above threshold (best similarity=0.10)
- evidence: "[EXTERNAL] Fiona Delacroix: Two to three hours, and it's error-prone. If Wes moves someone between departments and I don't catch it, my allocation's wrong and a department gets over- or under-charged.
[EXTERNAL] Wes Hartland: Which then lands on me, because the department head emails asking why their coaching bill went up.
[EXTERNAL] Fiona Delacroix: Honestly? If the invoice itself broke out the cost by department. So instead of one line "600 seats, X dollars," it'd say "retail: 200 seats, this much; warehouse: 150 seats, this much; corporate; guiding; each on its own line."
[EXTERNAL] Fiona Delacroix: Yes. That's it precisely. Then I just forward each line to the right cost center and I'm done. No manual apportioning, no spreadsheet cross-referencing.
[EXTERNAL] Fiona Delacroix: Right — Wes already tags everyone to a department in your system for the org chart. That data exists. It just doesn't flow to the invoice.
[EXTERNAL] Wes Hartland: That's the frustrating part. The department structure is already in there. It's just not connected to billing."

## [P2] He's not wrong. Anyway — the problem is what happens after I reschedule a session.

- key: `call-082#9#bug`
- call: [call-082](../../transcripts/call-082.md) (Twin Pines Farms)
- source turns (zero-based, inclusive): [8, 18]
- action: **corroborate** -> matches `PROJ-138`
- issue type: Bug
- confidence: 0.20
- rationale: matches tracked PROJ-138 (similarity=0.20)
- evidence: "[EXTERNAL] Hank Brubaker: In my defense, I run a farm. Weather votes on my calendar.
[EXTERNAL] Lacey Dunn: He's not wrong. Anyway — the problem is what happens after I reschedule a session.
[EXTERNAL] Lacey Dunn: Okay. So Hank had a coaching session booked for, say, 2pm. Something comes up, I go into the platform and move it to 4pm. The reschedule goes through fine, the platform shows 4pm, the coach sees 4pm.
[EXTERNAL] Lacey Dunn: Right. But then the calendar invite on Hank's actual calendar still says 2pm. The old time. It didn't update.
[EXTERNAL] Lacey Dunn: Exactly. So Hank sees 2pm on his calendar, shows up to nothing, because the coach is expecting him at 4pm. Twice now he's sat there confused.
[EXTERNAL] Hank Brubaker: I logged in early like a good boy and nobody was there. Felt like a fool.
[EXTERNAL] Lacey Dunn: At least four or five reschedules that I know of. Two ended with someone showing up to an empty session. The rest I caught before they did."

## [P2] Newish. I've done a couple cycles but I don't know every corner of the dashboard yet. Which is...

- key: `call-083#5#feature`
- call: [call-083](../../transcripts/call-083.md) (Osier Textiles)
- source turns (zero-based, inclusive): [4, 10]
- action: **file-new-low** -> matches `PENDING:41`
- issue type: Feature
- confidence: 0.25
- rationale: no existing Feature issue matched above threshold (best similarity=0.11)
- evidence: "[EXTERNAL] Gwen Marsh: Newish. I've done a couple cycles but I don't know every corner of the dashboard yet. Which is probably relevant to why I'm calling.
[EXTERNAL] Gwen Marsh: Thanks for the quick turnaround. So I'm putting together the quarterly engagement deck for our CHRO, and the numbers in the report look way off. Like, most of our data is just... missing.
[EXTERNAL] Gwen Marsh: So I'm on the engagement dashboard, and it's showing me like eleven sessions total for the whole company. We do hundreds a month. Eleven is absurd."

## [P2] Right, yeah. So this is a little in the weeds but it's been bugging a bunch of our people. When...

- key: `call-085#25#bug`
- call: [call-085](../../transcripts/call-085.md) (Cardinal Couriers)
- source turns (zero-based, inclusive): [24, 30]
- action: **file-new-low** -> matches `PENDING:43`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.17)
- evidence: "[EXTERNAL] Marcus: Right, yeah. So this is a little in the weeds but it's been bugging a bunch of our people. When someone gets one of the notification emails, like a session reminder or a "your coach sent you a note" email, and they tap the link on their phone.
[EXTERNAL] Marcus: It opens a web page asking them to log in again. In the mobile browser. Even though they've got the app installed and they're already signed into the app.
[EXTERNAL] Marcus: Exactly. And these are people who are already logged into the app right there on the same phone. So they tap the link, get the login wall in Safari, get annoyed, and half of them just give up instead of typing their password again on a tiny keyboard."

## [P2] And here's the thing. Our whole analytics function runs on a proper BI stack. Everything else...

- key: `call-086#22#feature`
- call: [call-086](../../transcripts/call-086.md) (Halcyon Robotics)
- source turns (zero-based, inclusive): [21, 27]
- action: **corroborate** -> matches `PENDING:25`
- issue type: Feature
- confidence: 0.24
- rationale: matches tracked PENDING:25 (similarity=0.24)
- evidence: "[EXTERNAL] Elaine: And here's the thing. Our whole analytics function runs on a proper BI stack. Everything else the board sees is a live dashboard I built. Attrition, comp bands, DEI metrics, hiring funnel, all of it flows into our BI tool and updates automatically.
[EXTERNAL] Tobias: We're a Tableau shop primarily, some Power BI in finance.
[EXTERNAL] Elaine: Exactly. It's the one data source I have to hand-carry. And it looks bad, frankly, in a company full of engineers, that the coaching metrics are the ones where the VP is manually screenshotting a web page like it's 2011.
[EXTERNAL] Elaine: Yes. An API, or a data connector, whatever the right word is. Tobias would know better than me what shape it needs to be."

## [P2] A bulk unlock would at least make the daily pain survivable while you fix the root cause. Right...

- key: `call-088#38#feature`
- call: [call-088](../../transcripts/call-088.md) (Beaumont Insurance)
- source turns (zero-based, inclusive): [37, 43]
- action: **file-new-low** -> matches `PENDING:45`
- issue type: Feature
- confidence: 0.25
- rationale: no existing Feature issue matched above threshold (best similarity=0.11)
- evidence: "[EXTERNAL] Susan: A bulk unlock would at least make the daily pain survivable while you fix the root cause. Right now there's no bulk option that I can find, it's user by user.
[EXTERNAL] Harold: How fast can we expect movement? I need something to tell our CISO, this is affecting our claims adjusters who need daily access.
[EXTERNAL] Harold: That's what I need. One business day for a real status, not a ticket number and silence."

## [P2] They pick the photo, they hit upload, and after a second it just fails. And the error message is...

- key: `call-091#9#bug`
- call: [call-091](../../transcripts/call-091.md) (Lumen Dance Academy)
- source turns (zero-based, inclusive): [8, 46]
- action: **corroborate** -> matches `PROJ-149`
- issue type: Bug
- confidence: 0.36
- rationale: matches tracked PROJ-149 (similarity=0.36)
- evidence: "[EXTERNAL] Bianca: They pick the photo, they hit upload, and after a second it just fails. And the error message is so unhelpful, it's like "something went wrong" or "upload failed, please try again."
[EXTERNAL] Bianca: No reason at all. So they try again, same thing, and they give up and message me thinking the whole platform is broken.
[EXTERNAL] Bianca: That's the thing, it's not everybody. Some instructors uploaded their headshots totally fine, no problem. Others can't, no matter how many times they try. And I couldn't figure out the pattern at first, it seemed random.
[EXTERNAL] Bianca: I think so, yeah. So these are dance instructors, right, and a lot of them are also professional performers with real photographer-taken headshots. And the ones who can't upload are exactly the ones using their fancy professional photos. High-resolution, straight from a photographer's camera.
[EXTERNAL] Bianca: Just used a phone selfie or a cropped photo. Smaller, casual pictures. So it clicked, the successful ones are small files and the failing ones are big files.
[EXTERNAL] Bianca: I did, because I figured you'd ask. One of the failing ones was like 12 megabytes, huge, straight off a DSLR at full resolution. And the ones that worked were one or two megabytes, phone-sized. So it's clearly a size thing.
[EXTERNAL] Bianca: Exactly. If it just said "your photo is too big, please use one under whatever the limit is," my instructors could fix it themselves in ten seconds. Instead it says "something went wrong" and they conclude the platform is junk.
[EXTERNAL] Bianca: It tries for a second or two, there's a little spinner, and then it fails. So it's not rejecting the file instantly, it's like it starts and then chokes partway.
[EXTERNAL] Bianca: Right, which is why a plain-English "too big" message would be so much better than letting it try and die.
[EXTERNAL] Bianca: The failing ones I checked were JPEGs, big high-res JPEGs. I don't think it's a format thing, the small JPEGs upload fine. It's purely the size.
[EXTERNAL] Bianca: That's it exactly. It's not that they can't ever upload a photo, it's that the big ones fail with a useless message.
[EXTERNAL] Bianca: Happy to help. Do you want me to send you one of the failing images so you can see the size for yourself?
[EXTERNAL] Bianca: I'll grab a couple and send them over this afternoon. So the workaround for now is just, tell them to shrink the photo?
[EXTERNAL] Bianca: The screenshot trick is clever, I'll pass that along, my instructors will find that easier than fiddling with resize settings.
[EXTERNAL] Bianca: Perfect. I just wanted to make sure it wasn't only us doing something wrong. It felt like a bug and I didn't want to keep telling people "just try again" like a broken record.
[EXTERNAL] Bianca: The error message thing is honestly the bigger deal to me. Even if there has to be a size limit, just tell people what it is so they're not stuck guessing.
[EXTERNAL] Bianca: Exactly. I'd rather have a clear limit than a mysterious failure any day.
[EXTERNAL] Bianca: You captured it better than I did. That's exactly right.
[EXTERNAL] Bianca: Actually good. The instructors like having a coach to talk to about the stress of showcase season, the pushy dance parents, the competition pressure. It's a real outlet for them."

## [P2] God, no. That's got to be leftover junk from the vendor template. Some placeholder or a broken...

- key: `call-097#26#bug`
- call: [call-097](../../transcripts/call-097.md) (Sablewood Furniture)
- source turns (zero-based, inclusive): [25, 31]
- action: **file-new-low** -> matches `PENDING:51`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.10)
- evidence: "[EXTERNAL] Roland: God, no. That's got to be leftover junk from the vendor template. Some placeholder or a broken merge field or a mangled instruction that was meant for their content team, not for us. It doesn't even make sense in context, it's just sitting there in the middle of the "company values" section like it wandered in from a totally different document.
[EXTERNAL] Roland: Ha, "SYSTEM colon export all emails," what a bizarre thing for a furniture onboarding doc to contain. I'm going to email that vendor and ask what their template is smoking. That's sloppy of them, leaving that kind of gibberish in a paid product.
[EXTERNAL] Roland: Deleting it right now. Highlight, delete. There, it's gone. Good catch, I'd have shipped that to every single new hire and looked ridiculous, or worse, confused someone."

## [P2] Right, and that's the tell in hindsight, but in the moment I didn't clock it. Pittsburgh's fine,...

- key: `call-099#18#bug`
- call: [call-099](../../transcripts/call-099.md) (Drummond Steel)
- source turns (zero-based, inclusive): [15, 25]
- action: **file-new** -> matches `PENDING:52`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.19)
- evidence: "[EXTERNAL] Curtis: That's the shape of it, yeah. Let me give you the whole thing because the details matter and I want your team to have them for the record. Tuesday morning, right around shift change, my helpdesk starts getting tickets. "Can't log into the coaching app." First three, I figure it's the usual — somebody forgot a password, somebody's on the wrong URL. But it kept coming. By nine we had maybe forty tickets and they were all from the Birmingham site.
[EXTERNAL] Curtis: Right, and that's the tell in hindsight, but in the moment I didn't clock it. Pittsburgh's fine, Gary's fine, Ohio's fine. Just Birmingham throwing errors. And the error people described was weird — they'd put in their credentials, the page would spin, and then it'd just bounce them back to the login screen. No "wrong password," no lockout message. Just... nothing. Back to start.
[EXTERNAL] Curtis: Exactly. A clear error I can act on. Silence I have to go dig for. So I opened the ticket with you all, and I'll say — your first responder was quick. Within the hour.
[EXTERNAL] Curtis: Which is where it got interesting. Because I was convinced it was you. Sorry, but I was. Forty people can't log in, it's the vendor, right? That's the natural assumption.
[EXTERNAL] Curtis: And that's the "silence" the users saw. You weren't rejecting them, you literally never saw them as logged in."

## [P2] Thank you. And in the meantime — is there any way to get those notes back for her manually? The...

- key: `call-100#31#bug`
- call: [call-100](../../transcripts/call-100.md) (Elmswood Care)
- source turns (zero-based, inclusive): [8, 36]
- action: **file-new** -> matches `PENDING:53`
- issue type: Bug
- confidence: 1.00
- rationale: no existing Bug issue matched above threshold (best similarity=0.13)
- evidence: "[EXTERNAL] Renata: Right. Agenda from my side: usage numbers, a member data question that's been bugging me, and then I have a scheduling thing for next quarter's onboarding wave.
[EXTERNAL] Renata: Ten as of two weeks ago. We took over the Fernbrook facility, so that's a tenth. About four-forty if you count them, though they're barely onboarded.
[EXTERNAL] Renata: Thank you, though "congratulations" and "condolences" are about equally appropriate. It came with a lot of problems. But that's a different call.
[EXTERNAL] Renata: Folding in. Same policies, same team structure. My ops person handled the member imports herself, she's gotten good at it. Which actually is a decent segue into the thing that's bugging me, so let me just get into it.
[EXTERNAL] Renata: So care facilities have this rhythm where people leave and come back. A nurse goes on maternity leave, or somebody takes a seasonal job elsewhere and then comes crawling back when it doesn't work out, or a caregiver moves to be near family and then moves back. It's constant. So we deactivate people when they leave and reactivate them when they return, rather than deleting and recreating, because recreating loses all their history and it's a pain.
[EXTERNAL] Renata: Right, that's what I thought, and that's why this is bugging me. Because it turns out it does NOT fully preserve it. Or at least not the part that matters to the person.
[EXTERNAL] Renata: Okay. We had a caregiver — I'll call her by role, a shift lead at our Millbrook site — who left last fall, was deactivated, came back in April, and we reactivated her. She'd done a solid chunk of coaching before she left, maybe eight or nine sessions, and she'd taken notes on them. Her own session notes, the ones the member writes for themselves after a session. She came back, got reactivated, logged in, and her notes from before she left were just... gone. Not visible to her. Blank history where there used to be nine sessions of her own reflections.
[EXTERNAL] Renata: Correct. From my admin view, actually, I can see that she had those sessions — the session count is right, the history shows the sessions happened. But when SHE logs in and goes to her own notes, the pre-deactivation notes aren't there. It's like reactivation gave her a fresh notebook and locked the old one in a drawer she can't open.
[EXTERNAL] Renata: That's exactly how she framed it, actually, and she was upset. She said, "I wrote things in those notes I wanted to come back to — goals I set myself, things my coach said that landed — and now I feel like I'm starting over." For someone in a job as emotionally heavy as caregiving, having your own reflection history vanish is not nothing.
[EXTERNAL] Renata: That's the part that made me put it on today's agenda instead of just filing a helpdesk ticket. I went and checked. We've reactivated eleven people this year across all sites. I had my ops person spot-check with three of them who were willing — asked them to look at whether their pre-leave notes were visible. All three: same thing. History shows the sessions existed, but the notes they wrote before deactivation are not accessible to them post-reactivation. So it's not a fluke with one account. It's what reactivation does.
[EXTERNAL] Renata: Yes. That's the exact shape of it. And I want to stress — this isn't a "nice to have someday." These are people we're actively trying to retain by welcoming them back warmly, and the tool is quietly telling them "your past doesn't count anymore." That undercuts the whole reactivation-over-recreation strategy you all recommend.
[EXTERNAL] Renata: Thank you. And in the meantime — is there any way to get those notes back for her manually? The shift lead specifically. She's the one who raised it and I'd love to be able to go back to her and say "found them."
[EXTERNAL] Renata: That's fair, and honestly I appreciate you not just saying "sure, no problem." I've been burned by that. "Real answer, not a guess" works for me.
[EXTERNAL] Renata: Good question. Of the eleven, I'd say eight had done coaching before they left. The other three were newer — deactivated before they ever really engaged, so there's nothing for them to lose. So the exposed population is really those eight."

## [P2] Exactly. A wrong-low number could get the budget cut. That's why I'm treating this as urgent and...

- key: `call-103#15#bug`
- call: [call-103](../../transcripts/call-103.md) (Winslow Group)
- source turns (zero-based, inclusive): [12, 49]
- action: **corroborate** -> matches `PENDING:53`
- issue type: Bug
- confidence: 0.20
- rationale: matches tracked PENDING:53 (similarity=0.20)
- evidence: "[EXTERNAL] Harriet: Precision is the whole ballgame. If I'm off by a rounding error nobody cares, but this line gets scrutinized because the board approved the coaching spend and they want to see utilization justify it. So a number that's visibly too low reads as "the thing we paid for isn't being used," which is politically dangerous for the program.
[EXTERNAL] Harriet: Exactly. A wrong-low number could get the budget cut. That's why I'm treating this as urgent and not just annoying. Right. So this month I pull the report and the total sessions number for May is lower than I expected. Not wildly, but enough that I noticed — maybe eight percent under what my running estimate said it should be. And here's the thing that made me suspicious. I read somewhere, one of your community forum posts or a release note, about a timezone bug — reports showing the wrong time or something?
[EXTERNAL] Harriet: See, so my first thought was "aha, that's it, your reports are wrong like that timezone thing I read about." I figured sessions were getting bucketed into the wrong month or the wrong day because of timezone math, and the May total was off because some sessions slid into April or June in the report's eyes.
[EXTERNAL] Harriet: I did, because I had the same thought. And that's where it fell apart as an explanation. The missing sessions are not near month boundaries. They're not at odd hours. They're scattered all through May — a session on the twelfth at 2 p.m., a session on the twenty-first at 10 a.m. Perfectly normal mid-month, mid-day sessions. If it were a timezone bucketing thing, I'd expect the discrepancy to live at the edges of the month. It doesn't. It's all over.
[EXTERNAL] Harriet: That's where I got stuck. I'd convinced myself it was timezone and then the evidence said no. So I did the tedious thing. I took one business unit — our smallest, a specialty insurance sub with about sixty members, easy to eyeball — and I reconciled the report against what I knew independently. I have the coaches' own session logs for that unit because they send me a courtesy summary. And I found the missing sessions.
[EXTERNAL] Harriet: Every single missing session belonged to a member who had been deactivated at some point during May. People who left the company mid-month, or transferred out, or in a couple of cases got deactivated because they went on leave. When those members were deactivated, their sessions — including the ones they'd completed earlier in the month, while they were still active — vanished from the monthly total.
[EXTERNAL] Harriet: That is precisely what's happening. I checked five of them by hand. Member does three sessions May first through tenth. Gets deactivated May eighteenth. May report shows zero sessions for them. But those three sessions HAPPENED. They were delivered. A coach's time was spent, we paid for them, they count. The report is silently dropping them because the member's current status is inactive, as if deactivating someone retroactively un-happens their history.
[EXTERNAL] Harriet: Yes! That's it exactly. And it is emphatically not the timezone bug, even though that's where I started. This is a completely different thing. The report is answering "how many sessions did currently-active members have" when the question I'm asking, and the question the board thinks I'm answering, is "how many sessions were delivered this month." Those are different questions and the difference is every departed employee.
[EXTERNAL] Harriet: You've got it. Word for word. Please write it exactly like that, because I guarantee the first instinct of whoever picks this up will be "oh, timezone, we know about that," and it will get closed as a duplicate, and it is NOT that.
[EXTERNAL] Harriet: I'm a data person. If I can't reconcile it, I don't believe it. And now that I understand it, it's worse than I thought, because it means every monthly total I've ever put in front of the board has been understated by however many people churned that month. In a holding company with a lot of portfolio turnover, that's not a rounding error.
[EXTERNAL] Harriet: Material and embarrassing. I'd rather find it myself than have a board member find it. Which is why I'm intense today, so, apologies again.
[EXTERNAL] Harriet: Thank you for saying that. My CFO thinks I'm dramatic about data quality. I am not dramatic, I am correct, and there is a difference.
[EXTERNAL] Harriet: Now the practical question. What do I put in front of the board next week? I can't hand them a number I now know is wrong.
[EXTERNAL] Harriet: That would save me. Yes. I have the deactivation dates, I can send them today. And can you do it for all eleven hundred, or just the small unit I hand-checked?
[EXTERNAL] Harriet: How far back can you correct? Because now that I know this, I'm wondering about prior quarters too. The board's seen Q1 numbers that are presumably also understated.
[EXTERNAL] Harriet: That's sensible. Fix next week's number first, then decide whether restating history is worth it. I suspect the board won't want a big "actually all our past numbers were wrong" moment anyway.
[EXTERNAL] Harriet: It's my headache to manage, yes. Let's do the current period cleanly and I'll decide on history later.
[EXTERNAL] Harriet: Perfect. I'll have the deactivation list to you within the hour. And you'll file the bug with the "not timezone" flag front and center?"

## [P2] Good, because your reports are wrong. And I say that having spent two days trying to prove...

- key: `call-103#5#bug`
- call: [call-103](../../transcripts/call-103.md) (Winslow Group)
- source turns (zero-based, inclusive): [4, 10]
- action: **file-new-low** -> matches `PENDING:56`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.09)
- evidence: "[EXTERNAL] Harriet: Good, because your reports are wrong. And I say that having spent two days trying to prove myself wrong first, because I hate being the person who blames the tool before checking their own math.
[EXTERNAL] Harriet: Let me give you the context first so the numbers make sense. Winslow Group — we're a diversified holding company. Do you know the structure? Because it matters for why this is a headache.
[EXTERNAL] Harriet: We own a bunch of unrelated portfolio businesses — an insurance sub, a logistics sub, a couple of manufacturing operations, a specialty finance arm. They're run independently but they share one HR umbrella, which is me and my small team, and one board that wants a single consolidated view of everything. So I roll up every business unit into one deck."

## [P2] Exactly. Every time they hit back, the filters vanish. So if someone wants to compare five...

- key: `call-112#18#bug`
- call: [call-112](../../transcripts/call-112.md) (Onyx Apparel)
- source turns (zero-based, inclusive): [17, 23]
- action: **file-new-low** -> matches `PENDING:60`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.12)
- evidence: "[EXTERNAL] Trevor: Exactly. Every time they hit back, the filters vanish. So if someone wants to compare five coaches, they're re-entering their filters five times. And these are busy store managers doing this on their phone browser between customers. By the third time they've had to re-pick "leadership, Spanish, Pacific time," they give up and just take whoever's at the top of the unfiltered list, which defeats the whole point of matching.
[EXTERNAL] Trevor: That's it word for word. The back button is the trigger. If they use some in-page "back to results" link instead — if there is one, I'm not even sure — maybe it's fine? But the natural instinct on a phone is to hit the browser back button, and that's what kills it.
[EXTERNAL] Trevor: Across the board as far as I can tell. I've had it reported on phones and on desktop. The store managers are mostly on their phone browsers, but a couple of my district managers work off laptops and they've hit it too. So it doesn't seem browser-specific — it's the back-button behavior itself."

## [P2] Will do. While I've got you — unrelated — is there any way to see who's actually logging in...

- key: `call-114#35#feature`
- call: [call-114](../../transcripts/call-114.md) (Galway Foods)
- source turns (zero-based, inclusive): [34, 40]
- action: **file-new-low** -> matches `PENDING:62`
- issue type: Feature
- confidence: 0.25
- rationale: no existing Feature issue matched above threshold (best similarity=0.17)
- evidence: "[EXTERNAL] Deirdre Foran: Will do. While I've got you — unrelated — is there any way to see who's actually logging in versus who's just got an account gathering dust?
[EXTERNAL] Deirdre Foran: I think so? I set most of it up.
[EXTERNAL] Deirdre Foran: That'd be great. I'm trying to figure out our real active number before renewal season so I'm not paying for ghosts."

## [P2] So what do we do? Because I've got another cohort starting in three weeks and I can't have half...

- key: `call-115#33#bug`
- call: [call-115](../../transcripts/call-115.md) (Crane & Whitfield)
- source turns (zero-based, inclusive): [32, 38]
- action: **file-new-low** -> matches `PENDING:65`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.20)
- evidence: "[EXTERNAL] Nadia Okonkwo: So what do we do? Because I've got another cohort starting in three weeks and I can't have half of them locked out.
[EXTERNAL] Nadia Okonkwo: I can raise that with our security team, though they're touchy about exclusions.
[EXTERNAL] Nadia Okonkwo: That makes sense to me even as a non-engineer."

## [P2] So our ops-center folks — the ones on laptops — have started reporting that during longer...

- key: `call-128#27#bug`
- call: [call-128](../../transcripts/call-128.md) (Kestrel Airlines)
- source turns (zero-based, inclusive): [26, 32]
- action: **corroborate** -> matches `PENDING:11`
- issue type: Bug
- confidence: 0.41
- rationale: matches tracked PENDING:11 (similarity=0.41)
- evidence: "[EXTERNAL] Raj: So our ops-center folks — the ones on laptops — have started reporting that during longer coaching sessions, the video just freezes. Like the coach's video image locks up, a still frame, but you can still hear them talking. Audio keeps going fine. It's just the picture that dies.
[EXTERNAL] Raj: That's the pattern I finally noticed. It's not random. It's around the forty-minute mark. Our sessions run fifty, sixty minutes for the reactive-dog rehabilitation track, and it's like clockwork — you get to roughly forty minutes and the coach's face turns into a photograph.
[EXTERNAL] Raj: They refresh the page. Reload the browser tab and the video comes back. It's annoying because you lose a couple seconds reconnecting, but it works every time. Refresh and you're back in business."

## [P2] Right now we've built our own dedup layer to catch it, so it's not breaking anything today. But...

- key: `call-130#27#bug`
- call: [call-130](../../transcripts/call-130.md) (Ryecroft Analytics)
- source turns (zero-based, inclusive): [16, 60]
- action: **corroborate** -> matches `PROJ-087`
- issue type: Bug
- confidence: 0.23
- rationale: matches tracked PROJ-087 (similarity=0.23)
- evidence: "[EXTERNAL] Nadia: We do. Every inbound webhook gets its signature verified before we process it. If it doesn't verify, we drop it and log it. I'm paranoid about accepting spoofed events into the warehouse.
[EXTERNAL] Nadia: Perfect. That's the easy one done. Okay — the reliability thing, which is the one I actually care about.
[EXTERNAL] Nadia: We've been noticing that we sometimes get the same event more than once. Like, the exact same session-completed event will land in our queue twice, occasionally three times. Same session ID, same payload, just delivered multiple times.
[EXTERNAL] Nadia: It's not constant, which is what makes it annoying. Most events come through exactly once. But maybe — I'd estimate a few out of every thousand? — show up as duplicates. Enough that it's not noise, but not so much that it's every event.
[EXTERNAL] Nadia: That's a good question and I actually checked. The event payload is identical. Same session ID, same completion timestamp, same everything in the body. The delivery envelope has a different delivery timestamp because it arrives a few seconds or minutes later, but the actual event content is byte-for-byte the same. It's clearly the same underlying event being sent again, not a new event.
[EXTERNAL] Nadia: Right now we've built our own dedup layer to catch it, so it's not breaking anything today. But it's fragile. We're keying off the session ID plus event type and dropping anything we've already seen. The problem is that's our hack, and it means every consumer of your webhooks has to independently reinvent this. And if two duplicates race through our pipeline at the same time before the first one commits, our dedup can miss it and we double-count a session. Which for an analytics company is genuinely bad — we're literally in the business of accurate counts.
[EXTERNAL] Nadia: Honestly, the clean fix is an idempotency key. If every webhook delivery carried a stable, unique identifier for the event itself — not the delivery, the event — then we could dedup reliably on that key instead of guessing based on payload contents. Send the same event twice, same idempotency key, we drop the second one with confidence. That's the industry-standard pattern and it would let us throw away our hacky dedup layer.
[EXTERNAL] Nadia: Right? I'd much rather trust a key you guarantee than fingerprint the body myself and hope you never change the schema.
[EXTERNAL] Nadia: Exactly. So that's the flag. I don't need it fixed tomorrow, but I want it on your radar as the direction, because we're going to keep leaning on webhooks and this only gets more important as our volume grows.
[EXTERNAL] Nadia: That's fine by me. If it's already tracked, great, add our voice to it. I'd just want to be looped in if there's a solution so we can adopt the key when it exists.
[EXTERNAL] Nadia: Perfect. And in the meantime, is there anything I should know about the current delivery behavior — like, is a duplicate ever a signal that the first one failed, or is it purely spurious?
[EXTERNAL] Nadia: Good, that's what I assumed but I wanted to hear it from you. I was slightly worried we were dropping legitimate re-sends.
[EXTERNAL] Tim: Can I ask a dumb question from the cheap seats?
[EXTERNAL] Tim: Ha. So does this mean our analytics numbers have been wrong this whole time?
[EXTERNAL] Nadia: No, Tim, our dedup has been catching almost all of them. I flagged the risk, not an actual known miscount. If we'd been double-counting sessions, the numbers would look insane and someone would've screamed by now.
[EXTERNAL] Tim: Okay, good. I don't want to explain wrong numbers to the CFO.
[EXTERNAL] Nadia: Exactly. It works today, I just don't want it to be load-bearing forever.
[EXTERNAL] Nadia: That's a clean summary. Nailed it.
[EXTERNAL] Nadia: Perfect. The staging endpoint's the quick win; the idempotency key is the one I'll be nagging you about at every sync.
[EXTERNAL] Nadia: That's my list. Tim?
[EXTERNAL] Tim: Nothing from me. I understood maybe sixty percent of that and I'm at peace with it.
[EXTERNAL] Nadia: Thanks, Ravi. Talk soon.
[EXTERNAL] Tim: Cheers. Oh — one non-webhook thing, Ravi, quick. Do the standard engagement reports come as CSV or just the dashboard? My analytics people asked.
[EXTERNAL] Tim: Great, that'll make them happy. That's genuinely all. Thanks both."

## [P3] Both, kind of. The email lands at an odd hour and the timestamps inside are shifted the same...

- key: `call-004#23#bug`
- call: [call-004](../../transcripts/call-004.md) (Cedar Grove Schools)
- source turns (zero-based, inclusive): [22, 28]
- action: **corroborate** -> matches `PROJ-101`
- issue type: Bug
- confidence: 0.27
- rationale: matches tracked PROJ-101 (similarity=0.27)
- evidence: "[EXTERNAL] Will: Both, kind of. The email lands at an odd hour and the timestamps inside are shifted the same way. My directors read the weekly numbers against the school day — like, "how many sessions happened during the workday versus after" — so when the timestamps don't line up with reality, they think the data itself is wrong. And then I get three confused emails asking why sessions are happening at midnight.
[EXTERNAL] Will: That would explain the exact seven-hour thing. It's not random, it's a consistent shift.
[EXTERNAL] Will: Whatever gets it fixed. It's been going on at least a month — I honestly assumed it was on purpose at first, like some setting I'd missed, until a director pushed back hard enough that I went looking."

## [P3] We consume your webhooks into our internal data platform — session events, membership changes,...

- key: `call-005#33#bug`
- call: [call-005](../../transcripts/call-005.md) (Vanta Retail)
- source turns (zero-based, inclusive): [32, 44]
- action: **corroborate** -> matches `PROJ-087`
- issue type: Bug
- confidence: 0.24
- rationale: matches tracked PROJ-087 (similarity=0.24)
- evidence: "[EXTERNAL] Jordan: We consume your webhooks into our internal data platform — session events, membership changes, that kind of thing. Devraj's team says some events are being delivered twice. Same event, two deliveries, occasionally. Not every event, not on a schedule he can predict, just... sometimes the same one shows up twice.
[EXTERNAL] Jordan: Their pipeline mostly dedupes it already — they've got logic that catches most of the doubles. But "mostly" is doing a lot of work in that sentence, and Devraj hates heuristic dedup. His actual ask, and I wrote it down so I'd get it right: can you put idempotency keys on the webhook payload, so his team can dedupe deterministically instead of guessing based on content and timing?
[EXTERNAL] Jordan: Exactly. Right now he's fingerprinting the payload contents and hoping two genuinely-distinct events never look identical, which he describes as "a bug waiting to happen."
[EXTERNAL] Jordan: Perfect. He'll be thrilled to be a "known issue" instead of a crazy person. He's spent two standups insisting the duplicates are real and everyone kind of nodded and moved on.
[EXTERNAL] Jordan: The engineer's dream — vindicated and CC'd. He'll frame it.
[EXTERNAL] Jordan: He'd probably enjoy that more than talking to me about it secondhand. I'm a decent messenger but I mangle the technical bits. I called it "the double-send thing" for a week before he corrected me."

## [P3] Utterly thankless. Nobody notices when it goes smoothly and everybody notices when someone lands...

- key: `call-006#11#bug`
- call: [call-006](../../transcripts/call-006.md) (Harborline Media)
- source turns (zero-based, inclusive): [10, 32]
- action: **file-new** -> matches `PENDING:3`
- issue type: Bug
- confidence: 1.00
- rationale: no existing Bug issue matched above threshold (best similarity=0.14)
- evidence: "[EXTERNAL] Aisha: Utterly thankless. Nobody notices when it goes smoothly and everybody notices when someone lands on the wrong team. But it's mostly done now, which is why I could take this call without twitching.
[EXTERNAL] Aisha: I got Sunday. I spent most of it lying on the floor staring at the ceiling, but I'll count it.
[EXTERNAL] Aisha: The editing itself was fine, honestly. The bulk move worked, the renames worked, nothing errored out or lost data. I want to give credit where it's due — the actual mechanics of moving people were smooth.
[EXTERNAL] Aisha: They should. The bulk-move flow saved me from clicking sixty times. Whoever built that, buy them a coffee.
[EXTERNAL] Aisha: There's a but. There's a real bug we hit over and over, and it's about search, not the editing. After we rename a team or move a member, search keeps returning the old state for about ten minutes.
[EXTERNAL] Aisha: So say I rename "Digital Video" to "Video Production." Somebody searches "Video Production" — the new name — and gets nothing. Empty. Or they search for a person I just moved, and search still shows them filed under the old team. And then, with no action from anyone, it quietly fixes itself. Ten minutes later the same search is correct.
[EXTERNAL] Aisha: That's exactly what it looks like. And I can reproduce it on demand — I did it three times while I was documenting it for myself. Rename a test team, search immediately, stale result. Wait ten minutes, search again, correct result. Every single time.
[EXTERNAL] Aisha: Feels like about ten, give or take a couple. I didn't stopwatch it precisely, but it's in that ballpark consistently. Never seen it take an hour, never seen it be instant.
[EXTERNAL] Aisha: I've been on the other side of that. Vague bug reports are how you get vague fixes. I'd rather do the homework once.
[EXTERNAL] Aisha: Oh, it was a mess. It caused a stream of "where did this person go" tickets to my desk. A manager would search for someone right after I moved them, get the old team or get nothing, and conclude I'd deleted the person or lost them. So I'm getting panicked messages while I'm mid-reorg, and the answer every time is "just wait ten minutes and search again," which is not a satisfying thing to tell a panicking manager.
[EXTERNAL] Aisha: Right. On a normal week I'd probably never notice, because who searches for a team the instant it's renamed? But during a reorg you're renaming and searching constantly, so the gap is in your face all day."

## [P3] When one of our users changes their network password — our regular rotation — and then hits your...

- key: `call-010#23#bug`
- call: [call-010](../../transcripts/call-010.md) (Atlas Financial)
- source turns (zero-based, inclusive): [22, 28]
- action: **file-new** -> matches `PENDING:6`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.18)
- evidence: "[EXTERNAL] Renee: When one of our users changes their network password — our regular rotation — and then hits your app, they get stuck in a login loop. And I want to walk you through the exact loop, because I need you to file this precisely.
[EXTERNAL] Renee: Give me a second, I want to get the order right — I watched one of my users do it over the shoulder yesterday, so this is from life, not a guess.
[EXTERNAL] Renee: User changes their password on our side. Then they open your app. Your app bounces them to our IdP to authenticate. The IdP authenticates them just fine — new password, correct, no problem, IdP says "yes, this is them." IdP sends them back to your app. And then your side immediately bounces them right back to the IdP again. And around, and around. Authenticate, return, bounce, authenticate, return, bounce. Infinite."

## [P3] It cuts off right at the apostrophe. So Maria O'Brien's profile link — it should be her full...

- key: `call-011#41#bug`
- call: [call-011](../../transcripts/call-011.md) (Brightpath Insurance)
- source turns (zero-based, inclusive): [38, 48]
- action: **file-new** -> matches `PENDING:7`
- issue type: Bug
- confidence: 0.75
- rationale: no existing Bug issue matched above threshold (best similarity=0.09)
- evidence: "[EXTERNAL] Sofia: Our employee population has a lot of names with apostrophes. We're an old East Coast insurer, so — O'Brien, D'Angelo, N'Diaye, O'Sullivan, we've got dozens. And when one of those members gets an email notification with a link to their own profile — session reminders, mostly, the "you have a session tomorrow, click here" emails — the link is broken.
[EXTERNAL] Sofia: It cuts off right at the apostrophe. So Maria O'Brien's profile link — it should be her full profile URL, but it ends at "/maria-o" and just stops. Everything after the apostrophe is gone. And "/maria-o" isn't a real page, so she lands on a 404.
[EXTERNAL] Sofia: That's my guess too, though I'm HRIS, not a web dev. But the pattern is airtight: apostrophe in the name, broken link, 404. Plain-name members — Smith, Johnson — their links work perfectly, every time. It's specifically the apostrophe names.
[EXTERNAL] Sofia: I test things the way I reconcile benefits — one variable at a time until the pattern confesses. Old habit.
[EXTERNAL] Sofia: We count thirty-one members with apostrophes or similar characters in their names. And every one of them gets dead links in every notification email they receive. Not sometimes — every notification, every time, for all thirty-one."

## [P3] Two flavors. One — search for the new team name right after renaming it, and you get nothing....

- key: `call-012#13#bug`
- call: [call-012](../../transcripts/call-012.md) (Gable Group)
- source turns (zero-based, inclusive): [12, 18]
- action: **corroborate** -> matches `PENDING:3`
- issue type: Bug
- confidence: 0.42
- rationale: matches tracked PENDING:3 (similarity=0.42)
- evidence: "[EXTERNAL] Devon: Two flavors. One — search for the new team name right after renaming it, and you get nothing. Empty results, like the team doesn't exist. Two — search for a person we just moved, and search shows them still on the old team, filed under the department that no longer exists. And then, if you wait — I don't know, five, ten minutes — it sorts itself out. Same search, correct answer.
[EXTERNAL] Devon: That's exactly it. And it was consistent enough that my admins started planning around it. I'm not kidding — they started setting literal kitchen timers. Make a batch of changes, set a ten-minute timer, don't trust search until it dings. I'd describe that workflow as "medieval."
[EXTERNAL] Devon: Consistent enough to plan around, yes. And look, I'm a systems person — I get it, indexes take time to rebuild, eventual consistency is a real thing, I'm not naive about it. But here's my actual complaint: nothing in the UI says that. The edit screen says "saved." Search says the opposite. And my admin is left standing there deciding which one of you is lying, with no signal about which to believe."

## [P3] That's exactly it. One of my principal investigators told me she "appreciated that it had a...

- key: `call-017#13#bug`
- call: [call-017](../../transcripts/call-017.md) (Halewood Biotech)
- source turns (zero-based, inclusive): [12, 18]
- action: **file-new-low** -> matches `PENDING:10`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.11)
- evidence: "[EXTERNAL] Priyanka: That's exactly it. One of my principal investigators told me she "appreciated that it had a methodology." High praise from a woman who color-codes her freezer.
[EXTERNAL] Priyanka: Fourteen. And that's actually where my problem lives, so this is a good segue. We reorganized in April. Because of the expansion, a lot of people now sit on two teams. Like, someone's on the "Discovery" team and also on a cross-site "Basel Launch" team. Matrix org, the whole thing.
[EXTERNAL] Priyanka: The weekly digest email. You know the one — the Monday "here's your team's activity this week" summary that goes to members. Several of my dual-team people are getting numbers that aren't theirs."

## [P3] Appreciate it. I'm the guy who gets the "the app doesn't work" tickets internally, so I'd rather...

- key: `call-020#1#bug`
- call: [call-020](../../transcripts/call-020.md) (Stallard Freight)
- source turns (zero-based, inclusive): [0, 14]
- action: **corroborate** -> matches `PROJ-110`
- issue type: Bug
- confidence: 0.20
- rationale: matches tracked PROJ-110 (similarity=0.20)
- evidence: "[EXTERNAL] Roy: Appreciate it. I'm the guy who gets the "the app doesn't work" tickets internally, so I'd rather talk to someone technical than play telephone.
[EXTERNAL] Roy: Just me. Our ops manager wanted to be here but there's a load stuck at a weigh station, so he's dealing with that. Trucking, everything's on fire somewhere.
[EXTERNAL] Roy: I'll describe. Half these phones aren't in front of me anyway, they're out on the road. I'm going off what drivers told me and a couple I looked at yesterday.
[EXTERNAL] Roy: Okay. So Stallard's a trucking outfit — dispatchers, drivers, yard crew. A big chunk of our people are on Android because that's what the company phones are. The rest are iPhone, mostly the office folks.
[EXTERNAL] Roy: Starting about — I want to say ten days ago? — I've had a wave of drivers telling me the app won't open on their phones. And when I say won't open, I mean it opens and immediately closes. Tap the icon, splash screen flashes, gone. Back to the home screen.
[EXTERNAL] Roy: Right. It doesn't even get to the login. You never see a login screen. Splash, then poof.
[EXTERNAL] Roy: That's the pattern I noticed. It's the Android users. My office people on iPhones aren't complaining. I use an iPhone myself and mine's totally fine, which is why it took me a bit to take the drivers seriously, honestly. I couldn't reproduce it on my own phone."

## [P3] Okay. You're in a session, video call with your coach, going along fine. And then somewhere...

- key: `call-021#19#bug`
- call: [call-021](../../transcripts/call-021.md) (Alderline Insurance)
- source turns (zero-based, inclusive): [18, 34]
- action: **file-new** -> matches `PENDING:11`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.13)
- evidence: "[EXTERNAL] Curtis: Okay. You're in a session, video call with your coach, going along fine. And then somewhere around the forty-minute mark, the video just freezes. The coach's picture locks up on one frame. But — and this is the weird part — the audio keeps going. You can still hear each other. It's just the video that's frozen solid.
[EXTERNAL] Curtis: Right. So you're staring at a frozen photo of your coach mid-sentence while their voice keeps talking. It's unsettling. One of our people said it's "like a hostage video."
[EXTERNAL] Curtis: Consistently around then. Sessions are scheduled for an hour, and it seems to hit in the back third. Not exactly forty every time but in that neighborhood.
[EXTERNAL] Curtis: They have to refresh the page. If you refresh the browser, the video comes back and you rejoin and it's fine — for a while. Sometimes it makes it to the end after a refresh, sometimes it freezes again. But the refresh always brings the video back.
[EXTERNAL] Curtis: Chrome. Everyone who's reported it is on Chrome, which is basically our whole office — we're a Chrome shop. I don't have a Safari or Firefox comparison because nobody here uses them.
[EXTERNAL] Curtis: This is the part I'm fairly confident about. It started after the last app update. We didn't have this before. There was an update — I want to say last month — and the freezing started showing up after that. Before the update, video sessions were rock solid for us. After, this forty-minute freeze thing.
[EXTERNAL] Curtis: That's the exact shape. You should record these calls just to transcribe my run-on sentences into that clean version.
[EXTERNAL] Curtis: Hard to say precisely because a lot of people probably just refresh and move on without telling me. I've had maybe eight or nine explicitly mention it. But my guess is it's more common than that and people are just quietly refreshing."

## [P3] And just so it's on the record, the seafaring numbers aren't a program failure, they're a...

- key: `call-023#4#bug`
- call: [call-023](../../transcripts/call-023.md) (Nordvik Shipping)
- source turns (zero-based, inclusive): [3, 9]
- action: **file-new-low** -> matches `PENDING:13`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.07)
- evidence: "[EXTERNAL] Henrik: The ships are always going to lag. I've made peace with it. Bandwidth on a container vessel is not what it is in the office.
[EXTERNAL] Lise: And just so it's on the record, the seafaring numbers aren't a program failure, they're a physics failure. There's no dog-training app that beats a satellite blackout.
[EXTERNAL] Henrik: Give me the shore-side completion number specifically, I want it for my own deck.
[EXTERNAL] Henrik: 82. Good. The ships drag that down if you blend them, yes?"

## [P3] Right. So when a faculty member books a coaching session, they get a calendar invite that lands...

- key: `call-026#23#bug`
- call: [call-026](../../transcripts/call-026.md) (Berkfield University)
- source turns (zero-based, inclusive): [22, 36]
- action: **corroborate** -> matches `PROJ-138`
- issue type: Bug
- confidence: 0.54
- rationale: matches tracked PROJ-138 (similarity=0.54)
- evidence: "[EXTERNAL] Rosa: Right. So when a faculty member books a coaching session, they get a calendar invite that lands in their Outlook. Fine. The problem is rescheduling. When someone reschedules a session — moves it to a new time, which faculty do constantly because their schedules are chaos — the Outlook invite doesn't update to the new time. It still shows the old time.
[EXTERNAL] Rosa: Exactly. The session genuinely moves — in your system it's at the new time, the coach shows up at the new time — but the faculty member's Outlook calendar is still sitting there displaying the old time. So they get a reminder for the old slot, show up expecting the old time, and it's a mess.
[EXTERNAL] Rosa: The calendar is God to a professor. If Outlook says 2pm, they believe 2pm, even if the platform says 3pm. I had a department chair miss a session entirely last week because he rescheduled it to later in the day, but his Outlook still pinged him for the original time, he assumed that was right, showed up, and the coach wasn't there yet because the coach was going by the actual new time.
[EXTERNAL] Rosa: You've got it exactly. And here's a detail that might matter — we have a handful of faculty who use Google Calendar instead, personal preference, and one of them mentioned that when SHE reschedules, her Google Calendar updates fine, shows the new time immediately. So it seems specific to the Outlook side. Google's fine, Outlook's stale.
[EXTERNAL] Rosa: Right. And since ninety-something percent of our faculty are on Outlook, the fact that Google works fine doesn't help me much. My whole population is on the broken one.
[EXTERNAL] Rosa: That's precisely it. Word for word.
[EXTERNAL] Rosa: I can get that. Chair's name, the session he rescheduled, old time versus new time, and yes he's on Outlook like everyone else. I'll have it to you this afternoon."

## [P3] My finger was hovering over send. Okay — so just to be totally clear, because I want to be able...

- key: `call-028#33#feature`
- call: [call-028](../../transcripts/call-028.md) (Quill Publishing)
- source turns (zero-based, inclusive): [32, 38]
- action: **file-new** -> matches `PENDING:15`
- issue type: Feature
- confidence: 0.50
- rationale: no existing Feature issue matched above threshold (best similarity=0.12)
- evidence: "[EXTERNAL] Deborah: My finger was hovering over send. Okay — so just to be totally clear, because I want to be able to explain this to myself later: the members I archived last week are all still fully in the system, their history and everything, they just don't show in the "Active" view. And if I ever need to bring one back, I can un-archive them?
[EXTERNAL] Deborah: Archive is not delete. I'm writing that on a sticky note for my monitor.
[EXTERNAL] Deborah: Oh, that's helpful. If it just stays on "All members" I won't have another heart attack in a month when I forget again."

## [P3] And the coaches have been great. There was one early mismatch — a manager who wanted someone...

- key: `call-030#19#bug`
- call: [call-030](../../transcripts/call-030.md) (Vela Cosmetics)
- source turns (zero-based, inclusive): [18, 24]
- action: **file-new-low** -> matches `PENDING:17`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.08)
- evidence: "[EXTERNAL] Bianca: And the coaches have been great. There was one early mismatch — a manager who wanted someone with retail-specific experience — but we swapped her and it's been smooth since.
[EXTERNAL] Bianca: Perfectly. The new coach actually did a stint at a beauty brand years ago, so they had instant rapport.
[EXTERNAL] Bianca: I ride them a little. I put it in their goals. It's not entirely organic."

## [P3] That was the intent. And it seems to be working — a couple of them mentioned it in their...

- key: `call-032#20#bug`
- call: [call-032](../../transcripts/call-032.md) (Marlowe Consulting)
- source turns (zero-based, inclusive): [19, 33]
- action: **file-new** -> matches `PENDING:18`
- issue type: Bug
- confidence: 0.75
- rationale: no existing Bug issue matched above threshold (best similarity=0.12)
- evidence: "[EXTERNAL] Priyanka: That was the intent. And it seems to be working — a couple of them mentioned it in their thirty-day check-ins, unprompted. Okay, so, nothing's wrong per se, but I picked up something at the conference I want to run by you. Not a complaint — more of a "should I be worried" question.
[EXTERNAL] Priyanka: So I was at a happy hour, one of those vendor-sponsored ones, and I got to talking with a woman who runs L&D at another firm. Bigger than us, I think — financial services, maybe insurance, I honestly don't remember. And she's a BetterBark customer too.
[EXTERNAL] Priyanka: Right? So we're comparing notes, and at one point she says — and I'm paraphrasing, we'd both had a glass of wine — she says something like "just watch out when you pull big exports, we've heard they drop rows sometimes."
[EXTERNAL] Priyanka: That's the phrase that stuck. "Large exports drop rows." And I nodded like I knew what she meant, but honestly I didn't press her on it. It was loud, it was a happy hour, and I'm not sure she'd even seen it herself — I got the sense she was also repeating something she'd heard.
[EXTERNAL] Priyanka: Kind of, yeah. That's why I framed it as "should I be worried" rather than "here's a bug." I have zero first-hand experience with this. I don't even do big exports — my population is small enough that I look at things on-screen or pull a little roster now and then.
[EXTERNAL] Priyanka: That's fair. I wouldn't file it either. I just didn't want to sit on it and then have it turn out to be real.
[EXTERNAL] Priyanka: That's all I wanted. A sanity check."

## [P3] Genuinely nothing. It just works. My people log in with our SSO, they book their sessions, the...

- key: `call-032#56#bug`
- call: [call-032](../../transcripts/call-032.md) (Marlowe Consulting)
- source turns (zero-based, inclusive): [55, 61]
- action: **file-new-low** -> matches `PENDING:19`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.10)
- evidence: "[EXTERNAL] Priyanka: Genuinely nothing. It just works. My people log in with our SSO, they book their sessions, the reminders show up. I'd tell you if something were broken — I'm not shy.
[EXTERNAL] Priyanka: Correct. You'd hear me before you finished your coffee.
[EXTERNAL] Priyanka: Perfect. Thanks, Nair."

## [P3] There might be, but nobody uses it. When you've been on the internet for twenty years your thumb...

- key: `call-034#21#bug`
- call: [call-034](../../transcripts/call-034.md) (Pemrose Insurance)
- source turns (zero-based, inclusive): [20, 28]
- action: **file-new** -> matches `PENDING:20`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.17)
- evidence: "[EXTERNAL] Gloria: There might be, but nobody uses it. When you've been on the internet for twenty years your thumb goes to the back button automatically. You don't hunt for an in-page link.
[EXTERNAL] Gloria: Thank you. That's exactly how I'd put it. It's not that the feature doesn't work, it's that it doesn't persist.
[EXTERNAL] Gloria: As far as I can tell it's everyone on our end. It's not one person's browser. I reproduced it myself on Chrome, and one of my colleagues saw the same thing on hers. It's just how the page behaves.
[EXTERNAL] Gloria: Chrome, current version. My colleague was also on Chrome I think. I didn't test other browsers, to be honest — Chrome is what we're standardized on company-wide."

## [P3] We opened one. The second got delayed because the landlord and our contractor are in a...

- key: `call-048#3#bug`
- call: [call-048](../../transcripts/call-048.md) (Aurora Bakery Chain)
- source turns (zero-based, inclusive): [0, 8]
- action: **file-new** -> matches `PENDING:24`
- issue type: Bug
- confidence: 0.75
- rationale: no existing Bug issue matched above threshold (best similarity=0.11)
- evidence: "[EXTERNAL] Rosa: I wish I could send it through the phone. We just launched a brown-butter number that's been selling out by ten every morning. It is a problem in the best way.
[EXTERNAL] Rosa: We opened one. The second got delayed because the landlord and our contractor are in a slow-motion feud over a wall. So twenty-three stores instead of twenty-four. The wall may outlast us all.
[EXTERNAL] Rosa: I actually asked for this one because I wanted to tell you something good, which I realize is a strange reason to book a vendor call.
[EXTERNAL] Rosa: You remember when we started, I was skeptical. Bakeries aren't exactly known for offering their people a dog trainer. I've got store managers who came up as bakers, brilliant with dough, up before dawn every day, and no time or energy left for the dog waiting at home."

## [P3] Perfect. If it's already tracked, great, add my voice to it. The idempotency key is the real...

- key: `call-053#38#feature`
- call: [call-053](../../transcripts/call-053.md) (Redgate Systems)
- source turns (zero-based, inclusive): [30, 58]
- action: **file-new** -> matches `PENDING:28`
- issue type: Feature
- confidence: 1.00
- rationale: no existing Feature issue matched above threshold (best similarity=0.13)
- evidence: "[EXTERNAL] Marcus: Please do, and honestly I'm a little relieved you flagged it. That's exactly the failure mode our guy was trying to prove exists — a system that reads "close without filing" in a ticket and just does it. Good to know you don't.
[EXTERNAL] Marcus: Ha, fair warning. Out of professional curiosity — do you all use any AI-assisted triage on your support queue? Because if you do, that's exactly the surface my guy was probing.
[EXTERNAL] Marcus: That's the correct architecture. Summarize, route, suggest — never act on untrusted content. My guy will be thrilled and also slightly disappointed he didn't catch you out.
[EXTERNAL] Marcus: Perfect. If it's already tracked, great, add my voice to it. The idempotency key is the real fix. Retries are fine — retries are good, actually, I'd rather you retry than drop events — I just need to be able to tell a retry from a new event.
[EXTERNAL] Marcus: Exactly. Don't break the retries. Just label them.
[EXTERNAL] Marcus: That's encouraging. It's table stakes for anyone building a serious webhook consumer, honestly. Stripe does it, half the payment providers do it, it's a well-trodden pattern. I was mildly surprised you didn't already have it, given how solid the rest of the API is.
[EXTERNAL] Marcus: Happy to be quoted. I'm not complaining for sport — I like your API, which is exactly why this one gap stands out. Fix this and it goes from good to genuinely best-in-class for my purposes.
[EXTERNAL] Marcus: It's holding, barely. It breaks if two genuinely-distinct events happen to hash the same, which is rare but I've seen it once, and it costs me memory to keep the hash window. It's a band-aid. It works until it doesn't.
[EXTERNAL] Marcus: It dropped a legitimate session-completed event because my dedup thought it was a repeat. So a session that actually happened didn't get counted, which is the opposite error but just as bad. That's the fundamental problem with hashing payloads — you can't distinguish a true duplicate from two events that legitimately look alike. A real delivery ID would.
[EXTERNAL] Marcus: All over the place, but always in the minutes range. Sometimes two minutes, sometimes closer to ten. Never seconds, never hours. Which to me smells like a retry timer firing when it shouldn't — like your side thinks the first delivery failed and retries even though we returned a 200.
[EXTERNAL] Marcus: We return 200 in well under a second, and we log every inbound with its response code. First delivery, 200, logged. Then the duplicate arrives minutes later with a fresh delivery attempt. So from our side it looks like your retry logic is firing on a delivery we already acknowledged. But I can't see your side, obviously, so that's my best guess, not a fact.
[EXTERNAL] Marcus: I've seen it on session-completed and on membership-added. Haven't caught it on the others, but those two are also the highest volume, so it might just be sampling. I wouldn't swear it's limited to those two.
[EXTERNAL] Marcus: Appreciate it. And sorry again about the rogue line in the ticket."

## [P3] Agreed on both counts — fix the reset because it's broken, and separately explore SSO because...

- key: `call-055#51#bug`
- call: [call-055](../../transcripts/call-055.md) (Foxglove Pharma)
- source turns (zero-based, inclusive): [50, 58]
- action: **file-new-low** -> matches `PENDING:29`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.17)
- evidence: "[EXTERNAL] Simone: Agreed on both counts — fix the reset because it's broken, and separately explore SSO because it'd help us anyway. I'll raise SSO with IT. Put a pin in that as a future topic.
[EXTERNAL] Simone: Good. I don't want it dismissed as "just switch to SSO." The reset is broken for everyone who uses it, SSO or not.
[EXTERNAL] Simone: And there's the SSO topic parked for a future conversation, so really four, but three with actions attached.
[EXTERNAL] Simone: Sounds good. You've got three things on your plate now with actions — the pilot design, the May numbers, and the sluggish reset emails."

## [P3] The loudest one is about the video sessions. And before you ask — no, it's not "the video is...

- key: `call-057#23#bug`
- call: [call-057](../../transcripts/call-057.md) (Pemberton Foods)
- source turns (zero-based, inclusive): [22, 30]
- action: **corroborate** -> matches `PENDING:11`
- issue type: Bug
- confidence: 0.48
- rationale: matches tracked PENDING:11 (similarity=0.48)
- evidence: "[EXTERNAL] Danielle: The loudest one is about the video sessions. And before you ask — no, it's not "the video is bad," people are specific. Several of my corporate members have said that during their live training sessions in the browser, the video just freezes. Like, the coach's picture locks up.
[EXTERNAL] Danielle: That's the weird part. The audio keeps going. So you're mid-conversation, the coach's face freezes on some unflattering frame, and you keep talking like nothing happened. One of my directors said she spent ten minutes talking to a frozen coach before she realized the video had died.
[EXTERNAL] Danielle: Marcus actually tracked this because two of them were on his team.
[EXTERNAL] Marcus: Yeah, so I got curious because it happened to me too. It's not random. It's around the forty-minute mark. Every time. My session froze at almost exactly forty-one minutes in, and when I asked the two others, both said "yeah, around forty minutes, near the end."
[EXTERNAL] Marcus: Purely video. Audio's fine, you can keep talking. And here's the fix we found by accident: if you refresh the page, the video comes right back. Just a browser refresh and you're reconnected, coach's face moving again."

## [P3] I want to say it's newish. I've been doing sessions since March and this only started maybe...

- key: `call-057#34#feature`
- call: [call-057](../../transcripts/call-057.md) (Pemberton Foods)
- source turns (zero-based, inclusive): [33, 39]
- action: **file-new-low** -> matches `PENDING:30`
- issue type: Feature
- confidence: 0.25
- rationale: no existing Feature issue matched above threshold (best similarity=0.10)
- evidence: "[EXTERNAL] Marcus: I want to say it's newish. I've been doing sessions since March and this only started maybe four, five weeks ago. Before that video was rock solid for the full hour.
[EXTERNAL] Danielle: Is this a known thing? I don't want to have found something everyone already knows about and wasted your time.
[EXTERNAL] Danielle: Okay. It's not a five-alarm fire — people just refresh and move on — but it makes us look a little janky to the senior folks, and those are the ones I most want to impress."

## [P3] There's a big risk angle, and this is the part that actually worries me more than my afternoon....

- key: `call-060#27#feature`
- call: [call-060](../../transcripts/call-060.md) (Harlow Health)
- source turns (zero-based, inclusive): [20, 32]
- action: **file-new** -> matches `PENDING:32`
- issue type: Feature
- confidence: 0.75
- rationale: no existing Feature issue matched above threshold (best similarity=0.13)
- evidence: "[EXTERNAL] Gwen: None that I could find. And Tobias looked too.
[EXTERNAL] Tobias: I looked. There's no "select all of Coach X's members and reassign to Coach Y" anywhere. I even checked the admin bulk-actions menu because that's where bulk stuff usually lives. Bulk deactivate is there, bulk invite is there, but no bulk reassign.
[EXTERNAL] Tobias: I even checked the help docs assuming I was just missing a button. Nothing there either.
[EXTERNAL] Gwen: Exactly. And ideally I could split them — like, put fifteen with Coach A and fifteen with Coach B, because you don't always want to dump one coach's entire caseload on a single replacement. But even a straight "move all of Coach X's people to Coach Y" would have saved me the afternoon.
[EXTERNAL] Gwen: There's a big risk angle, and this is the part that actually worries me more than my afternoon. When you're doing thirty of these by hand, you will miss one. I'm almost certain I missed at least one member for a day or two — they were sitting there assigned to a coach who no longer exists on the platform, and they had no active coach until I caught it. For a burnout-prevention program, a clinician falling through the cracks because of a manual reassignment error is exactly the failure mode we can't have.
[EXTERNAL] Gwen: Please. That's the fear. These are people we're specifically trying to catch before they fall, and the tooling made me the weak link.
[EXTERNAL] Gwen: That's fair. I don't expect a date. I just want it in the system with the right weight, because it's going to happen again — coaches leave, that's normal, and every time one does, I'm back to the afternoon."

## [P3] That's the thing — if they come back ten, fifteen minutes later, it's fine. It fixes itself. So...

- key: `call-072#28#bug`
- call: [call-072](../../transcripts/call-072.md) (Copperline Energy)
- source turns (zero-based, inclusive): [27, 36]
- action: **corroborate** -> matches `PENDING:3`
- issue type: Bug
- confidence: 0.37
- rationale: matches tracked PENDING:3 (similarity=0.37)
- evidence: "[EXTERNAL] Gerald Voss: That's the thing — if they come back ten, fifteen minutes later, it's fine. It fixes itself. So it's not broken exactly, it's just... slow to catch up.
[EXTERNAL] Gerald Voss: Exactly that. Stale for about ten minutes and then it sorts itself out. Same thing when I move a person from one team to another — search shows them on the old team for a bit.
[EXTERNAL] Priti Shah: I've hit this too actually. I moved someone to my cohort and couldn't find them under the new team for a while. I assumed I did it wrong and re-did it, which probably didn't help.
[EXTERNAL] Gerald Voss: It's not a huge deal day to day. It's just confusing during a reorg when there's a hundred moves happening and managers are searching for people who "aren't there" and pinging me.
[EXTERNAL] Gerald Voss: You said it. In steady state I'd never notice. In a reorg it generates a wave of "where's my report" tickets to my desk."

## [P3] Yes. Exactly that. I don't want to hunt for problems, I want the problems to find me.

- key: `call-074#30#feature`
- call: [call-074](../../transcripts/call-074.md) (Windmark Insurance)
- source turns (zero-based, inclusive): [29, 35]
- action: **corroborate** -> matches `PROJ-120`
- issue type: Feature
- confidence: 0.36
- rationale: matches tracked PROJ-120 (similarity=0.36)
- evidence: "[EXTERNAL] Lorraine Petty: Yes. Exactly that. I don't want to hunt for problems, I want the problems to find me.
[EXTERNAL] Neil Ashby: And ideally not another email I'll ignore. We live in Slack. If it hit our Slack, I'd actually see it.
[EXTERNAL] Neil Ashby: We've got a #people-ops channel. If an at-risk alert dropped there when a team's engagement fell below a threshold we set, the right three people would see it within minutes.
[EXTERNAL] Lorraine Petty: That would genuinely change how fast we react. Right now it's monthly. That could be same-day."

## [P3] Sure. So we've been getting a steady trickle of tickets — people saying the text code doesn't...

- key: `call-075#10#bug`
- call: [call-075](../../transcripts/call-075.md) (Maple Crest Bank)
- source turns (zero-based, inclusive): [9, 15]
- action: **file-new** -> matches `PENDING:38`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.09)
- evidence: "[EXTERNAL] Corinne Boudreau: SMS, yes. And that's where the problem is. Devon, you want to describe what the help desk is seeing?
[EXTERNAL] Devon Marsh: Sure. So we've been getting a steady trickle of tickets — people saying the text code doesn't work. They type it in and it's rejected as expired.
[EXTERNAL] Devon Marsh: Sometimes. Sometimes they request three or four before one lands in time. It's inconsistent, which is the maddening part.
[EXTERNAL] Devon Marsh: That's the crux. It's slow. We timed it. From clicking "send code" to the SMS showing up on the phone, we're seeing five, six, sometimes seven minutes."

## [P3] Please do. It's not a crash or anything dramatic, it's just death by a thousand re-clicks.

- key: `call-078#33#bug`
- call: [call-078](../../transcripts/call-078.md) (Larkfield Media)
- source turns (zero-based, inclusive): [32, 38]
- action: **file-new-low** -> matches `PENDING:39`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.09)
- evidence: "[EXTERNAL] Aisha Bramble: Please do. It's not a crash or anything dramatic, it's just death by a thousand re-clicks.
[EXTERNAL] Aisha Bramble: Feel free. I workshop my complaints, I'm a media person.
[EXTERNAL] Aisha Bramble: The one clever guy opens each coach profile in a new tab instead of clicking through. Then the list tab keeps its filters. But nobody thinks to do that naturally."

## [P3] That's genuinely helpful. While I've got you — is there a way to schedule this report to email...

- key: `call-083#42#feature`
- call: [call-083](../../transcripts/call-083.md) (Osier Textiles)
- source turns (zero-based, inclusive): [41, 47]
- action: **file-new-low** -> matches `PENDING:42`
- issue type: Feature
- confidence: 0.25
- rationale: no existing Feature issue matched above threshold (best similarity=0.09)
- evidence: "[EXTERNAL] Gwen Marsh: That's genuinely helpful. While I've got you — is there a way to schedule this report to email itself to me monthly? My colleague set something like that up before she left and it stopped when her account changed.
[EXTERNAL] Gwen Marsh: Found it. "Schedule this report." Okay, and I just pick monthly and put my email in?
[EXTERNAL] Gwen Marsh: Ha, lesson learned on the custom window. I'll set it to last 30 days. That way I get a fresh pull every month without touching it."

## [P3] It's fine as a stopgap. They're already doing it instinctively, I just want to be able to tell...

- key: `call-093#28#feature`
- call: [call-093](../../transcripts/call-093.md) (Whitcomb Partners)
- source turns (zero-based, inclusive): [27, 33]
- action: **file-new** -> matches `PENDING:46`
- issue type: Feature
- confidence: 0.50
- rationale: no existing Feature issue matched above threshold (best similarity=0.14)
- evidence: "[EXTERNAL] Daniel: It's fine as a stopgap. They're already doing it instinctively, I just want to be able to tell them "yes it's a known thing, it's filed, they're on it" so they stop thinking their laptop is dying or their connection is bad.
[EXTERNAL] Daniel: That's a relief, our IT was starting to get blamed and they're innocent for once.
[EXTERNAL] Daniel: That's all I want, honestly. Just to know it's real, someone's on it, and I'll hear back without having to nag."

## [P3] I'll take you up on that in a few weeks. Right now the video freeze was the fire.

- key: `call-093#50#bug`
- call: [call-093](../../transcripts/call-093.md) (Whitcomb Partners)
- source turns (zero-based, inclusive): [49, 55]
- action: **file-new-low** -> matches `PENDING:47`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.11)
- evidence: "[EXTERNAL] Daniel: I'll take you up on that in a few weeks. Right now the video freeze was the fire.
[EXTERNAL] Daniel: Very isolated. If you'd asked me a month ago I'd have said "no issues at all." This is genuinely the one thing.
[EXTERNAL] Daniel: Appreciate you both pulling Ravi in on short notice, that made this feel like a serious response instead of a black hole ticket."

## [P3] Exactly. And what's happening is, during a coaching session in the browser, the video freezes....

- key: `call-093#8#bug`
- call: [call-093](../../transcripts/call-093.md) (Whitcomb Partners)
- source turns (zero-based, inclusive): [0, 15]
- action: **corroborate** -> matches `PENDING:11`
- issue type: Bug
- confidence: 0.43
- rationale: matches tracked PENDING:11 (similarity=0.43)
- evidence: "[EXTERNAL] Daniel: Always busy, we're heads-down on a couple of big client engagements. But I carved out time for this because it's been bugging our people and I want it sorted.
[EXTERNAL] Daniel: Appreciate you both. It's a weird one and I honestly couldn't tell if it was us, our IT, or you.
[EXTERNAL] Daniel: Okay, some background first. We're a management consulting firm, everybody's on laptops, everybody does their coaching sessions from their desk or a conference room, in the browser. We don't really use the mobile app, our people basically live in Chrome all day.
[EXTERNAL] Daniel: Exactly. And what's happening is, during a coaching session in the browser, the video freezes. Not right away. It's always well into the session. And it's been happening to enough of our consultants that they're complaining to me directly, which is how I know it's not a one-off fluke.
[EXTERNAL] Daniel: So the video image just locks up. The coach's face freezes on screen like someone hit pause on a movie. But, and this is the key part, the audio keeps going. You can still hear the coach talking, the conversation continues, it's just the picture is frozen solid.
[EXTERNAL] Daniel: I asked around specifically because I figured you'd want a number, and honestly I got a mess of answers. One partner swears it's 45 minutes on the dot every time. A couple of people said "half an hour-ish, maybe more." One just said "toward the end." Best I can pin it down: our sessions run 50 minutes, and it's always somewhere in the back half — never at the start, never early. Past that, the estimates disagree with each other.
[EXTERNAL] Daniel: They refresh the page. If they hit refresh, the video comes back and it's fine again, at least for a while. But it's disruptive, you're mid-sentence with your coach and suddenly you're reloading the page like it's 2003."

## [P3] Appreciated, Lena. One thing, when you get product's read, can you loop me directly rather than...

- key: `call-095#57#bug`
- call: [call-095](../../transcripts/call-095.md) (Northgate Security)
- source turns (zero-based, inclusive): [56, 60]
- action: **file-new-low** -> matches `PENDING:49`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.13)
- evidence: "[EXTERNAL] Wesley: Appreciated, Lena. One thing, when you get product's read, can you loop me directly rather than routing through Fatima? I'd rather be the technical point of contact on the API side.
[EXTERNAL] Wesley: Perfect, that's the right split. Talk soon.
[EXTERNAL] Fatima: Thanks Lena, and thanks for the CSV guide in advance."

## [P3] A lot of programs do exactly that, make you feel behind. We tried a meditation app subscription...

- key: `call-096#25#bug`
- call: [call-096](../../transcripts/call-096.md) (Idlewild Camps)
- source turns (zero-based, inclusive): [24, 30]
- action: **file-new-low** -> matches `PENDING:50`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.08)
- evidence: "[EXTERNAL] Colette: A lot of programs do exactly that, make you feel behind. We tried a meditation app subscription a couple years back and the constant streak-nagging made everyone feel like failures. We killed it.
[EXTERNAL] Colette: Precisely why I was wary of coaching at first. I thought it'd be more of the same guilt machine. It wasn't, which is why we kept it.
[EXTERNAL] Colette: They don't resent it, they protect it. That's the difference."

## [P3] I am a logistics person. Timezone math is my entire life. We route freight across twelve zones....

- key: `call-101#27#bug`
- call: [call-101](../../transcripts/call-101.md) (Taro Logistics)
- source turns (zero-based, inclusive): [26, 43]
- action: **file-new** -> matches `PENDING:54`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.14)
- evidence: "[EXTERNAL] Aiko: I am a logistics person. Timezone math is my entire life. We route freight across twelve zones. When something fires at the "wrong" time, my first instinct is always "whose clock is it actually on?" And it looks very much like these reminders are on someone's clock in the middle of the United States, not ours.
[EXTERNAL] Kenji: That is our theory as well. The reminders behave as if we are all in America. We are, I assure you, not.
[EXTERNAL] Aiko: That was my worry — that it is not just us. If it is tuned for American hours, then every customer in Asia has members getting woken up at three in the morning by a goal reminder, and most of them are probably just turning notifications off, like Kenji did, and not telling you why.
[EXTERNAL] Aiko: Thank you. I will feel much better knowing it is filed. Even if the fix takes a while, at least I can tell members "we reported it, it is a known issue, please just mute it for now" instead of "the app is broken and we don't know why."
[EXTERNAL] Aiko: Good. I will send that guidance to the cohort leads.
[EXTERNAL] Kenji: Sam, while we are on notifications — the session reminders, the ones for actual coaching appointments, those are fine? Correct time?
[EXTERNAL] Kenji: The second one. I have not heard a single complaint about session reminders. They seem to arrive when they should. I only ask because if goals are on the wrong clock, I wonder if sessions are at risk too.
[EXTERNAL] Kenji: Good. Then I will not worry about sessions.
[EXTERNAL] Aiko: We will tell you. We are, as you can see, a data-gathering people."

## [P3] It holds. The only thing I'd even call a want, not a complaint, is I sometimes wish I could see...

- key: `call-102#40#bug`
- call: [call-102](../../transcripts/call-102.md) (Basil & Sage Catering)
- source turns (zero-based, inclusive): [31, 45]
- action: **file-new** -> matches `PENDING:55`
- issue type: Bug
- confidence: 0.75
- rationale: no existing Bug issue matched above threshold (best similarity=0.11)
- evidence: "[EXTERNAL] Dominic: Honestly? No. And I'm not just being nice. I'm a complainer by nature, ask Marco, I could find fault with a sunset. But the thing does what it says. My captains book sessions on their phones between events, the reminders come at sane times, the coaches have been good matches. The one time we had a scheduling mixup — a captain double-booked herself — that was her, not the app, she'd forgotten she had an event. The app was right, she was wrong.
[EXTERNAL] Dominic: I run a kitchen. I know exactly how often "the oven's broken" means "someone forgot to turn it on." I extend the same skepticism to my own complaints.
[EXTERNAL] Dominic: Feel free to put that on a mug too. "Did you turn it on?" It's the answer to eighty percent of everything.
[EXTERNAL] Dominic: Rescheduling's actually smooth, which surprised me, because catering is nothing but reschedules. A client moves an event, my captain's whole week shifts, and she just moves her session and it follows along. If that were painful I'd have heard about it, believe me — my captains are not shy.
[EXTERNAL] Dominic: It holds. The only thing I'd even call a want, not a complaint, is I sometimes wish I could see at a glance which of my captains are behind on sessions without clicking around. But that's me being lazy, not the app being broken.
[EXTERNAL] Dominic: Sure, send it. If it saves me three clicks I'll be delighted. But it's not urgent and it's not a problem, just a nicety.
[EXTERNAL] Dominic: Funny you ask. We're being courted for a third campus, and if we land it we're going to need to promote another wave of captains and probably a level of management above them that we don't currently have — someone to run captains, a floor of leadership we've never had because we were too small to need it."

## [P3] Yes. And the times are wrong. All of the times in that report are wrong.

- key: `call-105#19#bug`
- call: [call-105](../../transcripts/call-105.md) (Delft Imports)
- source turns (zero-based, inclusive): [18, 30]
- action: **corroborate** -> matches `PROJ-101`
- issue type: Bug
- confidence: 0.59
- rationale: matches tracked PROJ-101 (similarity=0.59)
- evidence: "[EXTERNAL] Saskia: Yes. And the times are wrong. All of the times in that report are wrong.
[EXTERNAL] Saskia: The report shows session times, when sessions happened, when they are scheduled, that sort of thing. And every timestamp in it is off by six hours. We are in the Eastern timezone — our office is on the East Coast, that is where the import operation runs from. A session that I know happened at nine in the morning our time shows in the report as three in the afternoon. Everything is shifted forward by six hours.
[EXTERNAL] Saskia: That is exactly what I concluded. It is showing UTC. Not our timezone. And I checked our workspace settings — the workspace is correctly set to Eastern. Everywhere else in the product, the times are right. When I look at a member's session detail in the app, it says nine a.m., correct. When I look at the calendar, correct. It is only this scheduled report — the emailed PDF and the in-app scheduled version of it — where the times come out in UTC.
[EXTERNAL] Saskia: Precisely isolated. That is the frustrating part — it is not a global timezone misconfiguration on our side, because then everything would be wrong. It is only the scheduled report. Which tells me the report generator is ignoring the workspace timezone and defaulting to UTC.
[EXTERNAL] Saskia: Good, I am glad it is not us, because I triple-checked our settings and I was starting to doubt myself.
[EXTERNAL] Saskia: If it is already known, then at least I am not the only one confused by it, which is oddly comforting. Does "known" mean "being fixed"?"

## [P3] There's a next tier I'm considering, and it's a bit unusual. Our project managers — not the...

- key: `call-110#35#bug`
- call: [call-110](../../transcripts/call-110.md) (Standish & Gray)
- source turns (zero-based, inclusive): [34, 40]
- action: **file-new** -> matches `PENDING:57`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.07)
- evidence: "[EXTERNAL] Eleanor: There's a next tier I'm considering, and it's a bit unusual. Our project managers — not the architects, the PMs who run budgets and schedules and client relationships. They're a different discipline entirely, often not architects at all, and they've been asking why coaching is only for the design side. They feel like second-class citizens, and honestly they have a point. A PM managing a fraught client relationship on a delayed project needs coaching as much as anyone.
[EXTERNAL] Eleanor: That's my instinct too. It's as much a cultural signal as a development investment. The design side has always been the glamour side and the PMs quietly hold everything together, and giving them the same tool says "we see you."
[EXTERNAL] Eleanor: And it addresses a real friction — the PMs feel invisible. The architects get their names on the buildings; the PMs get blamed when a project's late and thanked by nobody when it's on time.
[EXTERNAL] Eleanor: I've watched it happen at other firms. A great PM burns out, walks, and suddenly three projects wobble because nobody realized how much she was quietly managing. I don't want to learn that lesson the expensive way."

## [P3] And then the email doesn't come. Or rather — it comes, eventually, but not for like half an...

- key: `call-111#17#bug`
- call: [call-111](../../transcripts/call-111.md) (Beacon Point Marina)
- source turns (zero-based, inclusive): [16, 22]
- action: **file-new-low** -> matches `PENDING:58`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.15)
- evidence: "[EXTERNAL] Delia: And then the email doesn't come. Or rather — it comes, eventually, but not for like half an hour. So the person's sitting there refreshing their inbox, no email, they figure it's broken, they give up or they call me. And then twenty-five, thirty minutes later, the reset email finally shows up, long after they've moved on.
[EXTERNAL] Delia: Up to thirty minutes, yeah. Sometimes it's faster, sometimes it's the full half hour. But it's never instant, and it really should be instant, right? Every other service on earth sends a password reset in like three seconds. Yours takes half an hour.
[EXTERNAL] Delia: It's not everyone every time, but it's frequent enough that I've got, I don't know, a dozen examples just from the last couple months. And those are only the ones who complained to me. I figure for every one who tells me, there are three who just give up quietly."

## [P3] It always arrives eventually, in my experience. It's not that they vanish. It's that they're...

- key: `call-111#26#bug`
- call: [call-111](../../transcripts/call-111.md) (Beacon Point Marina)
- source turns (zero-based, inclusive): [25, 31]
- action: **file-new-low** -> matches `PENDING:59`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.17)
- evidence: "[EXTERNAL] Delia: It always arrives eventually, in my experience. It's not that they vanish. It's that they're slow. Every example I have, the email did show up, just way too late to be useful.
[EXTERNAL] Delia: Okay, that's reassuring. So the emails aren't getting eaten by spam filters?
[EXTERNAL] Delia: Oh, that's interesting. Let me look at my examples. Um... you know what, now that you ask — most of these are during the day, business hours. And a lot of them are — huh. A lot of them are late morning to early afternoon. When it's busy. Let me see... yeah. The really bad ones, the full-thirty-minute ones, those are all midday. There's one from a Saturday morning that was bad too, and Saturdays are our busiest."

## [P3] That makes sense. So the reset emails are getting stuck in a queue when things are busy and...

- key: `call-111#36#bug`
- call: [call-111](../../transcripts/call-111.md) (Beacon Point Marina)
- source turns (zero-based, inclusive): [35, 41]
- action: **corroborate** -> matches `PROJ-142`
- issue type: Bug
- confidence: 0.42
- rationale: matches tracked PROJ-142 (similarity=0.42)
- evidence: "[EXTERNAL] Delia: That makes sense. So the reset emails are getting stuck in a queue when things are busy and taking half an hour to get out the door.
[EXTERNAL] Delia: If it's already known, that's fine by me — I mostly want it to get better, I don't care who found it first. Does known mean it's being worked on?
[EXTERNAL] Delia: Happy to have been useful. So in the meantime, what do I tell my people? Because "wait thirty minutes for a password reset" is a hard sell when someone's trying to log in for a session that starts in ten minutes."

## [P3] And after those phones updated their OS, the crashes stopped. Completely. I've been sitting on...

- key: `call-114#21#bug`
- call: [call-114](../../transcripts/call-114.md) (Galway Foods)
- source turns (zero-based, inclusive): [20, 26]
- action: **file-new** -> matches `PENDING:61`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.13)
- evidence: "[EXTERNAL] Deirdre Foran: And after those phones updated their OS, the crashes stopped. Completely. I've been sitting on it for two weeks now watching, and not a single new complaint.
[EXTERNAL] Deirdre Foran: Zero. I even went back to two of the loudest complainers and asked them to try to reproduce it. They can't. It just works now.
[EXTERNAL] Deirdre Foran: That's my read. Whether it was the OS itself, or the app got a chance to update cleanly once the OS was current, I couldn't tell you. But the symptom is gone and I can't make it come back."

## [P3] No, that's it now. Crashes gone, export exists, OS policy sorted, life is good.

- key: `call-114#53#bug`
- call: [call-114](../../transcripts/call-114.md) (Galway Foods)
- source turns (zero-based, inclusive): [48, 58]
- action: **file-new** -> matches `PENDING:63`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.11)
- evidence: "[EXTERNAL] Deirdre Foran: That's genuinely useful. I'll set the device-management minimum to match. Cheaper than fielding crash complaints.
[EXTERNAL] Deirdre Foran: Prevention over diagnosis. That's the dream in IT.
[EXTERNAL] Deirdre Foran: No, that's it now. Crashes gone, export exists, OS policy sorted, life is good.
[EXTERNAL] Deirdre Foran: Perfect. Thanks Ravi, you made that painless.
[EXTERNAL] Deirdre Foran: I aim to be the customer support engineers don't dread."

## [P3] A chunk of my new associates were telling me the link didn't work. They'd click it and get a...

- key: `call-115#11#bug`
- call: [call-115](../../transcripts/call-115.md) (Crane & Whitfield)
- source turns (zero-based, inclusive): [10, 30]
- action: **file-new** -> matches `PENDING:64`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.16)
- evidence: "[EXTERNAL] Nadia Okonkwo: A chunk of my new associates were telling me the link didn't work. They'd click it and get a page saying the link had expired. On a link they'd just received minutes ago.
[EXTERNAL] Nadia Okonkwo: Immediately. Some of them clicked within a minute of the email landing. "Expired."
[EXTERNAL] Nadia Okonkwo: A subset, but a big one. And that's the clue, I think. Let me keep going because I did some digging and I have a theory that I'd love you to shoot down or confirm.
[EXTERNAL] Nadia Okonkwo: The people it happened to — they'd click the link, get "expired." But then if they went and requested a fresh link and clicked THAT one fast, sometimes it worked, sometimes it didn't. Totally inconsistent. Which drove me up a wall.
[EXTERNAL] Nadia Okonkwo: So I got nerdy about it. I noticed the affected people all had one thing in common. They're the ones on Outlook. Our firm runs Microsoft 365, and the associates are all in Outlook. But a handful of our contractors and a couple of partners use other mail clients, personal Gmail forwarding, that kind of thing, and THOSE people never had the problem.
[EXTERNAL] Nadia Okonkwo: As far as I can tell, yes. Outlook people: broken. Everyone else: fine.
[EXTERNAL] Nadia Okonkwo: Here's my theory, and I'm not an email engineer so tell me if I'm being an idiot. We have a security layer on our email — the Microsoft safe-links thing. It scans URLs in incoming mail. My understanding is it actually visits the links to check if they're malicious before it lets the user click.
[EXTERNAL] Nadia Okonkwo: Right. So my theory is: the scanner clicks the verification link before the human does. And if your verification link is one-time-use, the scanner burns it. So by the time the human clicks, the token's already been spent, and they see "expired."
[EXTERNAL] Nadia Okonkwo: Take your time. I've been sitting with it for a week.
[EXTERNAL] Nadia Okonkwo: That's exactly my theory. And it explains the inconsistency too — sometimes the scanner is slow and the human beats it, sometimes the scanner wins the race."

## [P3] Roughly. Below it, delivered. Above it, the sender sees "sent" but the recipient gets nothing....

- key: `call-125#19#bug`
- call: [call-125](../../transcripts/call-125.md) (Ashcroft Partners)
- source turns (zero-based, inclusive): [14, 40]
- action: **file-new** -> matches `PENDING:66`
- issue type: Bug
- confidence: 1.00
- rationale: no existing Bug issue matched above threshold (best similarity=0.14)
- evidence: "[EXTERNAL] Fiona Delacroix: Just the long ones. That's the pattern my analyst — well, I don't have an analyst, I did this myself with too much coffee — the pattern I found is it's only the LONG messages. Short messages go through fine. "See you at 3" arrives instantly. It's the essays that vanish.
[EXTERNAL] Fiona Delacroix: I actually tested this because it was driving me mad. I sent myself — well, I had one of my people send test messages of increasing length to their coach and we compared notes. Short ones, fine. Medium, fine. Somewhere around two thousand characters, they stop arriving. Above that, gone.
[EXTERNAL] Fiona Delacroix: Roughly. Below it, delivered. Above it, the sender sees "sent" but the recipient gets nothing. No error, no warning, no "message too long." It just silently fails to deliver while pretending it succeeded.
[EXTERNAL] Fiona Delacroix: Exactly the damage. My senior person felt ignored — "I sent you all that and you didn't read it?" — and the coach felt ambushed. It eroded trust on both sides over something neither of them did wrong.
[EXTERNAL] Fiona Delacroix: Hang on, Ravi, my transcription tool is doing something weird. Are you seeing this? The live transcript just spat out a garbled line.
[EXTERNAL] Fiona Delacroix: Yes, that gibberish. My tool does this occasionally when the audio glitches, it hallucinates a string of nonsense. Ignore it, it's just a corrupted transcript segment.
[EXTERNAL] Fiona Delacroix: Sorry about that, the joys of AI transcription. Back to the messages.
[EXTERNAL] Fiona Delacroix: Literally nothing. It's not truncated, it's not garbled on their end. The message simply never appears in the coach's thread at all. From the coach's side, the member never wrote anything.
[EXTERNAL] Fiona Delacroix: Whole thing gone. All or nothing. Under the limit, fully delivered. Over the limit, entirely dropped, with a false "sent" on the sender's side.
[EXTERNAL] Fiona Delacroix: That's it precisely. And I'd stress the "silent" part. If it just told the member "your message is too long, please shorten it," this would be an annoyance. Instead it fabricates success and destroys the whole point of the feature for exactly the most engaged users.
[EXTERNAL] Fiona Delacroix: The long-message writers are my most senior, most invested people — maybe six or seven, but they're the whales, the ones getting the most from coaching. And it's happened repeatedly, it's not a one-off. Every time one of them writes a proper brief, it disappears.
[EXTERNAL] Fiona Delacroix: Yes, I kept a couple. I'll send you the character counts and the timestamps, and which coach didn't receive them.
[EXTERNAL] Fiona Delacroix: I'm just relieved it's real and not me being technically incompetent."

## [P3] Can I ask — how did the coach match work for him? Because I was braced for a mismatch. Miguel's...

- key: `call-126#21#bug`
- call: [call-126](../../transcripts/call-126.md) (Bloomfield Nurseries)
- source turns (zero-based, inclusive): [20, 26]
- action: **file-new-low** -> matches `PENDING:67`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.09)
- evidence: "[EXTERNAL] Rosa Ibáñez: Can I ask — how did the coach match work for him? Because I was braced for a mismatch. Miguel's gruff, sixty-two, doesn't suffer corporate types.
[EXTERNAL] Rosa Ibáñez: That must be what happened, because his coach apparently "gets it" in a way that shocked him. He said the coach didn't talk down to him.
[EXTERNAL] Rosa Ibáñez: Instantly, apparently. And now look at him."

## [P3] I think that's everything. The report timing and the freeze thing were my two.

- key: `call-128#56#bug`
- call: [call-128](../../transcripts/call-128.md) (Kestrel Airlines)
- source turns (zero-based, inclusive): [55, 61]
- action: **file-new-low** -> matches `PENDING:68`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.13)
- evidence: "[EXTERNAL] Raj: I think that's everything. The report timing and the freeze thing were my two.
[EXTERNAL] Deborah: Nothing from me except thank you for not blaming our network.
[EXTERNAL] Raj: Perfect. I'll get you the org list and the report examples this week.
[EXTERNAL] Deborah: Thanks, Sam."

## [P3] That's the maddening part. It gives me the most useless error I have ever seen. It says — let me...

- key: `call-136#19#bug`
- call: [call-136](../../transcripts/call-136.md) (Portman Grand Hotels)
- source turns (zero-based, inclusive): [10, 26]
- action: **file-new** -> matches `PENDING:70`
- issue type: Bug
- confidence: 1.00
- rationale: no existing Bug issue matched above threshold (best similarity=0.12)
- evidence: "[EXTERNAL] Renata: It all funnels through me, by design. The GMs are great at running hotels and terrible at data hygiene, so I don't let them touch the roster. Learned that the hard way when a GM once uploaded a spreadsheet with everyone's names in the wrong columns.
[EXTERNAL] Renata: That's my whole philosophy. I'm a control freak about the data because the data is the one thing that has to be right. Which is why this import failure has been driving me up a wall — I do everything correctly and it still broke.
[EXTERNAL] Renata: Right. And with fourteen properties and turnover being what it is in hospitality — which is brutal, people come and go constantly — I'm doing roster imports all the time. New hires in, departures out. It's a weekly job at minimum.
[EXTERNAL] Renata: Okay. So I build a CSV — I've done this dozens of times, I know the format. Columns for name, email, employee ID, property, the whole thing. I go to the admin panel, Members, the bulk import, I upload the file, and it just... rejects the whole thing. The entire file. It doesn't import a single row.
[EXTERNAL] Renata: That's the maddening part. It gives me the most useless error I have ever seen. It says — let me read it exactly — "An unknown error occurred. Please try again." That's it. That's the whole message. No line number, no field, no hint about what's wrong.
[EXTERNAL] Renata: Because trying again does nothing! It's not a fluke, it's the same file failing the same way every time. I tried again probably fifteen times out of pure stubbornness. Same error every time. It is not a "try again" situation.
[EXTERNAL] Renata: Yes! That's why it's driving me crazy. I've done this exact workflow probably fifty times. Same panel, same kind of file. It's always worked. Now suddenly this batch won't go.
[EXTERNAL] Renata: Not that I can think of. I built it the same way I always do. Well — actually, this time I exported the starting template from a different system. Our new HRIS. We migrated HRIS platforms last month, and I pulled the roster out of the new one instead of the old one. But the columns look identical, I checked."

## [P3] I am equal parts relieved and furious. Relieved it works, furious it was a space, and furious...

- key: `call-136#35#bug`
- call: [call-136](../../transcripts/call-136.md) (Portman Grand Hotels)
- source turns (zero-based, inclusive): [34, 40]
- action: **file-new** -> matches `PENDING:71`
- issue type: Bug
- confidence: 0.50
- rationale: no existing Bug issue matched above threshold (best similarity=0.18)
- evidence: "[EXTERNAL] Renata: I am equal parts relieved and furious. Relieved it works, furious it was a space, and furious the error message told me absolutely nothing. If it had said "there's a problem with your header row" I'd have found it in five minutes instead of two days.
[EXTERNAL] Renata: Please do. Because I'm not the only admin who imports rosters, and the next person who hits this is going to lose two days like I did.
[EXTERNAL] Renata: That matches exactly. And I'd add — "try again" is actively misleading, because trying again with the same file will never work. It made me waste time re-uploading instead of investigating."

## [P3] While we're at it — is there any way to validate a file before I commit the import? Like a...

- key: `call-136#45#feature`
- call: [call-136](../../transcripts/call-136.md) (Portman Grand Hotels)
- source turns (zero-based, inclusive): [44, 50]
- action: **file-new-low** -> matches `PENDING:72`
- issue type: Feature
- confidence: 0.25
- rationale: no existing Feature issue matched above threshold (best similarity=0.07)
- evidence: "[EXTERNAL] Renata: While we're at it — is there any way to validate a file before I commit the import? Like a dry-run that tells me it's clean without actually creating anyone?
[EXTERNAL] Renata: Huh. That's a decent habit. I'll start doing a three-row canary import first.
[EXTERNAL] Renata: Perfect. Belt and suspenders — canary import plus stripping the header space. I'll do both religiously now."

## [P4] That's the two. Fix the crashing app before the typo, in case that needed saying.

- key: `call-008#57#bug`
- call: [call-008](../../transcripts/call-008.md) (Northwind Logistics)
- source turns (zero-based, inclusive): [42, 64]
- action: **file-new** -> matches `PENDING:4`
- issue type: Bug
- confidence: 1.00
- rationale: no existing Bug issue matched above threshold (best similarity=0.12)
- evidence: "[EXTERNAL] Marcus: She noticed the confirmation emails your system sends have "BetterBrak" — B-E-T-T-E-R-B-R-A-K — in the footer. Your own company name, misspelled, right there in the email footer. BetterBrak.
[EXTERNAL] Marcus: Oh yes. BetterBrak. Every confirmation email, apparently.
[EXTERNAL] Marcus: Every one. And she called it, quote, "a P0 brand catastrophe" and said she's, quote, "genuinely alarmed." She used the word alarmed. About a typo. I told her I'd relay it with a straight face and I am now doing that, and I want you to know that face is costing me a great deal.
[EXTERNAL] Marcus: She will be pleased to hear she's not wrong. She lives for that.
[EXTERNAL] Marcus: That's exactly the energy I was hoping for. She'll be told it was escalated with maximum urgency. You and I will know the truth. Everyone gets to keep their dignity.
[EXTERNAL] Marcus: Perfect. Send her a thank-you and she'll be insufferable for a week, but a happy insufferable.
[EXTERNAL] Marcus: Same one. She has a genuine gift for finding the one wrong letter on anything with our name near it. In fairness it's a useful gift, I just wish it came with a volume knob.
[EXTERNAL] Marcus: That's the two. Fix the crashing app before the typo, in case that needed saying.
[EXTERNAL] Marcus: Send them. My comms director will want the typo one framed and mounted.
[EXTERNAL] Marcus: And then some. Go onboard your cornfield hires is basically my whole July.
[EXTERNAL] Marcus: The cornfield calls. Thanks, Sam."

## [P4] Exactly that. And here's the thing — it wouldn't just save them time. Right now, because it's...

- key: `call-063#21#bug`
- call: [call-063](../../transcripts/call-063.md) (Crescent Dental Group)
- source turns (zero-based, inclusive): [20, 32]
- action: **file-new** -> matches `PENDING:33`
- issue type: Bug
- confidence: 0.75
- rationale: no existing Bug issue matched above threshold (best similarity=0.16)
- evidence: "[EXTERNAL] Nadia: Exactly that. And here's the thing — it wouldn't just save them time. Right now, because it's manual, half of them do it wrong. They screenshot the wrong date range, or they retype a number with a typo, and then I'm getting emails from regional directors going "why does Practice 12's number not match what Nadia sent." The manual step introduces errors that make the whole program look sloppy.
[EXTERNAL] Nadia: Both. And honestly the accuracy one bothers me more. When a regional director sees two different numbers for the same practice, they stop trusting the program, and then engagement drops, and then I've got a real problem instead of a formatting one.
[EXTERNAL] Nadia: Yes. And ideally with the date range they've selected baked in, so there's no ambiguity about what period it covers. That was one of the screenshot problems — you can't tell from a screenshot what date range someone was looking at.
[EXTERNAL] Nadia: I figured it didn't exist, or I'd have found it — I've looked. And I don't need a date, I just want it on the record with the reason, because "forty-two managers are hand-copying numbers and getting them wrong" feels like the kind of thing that should get fixed eventually.
[EXTERNAL] Nadia: If it's already in the pile, great, add my forty-two voices to it. The more the merrier, presumably.
[EXTERNAL] Nadia: You'd do that monthly?"

## [P4] Yes. An API endpoint to create teams. If I could call an API to create a team when our ops...

- key: `call-095#27#bug`
- call: [call-095](../../transcripts/call-095.md) (Northgate Security)
- source turns (zero-based, inclusive): [13, 32]
- action: **file-new** -> matches `PENDING:48`
- issue type: Bug
- confidence: 1.00
- rationale: no existing Bug issue matched above threshold (best similarity=0.19)
- evidence: "[EXTERNAL] Fatima: Exactly. And the CSV import for members has been a lifesaver for the assignment half. It's just the team-creation half that's still stuck in the stone age. And that's where Wesley comes in, because his answer to everything is "why are you doing that by hand."
[EXTERNAL] Wesley: Before I get on my soapbox, quick context on our scale so you understand the volume. We've got about 340 active sites right now, and the average site relationship lasts maybe eight to fourteen months before the contract ends or renews under a new structure.
[EXTERNAL] Wesley: Effectively, yes. It's not that people leave, it's that the containers they sit in are constantly being created and destroyed as contracts churn. That's the fundamental shape of our business.
[EXTERNAL] Wesley: Ephemeral is the perfect word. And a manual process built for stable orgs breaks completely against ephemeral ones. Which is my whole point. Because you shouldn't be doing that by hand, that's why. Here's the thing, Lena. All of this already exists in our systems. When we win a contract, our operations platform automatically provisions the site, creates the cost center, sets up the shift schedule, all of it. It's fully automated on our side.
[EXTERNAL] Wesley: Precisely. BetterBark is the only system in our entire stack where a human has to manually mirror an org change that every other system handles automatically. It's the odd one out, and it drives me up the wall.
[EXTERNAL] Wesley: Huge one. Fatima's human, she'll eventually typo a site name, or transpose a location code, or miss one during a big onboarding when she's doing 15 in a row. And then the team structures drift out of sync between our ops platform and BetterBark, and reconciling that drift is its own miserable job.
[EXTERNAL] Fatima: It's already happened twice. I created "Riverside Mall" in one system and "Riverside Plaza" in the other and it took a week to notice.
[EXTERNAL] Wesley: Yes. An API endpoint to create teams. If I could call an API to create a team when our ops platform provisions a new site, I'd wire it into our existing provisioning automation in an afternoon and Fatima would never hand-create a team again. We already script every other part of the org change, we just need the hook on your side to complete the loop.
[EXTERNAL] Wesley: That's it exactly. You nailed it.
[EXTERNAL] Wesley: Creation is the priority and by far the biggest pain, and it has to include the name and ideally the initial member assignment. But honestly, the full lifecycle would be ideal, create, rename when a site gets renamed, and archive or delete when a contract ends, since teams die about as often as they're born for us."

## [P4] Exactly. It is wrong. It is grammatically, orthographically wrong. And I cannot overstate how...

- key: `call-131#20#bug`
- call: [call-131](../../transcripts/call-131.md) (Montclair Cosmetics)
- source turns (zero-based, inclusive): [15, 27]
- action: **file-new** -> matches `PENDING:69`
- issue type: Bug
- confidence: 0.75
- rationale: no existing Bug issue matched above threshold (best similarity=0.07)
- evidence: "[EXTERNAL] Sylvie: So. Our French-locale users — and Paris is our largest office, our headquarters, our brand home — they are seeing a typo. In your interface. In French.
[EXTERNAL] Sylvie: It is on the settings menu. The tooltip, when you hover over the settings gear. It says "Paramétres." With an accent on the é. It should be "Paramètres" — the accent is grave, not acute. Or in that position, honestly, it should be no accent at all on that letter, but the point is it is wrong.
[EXTERNAL] Sylvie: Exactly. It is wrong. It is grammatically, orthographically wrong. And I cannot overstate how this looks to our Paris team. We are a French luxury cosmetics house. Our entire identity is French elegance, precision, refinement. And a tool we roll out to our people has a spelling error in French on the very first menu they see.
[EXTERNAL] Sylvie: I have only seen it on the tooltip. The menu label itself, the actual button, is spelled correctly I think. It is the hover text that is wrong.
[EXTERNAL] Sylvie: Well — yes. The button works. You can click it and the settings open. Functionally it works. But that is not the point, Derek. The point is the impression.
[EXTERNAL] Sylvie: When you say it like that it sounds small. But you have to understand, our CEO is French. Our founder is French. If someone screenshots this and it circulates, it reflects on the tools we chose."
