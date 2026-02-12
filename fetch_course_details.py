
import requests
import json
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = "f8df006962c71b2468033bfcf5ed9ed5"
BASE_URL = "https://moodle.ncku.edu.tw"
COURSE_ID = 48736

def call_moodle_api(function_name, params=None):
    if params is None:
        params = {}
    
    url = f"{BASE_URL}/webservice/rest/server.php"
    
    payload = {
        "wstoken": TOKEN,
        "wsfunction": function_name,
        "moodlewsrestformat": "json",
    }
    payload.update(params)
    
    try:
        response = requests.post(url, data=payload, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error calling {function_name}: {e}")
        return None

def main():
    print(f"🔍 Fetching ALL data for Course ID: {COURSE_ID}...\n")
    
    # 1. Get Course Content (Modules, Resources, Assignments)
    print("--- 1. Course Contents (Modules) ---")
    contents = call_moodle_api("core_course_get_contents", {"courseid": COURSE_ID})
    
    # Save raw JSON for inspection
    with open("course_48736_contents.json", "w", encoding="utf-8") as f:
        json.dump(contents, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved raw content to 'course_48736_contents.json'")

    if contents:
        # Simple summary
        for section in contents:
            name = section.get('name', 'Unnamed Section')
            print(f"\n📂 Section: {name}")
            modules = section.get('modules', [])
            if not modules:
                print("   (Empty)")
            for module in modules:
                mod_name = module.get('name')
                mod_type = module.get('modname')
                mod_url = module.get('url', 'No URL')
                print(f"   - [{mod_type}] {mod_name}")
                if mod_type == 'resource':
                    # Check for file download URL
                    contents = module.get('contents', [])
                    for c in contents:
                        if c.get('fileurl'):
                            print(f"     ⬇️ File: {c['fileurl']}")

    # 2. Get Course Assignments (if any)
    print("\n--- 2. Assignments ---")
    assignments = call_moodle_api("mod_assign_get_assignments", {"courseids[0]": COURSE_ID})
    
    with open("course_48736_assignments.json", "w", encoding="utf-8") as f:
        json.dump(assignments, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved assignments to 'course_48736_assignments.json'")
        
    if assignments and 'courses' in assignments and assignments['courses']:
        for assign in assignments['courses'][0].get('assignments', []):
            print(f"   📝 {assign['name']} (Due: {assign.get('duedate_str', 'No date')})")
            print(f"      {assign.get('intro', '')[:100]}...")  # Show preview of description

    else:
        print("   (No assignments found or API error)")


if __name__ == "__main__":
    main()
