
import json
import sys
import re

def clean_html(raw_html):
    """Remove HTML tags for cleaner output"""
    if not isinstance(raw_html, str):
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def load_notifications(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # The API returns a wrapper with 'notifications', OR sometimes direct list if we saved it directly
            # Let's handle both
            if isinstance(data, dict) and 'notifications' in data:
                return data['notifications']
            elif isinstance(data, list):
                return data
            else:
                return []
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return []

def diff_notifications(old_file, new_file, output_file=None):
    print(f"🔔 Comparing Notifications: {old_file} -> {new_file} ...\n")
    
    old_list = load_notifications(old_file)
    new_list = load_notifications(new_file)
    
    # Create dictionaries keyed by ID for easy lookup
    old_dict = {item['id']: item for item in old_list if 'id' in item}
    new_dict = {item['id']: item for item in new_list if 'id' in item}
    
    # 1. New Notifications (Keys in NEW but not in OLD)
    new_ids = set(new_dict.keys()) - set(old_dict.keys())
    
    results = []

    if new_ids:
        print(f"🆕 พบ {len(new_ids)} New Notification(s)!\n")
        sorted_ids = sorted(list(new_ids), reverse=True) # Newest first (usually higher ID)
        
        for nid in sorted_ids:
            note = new_dict[nid]
            subject = note.get('subject', 'No Subject')
            sender = note.get('userfromfullname', 'System')
            text = clean_html(note.get('smallmessage', ''))
            
            print(f"   [ID: {nid}] From: {sender}")
            print(f"   📌 Subject: {subject}")
            print(f"   📝 Preview: {text[:100]}...")
            print("-" * 40)
            
            results.append(f"New Notification [ID: {nid}] From: {sender} | Subject: {subject}")
    else:
        print("✅ No new notifications.")

    # Output to JSON file if requested
    if output_file:
         try:
             with open(output_file, "w", encoding="utf-8") as f:
                 json.dump(results, f, ensure_ascii=False, indent=2)
         except Exception as e:
             print(f"❌ Failed to write diff output to {output_file}: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python diff_notifications.py <old_notifications.json> <new_notifications.json> [output_diff.json]")
        sys.exit(1)
        
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    out_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    diff_notifications(file1, file2, out_file)

if __name__ == "__main__":
    main()
