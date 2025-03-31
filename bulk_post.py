import requests
import json
from urllib.parse import urljoin
import config
from config import topics

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

# Fetch categories
print("Fetching category IDs...")
response = requests.get(
    f"{DISCOURSE_URL}/categories.json",
    headers={"Api-Key": config.API_KEY, "Api-Username": config.ADMIN_USERNAME}
)

if response.status_code != 200:
    print("Error fetching categories:", response.text)
    exit(1)

categories = response.json().get("category_list", {}).get("categories", [])

# Normalize category names and store IDs
category_ids = {cat["name"].strip().replace("’", "'"): cat["id"] for cat in categories}

print("Available Categories:")
for name, cid in category_ids.items():
    print(f"- {name} (ID: {cid})")

# List to store post links
post_links = []

# Create topics
for category, title, description in topics:
    category_id = category_ids.get(category)

    if not category_id:
        print(f"Category '{category}' not found, skipping...")
        continue

    print(f"Creating topic: '{title}' in category '{category}' (ID: {category_id})...")

    post_data = {
        "title": title,
        "raw": description,
        "category": category_id
    }

    post_response = requests.post(
        f"{DISCOURSE_URL}/posts.json",
        headers={"Api-Key": config.API_KEY, "Api-Username": config.ADMIN_USERNAME, "Content-Type": "application/json"},
        data=json.dumps(post_data)
    )

    if post_response.status_code != 200:
        print(f"Failed to create topic '{title}':", post_response.text)
    else:
        topic_id = post_response.json().get("topic_id")
        post_url = f"{DISCOURSE_URL}t/{topic_id}"
        post_links.append(post_url)
        print(f"Successfully created: '{title}'")
        print(f"Post URL: {post_url}")

# Print all post links at the end
if post_links:
    print("\nAll Created Post Links:")
    for link in post_links:
        print(link)

print("Bulk topic creation completed!")
