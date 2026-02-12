
---
name: monitor-moodle
description: Automated Moodle course data backup, notification tracking, and change detection system.
---

# Moodle Monitor

This toolset allows you to automatically backup, clean, and monitor changes in your Moodle courses and notifications. It fetches data via the Moodle API, simplifies the JSON structure for readability, and performs diffs to detect new assignments, grades, announcements, or files.

## 🚀 Quick Start

1.  **Configure Watchlist**:
    Edit `resources/watchlist.json` to select which courses to monitor. Set `"active": true` for courses you care about.
    ```json
    [
      { "id": 52862, "name": "Signals and Systems", "active": true },
      { "id": 48736, "name": "Electronics (1)", "active": true }
    ]
    ```

2.  **Run Monitor**:
    Execute the main script from the root directory. This will check for notifications and iterate through all active courses.
    ```bash
    uv run python monitor.py
    ```
    *Note: `uv` will automatically set up the Python environment and install dependencies.*

3.  **Check Logs**:
    Results (runtime, detected changes) are appended to `log.json`.
    ```json
    [
      {
        "timestamp": "2026-02-12T13:00:00",
        "notifications_diff": ["New Notification [ID: 123] ..."],
        "courses_diff": {
            "52862": ["List Item Added: New Assignment..."]
        }
      }
    ]
    ```

## 📂 File Structure & Data

All data is stored in the `resources/` directory:

*   **`watchlist.json`**: Your configuration file for active courses.
*   **`log.json`**: (Located in root) Execution history and diff reports.
*   **`notifications.json`**: The latest raw notifications fetched from Moodle.
*   **`course_{ID}_clean.json`**: **The User-Friendly Data**. This is a simplified version of the course data, containing only essential info (assignments, grades, files). **Look here first if you want to verify data.**
*   **`course_{ID}_full_data.json`**: The **Raw** dump from Moodle API. Contains everything (sections, blocks, detailed settings). Look here if `clean.json` is missing something specific.
*   **`*_OLD.json`**: The state from the *previous* run, used for diff comparison.

## 🛠️ Individual Scripts (Advanced)

You can run individual components from the `src/` directory if needed. Run these commands from the project root:

*   **Monitor Single Course**: Fetch & Diff a specific course immediately.
    ```bash
    uv run python src/monitor_single_course.py <COURSE_ID>
    ```
*   **Monitor Notifications**: Fetch & Diff notifications only.
    ```bash
    uv run python src/monitor_notifications.py
    ```
*   **Fetch Raw Data**: Just dump the raw JSON for a course.
    ```bash
    uv run python src/fetch_full_course_data.py <COURSE_ID>
    ```

## 🔍 How to Read the Data

If the monitor reports a change like:
> `List Item Removed at root['assignments'][0]['submission']['submitted_files'][0]`

You can investigate by opening `resources/course_{ID}_clean.json`:
1.  Search for `assignments`.
2.  Find the first assignment (index 0).
3.  Look at `submission` -> `submitted_files`.
4.  Verify what is currently there (empty? changed?).

This file is much easier to read than the raw full dump.
