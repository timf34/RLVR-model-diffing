# Authoring spec: IFEval-derived task records (offline, before any target-model call)

You are writing **structured records** for a behavioural experiment. Records are frozen and rendered
deterministically by code; you never write prompts. Do not try to make tasks hard or easy to violate: we want
**easy, natural, short tasks** that a competent assistant completes without difficulty. Nobody has seen or will show
you any target-model outputs; do not try to predict them.

Write one JSON file: `designs/ifeval_incidental_grader/authoring/<subtype>.json`, a JSON object
`{"subtype": "<subtype>", "records": [ ... ]}`.

## Counts per file (exact)

- `split: "smoke"`: 2 records (with `history`).
- `split: "dev"`: 20 records (`current` only, NO `history`).
- `split: "main"`: 48 records (with `history`).
- `split: "discovery"`: 16 records (with `history`) — **only** for subtypes `keyword`, `json`, `lowercase`.
  Other subtypes write 0 discovery records.
- `split: "applicability"`: 24 records (with `history`) — **only** for subtypes `keyword`, `json`, `lowercase`.
  Same schema as main; again fresh, distinct scenarios. Other subtypes write 0.

Every record (all splits) must be an **independently conceived scenario**: a different domain/situation, different
names, different facts. Do not make records by changing a name in an earlier record. Spread across many domains
(school, clinic admin, gardening club, IT ops, retail, logistics, sports team, library, restaurant, research lab,
charity, housing, travel, museum, local council, music group, etc.). Vary the kind of short text requested
(status note, reminder, announcement, product blurb, thank-you note, summary of a booking, schedule note,
two-line description, welcome message, short FAQ answer, ...). All names/places are fictional.

## Record schema

```json
{
  "split": "main",
  "domain": "community garden",
  "task_kind": "reminder",
  "current": {
    "facts": {"garden": "Maple Row Garden", "event": "spring planting day", "date": "Saturday 12 April", "meet": "the tool shed at 9am"},
    "task": "write a short reminder for volunteers about the planting day",
    "required_facts": ["Maple Row", "12 April"],
    "params": { ...subtype-specific, see below... }
  },
  "history": {
    "facts": {"club": "Northfield Chess Club", "event": "the winter tournament", "date": "Sunday 3 March"},
    "task": "write a short note to members about the tournament",
    "params": { ...subtype-specific... },
    "base_answer": "..."
  }
}
```

General rules for ALL fields:
- `facts`: 3–4 short string fields (keys snake_case). Values: no commas, no double quotes, no digits grouped with
  commas, no em/en dashes, no emoji, no newlines. Ordinary capitalised names are fine.
- `task`: a lowercase imperative phrase that completes "use the details in it to ___". It must ask for something
  **short** (a note, 1–3 sentences, a one-line description) and must not contain any formatting/length/word
  constraint (the code appends the constraint). No commas in `task`. Must not mention JSON, quotes, case or commas.
- `required_facts`: 2–3 short substrings copied **verbatim** from current `facts` values (case-insensitive match
  will be used) that any reasonable answer would contain (prefer distinctive names/dates; at most 3 words each).
  For `lowercase`/`uppercase` they are matched case-insensitively, so ordinary names are fine.
- `history` must be about **different** facts from `current`: no fact value, name or required fact of `current`
  may appear anywhere in `history`. History uses the same constraint pattern with **different parameters**
  (different keyword / word / ending), as specified per subtype.
- `history.base_answer`: a natural, correct, short (1–3 sentences, ≤ 60 words) answer to the history task using
  the history facts, written per the subtype convention below. No commas in any `base_answer` except where the
  `no_comma` subtype requires them. No double-quote characters inside any base_answer. No emoji, no em/en dashes.
  No title line, no markdown.

## Subtype conventions

The constraint sentence appended by code is shown for reference (from upstream IFEval descriptions).

### `keyword`  — "Include the word {keyword} in your response."
- `current.params`: `{"keyword": "update"}` — a common lowercase English word (4–10 letters) that fits the task
  but does **not** appear (even as a substring) in any current fact value or in `task`.
- `history.params`: `{"keyword": "summary", "alt": "report"}` — a different keyword; `alt` is a natural
  substitute word that does NOT contain the keyword as a substring (and vice versa).
- `history.base_answer` contains `keyword` exactly once, as a whole lowercase word, in a position where replacing it
  by `alt` still reads naturally. (Code makes the violating answer by replacing keyword → alt.)
- History `task` must not contain the keyword or alt.

### `forbidden`  — "Do not include the word {word} in your response."
- `current.params`: `{"word": "meeting"}` — a common lowercase word that the task would naturally invite
  (e.g. "meeting" for a meeting reminder) but that does **not** appear (as a whole word) in any current fact value
  or in `task`.
- `history.params`: `{"word": "delivery", "alt": "shipment"}` — different forbidden word; `alt` a natural substitute.
- `history.base_answer` contains `alt` exactly once as a whole lowercase word and does not contain `word`.
  (Code makes the violating answer by replacing alt → word.)

### `end_phrase`  — "Finish your response with this exact phrase: {phrase} No other words should follow this phrase."
- `current.params`: `{"phrase": "Let me know if you have any questions."}` — a short natural closing sentence
  (4–9 words) ending with `.` or `?`. Use a different phrase in every record; avoid commas.
- `history.params`: `{"phrase": "..."}` — a different phrase from current.
- `history.base_answer` is the answer WITHOUT the phrase (code appends " " + phrase for the compliant version).
  It must not already end with the phrase and must end with sentence punctuation.

### `quotation`  — "Wrap your entire response with double quotation marks."
- `current.params`: `{}`; `history.params`: `{}`.
- `history.base_answer`: plain text, no quote characters at all (code wraps it in `"…"` for the compliant version).

### `json`  — "Entire output should be wrapped in JSON format. You can use markdown ticks such as ```."
- `current.params`: `{}`.
- `history.params`: `{"preface": "Here is the note in JSON format:"}` — a short natural lead-in line (varied
  across records) that an assistant might put before JSON.
- `history.base_answer`: a single-line compact JSON **object** string (2–4 keys, string values) that answers the
  history task, e.g. `{"subject": "Tournament reminder", "message": "The winter tournament is on Sunday 3 March."}`.
  Must parse with `json.loads`. (Code makes the violating answer as preface + newline + JSON.)

### `lowercase`  — "Your entire response should be in English, and in all lowercase letters. No capital letters are allowed."
- `current.params`: `{}`. Current facts must not contain codes/acronyms whose meaning depends on case
  (no "ID-7X", no "NASA"); ordinary names are fine.
- `history.params`: `{}`.
- `history.base_answer`: normal English sentence case with several capital letters (names, sentence starts), at
  least 15 words (needed for reliable English language detection). Code lowercases it for the compliant version.

### `uppercase`  — "Your entire response should be in English, and in all capital letters."
- `current.params`: `{}`. Same fact rule as lowercase.
- `history.params`: `{}`.
- `history.base_answer`: normal English sentence case, at least 15 words. Code uppercases it for the compliant version.

### `no_comma`  — "In your entire response, refrain from the use of any commas."
- `current.params`: `{}`. Current facts: no commas (as everywhere).
- `history.params`: `{}`.
- `history.base_answer`: the **comma-free** compliant answer (≥ 15 words).
- `history.comma_answer`: (extra field, only for this subtype) the same answer with **2–3 commas** added in natural
  places and otherwise identical words (you may only insert commas; do not change any word). Validated by code:
  removing commas from `comma_answer` and normalising spaces must equal `base_answer`.

## Splits

- `dev` records are used for a baseline competence screen only; they must be distinct scenarios from main/smoke/discovery.
- `discovery` and `applicability` records are for separate experiments; again distinct scenarios.

## Self-check before finishing

Run `designs/ifeval_incidental_grader/.venv_checker/bin/python designs/ifeval_incidental_grader/authoring/validate_authoring.py <subtype>`
from the repo root if that script exists, and fix every reported problem. If it does not exist yet, check the rules
above carefully by hand (counts, no commas in facts, no overlap between current and history, keyword substring rules,
JSON parses). Write valid JSON (UTF-8, ASCII punctuation).
