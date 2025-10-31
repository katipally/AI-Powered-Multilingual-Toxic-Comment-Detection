"""
Helper script to find popular YouTube video IDs
Uses YouTube API to search for Indian/Bollywood/Cricket videos

This helps you find video IDs to add to 3_collect_youtube.py
without manually searching YouTube!

Usage: python find_youtube_videos.py
"""

from googleapiclient.discovery import build
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# Setup
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / '.env'

# Search queries (modify these!)
SEARCH_QUERIES = [
    'bollywood trailer 2025 hindi',
    'IPL cricket highlights 2025',
    'indian gaming valorant',
    'bollywood new songs 2025',
    'india vs pakistan cricket',
    'carry minati new video',
    'total gaming',
    'indian street food',
]

print("=" * 70)
print("YOUTUBE VIDEO ID FINDER")
print("=" * 70)
print(f"\nThis will search for {len(SEARCH_QUERIES)} queries")
print(f"Cost: {len(SEARCH_QUERIES) * 100} quota units (out of 10,000/day)\n")

# Load API key
load_dotenv(ENV_FILE)
api_key = os.getenv('YOUTUBE_API_KEY')

if not api_key or api_key == 'YOUR_YOUTUBE_API_KEY_HERE':
    print("❌ ERROR: YOUTUBE_API_KEY not set in .env")
    sys.exit(1)

# Initialize
youtube = build('youtube', 'v3', developerKey=api_key)
print("✓ YouTube API initialized\n")

# Search
print("Searching for popular videos...\n")

all_videos = []
for idx, query in enumerate(SEARCH_QUERIES, 1):
    print(f"[{idx}/{len(SEARCH_QUERIES)}] Searching: {query}")
    
    try:
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=10,
            type='video',
            relevanceLanguage='hi',
            order='viewCount'
        ).execute()
        
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            channel = item['snippet']['channelTitle']
            all_videos.append((video_id, title, channel))
            print(f"    ✓ {video_id} - {title[:50]}...")
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
    
    print()

# Save results
output_file = PROJECT_ROOT / 'found_video_ids.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# YouTube Video IDs found by find_youtube_videos.py\n")
    f.write(f"# Generated: {__import__('datetime').datetime.now()}\n")
    f.write(f"# Total videos: {len(all_videos)}\n\n")
    
    for video_id, title, channel in all_videos:
        f.write(f"'{video_id}',  # {title[:50]} - {channel}\n")

print("=" * 70)
print(f"✓ Found {len(all_videos)} videos")
print(f"✓ Saved to: {output_file}")
print("=" * 70)
print("\nNext steps:")
print("  1. Open found_video_ids.txt")
print("  2. Copy video IDs you want")
print("  3. Paste into VIDEO_IDS list in scripts/3_collect_youtube.py")
print("  4. Run: python scripts/3_collect_youtube.py")
