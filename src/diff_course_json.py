
import json
import sys
import re
from deepdiff import DeepDiff
from deepdiff.helper import CannotCompare

# Filters: Be explicit about what we are filtering out
# 1. 'fetched_at': Always changes with every fetch.
# 2. 'token' parameter in Moodle URLs: Though our main token is static, sometimes dynamic download tokens appear.
#    We will use DeepDiff's 'exclude_regex_paths' or 'exclude_paths' for this.

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        sys.exit(1)

def diff_Jsons(file1, file2, output_file=None):
    print(f"🔄 Comparing {file1} -> {file2} ...\n")
    
    old_data = load_json(file1)
    new_data = load_json(file2)
    
    # --- FILTERS DEFINITION ---
    exclude_paths = [
        "root['fetched_at']",  # Explicitly ignore fetch timestamp
        # Moodle often changes these dynamically even if content is same:
        "root['assignments'][0]['contextid']", 
        "root['contents'][0]['modules'][0]['id']" # But be careful not to hide real changes
    ]

    # Use regex to exclude things like dynamic timestamps if they appear deep in structures
    # For now, let's keep it simple to just `fetched_at` as the main filter.
    
    diff = DeepDiff(old_data, new_data, 
                    ignore_order=True,
                    exclude_paths=exclude_paths,
                    verbose_level=2) # Level 2 gives us both old and new values

    results = []

    if not diff:
        print("✅ No differences found (filtered).")
    else:
        # --- OUTPUT ---
        print("🔍 Differences Found:\n")
        
        # 1. Added Items
        if 'dictionary_item_added' in diff:
            print("➕ [Added Items]")
            for item in diff['dictionary_item_added']:
                msg = f"Added Item at {item}"
                print(f"   {msg}")
                results.append(msg)

        # 2. Removed Items
        if 'dictionary_item_removed' in diff:
            print("➖ [Removed Items]")
            for item in diff['dictionary_item_removed']:
                msg = f"Removed Item at {item}"
                print(f"   {msg}")
                results.append(msg)

        # 3. Changed Values
        if 'values_changed' in diff:
            print("✏️ [Changed Values]")
            for path, change in diff['values_changed'].items():
                print(f"   path: {path}")
                print(f"     OLD: {change['old_value']}")
                print(f"     NEW: {change['new_value']}")
                print("-" * 40)
                results.append(f"Changed Value at {path}: OLD={change['old_value']} -> NEW={change['new_value']}")
                
        # 4. Iterable Item Added (e.g. to a list)
        if 'iterable_item_added' in diff:
             print("➕ [List Item Added]")
             for path, item in diff['iterable_item_added'].items():
                 print(f"   path: {path}")
                 print(f"     VALUE: {item}")
                 results.append(f"List Item Added at {path}: {item}")

        # 5. Iterable Item Removed
        if 'iterable_item_removed' in diff:
             print("➖ [List Item Removed]")
             for path, item in diff['iterable_item_removed'].items():
                 print(f"   path: {path}")
                 print(f"     VALUE: {item}")
                 results.append(f"List Item Removed at {path}: {item}")

    # Output to JSON file if requested
    if output_file:
         try:
             with open(output_file, "w", encoding="utf-8") as f:
                 json.dump(results, f, ensure_ascii=False, indent=2)
         except Exception as e:
             print(f"❌ Failed to write diff output to {output_file}: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: uv run python diff_course_json.py <old_file.json> <new_file.json> [output_diff.json]")
        sys.exit(1)
        
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    out_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    diff_Jsons(file1, file2, out_file)

if __name__ == "__main__":
    main()
