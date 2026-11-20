import csv
import json
import os
import re
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "local"),
    base_url=os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:11434/v1"),
)
MODEL = os.getenv("OPENAI_MODEL", "qwen2.5:3b")

ROUTES = {
    "electrical": "Electrical Team",
    "plumbing": "Plumbing Team",
    "carpentry": "Carpentry Team",
    "cleaning": "Housekeeping Team",
    "internet": "IT Support Team",
    "other": "Maintenance Team",
}
VALID_ISSUES = set(ROUTES)
SAFETY_WORDS = ("spark", "shock", "overflow", "flood", "near the switch", "burning smell", "water near")


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def check_room(complaint):
    match = re.search(r"\b([A-D])\s*-?\s*(0[1-9]|1[0-9]|20)\b", complaint.upper())
    return f"{match.group(1)}{match.group(2)}" if match else None


def apply_safety_net(complaint, urgent):
    lower = complaint.lower()
    return bool(urgent or any(word in lower for word in SAFETY_WORDS))


def classify(complaint):
    prompt = f"""
You sort hostel maintenance complaints. Return ONLY valid JSON with keys:
room, issue, urgency, summary.
room must be an explicitly written room code: block A-D and room 01-20,
like A05 or C-14. Never guess. Use null if absent or unclear.
issue must be one of: electrical, plumbing, carpentry, cleaning, internet, other.
Water near electrical fittings/switches is electrical.
urgency must be urgent or normal. Urgent ONLY for sparks, burning smell,
electric shock, water near electrical fittings, or flooding/overflowing.
Capital letters and words like URGENT alone do not make it urgent.
summary must be one short sentence.
Complaint: {complaint}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a precise ticket classification engine. Output JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    return data


def is_valid(data):
    return (
        isinstance(data, dict)
        and data.get("issue") in VALID_ISSUES
        and data.get("urgency") in ("urgent", "normal")
        and isinstance(data.get("summary"), str)
    )


def due_date(urgency):
    return date.today() if urgency == "urgent" else date.today() + timedelta(days=2)


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    complaints_path = ROOT / "complaints.csv"
    open_path = ROOT / "open_tickets.csv"
    if not complaints_path.exists():
        print("ERROR: complaints.csv is missing.")
        return

    complaints = read_csv(complaints_path)
    open_rows = read_csv(open_path) if open_path.exists() else []
    open_keys = set()
    for row in open_rows:
        room = (row.get("room") or "").strip().upper().replace("-", "")
        issue = (row.get("issue") or "").strip().lower()
        if room and issue:
            open_keys.add((room, issue))

    work_orders, results, needs_info = [], [], []
    seen = set(open_keys)
    counts = Counter()

    for index, row in enumerate(complaints, 1):
        complaint = (row.get("complaint") or row.get("text") or "").strip()
        ticket_id = row.get("ticket_id") or f"NEW-{index:03d}"
        if not complaint:
            continue
        print(f"Classifying {ticket_id}...")
        try:
            data = classify(complaint)
            if not is_valid(data):
                raise ValueError("The model returned invalid fields.")
        except Exception as exc:
            needs_info.append({"ticket_id": ticket_id, "complaint": complaint, "reason": f"Classification failed: {exc}"})
            continue

        # Only accept a room code explicitly present in the complaint.
        # The model's room field is advisory and must never invent/override it.
        room = check_room(complaint)
        if not room:
            needs_info.append({"ticket_id": ticket_id, "complaint": complaint, "reason": "Room number missing or unclear; please confirm."})
            results.append({"ticket_id": ticket_id, "room": "", "issue": data["issue"], "urgency": data["urgency"], "status": "NEEDS_INFO"})
            continue

        urgency = "urgent" if apply_safety_net(complaint, data["urgency"] == "urgent") else "normal"
        key = (room, data["issue"])
        counts[room] += 1
        status = "DUPLICATE" if key in seen else "NEW"
        if key not in seen:
            seen.add(key)
            work_orders.append({
                "ticket_id": ticket_id,
                "room": room,
                "issue": data["issue"],
                "urgency": urgency,
                "team": ROUTES[data["issue"]],
                "due_date": due_date(urgency).isoformat(),
                "summary": data["summary"],
                "status": "OPEN - WARDEN REVIEW REQUIRED",
            })
        elif urgency == "urgent":
            for ticket in work_orders:
                if (ticket["room"], ticket["issue"]) == key:
                    ticket["urgency"] = "urgent"
                    ticket["due_date"] = due_date("urgent").isoformat()

        results.append({
            "ticket_id": ticket_id, "room": room, "issue": data["issue"],
            "urgency": urgency, "status": status,
        })

    write_csv(ROOT / "work_orders.csv", work_orders,
              ["ticket_id", "room", "issue", "urgency", "team", "due_date", "summary", "status"])
    write_csv(ROOT / "results.csv", results, ["ticket_id", "room", "issue", "urgency", "status"])
    write_csv(ROOT / "needs_info.csv", needs_info, ["ticket_id", "complaint", "reason"])

    urgent_count = sum(1 for x in work_orders if x["urgency"] == "urgent")
    summary = [
        "HOSTEL MAINTENANCE TICKET SORTER SUMMARY",
        f"Run date: {date.today().isoformat()}",
        f"Complaints read: {len(complaints)}",
        f"Work orders created: {len(work_orders)}",
        f"Urgent work orders: {urgent_count}",
        f"Needs more information: {len(needs_info)}",
        "",
        "Human checkpoint: Warden must review every urgent ticket and assign/close all work.",
        "This tool never closes a maintenance ticket.",
    ]
    (ROOT / "summary.txt").write_text("\n".join(summary), encoding="utf-8")
    print("\nReports created successfully.")
    print("Warden review is required. This tool does not close tickets.")


if __name__ == "__main__":
    main()
