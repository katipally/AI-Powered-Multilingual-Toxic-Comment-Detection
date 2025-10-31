"""
Script to set up the folder structure for Person 1 data collection

This creates all the folders you'll need and templates for credential files.

Author: Person 1 - Data Collection
"""

import os

# Folder structure
folders = [
    '../Input/hatexplain',
    '../Input/reddit',
    '../Input/youtube',
    '../Input/processed',  # For cleaned/processed data later
    '../scripts',  # For your scripts
    '../Documents',  # For documentation
]

print("=" * 70)
print("SETTING UP FOLDER STRUCTURE")
print("=" * 70)
print()

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"✓ Created: {folder}")

print()
print("-" * 70)
print("Creating credential templates...")
print("-" * 70)
print()

# Reddit credentials template
reddit_creds_template = """{
    "client_id": "PASTE_YOUR_CLIENT_ID_HERE",
    "client_secret": "PASTE_YOUR_CLIENT_SECRET_HERE",
    "user_agent": "toxic_comment_research_v1.0"
}
"""

with open('reddit_credentials.json.template', 'w') as f:
    f.write(reddit_creds_template)
print("✓ Created: reddit_credentials.json.template")
print("  → Copy this to reddit_credentials.json and fill in your credentials")

# YouTube credentials template
youtube_creds_template = """{
    "api_key": "PASTE_YOUR_YOUTUBE_API_KEY_HERE"
}
"""

with open('youtube_credentials.json.template', 'w') as f:
    f.write(youtube_creds_template)
print("✓ Created: youtube_credentials.json.template")
print("  → Copy this to youtube_credentials.json and fill in your API key")

# Create .gitignore to avoid committing secrets
gitignore_content = """# Credentials - NEVER commit these!
reddit_credentials.json
youtube_credentials.json
*_credentials.json
*.env

# API keys
api_keys.txt
secrets.txt

# Large data files
*.zip
*.csv
*.jsonl

# Python
__pycache__/
*.pyc
*.pyo
.ipynb_checkpoints/
"""

with open('../.gitignore', 'w') as f:
    f.write(gitignore_content)
print("✓ Created: .gitignore")

print()
print("=" * 70)
print("SETUP COMPLETE!")
print("=" * 70)
print()
print("Folder structure created:")
for folder in folders:
    print(f"  {folder}/")

print()
print("Next steps:")
print("  1. Copy credential templates and fill in your API keys")
print("  2. Run: python 1_download_hatexplain.py")
print("  3. Run: python 2_collect_reddit.py")
print("  4. Run: python 3_collect_youtube.py")
print()
print("For detailed instructions, see:")
print("  PERSON1_DATA_COLLECTION_GUIDE.md")
