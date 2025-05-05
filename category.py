import requests
import json
from urllib.parse import urljoin
import re
import config
from config import CATEGORIES

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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

# For storing results to display at the end
results = {
    "categories_created": [],
    "categories_updated": [],
    "topics_renamed": [],
    "errors": []
}

def create_category(name, description):
    """Creates a category in Discourse"""
    print(f"✨ Creating category: {name}")
    data = {
        "name": name,
        "description": description,
        "color": "0088CC",  # Blue color
        "text_color": "FFFFFF"  # White text
    }
    response = requests.post(f"{DISCOURSE_URL}/categories.json", headers=HEADERS, json=data)
    result = response.json()
    
    if "category" in result:
        results["categories_created"].append({"name": name, "success": True})
    else:
        results["categories_created"].append({"name": name, "success": False})
        results["errors"].append(f"Failed to create category '{name}': {result}")


def fetch_category_id(name):
    """Fetches the category ID by name"""
    response = requests.get(f"{DISCOURSE_URL}/categories.json", headers=HEADERS)
    categories = response.json().get("category_list", {}).get("categories", [])

    for category in categories:
        if category["name"] == name:
            return category["id"]
    return None


def fetch_about_topic_id(category_id):
    """Fetches the 'About this category' topic ID"""
    response = requests.get(f"{DISCOURSE_URL}/c/{category_id}/show.json", headers=HEADERS)
    topic_url = response.json().get("category", {}).get("topic_url")

    if topic_url:
        match = re.search(r"(\d+)$", topic_url)
        return int(match.group(1)) if match else None
    return None


def fetch_first_post_id(topic_id):
    """Fetches the first post ID of a topic"""
    response = requests.get(f"{DISCOURSE_URL}/t/{topic_id}/posts.json", headers=HEADERS)
    posts = response.json().get("post_stream", {}).get("posts", [])

    return posts[0]["id"] if posts else None


def update_about_category_content(post_id, content, title):
    """Updates the content and title of the first post in the 'About this category' topic"""
    print(f"🔄 Updating Post ID {post_id} with new content and title: {title}")
    data = {"post": {"raw": content, "title": title}}

    response = requests.put(f"{DISCOURSE_URL}/posts/{post_id}.json", headers=HEADERS, json=data)
    result = response.json()
    
    if "post" in result:
        results["categories_updated"].append({"title": title, "success": True})
    else:
        results["categories_updated"].append({"title": title, "success": False})
        results["errors"].append(f"Failed to update post '{title}': {result}")


def rename_about_topics():
    """Renames 'About this category' topics by removing 'About'"""
    response = requests.get(f"{DISCOURSE_URL}/categories.json", headers=HEADERS)
    categories = response.json().get("category_list", {}).get("categories", [])

    for category in categories:
        category_id = category["id"]
        category_name = category["name"]

        topic_id = fetch_about_topic_id(category_id)
        if not topic_id:
            print(f"⏭️ No 'About this category' topic found for '{category_name}'. Skipping...")
            continue

        topic_response = requests.get(f"{DISCOURSE_URL}/t/{topic_id}.json", headers=HEADERS)
        current_title = topic_response.json().get("title", "")

        # Match both "About the X category" and "About this X category" patterns
        match = re.match(r"About (?:the|this) (.*) category", current_title)
        if match:
            new_title = match.group(1)
            print(f"🔄 Renaming '{current_title}' -> '{new_title}'")

            data = {"title": new_title}
            response = requests.put(f"{DISCOURSE_URL}/t/{topic_id}.json", headers=HEADERS, json=data)
            result = response.json()
            
            if "basic_topic" in result:
                results["topics_renamed"].append({"old": current_title, "new": new_title, "success": True})
            else:
                results["topics_renamed"].append({"old": current_title, "new": new_title, "success": False})
                results["errors"].append(f"Failed to rename topic '{current_title}': {result}")
        else:
            print(f"Title '{current_title}' does not match expected pattern. Skipping...")

def print_summary():
    """Prints a well-formatted summary of all operations performed"""
    print("\n" + "="*80)
    print(f"{'📊 EXECUTION SUMMARY':^80}")
    print("="*80)
    
    # Site Information
    print(f"\n📡 SITE CONFIGURATION:")
    print(f"  • Site URL:         {SITE_URL}")
    print(f"  • Discourse URL:    {DISCOURSE_URL}")
    print(f"  • Site Title:       {SITE_TITLE}")
    print(f"  • Occupation:       {config.OCCUPATION}")
    
    # Categories Created
    print(f"\n✨ CATEGORIES CREATED: {len(results['categories_created'])}")
    for idx, item in enumerate(results['categories_created'], 1):
        status = "✅" if item["success"] else "❌"
        print(f"  {idx}. {status} {item['name']}")
    
    # Categories Updated
    print(f"\n🔄 CATEGORIES UPDATED: {len(results['categories_updated'])}")
    for idx, item in enumerate(results['categories_updated'], 1):
        status = "✅" if item["success"] else "❌"
        print(f"  {idx}. {status} {item['title']}")
    
    # Topics Renamed
    print(f"\n📝 TOPICS RENAMED: {len(results['topics_renamed'])}")
    for idx, item in enumerate(results['topics_renamed'], 1):
        status = "✅" if item["success"] else "❌"
        print(f"  {idx}. {status} '{item['old']}' → '{item['new']}'")
    
    # Errors (if any)
    if results["errors"]:
        print(f"\n⚠️ ERRORS: {len(results['errors'])}")
        for idx, error in enumerate(results["errors"], 1):
            print(f"  {idx}. {error}")
    else:
        print(f"\n✅ NO ERRORS REPORTED")
    
    print("\n" + "="*80)
    print(f"{'🎉 ALL TASKS COMPLETED':^80}")
    print("="*80)


# Main Execution
if __name__ == "__main__":
    print("\n" + "="*80)
    print(f"{'🚀 STARTING DISCOURSE CATEGORY SETUP':^80}")
    print("="*80)
    
    # Step 1: Create Categories
    print("\n📂 STEP 1: CREATING CATEGORIES")
    for name, description in CATEGORIES.items():
        create_category(name, description)

    # Step 2: Update 'About this category' topics
    print("\n📝 STEP 2: UPDATING CATEGORY DESCRIPTIONS")
    for name, description in CATEGORIES.items():
        category_id = fetch_category_id(name)
        if not category_id:
            print(f"⏭️ Category '{name}' not found! Skipping...")
            results["errors"].append(f"Category '{name}' not found")
            continue

        topic_id = fetch_about_topic_id(category_id)
        if not topic_id:
            print(f"⏭️ No 'About this category' topic exists for '{name}'. Skipping...")
            results["errors"].append(f"No 'About this category' topic for '{name}'")
            continue

        post_id = fetch_first_post_id(topic_id)
        if not post_id:
            print(f"⏭️ Failed to fetch first post ID for topic {topic_id}. Skipping...")
            results["errors"].append(f"Failed to fetch first post ID for '{name}'")
            continue

        update_about_category_content(post_id, description, name)

    # Step 3: Rename 'About this category' topics
    print("\n✂️ STEP 3: RENAMING 'ABOUT THIS CATEGORY' TOPICS")
    rename_about_topics()

    # Print summary of all operations
    print_summary()
