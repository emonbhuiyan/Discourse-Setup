import requests
import json
from urllib.parse import urljoin
import re
import config
from config import CATEGORIES

HEADERS = {
    "Api-Key": config.API_KEY,
    "Api-Username": config.ADMIN_USERNAME,
    "Content-Type": "application/json"
}

def create_category(name, description):
    """Creates a category in Discourse"""
    print(f"Creating category: {name}")
    data = {
        "name": name,
        "description": description,
        "color": "0088CC",  # Blue color
        "text_color": "FFFFFF"  # White text
    }
    response = requests.post(f"{config.DISCOURSE_URL}/categories.json", headers=HEADERS, json=data)
    print("Response:", response.json())


def fetch_category_id(name):
    """Fetches the category ID by name"""
    response = requests.get(f"{config.DISCOURSE_URL}/categories.json", headers=HEADERS)
    categories = response.json().get("category_list", {}).get("categories", [])
    
    for category in categories:
        if category["name"] == name:
            return category["id"]
    return None


def fetch_about_topic_id(category_id):
    """Fetches the 'About this category' topic ID"""
    response = requests.get(f"{config.DISCOURSE_URL}/c/{category_id}/show.json", headers=HEADERS)
    topic_url = response.json().get("category", {}).get("topic_url")
    
    if topic_url:
        match = re.search(r"(\d+)$", topic_url)
        return int(match.group(1)) if match else None
    return None


def fetch_first_post_id(topic_id):
    """Fetches the first post ID of a topic"""
    response = requests.get(f"{config.DISCOURSE_URL}/t/{topic_id}/posts.json", headers=HEADERS)
    posts = response.json().get("post_stream", {}).get("posts", [])
    
    return posts[0]["id"] if posts else None


def update_about_category_content(post_id, content, title):
    """Updates the content and title of the first post in the 'About this category' topic"""
    print(f"Updating Post ID {post_id} with new content and title: {title}")
    data = {"post": {"raw": content, "title": title}}
    
    response = requests.put(f"{config.DISCOURSE_URL}/posts/{post_id}.json", headers=HEADERS, json=data)
    print("Updated content response:", response.json())


def rename_about_topics():
    """Renames 'About this category' topics by removing 'About'"""
    response = requests.get(f"{config.DISCOURSE_URL}/categories.json", headers=HEADERS)
    categories = response.json().get("category_list", {}).get("categories", [])

    for category in categories:
        category_id = category["id"]
        category_name = category["name"]

        topic_id = fetch_about_topic_id(category_id)
        if not topic_id:
            print(f"No 'About this category' topic found for '{category_name}'. Skipping...")
            continue

        topic_response = requests.get(f"{config.DISCOURSE_URL}/t/{topic_id}.json", headers=HEADERS)
        current_title = topic_response.json().get("title", "")

        match = re.match(r"About the (.*) category", current_title)
        if match:
            new_title = match.group(1)
            print(f"Renaming '{current_title}' -> '{new_title}'")

            data = {"title": new_title}
            response = requests.put(f"{config.DISCOURSE_URL}/t/{topic_id}.json", headers=HEADERS, json=data)
            print("Updated title response:", response.json())
        else:
            print(f"Title '{current_title}' does not match expected pattern. Skipping...")


# Main Execution
if __name__ == "__main__":
    # Step 1: Create Categories
    for name, description in CATEGORIES.items():
        create_category(name, description)

    # Step 2: Update 'About this category' topics
    for name, description in CATEGORIES.items():
        category_id = fetch_category_id(name)
        if not category_id:
            print(f"Category '{name}' not found! Skipping...")
            continue

        topic_id = fetch_about_topic_id(category_id)
        if not topic_id:
            print(f"No 'About this category' topic exists for '{name}'. Skipping...")
            continue

        post_id = fetch_first_post_id(topic_id)
        if not post_id:
            print(f"Failed to fetch first post ID for topic {topic_id}. Skipping...")
            continue

        update_about_category_content(post_id, description, name)

    # Step 3: Rename 'About this category' topics
    rename_about_topics()

    print("All tasks completed!")
