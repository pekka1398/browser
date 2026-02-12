
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
    print(f"🔍 Fetching Site Info (User ID)...")
    
    # 1. Get User ID
    site_info = call_moodle_api("core_webservice_get_site_info")
    if not site_info:
        print("❌ Failed to get site info.")
        return
        
    user_id = site_info['userid']
    fullname = site_info['fullname'] 
    print(f"✅ User: {fullname} (ID: {user_id})\n")

    # 2. Get User Grades Overview (Usually for all courses)
    print("📊 Fetching Grade Overview (gradereport_overview_get_course_grades)...")
    grades_overview = call_moodle_api("gradereport_overview_get_course_grades", {"userid": user_id})
    
    # Save Raw Response
    with open("grades_overview.json", "w", encoding="utf-8") as f:
        json.dump(grades_overview, f, indent=2, ensure_ascii=False)
        
    if grades_overview and 'grades' in grades_overview:
        print(f"✅ Found grades for {len(grades_overview['grades'])} courses:\n")
        
        for course_grade in grades_overview['grades']:
            course_id = course_grade['courseid']
            # We might not have course fullnames here, just IDs
            grade_raw = course_grade.get('rawgrade', 'N/A')
            grade_final = course_grade.get('grade', 'N/A')
            rank = course_grade.get('rank', 'N/A')
            
            print(f"📚 Course ID: {course_id}")
            print(f"   Score: {grade_raw}")
            print(f"   Final Grade: {grade_final}")
            if rank != 'N/A':
                 print(f"   Rank: {rank}")
            print("-" * 20)
    else:
         print("⚠️ Could not fetch grade overview (gradereport_overview_get_course_grades). Trying user report...")
         
    # 3. Fallback: gradereport_user_get_grades_table (Get HTML table of grades)
    print("\nAttempting Fallback: gradereport_user_get_grades_table...")
    # This one usually gets the HTML table for a specific course or user
    # Try fetching for the electronic course ID: 48736
    grades_table = call_moodle_api("gradereport_user_get_grades_table", {"userid": user_id, "courseid": 48736})
    
    if grades_table and 'tables' in grades_table:
         print("✅ Found grade tables (HTML format). Saved to 'grades_table.json'.")
         with open("grades_table.json", "w", encoding="utf-8") as f:
            json.dump(grades_table, f, indent=2, ensure_ascii=False)
            
         # If we are lucky, table data is structured
         for table in grades_table['tables']:
             if 'tabledata' in table:
                 print("\n📝 Specific Grade Items for Course 48736:")
                 for row in table['tabledata']:
                     # Often the structure is complex inside 'itemname' and 'grade'
                     item = row.get('itemname', {}).get('content', 'Unknown Item')
                     grade = row.get('grade', {}).get('content', '-')
                     if 'class' in row and 'level1' in row['class']: # Main category
                          print(f"\n📂 {item}")
                     else:
                          print(f"   - {item}: {grade}")


if __name__ == "__main__":
    main()
