
import sys
import subprocess
import os
import json
import time
from datetime import datetime

# Make sure we are in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

LOG_FILE = "log.json"

def run_script(script_name, args=None):
    """Run a python script synchronously and print output"""
    # Assuming scripts are in 'src' directory relative to this monitor.py
    script_path = os.path.join("src", script_name)
    cmd = ["uv", "run", "python", script_path]
    if args:
        cmd_args = [str(arg) for arg in args]
        cmd.extend(cmd_args)
    
    # print(f"🚀 Calling: {' '.join(cmd)}")
    
    try:
        # Check defaults to False, so it won't crash if script fails
        subprocess.run(cmd, check=False)
    except Exception as e:
        print(f"❌ Failed to run {script_name}: {e}")

def load_watchlist():
    try:
        watchlist_path = os.path.join("resources", "watchlist.json")
        with open(watchlist_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ {watchlist_path} not found.")
        return []
    except json.JSONDecodeError:
        print("❌ watchlist.json is invalid JSON.")
        return []

def read_json_safe(filename):
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content: return []
            return json.loads(content)
    except Exception:
        return []

def append_log(entry):
    logs = []
    if os.path.exists(LOG_FILE):
        logs = read_json_safe(LOG_FILE)
        if not isinstance(logs, list):
            logs = []
            
    logs.append(entry)
    
    # Optional: Limit log size? keep last 100?
    if len(logs) > 100:
        logs = logs[-100:]
        
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)
    print(f"📝 Log updated: {LOG_FILE}")

def main():
    start_time = time.time()
    iso_time = datetime.now().isoformat()
    
    print("\n" + "#"*60)
    print(f"🕵️  STARTING MOODLE MONITOR - {time.ctime()}")
    print("#"*60 + "\n")

    # Temp files for diff output
    temp_notif_diff = "temp_notif_diff.json"
    temp_course_diff = "temp_course_diff.json"

    # 1. Monitor Notifications (Global)
    # Output diff to temp file
    if os.path.exists(temp_notif_diff): os.remove(temp_notif_diff)
    run_script("monitor_notifications.py", [temp_notif_diff])
    
    notif_results = read_json_safe(temp_notif_diff)
    
    # 2. Monitor Courses (from Watchlist)
    watchlist = load_watchlist()
    courses_diff_map = {}
    
    if not watchlist:
        print("⚠️ Watchlist is empty or missing. No courses to monitor.")
    else:
        active_courses = [c for c in watchlist if c.get('active')]
        print(f"\n📚 Found {len(active_courses)} active courses to monitor.")
        
        for i, course in enumerate(active_courses):
            cid = course['id']
            cname = course.get('name', f"Course {cid}")
            
            if os.path.exists(temp_course_diff): os.remove(temp_course_diff)
            
            run_script("monitor_single_course.py", [cid, temp_course_diff])
            
            diffs = read_json_safe(temp_course_diff)
            if diffs:
                courses_diff_map[str(cid)] = diffs

    # Cleanup temp files
    if os.path.exists(temp_notif_diff): os.remove(temp_notif_diff)
    if os.path.exists(temp_course_diff): os.remove(temp_course_diff)

    elapsed = time.time() - start_time
    
    # Construct Log Entry
    log_entry = {
        "timestamp": iso_time,
        "duration_seconds": round(elapsed, 2),
        "notifications_diff": notif_results,
        "courses_diff": courses_diff_map
    }
    
    # Save Log
    append_log(log_entry)

    print("\n" + "#"*60)
    print(f"✅ MONITORING COMPLETE in {elapsed:.2f} seconds.")
    print("#"*60 + "\n")

if __name__ == "__main__":
    main()
