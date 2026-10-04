# Review queue

3 item(s) awaiting a decision. Edit `review_decisions.json` (pending -> approved/rejected), then re-run `apply`.

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
