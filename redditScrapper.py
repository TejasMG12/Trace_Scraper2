import praw
import requests
import os
import re
from Secrets import client_id, client_secret, user_agent
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)


def extract_subreddit_links(submission):
    """
    Extracts subreddit mentions from a Reddit submission's title, self-text, and comments.

    Args:
        submission (praw.models.Submission): Reddit submission object.

    Returns:
        list: A list of extracted subreddit links.
    """
    subreddit_links = set()

    # Check for subreddit mentions in the title and self-text
    content = f"{submission.title} {submission.selftext}"
    subreddits = re.findall(r'r/\w+', content)
    subreddit_links.update(
        [f"https://www.reddit.com/{sr}" for sr in subreddits])

    # Fetch and parse comments for subreddit mentions
    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list():
        subreddits = re.findall(r'r/\w+', comment.body)
        subreddit_links.update(
            [f"https://www.reddit.com/{sr}" for sr in subreddits])

    return list(subreddit_links)


def download_media_and_find_subreddits(subreddit_name, limit=10):
    subreddit = reddit.subreddit(subreddit_name)

    # Ensure the media folder exists
    os.makedirs("media_files", exist_ok=True)
    downloaded_files = []

    # Fetch media posts
    for submission in subreddit.hot(limit=limit):  # Adjust the limit as needed
        # Filter for media files
        if submission.url.endswith(('jpg', 'png', 'jpeg', 'mp4', 'webm')):
            media_url = submission.url
            try:
                response = requests.get(
                    media_url, allow_redirects=True, timeout=10)
                response.raise_for_status()

                file_extension = media_url.split(
                    '.')[-1].split('?')[0]  # Handle query strings
                filename = os.path.join(
                    "media_files", f"{submission.id}.{file_extension}")
                with open(filename, 'wb') as file:
                    file.write(response.content)

                downloaded_files.append(filename)
                print(f"Downloaded: {filename}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {media_url}: {e}")
        else:
            print(f"Skipped: {submission.url} (Not a supported media file)")

        # Extract related subreddit links for the current submission
        subreddit_links = extract_subreddit_links(submission)
        if subreddit_links:
            print(f"Subreddit links found for submission '{submission.id}':")
            for link in subreddit_links:
                print(f" - {link}")

    if not downloaded_files:
        print("No media files found.")
    else:
        print(f"Total downloaded files: {len(downloaded_files)}")


# Example usage
download_media_and_find_subreddits(subreddit_name="weed", limit=10)
