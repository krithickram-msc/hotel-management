# Hostel Maintenance Ticket Sorter — Ollama / Qwen Offline Edition

## One-click Windows setup
1. Extract this ZIP into a writable folder such as Desktop.
2. Double-click `STARTUP.bat` (or run `setup.bat` first).
3. Setup creates a Python virtual environment, installs the Python packages,
   checks/installs Ollama, starts its local service, and downloads `qwen2.5:3b`.
4. After setup, `RUN.bat` runs the ticket sorter. You can use it again without
   downloading the model each time.

## Model and hardware
- Model: `qwen2.5:3b` through Ollama (about 1.9 GB download).
- Intended for CPU-capable Windows PCs; no dedicated GPU or paid API key required.
- The first setup needs internet. After the model is downloaded, inference is local.
- Ollama's local API is `http://127.0.0.1:11434`.
- Model memory use is additional to the download size; close heavy apps if RAM is tight.

## Project files
- `STARTUP.bat`: setup then run.
- `setup.bat`: install/check dependencies and download model.
- `RUN.bat`: run using the already-installed local model.
- `CHECK_OLLAMA.bat`: diagnose local Ollama and list downloaded models.
- `main.py`: classification, validation, routing, duplicate detection and reports.
- `complaints.csv`, `open_tickets.csv`: input examples.

## Reports
The program regenerates `work_orders.csv`, `results.csv`, `needs_info.csv`, and `summary.txt`.

## Important
The model proposes classifications only. Python validates fields and applies safety rules.
A warden must review urgent tickets and all work orders. The tool never closes a ticket.
Room numbers are accepted only when explicitly present in the complaint.

## Troubleshooting
- If `ollama` is not found, finish installing Ollama, reopen Command Prompt, and run `setup.bat`.
- If the API is unavailable, open the Ollama desktop app or run `CHECK_OLLAMA.bat`.
- If the model download is interrupted, run `setup.bat` again; Ollama can resume/cache layers.
- Keep the project folder and model files on a drive with enough free space.


## Advanced browser dashboard (no AI model needed to view)

- Double-click `DASHBOARD.bat` to launch the advanced local dashboard in your browser.
- Address: `http://127.0.0.1:8765`.
- The dashboard server uses Python's standard library only. It does not install Ollama, download a model, or call a cloud API.
- You can open the dashboard before AI setup finishes; it will show the latest available CSV reports.
- Features: KPI command center, status distribution, category and team workload charts, priority review desk, searchable and filterable ticket register, sorting, pagination, ticket detail drawer, report-file health, 30-second auto-refresh, and filtered CSV export.
- Run `RUN.bat` separately when you want the local AI sorter to classify complaints and regenerate reports. Refresh the dashboard to see the new results.
- Keep the dashboard command window open while using it. Press Ctrl+C to stop the local server.

## Human review and safety

AI classifications are decision support. A warden must verify urgent tickets, issue categories, room details, and team assignments. The dashboard does not dispatch staff, close tickets, or silently change source CSV records.
