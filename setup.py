import requests
import json
from urllib.parse import urljoin
import config

HEADERS = {
    "Api-Key": config.API_KEY,
    "Api-Username": config.ADMIN_USERNAME,
    "Content-Type": "application/json"
}

#title description automation
def update_site_settings():
    print("Updating Discourse Site Settings...")
    
    # Update Site Title
    title_response = requests.put(
        urljoin(config.DISCOURSE_URL, "/admin/site_settings/title"),
        headers=HEADERS,
        json={"title": config.SITE_TITLE}
    )
    
    if title_response.status_code == 200:
        print(f"✓ Successfully updated site title to: {config.SITE_TITLE}")
    else:
        print(f"✗ Failed to update title. Status: {title_response.status_code}, Response: {title_response.text}")

    # Update Site Description
    desc_response = requests.put(
        urljoin(config.DISCOURSE_URL, "/admin/site_settings/site_description"), 
        headers=HEADERS,
        json={"site_description": config.SITE_DESCRIPTION}
    )
    
    if desc_response.status_code == 200:
        print(f"✓ Successfully updated site description to: {config.SITE_DESCRIPTION}")
    else:
        print(f"✗ Failed to update description. Status: {desc_response.status_code}, Response: {desc_response.text}")

#Disable powered by discourse
def disable_powered_by():
    print("\nDisabling 'Powered by Discourse'...")
    response = requests.put(
        urljoin(config.DISCOURSE_URL, "/admin/site_settings/enable_powered_by_discourse"),
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
        urljoin(config.DISCOURSE_URL, "/admin/site_settings/google_oauth2_client_id"),
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
        urljoin(config.DISCOURSE_URL, "/admin/site_settings/google_oauth2_client_secret"),
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
        urljoin(config.DISCOURSE_URL, "/admin/site_settings/enable_google_oauth2_logins"),
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
        urljoin(config.DISCOURSE_URL, "/admin/site_settings/gtm_container_id"),
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
        urljoin(config.DISCOURSE_URL, "/admin/site_settings/top_menu"),  # Construct endpoint like GTM
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
        urljoin(config.DISCOURSE_URL, "/admin/site_settings/base_font"),
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
        urljoin(config.DISCOURSE_URL, "/admin/site_settings/heading_font"),
        headers=HEADERS,
        json={"heading_font": "arial"}
    )

    if heading_font_response.status_code == 200:
        print("✓ Heading font set to Arial successfully")
    else:
        print(f"✗ Failed to set heading font: {heading_font_response.status_code} - {heading_font_response.text}")
        return False

    return True  # Only returns True if both fonts are configured successfully

#Disable Full page login
def disable_full_page_login():
    print("\nDisabling 'Full page login'...")
    response = requests.put(
        urljoin(config.DISCOURSE_URL, "/admin/site_settings/full_page_login"),
        headers=HEADERS,
        json={"full_page_login": "false"}
    )
    
    if response.status_code == 200:
        print("✓ Successfully disabled 'Full page login'")
    else:
        print(f"✗ Failed to disable. Status: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    update_site_settings()
    disable_powered_by()
    configure_google_oauth()
    configure_gtm()
    update_top_menu()
    configure_fonts()
    disable_full_page_login()