
import requests
import json
import urllib3
import os
from datetime import datetime

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import sys

TOKEN = "f8df006962c71b2468033bfcf5ed9ed5"
BASE_URL = "https://moodle.ncku.edu.tw"

import os

# Check for command line argument for Course ID
if len(sys.argv) > 1:
    COURSE_ID = int(sys.argv[1])
else:
    COURSE_ID = 48736 # Default (Electronics 1)

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", f"course_{COURSE_ID}_full_data.json")

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
    print(f"🚀 Fetching EVERYTHING for Course ID: {COURSE_ID}...\n")
    
    full_data = {
        "course_id": COURSE_ID,
        "fetched_at": datetime.now().isoformat(),
        "contents": [],
        "assignments": [],
        "grades": [],
        "assignments": [],
        "grades": [],
        "forums": [],
        "labels": [],
        "pages": [],
        "blocks": [],
        "quizzes": [],
        "feedbacks": [],
        "surveys": [],
        "wikis": [],
        "workshops": [],
        "calendar_events": []
    }

    # 1. Course Contents (Modules, Resources, URLs)
    print("📦 1. Fetching Course Structure & Contents...")
    contents = call_moodle_api("core_course_get_contents", {"courseid": COURSE_ID})
    if contents:
        full_data["contents"] = contents
        print(f"   ✅ Fetched {len(contents)} sections")

    # 2. Assignments
    print("📝 2. Fetching Assignments...")
    assignments = call_moodle_api("mod_assign_get_assignments", {"courseids[0]": COURSE_ID})
    if assignments and 'courses' in assignments and assignments['courses']:
        assign_list = assignments['courses'][0].get('assignments', [])
        full_data["assignments"] = assign_list
        print(f"   ✅ Fetched {len(assign_list)} assignments")
        
        # Deep fetch: Get submission status for each assignment
        print("      ...Fetching detailed submission status for each assignment...")
        for assign in assign_list:
            assign_id = assign['id']
            # mod_assign_get_submission_status requires 'assignid'
            sub_status = call_moodle_api("mod_assign_get_submission_status", {"assignid": assign_id})
            if sub_status:
                assign['submission_details'] = sub_status
                # Quick preview of status
                if 'lastattempt' in sub_status:
                    status = sub_status['lastattempt'].get('submission', {}).get('status', 'unknown')
                    print(f"      - {assign['name']}: {status}")
            else:
                assign['submission_details'] = {"error": "Could not fetch status"}

    else:
        print("   ⚠️ No assignments found or API structure differed")

    # 3. Grades (Using HTML Table fallback)
    print("📊 3. Fetching Grades...")
    
    # Need User ID first
    site_info = call_moodle_api("core_webservice_get_site_info")
    if site_info:
        user_id = site_info['userid']
        grades_table = call_moodle_api("gradereport_user_get_grades_table", {"userid": user_id, "courseid": COURSE_ID})
        
        if grades_table and 'tables' in grades_table:
             parsed_grades = []
             for table in grades_table['tables']:
                 if 'tabledata' in table:
                     for row in table['tabledata']:
                         # Handle list vs dict (API sometimes returns empty list for dict)
                         if isinstance(row, list): continue
                         
                         item_data = row.get('itemname', {})
                         # Extract content handling both string and huge object
                         item_name = "Unknown"
                         if isinstance(item_data, dict):
                            item_name = item_data.get('content', 'Unknown')
                            # Clean HTML tags
                            if "<" in item_name:
                                try:
                                    import re
                                    # Simple regex to strip HTML tags
                                    item_name = re.sub('<[^<]+?>', '', item_name).strip()
                                except: pass
                         
                         grade_data = row.get('grade', {})
                         grade_val = "-"
                         if isinstance(grade_data, dict):
                             grade_val = grade_data.get('content', '-')

                         if item_name != "Unknown":
                             parsed_grades.append({"item": item_name, "grade": grade_val})
             
             full_data["grades"] = parsed_grades
             print(f"   ✅ Fetched {len(parsed_grades)} grade items")
        else:
             print("   ⚠️ No grade table returned")
    else:
         print("   ⚠️ Could not get user ID for grades")

    # 4. Forums & Announcements
    print("📢 4. Fetching Forums & Discussions...")
    forums = call_moodle_api("mod_forum_get_forums_by_courses", {"courseids[0]": COURSE_ID})
    if forums:
        print(f"   ✅ Found {len(forums)} forums. Fetching discussions for each...")
        for forum in forums:
            forum_data = {
                "id": forum['id'],
                "name": forum['name'],
                "type": forum.get('type', 'unknown'),
                "discussions": []
            }
            
            # Fetch discussions for this forum
            discussions = call_moodle_api("mod_forum_get_forum_discussions_paginated", {"forumid": forum['id']})
            if discussions and 'discussions' in discussions:
                forum_data["discussions"] = discussions['discussions']
                print(f"      - {forum['name']}: {len(discussions['discussions'])} posts")
            
            full_data["forums"].append(forum_data)
    else:
        print("   ⚠️ No forums found")

    # 5. Participants (Users) - Optional, might be privacy restricted
    print("👥 5. Fetching Participants (Users)...")
    users = call_moodle_api("core_enrol_get_enrolled_users", {"courseid": COURSE_ID})
    if users:
         # Filter sensitive data, keep minimal info
         safe_users = [{"id": u['id'], "fullname": u['fullname'], "roles": u.get('roles', [])} for u in users]
         full_data["participants"] = safe_users
         print(f"   ✅ Fetched {len(safe_users)} participants")
    else:
         print("   ⚠️ Could not fetch participants (likely permission denied)")

    # 6. Labels (Often used for course info/announcements on main page)
    print("🏷️ 6. Fetching Labels (Course Info)...")
    labels = call_moodle_api("mod_label_get_labels_by_courses", {"courseids[0]": COURSE_ID})
    if labels and 'labels' in labels:
         full_data["labels"] = labels['labels']
         print(f"   ✅ Fetched {len(labels['labels'])} labels")
         # Preview content to see if it matches "課程快速設定"
         for l in labels['labels']:
             if "快速設定" in l.get('name', '') or "快速設定" in l.get('intro', ''):
                 print(f"      🎯 FOUND '課程快速設定' in Label ID {l['id']}!")
    else:
         print("   ⚠️ No labels found")

    # 7. Pages (HTML Content Pages)
    print("📄 7. Fetching Pages...")
    pages = call_moodle_api("mod_page_get_pages_by_courses", {"courseids[0]": COURSE_ID})
    if pages and 'pages' in pages:
         full_data["pages"] = pages['pages']
         print(f"   ✅ Fetched {len(pages['pages'])} pages")
    else:
         print("   ⚠️ No pages found")

    # 8. Blocks (Sidebars/Top Blocks)
    print("🧱 8. Fetching Blocks...")
    blocks = call_moodle_api("core_block_get_course_blocks", {"courseid": COURSE_ID})
    if blocks and 'blocks' in blocks:
         full_data["blocks"] = blocks['blocks']
         print(f"   ✅ Fetched {len(blocks['blocks'])} blocks")
    else:
         print("   ⚠️ No blocks found")

    # 9. Quizzes (Online Tests)
    print("📝 9. Fetching Quizzes & Attempts...")
    quizzes = call_moodle_api("mod_quiz_get_quizzes_by_courses", {"courseids[0]": COURSE_ID})
    if quizzes and 'quizzes' in quizzes:
         quiz_list = quizzes['quizzes']
         full_data["quizzes"] = quiz_list
         print(f"   ✅ Fetched {len(quiz_list)} quizzes")
         
         # Deep fetch: Get user attempts for each quiz
         print("      ...Fetching user attempts for each quiz...")
         for quiz in quiz_list:
             quiz_id = quiz['id']
             attempts = call_moodle_api("mod_quiz_get_user_attempts", {"quizid": quiz_id})
             if attempts and 'attempts' in attempts:
                 quiz['user_attempts'] = attempts['attempts']
                 print(f"      - {quiz['name']}: {len(attempts['attempts'])} attempts")
             else:
                 quiz['user_attempts'] = []
    else:
         print("   ⚠️ No quizzes found")

    # 10. Feedbacks (Course Evaluations/Surveys)
    print("📝 10. Fetching Feedbacks...")
    feedbacks = call_moodle_api("mod_feedback_get_feedbacks_by_courses", {"courseids[0]": COURSE_ID})
    if feedbacks and 'feedbacks' in feedbacks:
         full_data["feedbacks"] = feedbacks['feedbacks']
         print(f"   ✅ Fetched {len(feedbacks['feedbacks'])} feedbacks")
    else:
         print("   ⚠️ No feedbacks found")

    # 11. Surveys (Standard Moodle Surveys)
    print("📋 11. Fetching Surveys...")
    surveys = call_moodle_api("mod_survey_get_surveys_by_courses", {"courseids[0]": COURSE_ID})
    if surveys and 'surveys' in surveys:
         full_data["surveys"] = surveys['surveys']
         print(f"   ✅ Fetched {len(surveys['surveys'])} surveys")
    else:
         print("   ⚠️ No surveys found")

    # 12. Wikis (Collaborative Content)
    print("📖 12. Fetching Wikis...")
    wikis = call_moodle_api("mod_wiki_get_wikis_by_courses", {"courseids[0]": COURSE_ID})
    if wikis and 'wikis' in wikis:
         full_data["wikis"] = wikis['wikis']
         print(f"   ✅ Fetched {len(wikis['wikis'])} wikis")
    else:
         print("   ⚠️ No wikis found")

    # 13. Workshops (Peer Review Assignments)
    print("🛠️ 13. Fetching Workshops...")
    workshops = call_moodle_api("mod_workshop_get_workshops_by_courses", {"courseids[0]": COURSE_ID})
    if workshops and 'workshops' in workshops:
         full_data["workshops"] = workshops['workshops']
         print(f"   ✅ Fetched {len(workshops['workshops'])} workshops")
    else:
         print("   ⚠️ No workshops found")
         
    # 14. Calendar Events (Specific to this course)
    print("📅 14. Fetching Calendar Events...")
    # This API is great because it gets strict course events
    events = call_moodle_api("core_calendar_get_action_events_by_course", {"courseid": COURSE_ID})
    if events and 'events' in events:
         full_data["calendar_events"] = events['events']
         print(f"   ✅ Fetched {len(events['events'])} calendar events")
    else:
         print("   ⚠️ No calendar events found")


    # Save Everything to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(full_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ DONE! All data saved to {os.path.abspath(OUTPUT_FILE)}")
    print(f"   File size: {os.path.getsize(OUTPUT_FILE) / 1024:.2f} KB")

if __name__ == "__main__":
    main()
