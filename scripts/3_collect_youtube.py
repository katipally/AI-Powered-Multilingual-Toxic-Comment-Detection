"""
YouTube Comment Collection Script - QUOTA SAFE (Free Tier)
Collects code-mixed comments from Indian/Bollywood videos

FREE TIER LIMITS:
- 10,000 quota units/day (resets midnight PT)
- commentThreads().list = 1 unit per request (max 100 comments)
- search.list = 100 units per request (EXPENSIVE!)
- videos.list = 1 unit per request
- Safe target: Use ~8,000 units max (buffer for safety)

Author: Person 1 - Data Collection
Date: Oct 2025
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import json
import time
from datetime import datetime
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Get project root directory (works from anywhere)
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / '.env'
OUTPUT_DIR = PROJECT_ROOT / 'Input' / 'youtube'

# Configuration
TARGET_COUNT = 10000
MAX_QUOTA_USAGE = 7500  # Stay well under 10k limit (safety buffer)
COMMENTS_PER_VIDEO = 500  # Fetch max 500 comments per video (quota safe)

# Manually add video IDs here (RECOMMENDED - no quota cost for getting IDs manually!)
# Find popular videos on YouTube and copy their IDs from the URL
# URL format: youtube.com/watch?v=VIDEO_ID
VIDEO_IDS = [
    # Add video IDs manually for quota efficiency
    # Example format:
    # 'dQw4w9WgXcQ',  # Video description
]

# Alternatively, search queries to find videos (WARNING: Uses 100 quota per search!)
SEARCH_QUERIES = [
    'bollywood trailer 2025 hindi',
    'IPL highlights 2025',
    'indian gaming hindi',
    'bollywood songs new',
]

# ============================================================================
# SETUP & INITIALIZATION
# ============================================================================

print("=" * 80)
print("YOUTUBE COMMENT COLLECTION - QUOTA SAFE (FREE TIER)")
print("=" * 80)
print(f"\nTarget: {TARGET_COUNT:,} comments")
print(f"Max Quota Usage: {MAX_QUOTA_USAGE:,} / 10,000 units (daily limit)")
print(f"Project Root: {PROJECT_ROOT}")
print()

# Load environment variables
if not ENV_FILE.exists():
    print(f"❌ ERROR: .env file not found at {ENV_FILE}")
    print("\nAdd to your .env file:")
    print("  YOUTUBE_API_KEY=your_youtube_api_key_here")
    print("\nGet API key from: https://console.cloud.google.com/")
    sys.exit(1)

load_dotenv(ENV_FILE)
print(f"✓ Loaded credentials from {ENV_FILE}")

# Get API key from environment
api_key = os.getenv('YOUTUBE_API_KEY')

if not api_key or api_key == 'YOUR_YOUTUBE_API_KEY_HERE':
    print("❌ ERROR: YOUTUBE_API_KEY not set or still has placeholder value!")
    print("\nEdit .env and replace with your actual API key:")
    print("  YOUTUBE_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    print("\nGet API key from:")
    print("  1. Go to https://console.cloud.google.com/")
    print("  2. Select your project")
    print("  3. APIs & Services → Credentials")
    print("  4. Create credentials → API key")
    sys.exit(1)

print(f"✓ API key validated ({api_key[:8]}...{api_key[-4:]})")

# Initialize YouTube API
try:
    youtube = build('youtube', 'v3', developerKey=api_key)
    print(f"✓ YouTube API initialized")
except Exception as e:
    print(f"❌ ERROR initializing YouTube API: {e}")
    sys.exit(1)

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
print(f"✓ Output directory: {OUTPUT_DIR}")

# ============================================================================
# VIDEO DISCOVERY (if needed)
# ============================================================================

quota_used = 0

# If no manual video IDs, search for videos (QUOTA EXPENSIVE!)
if len(VIDEO_IDS) == 0:
    print("\n" + "=" * 80)
    print("VIDEO DISCOVERY (Using Search API - QUOTA EXPENSIVE!)")
    print("=" * 80)
    print(f"⚠️  WARNING: Each search costs 100 quota units!")
    print(f"⚠️  Searching for {len(SEARCH_QUERIES)} queries = {len(SEARCH_QUERIES) * 100} units")
    print()
    
    user_input = input("Continue with search? (y/n): ").lower()
    if user_input != 'y':
        print("\n💡 TIP: Add video IDs manually to VIDEO_IDS list to avoid quota cost!")
        print("   1. Search YouTube for popular Indian content")
        print("   2. Copy video IDs from URLs")
        print("   3. Add to VIDEO_IDS list in this script")
        sys.exit(0)
    
    print("\nSearching for videos...")
    discovered_videos = []
    
    for query in SEARCH_QUERIES:
        try:
            search_response = youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=10,
                type='video',
                relevanceLanguage='hi',  # Hindi language
                order='viewCount'
            ).execute()
            
            quota_used += 100  # search.list costs 100 units
            
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                discovered_videos.append((video_id, title))
                print(f"  ✓ Found: {video_id} - {title[:50]}...")
            
            time.sleep(1)  # Rate limiting
            
        except HttpError as e:
            print(f"  ❌ Search error: {e}")
            continue
    
    VIDEO_IDS = [vid for vid, _ in discovered_videos]
    print(f"\n✓ Discovered {len(VIDEO_IDS)} videos (Used {quota_used} quota)")

if len(VIDEO_IDS) == 0:
    print("\n❌ ERROR: No video IDs available!")
    print("\nAdd video IDs manually to VIDEO_IDS list in the script.")
    sys.exit(1)

# Save video IDs for reference
video_ids_file = OUTPUT_DIR / 'video_ids.txt'
with open(video_ids_file, 'w') as f:
    for vid in VIDEO_IDS:
        f.write(f"https://youtube.com/watch?v={vid}\n")

print(f"\n✓ Video IDs saved to: {video_ids_file}")
print(f"✓ Total videos to process: {len(VIDEO_IDS)}")

# ============================================================================
# COMMENT COLLECTION
# ============================================================================

collected_comments = []
start_time = time.time()

print("\n" + "=" * 80)
print("STARTING COMMENT COLLECTION")
print("=" * 80)
print(f"⚠️  Quota used so far: {quota_used:,} / 10,000")
print(f"⚠️  Quota available: {10000 - quota_used:,}")
print()

for idx, video_id in enumerate(VIDEO_IDS, 1):
    # Check quota limit before processing
    if quota_used >= MAX_QUOTA_USAGE:
        print(f"\n⚠️  Reached quota safety limit ({MAX_QUOTA_USAGE:,} units)")
        print(f"Stopping collection to stay within free tier.")
        break
    
    print(f"[{idx}/{len(VIDEO_IDS)}] Video: {video_id}")
    print(f"    URL: https://youtube.com/watch?v={video_id}")
    
    try:
        # Get video metadata
        try:
            video_response = youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()
            
            quota_used += 1  # videos.list costs 1 unit
            
            if video_response['items']:
                video_info = video_response['items'][0]
                video_title = video_info['snippet']['title']
                video_stats = video_info.get('statistics', {})
                comment_count = int(video_stats.get('commentCount', 0))
                
                print(f"    Title: {video_title[:60]}...")
                print(f"    Comments available: {comment_count:,}")
            else:
                print(f"    ⚠️  Video not found or unavailable")
                continue
                
        except Exception as e:
            print(f"    ⚠️  Could not get video info: {e}")
            video_title = "Unknown"
            comment_count = 0
        
        # Collect comments
        comments_from_video = 0
        next_page_token = None
        pages_fetched = 0
        max_pages = (COMMENTS_PER_VIDEO // 100) + 1  # Each page = 100 comments
        
        while pages_fetched < max_pages:
            try:
                # Get comment threads
                request = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=100,  # Max per request
                    pageToken=next_page_token,
                    textFormat='plainText',
                    order='relevance'
                )
                
                response = request.execute()
                quota_used += 1  # commentThreads.list costs 1 unit
                pages_fetched += 1
                
                # Extract comments
                for item in response['items']:
                    comment_data = item['snippet']['topLevelComment']['snippet']
                    
                    # Skip very short comments
                    if len(comment_data['textDisplay']) < 10:
                        continue
                    
                    collected_comments.append({
                        'id': item['id'],
                        'video_id': video_id,
                        'video_title': video_title,
                        'text': comment_data['textDisplay'],
                        'author': comment_data['authorDisplayName'],
                        'likes': comment_data['likeCount'],
                        'published_at': comment_data['publishedAt'],
                        'video_url': f"https://youtube.com/watch?v={video_id}",
                    })
                    
                    comments_from_video += 1
                
                # Check for more pages
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                # Safety checks
                if len(collected_comments) >= TARGET_COUNT:
                    break
                if quota_used >= MAX_QUOTA_USAGE:
                    break
                
                time.sleep(0.5)  # Rate limiting
                
            except HttpError as e:
                error_str = str(e)
                if 'commentsDisabled' in error_str:
                    print(f"    ⚠️  Comments disabled")
                elif 'quotaExceeded' in error_str:
                    print(f"\n❌ QUOTA EXCEEDED! Used {quota_used:,} units")
                    print(f"Collected {len(collected_comments):,} comments before limit.")
                    break
                else:
                    print(f"    ⚠️  HTTP Error: {e}")
                break
            
            except Exception as e:
                print(f"    ⚠️  Error: {e}")
                break
        
        # Progress update
        elapsed = time.time() - start_time
        rate = len(collected_comments) / (elapsed / 60) if elapsed > 0 else 0
        
        print(f"    ✓ +{comments_from_video} comments from this video")
        print(f"    → Total: {len(collected_comments):,} | Quota: {quota_used:,}/10,000 | Rate: {rate:.1f}/min")
        
        if len(collected_comments) >= TARGET_COUNT:
            print(f"\n✓ TARGET REACHED! ({len(collected_comments):,} comments)")
            break
        
        time.sleep(1)  # Delay between videos
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        continue

# ============================================================================
# SAVE DATA
# ============================================================================

print("\n" + "=" * 80)
print("SAVING DATA")
print("=" * 80)

if len(collected_comments) == 0:
    print("❌ ERROR: No comments collected!")
    print("\nPossible issues:")
    print("  1. Videos have comments disabled")
    print("  2. API key invalid or restricted")
    print("  3. Quota exceeded")
    print("  4. Video IDs are invalid")
    sys.exit(1)

# Save as CSV
df = pd.DataFrame(collected_comments)
output_file = OUTPUT_DIR / 'raw_comments.csv'
df.to_csv(output_file, index=False, encoding='utf-8')

# Save collection metadata
metadata = {
    'collection_date': datetime.now().isoformat(),
    'target_count': TARGET_COUNT,
    'actual_count': len(collected_comments),
    'videos_processed': idx,
    'videos_total': len(VIDEO_IDS),
    'quota_used': quota_used,
    'quota_limit': 10000,
    'time_taken_seconds': int(time.time() - start_time),
}

manifest_file = OUTPUT_DIR / 'manifest.json'
with open(manifest_file, 'w') as f:
    json.dump(metadata, f, indent=2)

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("COLLECTION COMPLETE!")
print("=" * 80)

total_time = time.time() - start_time
print(f"\nStatistics:")
print(f"  Total comments collected:  {len(collected_comments):,}")
print(f"  Videos processed:          {idx} / {len(VIDEO_IDS)}")
print(f"  Time taken:                {total_time / 60:.1f} minutes")
print(f"  Average rate:              {len(collected_comments) / (total_time / 60):.1f} comments/min")

print(f"\nQuota Usage:")
print(f"  Total quota used:          {quota_used:,} / 10,000 units")
print(f"  Remaining today:           {10000 - quota_used:,} units")
print(f"  Percentage used:           {(quota_used / 10000) * 100:.1f}%")
print(f"  ✓ Stayed within free tier: {'YES' if quota_used < 10000 else 'NO'}")

if len(collected_comments) > 0:
    print(f"\nTop videos by comment count:")
    video_counts = df['video_id'].value_counts()
    for vid, count in video_counts.head(5).items():
        title = df[df['video_id'] == vid].iloc[0]['video_title']
        print(f"  {count:4,} comments - {title[:50]}...")

print(f"\nFiles saved:")
print(f"  {output_file}")
print(f"  {manifest_file}")
print(f"  {video_ids_file}")

print(f"\nCheck quota usage at:")
print(f"  https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas")

print("\n✓ YouTube collection complete!")
print("\nNext steps:")
print("  1. Check data: pandas.read_csv('Input/youtube/raw_comments.csv')")
print("  2. Look for code-mixed content (Hindi+English)")
print("  3. Create data card documentation")
