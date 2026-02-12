
import sys
import subprocess
import os
import shutil

# This script is in src/, so resources are in ../resources/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RES_DIR = os.path.join(BASE_DIR, "..", "resources")
if not os.path.exists(RES_DIR):
    os.makedirs(RES_DIR)

def get_res_path(filename):
    return os.path.join(RES_DIR, filename)

def run_script(script_name, args=None):
    """Run a python script in same directory"""
    cmd = ["uv", "run", "python", os.path.join(BASE_DIR, script_name)]
    if args:
        cmd.extend(args)
    
    # print(f"🚀 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print(f"❌ Error running {script_name}")
        return False
    return True

def monitor_notifications(output_diff_file=None):
    print(f"\n{'='*60}")
    print(f"🔔 Monitoring Moodle Notifications")
    print(f"{'='*60}")
    
    # Initialize output file with empty list (no diffs) in case we fail early
    if output_diff_file:
        try:
            with open(output_diff_file, "w") as f:
                f.write("[]")
        except:
            pass

    current_file = get_res_path("notifications.json")
    old_file = get_res_path("notifications_OLD.json")
    
    # 1. Archive current
    if os.path.exists(current_file):
        shutil.copy(current_file, old_file)
    else:
        print("🆕 First run for notifications. No comparison possible yet.")

    # 2. Fetch Fresh Data (to notifications.json in resources)
    # Again, ensure fetch_notifications saves to correct place
    if not run_script("fetch_notifications.py"):
        return

    # 3. Diff (Only if we have an OLD file)
    if os.path.exists(old_file) and os.path.exists(current_file):
        args = [old_file, current_file]
        if output_diff_file:
            args.append(output_diff_file)
            
        run_script("diff_notifications.py", args)
    else:
        print("ℹ️ Skipping diff (missing old or new file).")

def main():
    out_file = sys.argv[1] if len(sys.argv) > 1 else None
    monitor_notifications(out_file)

if __name__ == "__main__":
    main()
