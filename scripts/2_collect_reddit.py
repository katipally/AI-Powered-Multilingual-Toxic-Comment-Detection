"""
Optimized Reddit Comment Collection Script for Code-Mixed Toxic Comment Detection
Uses PRAW with proper rate limiting (100 QPM averaged over 10 min window)
Collects diverse, code-mixed comments from Indian subreddits

Author: Person 1 - Data Collection Team
Date: Oct 2025
"""

import praw
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
OUTPUT_DIR = PROJECT_ROOT / 'Input' / 'reddit'

# Configuration
TARGET_COUNT = 10000

# Expanded list of Indian subreddits for better code-mixed content
SUBREDDITS = [
    # Main Indian subreddits
    'india', 'IndiaSpeaks', 'IndianDankMemes',
    # Entertainment
    'bollywood', 'BollyBlindsNGossip', 'IndianCinema',
    # Gaming & Tech
    'IndianGaming', 'IndiaGaming', 'IndianGames',
    # Sports
    'Cricket', 'CricketShitpost',
    # Cities (high code-mixing)
    'mumbai', 'delhi', 'bangalore', 'hyderabad', 'Chennai', 'pune', 'kolkata', 'Ahmedabad',
    # Casual/Meme subreddits (lots of code-mixing)
    'bakchodi', 'Chodi', 'desimemes',
    # Other
    'IndianFood', 'IndianStreetBets', 'IndianFootball'
]

# ============================================================================
# SETUP & INITIALIZATION
# ============================================================================

print("=" * 80)
print("REDDIT COMMENT COLLECTION - OPTIMIZED FOR CODE-MIXED CONTENT")
print("=" * 80)
print(f"\nTarget: {TARGET_COUNT:,} comments")
print(f"Subreddits: {len(SUBREDDITS)}")
print(f"Rate Limit: 100 QPM (averaged over 10 min window)")
print(f"Project Root: {PROJECT_ROOT}")
print()

# Load environment variables from .env file
if not ENV_FILE.exists():
    print(f"❌ ERROR: .env file not found at {ENV_FILE}")
    print("\nCreate a .env file in the project root with:")
    print("  REDDIT_CLIENT_ID=your_client_id")
    print("  REDDIT_CLIENT_SECRET=your_client_secret")
    print("  REDDIT_USER_AGENT=your_user_agent")
    sys.exit(1)

load_dotenv(ENV_FILE)
print(f"✓ Loaded credentials from {ENV_FILE}")

# Get credentials from environment
client_id = os.getenv('REDDIT_CLIENT_ID')
client_secret = os.getenv('REDDIT_CLIENT_SECRET')
user_agent = os.getenv('REDDIT_USER_AGENT')

# Validate credentials
if not all([client_id, client_secret, user_agent]):
    print("❌ ERROR: Missing Reddit credentials in .env file!")
    print("\nRequired variables:")
    print(f"  REDDIT_CLIENT_ID: {'✓' if client_id else '❌'}")
    print(f"  REDDIT_CLIENT_SECRET: {'✓' if client_secret else '❌'}")
    print(f"  REDDIT_USER_AGENT: {'✓' if user_agent else '❌'}")
    sys.exit(1)

print(f"✓ Credentials validated (Client ID: {client_id[:10]}...)")

# Initialize Reddit API
try:
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        check_for_async=False  # Disable async warnings
    )
    # Test authentication
    reddit.user.me()
    print(f"✓ Reddit API initialized (read-only mode)")
except Exception as e:
    print(f"❌ ERROR connecting to Reddit: {e}")
    print("\nTroubleshooting:")
    print("  1. Check your client_id and client_secret are correct")
    print("  2. Make sure your Reddit app type is 'script'")
    print("  3. Check https://www.reddit.com/prefs/apps")
    sys.exit(1)

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
print(f"✓ Output directory: {OUTPUT_DIR}")

# ============================================================================
# COLLECTION
# ============================================================================

collected_comments = []
request_count = 0
start_time = time.time()
last_progress_time = start_time

print("\n" + "-" * 80)
print("Starting collection... (Estimated time: 2-3 hours due to rate limits)")
print("-" * 80 + "\n")

for idx, subreddit_name in enumerate(SUBREDDITS, 1):
    print(f"[{idx}/{len(SUBREDDITS)}] r/{subreddit_name}...")
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        # Collect from multiple sources for diversity
        posts_to_process = []
        
        # Hot posts (trending now)
        try:
            posts_to_process.extend(list(subreddit.hot(limit=20)))
            request_count += 1
        except Exception as e:
            print(f"    ⚠ Could not get hot posts: {e}")
        
        # New posts (recent content)
        try:
            posts_to_process.extend(list(subreddit.new(limit=20)))
            request_count += 1
        except Exception as e:
            print(f"    ⚠ Could not get new posts: {e}")
        
        # Top posts from this week (quality content)
        try:
            posts_to_process.extend(list(subreddit.top(time_filter='week', limit=15)))
            request_count += 1
        except Exception as e:
            print(f"    ⚠ Could not get top posts: {e}")
        
        comments_from_subreddit = 0
        
        for submission in posts_to_process:
            try:
                # Replace "load more comments" with actual comments (limited to save time)
                submission.comments.replace_more(limit=2)
                request_count += 1
                
                # Process all top-level comments and replies
                for comment in submission.comments.list()[:150]:  # Max 150 per post
                    try:
                        # Skip deleted/removed comments
                        if comment.body in ['[deleted]', '[removed]', '']:
                            continue
                        
                        # Skip very short comments (likely not useful)
                        if len(comment.body.strip()) < 10:
                            continue
                        
                        # Skip AutoModerator and bot comments
                        if hasattr(comment, 'author') and comment.author:
                            author_name = str(comment.author).lower()
                            if 'bot' in author_name or 'automoderator' in author_name:
                                continue
                        
                        # Store comment with all relevant metadata
                        collected_comments.append({
                            'id': comment.id,
                            'subreddit': subreddit_name,
                            'text': comment.body,
                            'score': comment.score,
                            'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat(),
                            'post_id': submission.id,
                            'post_title': submission.title,
                            'post_url': f"https://reddit.com{submission.permalink}",
                            'comment_depth': comment.depth,  # 0 = top-level, 1+ = replies
                            'is_submitter': comment.is_submitter,  # Is this the post author?
                        })
                        
                        comments_from_subreddit += 1
                        
                        if len(collected_comments) >= TARGET_COUNT:
                            break
                    
                    except AttributeError:
                        # Some comments might be MoreComments objects
                        continue
                    except Exception as e:
                        # Skip problematic comments
                        continue
                
                if len(collected_comments) >= TARGET_COUNT:
                    break
                
                # Rate limiting: Sleep to stay under 100 QPM (averaged over 10 min)
                # Conservative: 1 request per second = 60 per minute
                time.sleep(1.0)
                
            except Exception as e:
                # Skip problematic posts
                continue
        
        # Progress update
        elapsed = time.time() - start_time
        rate = len(collected_comments) / (elapsed / 60) if elapsed > 0 else 0
        estimated_remaining = ((TARGET_COUNT - len(collected_comments)) / rate) if rate > 0 else 0
        
        print(f"    ✓ +{comments_from_subreddit} comments → Total: {len(collected_comments):,} " +
              f"({rate:.1f}/min, ~{estimated_remaining:.0f}min remaining)")
        
        if len(collected_comments) >= TARGET_COUNT:
            print(f"\n✓ TARGET REACHED! Collected {len(collected_comments):,} comments")
            break
        
        # Small delay between subreddits
        time.sleep(2)
        
    except Exception as e:
        print(f"    ❌ Error with r/{subreddit_name}: {e}")
        continue

# ============================================================================
# SAVE DATA
# ============================================================================

print("\n" + "-" * 80)
print("Saving data...")
print("-" * 80)

if len(collected_comments) == 0:
    print("❌ ERROR: No comments collected!")
    print("\nPossible issues:")
    print("  1. API credentials invalid")
    print("  2. Subreddits are private/banned")
    print("  3. Rate limiting too aggressive")
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
    'subreddits': SUBREDDITS,
    'subreddits_processed': idx,
    'time_taken_seconds': int(time.time() - start_time),
    'api_requests_approx': request_count,
    'rate_limit_compliant': True,
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
print(f"  Time taken:                {total_time / 60:.1f} minutes ({total_time / 3600:.2f} hours)")
print(f"  Average rate:              {len(collected_comments) / (total_time / 60):.1f} comments/min")
print(f"  API requests (approx):     {request_count:,}")
print(f"  Subreddits processed:      {idx} / {len(SUBREDDITS)}")

print(f"\nSubreddit breakdown (top 10):")
subreddit_counts = df['subreddit'].value_counts()
for sub, count in subreddit_counts.head(10).items():
    percentage = (count / len(df)) * 100
    print(f"  r/{sub:20s}: {count:5,} comments ({percentage:5.1f}%)")

print(f"\nComment depth distribution:")
if 'comment_depth' in df.columns:
    depth_counts = df['comment_depth'].value_counts().sort_index()
    for depth, count in depth_counts.head(5).items():
        print(f"  Depth {depth}: {count:,} comments")

print(f"\nScore statistics:")
print(f"  Mean score:   {df['score'].mean():.1f}")
print(f"  Median score: {df['score'].median():.1f}")
print(f"  Max score:    {df['score'].max()}")
print(f"  Min score:    {df['score'].min()}")

print(f"\nFiles saved:")
print(f"  {output_file}")
print(f"  {manifest_file}")

print("\n✓ Reddit collection complete!")
print("\nNext steps:")
print("  1. Check the data: pandas.read_csv('../Input/reddit/raw_comments.csv')")
print("  2. Look for code-mixed content (Hindi+English, etc.)")
print("  3. Move on to YouTube collection (run 3_collect_youtube.py)")