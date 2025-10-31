"""
Download TextDetox Multilingual Toxicity Dataset
Dataset: textdetox/multilingual_toxicity_dataset
Source: Hugging Face

This dataset contains multilingual toxic/non-toxic text pairs across various languages
including English, Russian, Ukrainian, Hindi, Arabic, Chinese, Spanish, and more.

Author: Person 1 - Data Collection
Date: Oct 2025
"""

from datasets import load_dataset
import pandas as pd
import json
from datetime import datetime
import sys
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'Input' / 'textdetox'

print("=" * 80)
print("TEXTDETOX MULTILINGUAL TOXICITY DATASET DOWNLOAD")
print("=" * 80)
print(f"\nDataset: textdetox/multilingual_toxicity_dataset")
print(f"Source: Hugging Face")
print(f"Output: {OUTPUT_DIR}")
print()

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
print(f"✓ Output directory created: {OUTPUT_DIR}")

# Download dataset
print("\nDownloading dataset from Hugging Face...")
print("⚠️  Note: This may require authentication if dataset is gated.")
print("   Run: huggingface-cli login (if needed)")
print()

try:
    # Load dataset
    print("Loading dataset...")
    ds = load_dataset("textdetox/multilingual_toxicity_dataset")
    
    print(f"✓ Dataset loaded successfully!")
    print(f"\nDataset structure: {ds}")
    
    # Get dataset info
    if hasattr(ds, 'keys'):
        splits = list(ds.keys())
        print(f"\nAvailable splits: {splits}")
    else:
        splits = ['train']
        ds = {'train': ds}
    
    # Save each split
    total_samples = 0
    for split in splits:
        print(f"\nProcessing '{split}' split...")
        
        # Convert to pandas DataFrame
        df = ds[split].to_pandas()
        
        print(f"  Samples: {len(df):,}")
        print(f"  Columns: {list(df.columns)}")
        
        # Save to CSV
        output_file = OUTPUT_DIR / f'{split}.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"  ✓ Saved: {output_file}")
        
        total_samples += len(df)
    
    # Save metadata
    metadata = {
        'dataset_name': 'textdetox/multilingual_toxicity_dataset',
        'source': 'Hugging Face',
        'download_date': datetime.now().isoformat(),
        'total_samples': total_samples,
        'splits': splits,
        'description': 'Multilingual toxic/non-toxic text pairs',
    }
    
    manifest_file = OUTPUT_DIR / 'manifest.json'
    with open(manifest_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✓ Metadata saved: {manifest_file}")
    
    # Summary
    print("\n" + "=" * 80)
    print("DOWNLOAD COMPLETE!")
    print("=" * 80)
    print(f"\nDataset Statistics:")
    print(f"  Total samples: {total_samples:,}")
    print(f"  Splits: {', '.join(splits)}")
    
    # Show sample data
    if 'train' in splits and len(ds['train']) > 0:
        print(f"\nSample data (first row):")
        sample = ds['train'][0]
        for key, value in sample.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {value[:100]}...")
            else:
                print(f"  {key}: {value}")
    
    print(f"\nFiles saved to: {OUTPUT_DIR}")
    print(f"  - {', '.join([f'{split}.csv' for split in splits])}")
    print(f"  - manifest.json")
    
    print("\n✓ TextDetox dataset download complete!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nPossible issues:")
    print("  1. Dataset requires authentication")
    print("     Solution: Run 'huggingface-cli login' first")
    print("  2. Network connection issue")
    print("  3. Dataset name changed or removed")
    print("\nCheck: https://huggingface.co/datasets/textdetox/multilingual_toxicity_dataset")
    sys.exit(1)
