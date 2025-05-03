import requests
import json
from urllib.parse import urljoin
import config

HEADERS = {
    "Api-Key": config.API_KEY,
    "Api-Username": config.ADMIN_USERNAME,
    "Content-Type": "application/json",
    "User-Agent": "Discourse-Setup-Tool/1.0"
}

#Formatted occupation and URLs (No manual input here)
FORMATTED_OCCUPATION = config.OCCUPATION.replace(" ", "")
SITE_URL = f"https://www.get{FORMATTED_OCCUPATION.lower()}jobs.com"
DISCOURSE_URL = f"https://forum.get{FORMATTED_OCCUPATION.lower()}jobs.com"
SITE_TITLE = f"Get{FORMATTED_OCCUPATION}Jobs.com Forum"
SITE_DESCRIPTION = f"A community for {config.OCCUPATION.lower()} to connect, share, and find jobs."

#Formatted occupation and URLs (No manual input here) For .net domain
#FORMATTED_OCCUPATION = config.OCCUPATION.replace(" ", "")
#SITE_URL = f"https://www.get{FORMATTED_OCCUPATION.lower()}jobs.net"
#DISCOURSE_URL = f"https://forum.get{FORMATTED_OCCUPATION.lower()}jobs.net"
#SITE_TITLE = f"Get{FORMATTED_OCCUPATION}Jobs.net Forum"
#SITE_DESCRIPTION = f"A community for {config.OCCUPATION.lower()} to connect, share, and find jobs."

# Change contact email to desired contact Email
CONTACT_EMAIL = "yourcontact@email"

#title description automation
def update_site_settings():
    print("Updating Discourse Site Settings...")
    
    # Update Site Title
    title_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/title"),
        headers=HEADERS,
        json={"title": SITE_TITLE}
    )
    
    if title_response.status_code == 200:
        print(f"✓ Successfully updated site title to: {SITE_TITLE}")
    else:
        print(f"✗ Failed to update title. Status: {title_response.status_code}, Response: {title_response.text}")

    # Update Site Description
    desc_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/site_description"), 
        headers=HEADERS,
        json={"site_description": SITE_DESCRIPTION}
    )
    
    if desc_response.status_code == 200:
        print(f"✓ Successfully updated site description to: {SITE_DESCRIPTION}")
    else:
        print(f"✗ Failed to update description. Status: {desc_response.status_code}, Response: {desc_response.text}")

#Disable powered by discourse
def disable_powered_by():
    print("\nDisabling 'Powered by Discourse'...")
    response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/enable_powered_by_discourse"),
        headers=HEADERS,
        json={"enable_powered_by_discourse": "false"}
    )
    
    if response.status_code == 200:
        print("✓ Successfully disabled 'Powered by Discourse'")
    else:
        print(f"✗ Failed to disable. Status: {response.status_code}, Response: {response.text}")

#Google login enable, client id and secret
def configure_google_oauth():
    print("\nConfiguring Google OAuth...")
    
    # 1. Set Client ID
    client_id_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/google_oauth2_client_id"),
        headers=HEADERS,
        json={"google_oauth2_client_id": config.GOOGLE_CLIENT_ID}
    )
    
    if client_id_response.status_code == 200:
        print("✓ Google Client ID configured successfully")
    else:
        print(f"✗ Failed to set Client ID: {client_id_response.status_code} - {client_id_response.text}")
        return False

    # 2. Set Client Secret
    client_secret_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/google_oauth2_client_secret"),
        headers=HEADERS,
        json={"google_oauth2_client_secret": config.GOOGLE_CLIENT_SECRET}
    )
    
    if client_secret_response.status_code == 200:
        print("✓ Google Client Secret configured successfully")
    else:
        print(f"✗ Failed to set Client Secret: {client_secret_response.status_code} - {client_secret_response.text}")
        return False

    # 3. Enable Google OAuth
    enable_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/enable_google_oauth2_logins"),
        headers=HEADERS,
        json={"enable_google_oauth2_logins": "true"}
    )
    
    if enable_response.status_code == 200:
        print("✓ Google OAuth logins enabled successfully")
        return True
    else:
        print(f"✗ Failed to enable Google OAuth: {enable_response.status_code} - {enable_response.text}")
        return False

# Configure Google TAG Manager
def configure_gtm():
    print("\nConfiguring Google TAG Manager...")
    
    # 1. Set GTM ID
    client_id_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/gtm_container_id"),
        headers=HEADERS,
        json={"gtm_container_id": config.GTM_ID}
    )
    
    if client_id_response.status_code == 200:
        print("✓ GTM ID configured successfully")
    else:
        print(f"✗ Failed to set GTM ID: {client_id_response.status_code} - {client_id_response.text}")
        return False

# Update the top menu setting
def update_top_menu():
    print("\nUpdating top menu...")
    
    # 1. Set the top menu items
    menu_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/top_menu"),  # Construct endpoint like GTM
        headers=HEADERS,
        json={"top_menu": "categories|latest|new|unread|hot"}
    )
    
    if menu_response.status_code == 200:
        print("✓ Top menu updated successfully")
    else:
        print(f"✗ Failed to update top menu: {menu_response.status_code} - {menu_response.text}")
        return False

# Configure Base Font and Heading Font
def configure_fonts():
    print("\nConfiguring Font Settings...")

    # 1. Set Base Font (Arial)
    base_font_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/base_font"),
        headers=HEADERS,
        json={"base_font": "arial"}
    )

    if base_font_response.status_code == 200:
        print("✓ Base font set to Arial successfully")
    else:
        print(f"✗ Failed to set base font: {base_font_response.status_code} - {base_font_response.text}")
        return False

    # 2. Set Heading Font (Arial)
    heading_font_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/heading_font"),
        headers=HEADERS,
        json={"heading_font": "arial"}
    )

    if heading_font_response.status_code == 200:
        print("✓ Heading font set to Arial successfully")
    else:
        print(f"✗ Failed to set heading font: {heading_font_response.status_code} - {heading_font_response.text}")
        return False

    return True  # Only returns True if both fonts are configured successfully

# #Disable Full page login
# def disable_full_page_login():
#     print("\nDisabling 'Full page login'...")
#     response = requests.put(
#         urljoin(DISCOURSE_URL, "/admin/site_settings/full_page_login"),
#         headers=HEADERS,
#         json={"full_page_login": "false"}
#     )
    
#     if response.status_code == 200:
#         print("✓ Successfully disabled 'Full page login'")
#     else:
#         print(f"✗ Failed to disable. Status: {response.status_code}, Response: {response.text}")

# Set default color scheme to light (ID 7)
def set_default_color_scheme():
    print("\nSetting default color scheme to light (ID 7)...")
    
    # Update default dark mode color scheme (forces light mode)
    dark_mode_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/default_dark_mode_color_scheme_id"),
        headers=HEADERS,
        json={"default_dark_mode_color_scheme_id": 7}
    )
    
    if dark_mode_response.status_code == 200:
        print("✓ Default dark mode color scheme set to ID 7 (light)")
    else:
        print(f"✗ Failed to set dark mode color scheme. Status: {dark_mode_response.status_code}, Response: {dark_mode_response.text}")
        return False

    return True

# Configure Contact Email
def configure_contact_email():
    print("\nConfiguring Contact Email...")
    
    client_id_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/contact_email"),
        headers=HEADERS,
        json={"contact_email": CONTACT_EMAIL}
    )
    
    if client_id_response.status_code == 200:
        print("✓ Contact Email configured successfully")
    else:
        print(f"✗ Failed to set Contact Email: {client_id_response.status_code} - {client_id_response.text}")
        return False

# Purge Unactivated Users Settings to 0 days
def purge_unactive_users_settings():
    print("\nSetting Purge Unactivated Users Settings to 0 days")
    
    client_id_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/purge_unactivated_users_grace_period_days"),
        headers=HEADERS,
        json={"purge_unactivated_users_grace_period_days": 0}
    )
    
    if client_id_response.status_code == 200:
        print("✓ Setting Purge Unactivated Users Settings to 0 days successfully")
    else:
        print(f"✗ Failed to Setting Purge Unactivated Users Settings to 0 days: {client_id_response.status_code} - {client_id_response.text}")
        return False

# Update Discourse Add Jobs To Digest
def configure_job_digest_plugin():
    # 0. Enable Discourse add jobs to digest
    print("\nConfiguring Discourse add jobs to digest")
    print("\nEnabling Discourse add jobs to digest")
    
    client_id_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/discourse_add_jobs_to_digest_enabled"),
        headers=HEADERS,
        json={"discourse_add_jobs_to_digest_enabled": "true"}
    )
    
    if client_id_response.status_code == 200:
        print("✓ Discourse add jobs to digest enabled Successfully")
    else:
        print(f"✗ Failed to Enable Discourse add jobs to digest: {client_id_response.status_code} - {client_id_response.text}")
        return False

    # 1. Update Job API URL
    print("\nUpdating Job API URL")

    client_id_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/job_api_url"),
        headers=HEADERS,
        json={"job_api_url": f"https://api.get{FORMATTED_OCCUPATION.lower()}jobs.com/site/v1/digest/search"}
        #json={"job_api_url": f"https://api.get{FORMATTED_OCCUPATION.lower()}jobs.net/site/v1/digest/search"}
    )
    
    if client_id_response.status_code == 200:
        print("✓ Job API URL Updated Successfully")
    else:
        print(f"✗ Failed to update Job API URL: {client_id_response.status_code} - {client_id_response.text}")
        return False

    # 2. Update Job Site URL
    print("\nUpdating Job Site URL")

    client_id_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/job_site_url"),
        headers=HEADERS,
        json={"job_site_url": SITE_URL}
    )
    
    if client_id_response.status_code == 200:
        print("✓ Job Site URL Updated Successfully")
    else:
        print(f"✗ Failed to update Job Site URL: {client_id_response.status_code} - {client_id_response.text}")
        return False

    # 3. Update Job Site Name
    print("\nUpdating Job Site URL")

    client_id_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/job_site_name"),
        headers=HEADERS,
        json={"job_site_name": f"Get{FORMATTED_OCCUPATION}Jobs.com"}
        #json={"job_site_name": f"Get{FORMATTED_OCCUPATION}Jobs.net"}
    )
    
    if client_id_response.status_code == 200:
        print("✓ Job Site Name Updated Successfully")
    else:
        print(f"✗ Failed to update Job Site Name: {client_id_response.status_code} - {client_id_response.text}")
        return False

    # 4. Clean Job search term
    print("\nCleaning Job search term")
    
    client_id_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/job_search_term"),
        headers=HEADERS,
        json={"job_search_term": ""}
    )
    
    if client_id_response.status_code == 200:
        print("✓ Job search term cleaned Successfully")
    else:
        print(f"✗ Failed to clean Job search term: {client_id_response.status_code} - {client_id_response.text}")
        return False

    # 5. Clean Job utm parameters
    print("\nCleaning Job utm parameters")
    
    client_id_response = requests.put(
        urljoin(DISCOURSE_URL, "/admin/site_settings/job_utm_parameters"),
        headers=HEADERS,
        json={"job_utm_parameters": ""}
    )
    
    if client_id_response.status_code == 200:
        print("✓ Job utm parameters cleaned Successfully")
    else:
        print(f"✗ Failed to clean Job utm parameters: {client_id_response.status_code} - {client_id_response.text}")
        return False

if __name__ == "__main__":
    update_site_settings()
    disable_powered_by()
    configure_google_oauth()
    configure_gtm()
    update_top_menu()
    configure_fonts()
    # disable_full_page_login()
    set_default_color_scheme()
    configure_contact_email()
    purge_unactive_users_settings()
    configure_job_digest_plugin()
