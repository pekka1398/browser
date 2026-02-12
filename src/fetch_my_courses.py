
import requests
import json
import urllib3
import os

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = "f8df006962c71b2468033bfcf5ed9ed5"
BASE_URL = "https://moodle.ncku.edu.tw"

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
    print(f"🔎 Fetching Enrolled Courses...\n")
    
    # Get User ID first
    site_info = call_moodle_api("core_webservice_get_site_info")
    if not site_info:
        print("❌ Failed to get site info.")
        return
    user_id = site_info['userid']
    print(f"👤 User: {site_info['fullname']} (ID: {user_id})")

    # Get Courses
    courses = call_moodle_api("core_enrol_get_users_courses", {"userid": user_id})
    if not courses:
        print("❌ No courses found for this user.")
        return
        
    print(f"📚 Found {len(courses)} enrolled courses.\n")
    
    watchlist = []
    
    # List nice summary
    for course in courses:
        cid = course['id']
        cname = course['fullname']
        cshort = course['shortname']
        startdate = course.get('startdate', 0)
        
        # Simple heuristic to identify "recent" courses if needed (by ID or date)
        # But for now just list all
        
        print(f"   [ID: {cid}] {cname} ({cshort})")
        
        watchlist.append({
            "id": cid,
            "name": cname,
            "active": True # Default to True, user can modify later
        })
        
    # Save to JSON
    output_file = "all_my_courses.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(watchlist, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ Saved course list to '{output_file}'.")
    print("👉 Please edit this file to keep only the courses you want to monitor.")

if __name__ == "__main__":
    main()
