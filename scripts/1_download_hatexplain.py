"""
Script to download HateXplain dataset from GitHub (Original Source)
Updated Oct 2025 - Downloads directly from GitHub since HF deprecated dataset scripts

Prerequisites:
    pip install pandas requests

Dataset Info:
    - Original Paper: HateXplain: A Benchmark Dataset for Explainable Hate Speech Detection
    - Source: https://github.com/hate-alert/HateXplain
    - Size: ~20,000 posts with rationales from Gab and Twitter

Author: Person 1 - Data Collection
"""

import os
import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
import requests

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'Input' / 'hatexplain'

print("=" * 80)
print("HATEXPLAIN DATASET DOWNLOAD")
print("=" * 80)
print(f"\nDataset: HateXplain (Hate Speech with Rationales)")
print(f"Source: GitHub (hate-alert/HateXplain)")
print(f"Output: {OUTPUT_DIR}")
print()

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
print(f"✓ Output directory created: {OUTPUT_DIR}")

# GitHub raw URLs for the dataset files
BASE_URL = "https://raw.githubusercontent.com/hate-alert/HateXplain/master/Data"
DATASET_URL = f"{BASE_URL}/dataset.json"
POST_ID_DIVISIONS_URL = f"{BASE_URL}/post_id_divisions.json"

try:
    print("\nStep 1/3: Downloading dataset.json from GitHub...")
    print(f"  URL: {DATASET_URL}")
    
    response = requests.get(DATASET_URL, timeout=60)
    response.raise_for_status()
    dataset = json.loads(response.text)
    print(f"  ✓ Downloaded {len(dataset)} total posts")
    
    print("\nStep 2/3: Downloading post_id_divisions.json...")
    print(f"  URL: {POST_ID_DIVISIONS_URL}")
    
    response = requests.get(POST_ID_DIVISIONS_URL, timeout=30)
    response.raise_for_status()
    post_id_divisions = json.loads(response.text)
    print(f"  ✓ Downloaded split information")
    print(f"    Train IDs: {len(post_id_divisions['train'])}")
    print(f"    Val IDs: {len(post_id_divisions['val'])}")
    print(f"    Test IDs: {len(post_id_divisions['test'])}")
    
    print("\n✓ All files downloaded successfully!")
    
    # Split dataset according to post_id_divisions
    print("\nSplitting dataset into train/val/test...")
    all_data = {
        'train': {pid: dataset[pid] for pid in post_id_divisions['train'] if pid in dataset},
        'validation': {pid: dataset[pid] for pid in post_id_divisions['val'] if pid in dataset},
        'test': {pid: dataset[pid] for pid in post_id_divisions['test'] if pid in dataset}
    }
    
    print(f"  Train split: {len(all_data['train'])} posts")
    print(f"  Val split: {len(all_data['validation'])} posts")
    print(f"  Test split: {len(all_data['test'])} posts")
    
    # Process and convert to DataFrames
    print("\nStep 3/3: Processing data and converting to CSV...")
    
    def process_hatexplain_data(data_dict):
        """Convert HateXplain JSON format to DataFrame"""
        rows = []
        for post_id, content in data_dict.items():
            # Get majority label
            annotators = content.get('annotators', [])
            labels = [ann.get('label', '') for ann in annotators if 'label' in ann]
            
            # Count labels
            label_counts = {}
            for label in labels:
                label_counts[label] = label_counts.get(label, 0) + 1
            
            # Get majority label
            majority_label = max(label_counts, key=label_counts.get) if label_counts else 'normal'
            
            # Get post tokens (text)
            post_tokens = content.get('post_tokens', [])
            text = ' '.join(post_tokens)
            
            # Get rationales (toxic spans)
            rationales = content.get('rationales', [])
            
            row = {
                'post_id': post_id,
                'text': text,
                'label': majority_label,
                'post_tokens': post_tokens,
                'rationales': rationales,
                'annotators': annotators,
                'num_annotators': len(annotators)
            }
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    train_df = process_hatexplain_data(all_data['train'])
    val_df = process_hatexplain_data(all_data['validation'])
    test_df = process_hatexplain_data(all_data['test'])
    
    # Save CSV files
    print("\nSaving CSV files...")
    train_file = OUTPUT_DIR / 'train.csv'
    val_file = OUTPUT_DIR / 'validation.csv'
    test_file = OUTPUT_DIR / 'test.csv'
    
    train_df.to_csv(train_file, index=False, encoding='utf-8')
    val_df.to_csv(val_file, index=False, encoding='utf-8')
    test_df.to_csv(test_file, index=False, encoding='utf-8')
    print(f"  ✓ Saved: {train_file}")
    print(f"  ✓ Saved: {val_file}")
    print(f"  ✓ Saved: {test_file}")
    
    # Also save original JSON format (preserves nested structure for rationales)
    print("\nSaving original JSON files...")
    with open(OUTPUT_DIR / 'dataset_train.json', 'w') as f:
        json.dump(all_data['train'], f, indent=2)
    with open(OUTPUT_DIR / 'dataset_val.json', 'w') as f:
        json.dump(all_data['validation'], f, indent=2)
    with open(OUTPUT_DIR / 'dataset_test.json', 'w') as f:
        json.dump(all_data['test'], f, indent=2)
    print(f"  ✓ Saved: {OUTPUT_DIR / 'dataset_train.json'}")
    print(f"  ✓ Saved: {OUTPUT_DIR / 'dataset_val.json'}")
    print(f"  ✓ Saved: {OUTPUT_DIR / 'dataset_test.json'}")
    
    # Save metadata
    metadata = {
        'dataset_name': 'HateXplain',
        'source': 'GitHub (hate-alert/HateXplain)',
        'source_url': 'https://github.com/hate-alert/HateXplain',
        'download_date': datetime.now().isoformat(),
        'total_samples': len(train_df) + len(val_df) + len(test_df),
        'train_samples': len(train_df),
        'validation_samples': len(val_df),
        'test_samples': len(test_df),
        'columns': list(train_df.columns),
        'label_distribution': {
            'train': train_df['label'].value_counts().to_dict(),
            'validation': val_df['label'].value_counts().to_dict(),
            'test': test_df['label'].value_counts().to_dict()
        },
        'description': 'Hate speech dataset with span-level rationales from Gab and Twitter',
        'paper': 'HateXplain: A Benchmark Dataset for Explainable Hate Speech Detection'
    }
    
    manifest_file = OUTPUT_DIR / 'manifest.json'
    with open(manifest_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"\n✓ Metadata saved: {manifest_file}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("DOWNLOAD COMPLETE!")
    print("=" * 80)
    
    print(f"\nDataset Statistics:")
    print(f"  Train samples:      {len(train_df):,}")
    print(f"  Validation samples: {len(val_df):,}")
    print(f"  Test samples:       {len(test_df):,}")
    print(f"  Total samples:      {len(train_df) + len(val_df) + len(test_df):,}")
    
    print(f"\nLabel Distribution (Train):")
    for label, count in train_df['label'].value_counts().items():
        pct = (count / len(train_df)) * 100
        print(f"  {label:15s}: {count:5,} ({pct:5.1f}%)")
    
    print(f"\nFiles saved to: {OUTPUT_DIR}")
    print(f"  CSV files:  train.csv, validation.csv, test.csv")
    print(f"  JSON files: dataset_train.json, dataset_val.json, dataset_test.json")
    print(f"  Metadata:   manifest.json")
    
    print(f"\nColumns in CSV:")
    for col in train_df.columns:
        print(f"  - {col}")
    
    # Show sample
    if len(train_df) > 0:
        print(f"\nSample data (first row):")
        sample = train_df.iloc[0]
        print(f"  post_id: {sample['post_id']}")
        print(f"  label: {sample['label']}")
        print(f"  text: {sample['text'][:100]}..." if len(sample['text']) > 100 else f"  text: {sample['text']}")
        print(f"  num_annotators: {sample['num_annotators']}")
    
    print("\n✓ HateXplain dataset ready to use!")
    print("\nNext steps:")
    print("  1. Run: python scripts\\2_collect_reddit.py")
    print("  2. Or explore: pd.read_csv('Input/hatexplain/train.csv')")
    print("\nNote: Rationales are preserved in JSON files (dataset_train.json, etc.)")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    print(f"\nFull error:")
    traceback.print_exc()
    print("\nTroubleshooting:")
    print("  1. Install: pip install pandas requests")
    print("  2. Check internet connection")
    print("  3. GitHub might be down - try again later")
    print("  4. Check: https://github.com/hate-alert/HateXplain")
    sys.exit(1)
