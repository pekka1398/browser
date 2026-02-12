
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

def monitor_course(course_id, output_diff_file=None):
    print(f"\n{'='*60}")
    print(f"👀 Monitoring Course ID: {course_id}")
    print(f"{'='*60}")
    
    # Initialize output file with empty list (no diffs) in case we fail early
    if output_diff_file:
        try:
            with open(output_diff_file, "w") as f:
                f.write("[]")
        except:
            pass

    # Filenames (now full paths)
    full_file = get_res_path(f"course_{course_id}_full_data.json")
    clean_file = get_res_path(f"course_{course_id}_clean.json")
    old_clean_file = get_res_path(f"course_{course_id}_clean_OLD.json")
    
    # 1. Archive previous clean file (if exists) to OLD
    if os.path.exists(clean_file):
        shutil.copy(clean_file, old_clean_file)
    else:
        print("🆕 First run for this course. No comparison possible yet.")

    # 2. Fetch Fresh Data (Pass ID)
    if not run_script("fetch_full_course_data.py", [str(course_id)]):
        return

    # 3. Clean Data (Pass ID)
    if not run_script("clean_course_data.py", [str(course_id)]):
        return
        
    # 4. Diff (Only if we have an OLD file)
    if os.path.exists(old_clean_file) and os.path.exists(clean_file):
        print("⚖️ Comparing OLD vs NEW state...")
        
        args = [old_clean_file, clean_file]
        if output_diff_file:
            args.append(output_diff_file)
            
        run_script("diff_course_json.py", args)
    else:
        print("ℹ️ Skipping diff (missing old or new file).")

def main():
    if len(sys.argv) < 2:
        print("Usage: python monitor_single_course.py <course_id> [output_diff.json]")
        sys.exit(1)
        
    course_id = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    monitor_course(course_id, out_file)

if __name__ == "__main__":
    main()
