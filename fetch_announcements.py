
import requests
import json
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = "f8df006962c71b2468033bfcf5ed9ed5"
BASE_URL = "https://moodle.ncku.edu.tw"

# From previous output: "公佈欄" instance ID is usually found in the module info
# We need to find the FORUM ID (instance ID) not the course module (cmid) ID 1010504
# But wait, mod_forum_get_forum_discussions_paginated usually takes the forum instance ID.
# Let's try to get all forums in the course first to find the correct ID.
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
    print(f"🔍 Fetching Forums for Course ID: {COURSE_ID}...\n")
    
    # 1. Get List of Forums in the Course
    forums = call_moodle_api("mod_forum_get_forums_by_courses", {"courseids[0]": COURSE_ID})
    
    if not forums:
        print("❌ No forums found or API error.")
        return

    target_forum_id = None
    
    for forum in forums:
        print(f"📌 Found Forum: {forum['name']} (ID: {forum['id']})")
        # We are looking for "公佈欄" or "最新消息"
        if "公佈欄" in forum['name'] or "最新消息" in forum['name'] or "News" in forum['name']:
            target_forum_id = forum['id']
            print(f"   ✅ Targeted this forum for fetching messages.")

    if target_forum_id:
        print(f"\n📨 Fetching discussions from Forum ID: {target_forum_id}...")
        discussions = call_moodle_api("mod_forum_get_forum_discussions_paginated", {"forumid": target_forum_id})
        
        if discussions and 'discussions' in discussions:
            print(f"✅ Found {len(discussions['discussions'])} discussions:\n")
            for d in discussions['discussions']:
                print(f"📢 Subject: {d['subject']}")
                print(f"   👤 Author: {d['userfullname']}")
                # Clean up HTML tags for cleaner output if possible, or just print raw
                import re
                clean_msg = re.sub('<[^<]+?>', '', d['message'])
                print(f"   📝 Message: {clean_msg[:200]}...") # Preview first 200 chars
                print(f"   📅 Time: {d['created']}") # This is timestamp, could convert
                print("-" * 30)
        else:
             print("   (No discussions found in this forum)")
    else:
        print("❌ Could not find '公佈欄' or 'News' forum in this course.")

if __name__ == "__main__":
    main()
