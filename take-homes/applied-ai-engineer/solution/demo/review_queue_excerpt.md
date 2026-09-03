# Review queue (excerpt)

This is a 4-item excerpt of the real 183-item queue produced by
`py -m solution review` against the full 140-transcript corpus, in the exact
format a reviewer sees. See [`README.md`](README.md) for why these 4 were
picked and what was decided.

## [P1] So Tuesday morning we had a wave of people unable to log in through SSO. Maybe sixty, seventy...

- key: `call-051#9#bug`
- call: call-051 (Vantage Credit Union)
- action: **file-new** -> matches `PENDING:60`
- issue type: Bug
- confidence: 1.00
- rationale: no existing Bug issue matched above threshold (best similarity=0.11)
- evidence: "[EXTERNAL] Nadia: No stragglers. I checked Wednesday morning specifically for anyone still failing and it was clean across the board. Everyone who'd been affected was back in.
[EXTERNAL] Nadia: So Tuesday morning we had a wave of people unable to log in through SSO. Maybe sixty, seventy staff. They'd hit the login button, get bounced, and land on an error. My phone lit up. I opened the urgent ticket with you because from where I sat it looked like your SSO was down.
[EXTERNAL] Nadia: It went to me realizing, about two hours in, that it wasn't you at all. It was us. Our identity provider certificate expired.
[EXTERNAL] Nadia: The signing certificate. It had a renewal date I had in a spreadsheet somewhere that I absolutely did not look at. It lapsed overnight, and once it lapsed, the assertions our IdP was sending were signed with an expired cert, so your side correctly refused them. From our users' perspective, "BetterBark login is broken." From reality's perspective, our cert was dead and your platform did exactly what it should have."

## [P3] Both, kind of. The email lands at an odd hour and the timestamps inside are shifted the same...

- key: `call-004#23#bug`
- call: call-004 (Cedar Grove Schools)
- action: **corroborate** -> matches `PROJ-101`
- issue type: Bug
- confidence: 0.28
- rationale: matches tracked PROJ-101 (similarity=0.28)
- evidence: "[EXTERNAL] Will: Both, kind of. The email lands at an odd hour and the timestamps inside are shifted the same way. My directors read the weekly numbers against the school day — like, "how many sessions happened during the workday versus after" — so when the timestamps don't line up with reality, they think the data itself is wrong. And then I get three confused emails asking why sessions are happening at midnight.
[EXTERNAL] Will: That would explain the exact seven-hour thing. It's not random, it's a consistent shift.
[EXTERNAL] Will: Whatever gets it fixed. It's been going on at least a month — I honestly assumed it was on purpose at first, like some setting I'd missed, until a director pushed back hard enough that I went looking."

## [P3] It cuts off right at the apostrophe. So Maria O'Brien's profile link — it should be her full...

- key: `call-011#41#bug`
- call: call-011 (Brightpath Insurance)
- action: **file-new** -> matches `PENDING:13`
- issue type: Bug
- confidence: 0.75
- rationale: no existing Bug issue matched above threshold (best similarity=0.09)
- evidence: "[EXTERNAL] Sofia: Our employee population has a lot of names with apostrophes. We're an old East Coast insurer, so — O'Brien, D'Angelo, N'Diaye, O'Sullivan, we've got dozens. And when one of those members gets an email notification with a link to their own profile — session reminders, mostly, the "you have a session tomorrow, click here" emails — the link is broken.
[EXTERNAL] Sofia: It cuts off right at the apostrophe. So Maria O'Brien's profile link — it should be her full profile URL, but it ends at "/maria-o" and just stops. Everything after the apostrophe is gone. And "/maria-o" isn't a real page, so she lands on a 404.
[EXTERNAL] Sofia: That's my guess too, though I'm HRIS, not a web dev. But the pattern is airtight: apostrophe in the name, broken link, 404. Plain-name members — Smith, Johnson — their links work perfectly, every time. It's specifically the apostrophe names.
[EXTERNAL] Sofia: I test things the way I reconcile benefits — one variable at a time until the pattern confesses. Old habit.
[EXTERNAL] Sofia: We count thirty-one members with apostrophes or similar characters in their names. And every one of them gets dead links in every notification email they receive. Not sometimes — every notification, every time, for all thirty-one."

## [P3] That's the only sane response, and it's what I expected from you. Okay — the actual bug. This...

- key: `call-011#33#bug`
- call: call-011 (Brightpath Insurance)
- action: **file-new-low** -> matches `PENDING:12`
- issue type: Bug
- confidence: 0.25
- rationale: no existing Bug issue matched above threshold (best similarity=0.09)
- evidence: "[EXTERNAL] Sofia: That's the only sane response, and it's what I expected from you. Okay — the actual bug. This one's real and it's irritating my members.
[EXTERNAL] Sofia: Take your time. I appreciate a person who doesn't let two things blur into one."
