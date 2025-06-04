import os
import requests
from datetime import datetime

# 🔧 Configuration
INSTANCE = 'xxxx.service-now.com' # e.g., dev12345.service-now.com 

LOCAL_BASE_FOLDER = './incident_attachments'

# 📦 Headers get the cookie and user token from existing servicenow session. Otherwise use basic auth using userid / pwd 
HEADERS = {
    "Accept": "application/json",
    "Cookie":"glide_sso_id=XXXXXX",
    "x-usertoken": "xxxxx"
}

# user proxies if you are behind a firewall.
proxies = {
    "http": "http://x.yyyyy.com:8080",
    "https": "http://x.yyyyy.com:8080"
}

# 🔍 Step 1: Get today's incidents
def get_today_incidents():
    url = f"https://{INSTANCE}/api/now/table/incident"
    params = {
        'sysparm_query': f"numberININC10275XXX,INC102758XXX",  # update with your query or dynamic filter
        'sysparm_fields': 'sys_id,number',
        'sysparm_limit': '1300'
    }
    response = requests.get(url, headers=HEADERS, params=params, proxies=proxies)
    response.raise_for_status()
    return response.json().get('result', [])

# 📎 Step 2: Get attachments for an incident
def get_attachments(incident_sys_id):
    url = f"https://{INSTANCE}/api/now/table/sys_attachment"
    params = {
        'table_name': 'incident',
        'table_sys_id': incident_sys_id
    }
    response = requests.get(url, headers=HEADERS, params=params, proxies=proxies)
    response.raise_for_status()
    return response.json().get('result', [])

# 💾 Step 3: Download attachment
def download_attachment(sys_id, filename, folder_path):
    url = f"https://{INSTANCE}/api/now/attachment/{sys_id}/file"
    response = requests.get(url, headers=HEADERS, stream=True, proxies=proxies)
    response.raise_for_status()
    file_path = os.path.join(folder_path, filename)
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

# 🚀 Main
def main():
    incidents = get_today_incidents()
    print(f"Found {len(incidents)} incidents created today.")

    for incident in incidents:
        incident_sys_id = incident['sys_id']
        incident_number = incident['number']
        print(f"\nProcessing Incident: {incident_number}")

        # Get attachments first
        attachments = get_attachments(incident_sys_id)

        if not attachments:
            print(f"  No attachments found for incident {incident_number}. Skipping folder creation.")
            continue  # Skip folder creation and download if no attachments

        # Create local folder only if attachments exist
        incident_folder = os.path.join(LOCAL_BASE_FOLDER, incident_number)
        os.makedirs(incident_folder, exist_ok=True)

        # Download attachments
        for att in attachments:
            print(f"  Downloading: {att['file_name']}")
            download_attachment(att['sys_id'], att['file_name'], incident_folder)

if __name__ == "__main__":
    main()
