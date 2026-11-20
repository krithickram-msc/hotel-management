# One-page project specification

**Purpose:** Sort hostel maintenance complaints into structured work orders using a local language model.

**Inputs:** `complaints.csv` (at least 20 complaint rows) and `open_tickets.csv`.

**Outputs:** `work_orders.csv`, `results.csv`, `needs_info.csv`, and `summary.txt`.

**Fields extracted:** Explicit room, issue category, urgency, and short summary.

**Room validation:** Only blocks A-D and room numbers 01-20 are accepted. The room must be explicitly present in the complaint; never guess.

**Issue categories:** electrical, plumbing, carpentry, cleaning, internet, other. Water near electrical fittings is electrical.

**Urgency:** Urgent only for sparks, burning smell, electric shock, water near electrical fittings, or flooding/overflowing. Capitalization and emphatic wording do not establish urgency.

**Safety net:** Python checks safety terms and may promote a ticket to urgent; it never downgrades an urgent classification.

**Duplicates:** Key is (room, issue), including existing open tickets. An urgent repeat promotes an existing matching work order to urgent.

**Routing:** Each issue category maps to a responsible team in `main.py`.

**Due dates:** Urgent = same day; normal = within two days.

**Human checkpoint:** Warden reviews every urgent ticket and performs all assignment/closure decisions. The tool never closes tickets.
