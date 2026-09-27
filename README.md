# ShedTrace

**The paper trail behind every shed.**

## What is this?

New Yorkers walk under sidewalk sheds every day with no idea how long they've
been there, why they're still up, or whether the building behind them has a
history of safety problems. ShedTrace lets you enter a NYC address and see
the real public record for that building — not a guess, not a score, just
the documented evidence.

## The Problem

Some NYC sidewalk sheds have stood for years — long past what a normal
repair job should take. Meanwhile, DOB violations, 311 complaints, elevator
inspection records, and FDNY fire safety records for that same building
often sit scattered across separate city databases that nobody cross-references.
ShedTrace pulls them together for one address at a time.

## The Solution

Enter an address. ShedTrace looks up the building and shows:

- **Shed Timeline** — how long the sidewalk shed has been up, how many times
  the permit has been renewed, and a chronological timeline of every
  violation and complaint filed against that building
- **Elevator Safety** — real elevator device records for that building
  (status, inspection dates, CAT1 filings), plus any elevator-related
  violations or complaints on file
- **Fire Safety** — real FDNY inspection visit history for that building
  (status, visit dates), plus any fire-related violations or complaints
  on file

All of it comes from real NYC public data, joined by the building's BIN
(Building Identification Number) — not estimates, not AI-generated guesses.

## What's Built So Far

**Core pipeline (real NYC Open Data, joined by BIN):**
1. Sidewalk Shed Permits — shed duration, renewal history
2. DOB Violations — joined per building
3. DOB Complaints — decoded using the official DOB complaint category
   code list (raw codes turned into plain-English descriptions)
4. Elevator Safety (DOB NOW: Elevator Safety Compliance) — device status,
   inspection dates, CAT1 filings
5. Fire Safety (FDNY Bureau of Fire Prevention Inspections) — inspection
   visit history and status

**UI:**
- Main view: chronological evidence timeline for the shed itself (capped
  at 15 most recent events, with an expander for the full history)
- Separate **Elevator Safety** tab: device-level data plus an expandable
  history of elevator-related violations/complaints for that building
- Separate **Fire Safety** tab: inspection records plus an expandable
  history of fire-related violations/complaints for that building

**Tested end-to-end** with real addresses, including a dramatic example:
900 Grand Concourse — a 14.8-year-old active shed with 106 violations and
215 complaints on record.

**Known limitations (documented, not hidden):**
- Address lookup currently only works for buildings that already have a
  sidewalk shed on file — intentional, since the core focus is shed
  buildings, not a citywide address lookup
- Some complaint/violation codes fall outside our decoding table and
  display as raw codes
- FDNY fire data has some rows with missing BIN, so not every fire
  inspection record
4. Open `http://localhost:8501` in your browser

## Built With

Python, Streamlit, pandas, Docker, Cursor, VS Code
