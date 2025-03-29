import requests
import json
from urllib.parse import urljoin
import config

HEADERS = {
    "Api-Key": config.API_KEY,
    "Api-Username": config.ADMIN_USERNAME,
    "Content-Type": "application/json"
}

# Color Scheme Definition
COLOR_SCHEME = {
    "name": "GetJobs Colors",  # Display name in admin UI
    "colors": [
        {"name": "primary", "hex": "222222"},
        {"name": "secondary", "hex": "FFFFFF"},
        {"name": "tertiary", "hex": "EB6427"},
        {"name": "quaternary", "hex": "0D245D"},
        {"name": "header_background", "hex": "0D245D"},
        {"name": "header_primary", "hex": "FFFFFF"},
        {"name": "highlight", "hex": "FFFF4D"},
        {"name": "danger", "hex": "C80001"},
        {"name": "success", "hex": "009900"},
        {"name": "love", "hex": "FA6C8D"},
        {"name": "hover", "hex": "F2F2F2"},
        {"name": "selected", "hex": "D1F0FF"},
    ]
}

def create_color_scheme():
    """Creates a new color scheme in Discourse."""
    print("\nCreating new color scheme...")

    # Endpoint for creating color schemes
    endpoint = urljoin(config.DISCOURSE_URL, "/admin/color_schemes.json")

    # Structure data for API
    scheme_payload = {
        "name": COLOR_SCHEME["name"],
        "colors": {color["name"]: color["hex"] for color in COLOR_SCHEME["colors"]}
    }

    try:
        response = requests.post(
            endpoint,
            headers=HEADERS,
            json=scheme_payload,
            timeout=10
        )

        if response.status_code == 200:
            scheme_id = response.json().get("id")
            print(f"✓ Successfully created color scheme (ID: {scheme_id})")
            return scheme_id
        else:
            print(f"✗ Failed to create scheme (HTTP {response.status_code})")
            print("Error:", response.text)
            return None

    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {str(e)}")
        return None

def apply_color_scheme_to_theme(scheme_id, theme_id):
    """Applies a color scheme to a theme."""
    print(f"\nApplying color scheme (ID: {scheme_id}) to theme (ID: {theme_id})...")

    # Endpoint to update the theme with color scheme
    endpoint = urljoin(config.DISCOURSE_URL, f"/admin/themes/{theme_id}.json")

    # Data payload to apply the color scheme
    data = {
        "theme": {
            "color_scheme_id": scheme_id
        }
    }

    try:
        response = requests.put(
            endpoint,
            headers=HEADERS,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            print(f"✓ Successfully applied color scheme to theme.")
            return True
        else:
            print(f"✗ Failed to apply scheme (HTTP {response.status_code})")
            print("Error:", response.text)
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {str(e)}")
        return False


if __name__ == "__main__":
    # Step 1: Create a new color scheme
    scheme_id = create_color_scheme()

    # Replace with your theme ID to apply the scheme
    THEME_ID = 1  # Replace with your actual Theme ID (e.g., default theme)
    if scheme_id:
        # Step 2: Apply the color scheme to a theme
        if apply_color_scheme_to_theme(scheme_id, theme_id=THEME_ID):
            print("\nNext steps:")
            print(f"1. Visit {config.DISCOURSE_URL}/admin/customize/themes")
            print("2. Verify the 'GetJobs Colors' scheme is applied properly")
    else:
        print("\nTroubleshooting:")
        print("- Verify API credentials")
        print("- Check color values are valid HEX codes")
        print("- Ensure user has admin privileges")