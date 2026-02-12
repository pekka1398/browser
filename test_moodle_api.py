
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://moodle.ncku.edu.tw"
TOKEN_URL = f"{BASE_URL}/login/token.php"

def get_moodle_token():
    username = os.getenv("MOODLE_USER")
    password = os.getenv("MOODLE_PASS")

    if not username or not password:
        print("Error: MOODLE_USER or MOODLE_PASS not found in .env")
        return

    # Standard Moodle Mobile App Service
    service = "moodle_mobile_app" 

    params = {
        "username": username,
        "password": password,
        "service": service
    }

    # SSL Warning suppression
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        print(f"Attempting to get token from {TOKEN_URL}...")
        # Add verify=False to bypass SSL check
        response = requests.get(TOKEN_URL, params=params, verify=False)
        if response.status_code != 200:
            print(f"Failed with status code: {response.status_code}")
            return
            
        try:
            data = response.json()
        except ValueError:
             print(f"Response is not JSON: {response.text[:200]}")
             return
        
        if "token" in data:
            print(f"\n✅ Success! Token acquired: {data['token']}")
            return data['token']
        elif "error" in data:
            print(f"\n❌ API Error: {data['error']} - {data.get('errorcode', '')}")
            if data.get('errorcode') == 'enablewsdescription':
                 print("Hint: It seems web services are enabled but user might not have permission or service is different.")
        else:
            print(f"\n❓ Unknown response format: {data}")

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    get_moodle_token()
