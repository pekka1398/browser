
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
    print(f"🔍 Fetching Site Info (Functions)...")
    
    # Get Site Info
    site_info = call_moodle_api("core_webservice_get_site_info")
    if not site_info:
        print("❌ Failed to get site info.")
        return
        
    print(f"✅ User: {site_info['fullname']} (ID: {site_info['userid']})\n")

    # List Available Functions
    if 'functions' in site_info:
        functions = site_info['functions']
        print(f"📋 Available API Functions ({len(functions)}):")
        
        # Save full list to file
        with open("available_functions.json", "w", encoding="utf-8") as f:
            json.dump(functions, f, indent=2, ensure_ascii=False)
            
        # Print relevant ones (course, grade, user, block)
        relevant_keywords = ["course", "grade", "user", "block", "calendar", "event"]
        
        for func in functions:
            name = func['name']
            version = func['version']
            
            # Simple keyword matching
            if any(k in name for k in relevant_keywords):
                print(f"   - {name} (v{version})")

    else:
        print("❌ No function list returned in site info.")

if __name__ == "__main__":
    main()
