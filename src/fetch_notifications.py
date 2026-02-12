
import requests
import json
import urllib3
import os
from datetime import datetime
import re

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

def clean_html(raw_html):
    """Remove HTML tags for cleaner output"""
    if not isinstance(raw_html, str):
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def main():
    print(f"🔔 Checking Moodle Notifications...\n")
    
    # Get User ID first
    site_info = call_moodle_api("core_webservice_get_site_info")
    if not site_info:
        print("❌ Failed to get site info.")
        return
    user_id = site_info['userid']

    # Fetch Notifications
    # message_popup_get_popup_notifications returns detailed notification list
    # limit: default 0 (all), offset: 0
    notifications = call_moodle_api("message_popup_get_popup_notifications", {
        "useridto": user_id, 
        "limit": 20, # Limit to latest 20 notifications
        "offset": 0
    })

    if not notifications:
        print("⚠️ No response from notification API.")
        return

    unread_count = notifications.get('unreadcount', 0)
    print(f"📬 Unread Notifications: {unread_count}\n")

    # Both read and unread messages are usually in 'notifications' array
    all_notifs = notifications.get('notifications', [])
    
    if not all_notifs:
         print("✅ No recent notifications found.")
         return

    print("📜 Latest Notifications:\n")
    
    for note in all_notifs:
        # Extract key info
        subject = note.get('subject', 'No Subject')
        text_short = note.get('smallmessage', '') # Often HTML
        text_full = note.get('fullmessage', '') 
        sender = note.get('userfromfullname', 'System')
        
        # Timestamp
        ts = note.get('timecreated', 0)
        date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
        
        # Read/Unread Status
        is_read = note.get('read', False)
        status_icon = "⚪" if is_read else "🔵"
        
        # Link (if any)
        context_url = note.get('contexturl', '')
        context_name = note.get('contexturlname', '')

        # Output formatting
        print(f"{status_icon} [{date_str}] From: {sender}")
        print(f"   📌 Subject: {subject}")
        if text_short:
             print(f"   📝 Message: {clean_html(text_short)[:150]}...") # Preview first 150 chars
        if context_name and context_url:
             print(f"   🔗 Link: {context_name} ({context_url})")
        print("-" * 40)

    # Save raw for inspection (in resources)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", "notifications.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(notifications, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Raw data saved to {output_path}")

if __name__ == "__main__":
    main()
