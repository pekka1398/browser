
import requests
import urllib3
import os

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = "f8df006962c71b2468033bfcf5ed9ed5"
FILE_URL = "https://moodle.ncku.edu.tw/webservice/pluginfile.php/1991490/mod_resource/content/1/%E9%9B%BB%E5%AD%90%E5%AD%B8%E5%BA%A7%E4%BD%8D%E8%A1%A8.xlsx?forcedownload=1"
OUTPUT_FILENAME = "電子學座位表.xlsx"

def download_file_with_token(url, filename):
    # Append token to URL as query parameter for authentication
    # Usually Moodle file downloads need the token appended like this:
    # &token=YOUR_TOKEN
    
    download_url = f"{url}&token={TOKEN}"
    
    print(f"⬇️ Downloading {filename}...")
    # print(f"🔗 URL: {download_url}") # Don't print full URL with token in logs for security
    
    try:
        response = requests.get(download_url, verify=False, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        print(f"✅ Successfully downloaded to: {os.path.abspath(filename)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download: {e}")
        return False

if __name__ == "__main__":
    download_file_with_token(FILE_URL, OUTPUT_FILENAME)
