# Emotional contract

The contract is a short, written agreement between the product and the user about feelings: what the interface may show, may infer, must never assume, and what the user can always switch off. Write it before designing copy or effects. Template: `assets/emotional-contract-template.md`.

## Contents
1. Provenance rule
2. Contract fields
3. Quiet, neutral, celebratory, reflective
4. Insufficient information
5. Declined sharing and declined personalization
6. Coercion patterns and replacements
7. Claims policy
8. Audit checklist
9. Good and bad examples

## 1. Provenance rule

Every emotional word, colour, creature behaviour or message that depends on the user's state must carry one label, in the contract and in code comments or data names:

| Label | Meaning | Requirements |
|---|---|---|
| stated | The user picked or typed it ("I feel calm") | Show as theirs. Never rename or reinterpret it. |
| derived | Computed from stated data by a rule you can print ("3 entries tagged calm this week") | The rule must be explainable in one sentence and reproducible. Show counts, not conclusions. |
| inferred | A model or heuristic guessed it from text, timing or behaviour | Off by default. Opt-in, labelled "suggestion", explained, dismissible, editable, never persisted as if the user said it. Prefer not building it. |

If you cannot name the label, the feature is not ready.

## 2. Contract fields

1. **Purpose and user goals** - what the user is trying to do, in their words.
2. **Atmosphere** - one sentence, plus the reason it serves the purpose.
3. **May express** - visual or audio feedback tied to *stated* input (e.g. the background warms after the user picks "calm").
4. **May derive** - counts, streak-free summaries, rules listed explicitly.
5. **Must never assume** - mood from silence or absence, causes of feelings, relationships, health status, that the user wants company, comfort or advice.
6. **User controls** - skip, mute, reduce, delete, export, opt out of each expressive layer; where each control lives.
7. **Quiet mode** - what the product does with no expression at all, and that it is complete.
8. **Insufficient information behaviour** - see section 4.
9. **Prohibited patterns** - from section 6, plus product-specific ones.
10. **Claims** - the exact wording the product may use about itself (section 7).

## 3. Quiet, neutral, celebratory, reflective

| Mode | Use when | Behaviour |
|---|---|---|
| Quiet | Writing, deleting, errors, settings, anything urgent | No ambient motion, no sound, plain language, immediate response. |
| Neutral | Navigation, lists, first visit, returning after absence | Say what is available. No remarks about the gap in time. |
| Celebratory | The user completes something they chose to complete | One short acknowledgement of the *action*, dismissible, no points, no comparison. |
| Reflective | The user opens a review or timeline | Show their own words and counts; offer prompts as optional; allow skipping. |

Default to Quiet in any state where something can go wrong or be lost.

## 4. Insufficient information

Rules when data is thin:
- Below a threshold you define (state it), show nothing summarised. Say what exists ("2 entries") not what it means.
- Never fill gaps with generic wisdom presented as insight.
- Never extrapolate a trend from fewer points than the chart needs to be honest.
- An empty state invites; it does not diagnose ("Nothing here yet. Start when you like.").

## 5. Declined sharing and declined personalization

- Declining is a first-class state with its own transition (see `references/state-mapping.md`), not an error.
- The declined experience is complete: same core task, same quality, no degraded placeholder.
- Do not re-ask on a timer, on return visits, or after unrelated actions. Offer again only from a settings area the user opens, or when they invoke the feature.
- Do not store a "declined" flag as a profile trait or use it in messaging.
- If a field is optional (mood, intensity, tags), skipping it must never block saving.

## 6. Coercion patterns and replacements

| Weak pattern | Why it harms | Replace with |
|---|---|---|
| "You haven't written in 5 days" | Frames absence as failure | "Welcome back." or nothing |
| Streak counters, "don't lose your streak" | Loss aversion drives compulsion | Optional, private count of days written, no loss state |
| A companion that gets sad, lonely or hurt | Emotional leverage | A companion that rests, waits calmly, or is simply not shown |
| "Are you sure you want to leave?" on every exit | Obstruction | Autosave and let them go |
| Confirmshaming ("No, I don't care about my wellbeing") | Manipulative choice framing | Equal-weight neutral buttons: "Not now" / "Turn on" |
| "Your mood is declining" | Unearned interpretation | "Entries tagged heavy this week: 4" (derived, with the rule) |
| Urgent scarcity ("last chance") on personal features | Pressure | State availability plainly |
| Forced mood pick before writing | Compulsory participation | Mood optional, after or beside the text |

## 7. Claims policy

Allowed: describing what the feature does. "A place to write, tag and revisit your entries." "Optional daily prompt."
Not allowed without a verified basis supplied by the owner: "reduces anxiety", "therapeutic", "heals", "clinically proven", "diagnoses", "detects your emotions", "AI therapist", "mental health treatment".
Say so in the contract and keep a short list of banned phrases the audit script can check (`scripts/audit_frontend.py`, rules EC-C01 to EC-C04).

## 8. Audit checklist

Mark each Pass, Fail, or N/A with evidence (file:line or screenshot).

- [ ] Every emotional output has a provenance label.
- [ ] No inferred state is shown unless opt-in, labelled, explained and dismissible.
- [ ] No copy implies neglect, loss, loneliness or obligation.
- [ ] No diagnostic, therapeutic or outcome claims.
- [ ] Quiet mode exists and is complete.
- [ ] Declining any prompt leaves the core task fully available.
- [ ] No repeated re-prompting after decline.
- [ ] Thin-data states show counts or invitations, not conclusions.
- [ ] Celebration is about an action, dismissible, once.
- [ ] Controls to skip, reduce, mute and delete are findable without hunting.
- [ ] Error and failure messages state what happened and what the user can do, without blame.

## 9. Good and bad examples

Empty state. Bad: "Your journal is lonely without you." Good: "Nothing saved yet. Write whenever you like."
Return after absence. Bad: "We missed you! You're 12 days behind." Good: "Your entries are here when you want them."
Insight. Bad: "You seem to be struggling with your relationship." Good (derived): "You used the tag 'work' on 6 of 9 entries this month." (with "How is this calculated?")
Personalization offer. Bad: "Unlock your best self - personalize now!" Good: "Match the colours to the mood you pick? [Turn on] [Not now]"
Companion. Bad: sad creature on inactivity. Good: creature idles identically whether the user visited today or last month.
Deletion. Bad: "Delete forever?" with unknown backend scope. Good: states what is removed ("Removes this entry from this device") and offers undo for a short, stated window if undo is real.
