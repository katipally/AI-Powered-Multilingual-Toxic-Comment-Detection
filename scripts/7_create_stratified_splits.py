"""
Create Stratified Train/Dev/Test Splits
Stratifies by toxicity label and language mix for balanced evaluation

Requirements from Person 1:
- Stratified splits by toxicity label and language mix
- Freeze random seed and store split manifest
- Proper class balance in each split

Author: Person 1 - Data Collection & Preprocessing
Date: Oct 30, 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import json
from datetime import datetime
from collections import Counter

# Fixed random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_DIR = PROJECT_ROOT / 'Final_input' / 'labeled'
OUTPUT_DIR = PROJECT_ROOT / 'Final_input' / 'splits'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("STRATIFIED TRAIN/DEV/TEST SPLIT CREATION")
print("=" * 80)
print(f"\nRandom Seed: {RANDOM_SEED}")
print(f"Input:  {INPUT_DIR}")
print(f"Output: {OUTPUT_DIR}")
print("\n" + "=" * 80)

def create_stratification_key(df):
    """
    Create stratification key combining:
    - Label (toxic/non-toxic)
    - Language group (English, Hindi, Other)
    - Code-mixed status
    """
    print("\nCreating stratification keys...")
    
    # Language groups for better stratification
    def get_lang_group(lang):
        if lang == 'en':
            return 'english'
        elif lang in ['hi', 'hin']:
            return 'hindi'
        else:
            return 'other'
    
    df['lang_group'] = df['language'].apply(get_lang_group)
    df['strat_key'] = (
        df['label'].astype(str) + '_' + 
        df['lang_group'] + '_' + 
        df['code_mixed'].astype(str)
    )
    
    # Show stratification distribution
    print(f"\nStratification keys created:")
    key_counts = df['strat_key'].value_counts()
    for key, count in key_counts.items():
        pct = (count / len(df)) * 100
        print(f"  • {key:30s}: {count:6,} ({pct:5.2f}%)")
    
    return df

def create_splits(df, train_size=0.7, dev_size=0.15, test_size=0.15):
    """
    Create stratified train/dev/test splits
    
    Args:
        df: DataFrame with data
        train_size: Proportion for training (default 0.7)
        dev_size: Proportion for development/validation (default 0.15)
        test_size: Proportion for testing (default 0.15)
    """
    print(f"\n" + "-" * 80)
    print(f"Creating splits: Train={train_size:.0%}, Dev={dev_size:.0%}, Test={test_size:.0%}")
    print("-" * 80)
    
    # Validate split sizes
    assert abs(train_size + dev_size + test_size - 1.0) < 0.01, "Split sizes must sum to 1.0"
    
    # Create stratification key
    df = create_stratification_key(df)
    
    # First split: train vs (dev + test)
    train_df, temp_df = train_test_split(
        df,
        test_size=(dev_size + test_size),
        random_state=RANDOM_SEED,
        stratify=df['strat_key']
    )
    
    # Second split: dev vs test
    relative_test_size = test_size / (dev_size + test_size)
    dev_df, test_df = train_test_split(
        temp_df,
        test_size=relative_test_size,
        random_state=RANDOM_SEED,
        stratify=temp_df['strat_key']
    )
    
    print(f"\n✓ Splits created:")
    print(f"  Train: {len(train_df):6,} samples ({len(train_df)/len(df)*100:.1f}%)")
    print(f"  Dev:   {len(dev_df):6,} samples ({len(dev_df)/len(df)*100:.1f}%)")
    print(f"  Test:  {len(test_df):6,} samples ({len(test_df)/len(df)*100:.1f}%)")
    
    return train_df, dev_df, test_df

def validate_splits(train_df, dev_df, test_df):
    """Validate that splits maintain class balance"""
    print(f"\n" + "-" * 80)
    print("Validating Split Balance")
    print("-" * 80)
    
    splits = {
        'train': train_df,
        'dev': dev_df,
        'test': test_df
    }
    
    all_valid = True
    
    for split_name, split_df in splits.items():
        print(f"\n{split_name.upper()} Split:")
        print(f"  Total samples: {len(split_df):,}")
        
        # Label distribution
        label_dist = split_df['label'].value_counts(normalize=True)
        toxic_pct = label_dist.get(1, 0) * 100
        print(f"  Toxic: {toxic_pct:.1f}%")
        
        # Language distribution
        lang_dist = split_df['lang_group'].value_counts(normalize=True)
        print(f"  Languages:")
        for lang, pct in lang_dist.items():
            print(f"    • {lang:10s}: {pct*100:5.1f}%")
        
        # Code-mixed
        cm_pct = split_df['code_mixed'].sum() / len(split_df) * 100
        print(f"  Code-mixed: {cm_pct:.1f}%")
        
        # Validation: Check reasonable balance
        if toxic_pct < 15 or toxic_pct > 40:
            print(f"  ⚠️  Warning: Toxic ratio {toxic_pct:.1f}% may be unbalanced")
            all_valid = False
    
    if all_valid:
        print(f"\n✓ All splits have reasonable class balance")
    else:
        print(f"\n⚠️  Some splits may have balance issues")
    
    return all_valid

def save_splits(train_df, dev_df, test_df):
    """Save splits to CSV files"""
    print(f"\n" + "-" * 80)
    print("Saving Split Files")
    print("-" * 80)
    
    # Remove temporary columns
    cols_to_drop = ['lang_group', 'strat_key']
    train_clean = train_df.drop(columns=cols_to_drop)
    dev_clean = dev_df.drop(columns=cols_to_drop)
    test_clean = test_df.drop(columns=cols_to_drop)
    
    # Save files
    train_file = OUTPUT_DIR / 'train.csv'
    dev_file = OUTPUT_DIR / 'dev.csv'
    test_file = OUTPUT_DIR / 'test.csv'
    
    train_clean.to_csv(train_file, index=False)
    dev_clean.to_csv(dev_file, index=False)
    test_clean.to_csv(test_file, index=False)
    
    print(f"\n✓ Split files saved:")
    print(f"  {train_file} ({len(train_clean):,} samples)")
    print(f"  {dev_file} ({len(dev_clean):,} samples)")
    print(f"  {test_file} ({len(test_clean):,} samples)")
    
    return train_file, dev_file, test_file

def create_split_manifest(train_df, dev_df, test_df, files):
    """Create manifest documenting the split"""
    print(f"\n" + "-" * 80)
    print("Creating Split Manifest")
    print("-" * 80)
    
    manifest = {
        'creation_date': datetime.now().isoformat(),
        'random_seed': RANDOM_SEED,
        'total_samples': len(train_df) + len(dev_df) + len(test_df),
        'splits': {
            'train': {
                'file': str(files[0].name),
                'samples': int(len(train_df)),
                'toxic_count': int(train_df['label'].sum()),
                'toxic_pct': float(train_df['label'].mean() * 100),
                'languages': train_df['language'].value_counts().head(5).to_dict(),
                'code_mixed': int(train_df['code_mixed'].sum())
            },
            'dev': {
                'file': str(files[1].name),
                'samples': int(len(dev_df)),
                'toxic_count': int(dev_df['label'].sum()),
                'toxic_pct': float(dev_df['label'].mean() * 100),
                'languages': dev_df['language'].value_counts().head(5).to_dict(),
                'code_mixed': int(dev_df['code_mixed'].sum())
            },
            'test': {
                'file': str(files[2].name),
                'samples': int(len(test_df)),
                'toxic_count': int(test_df['label'].sum()),
                'toxic_pct': float(test_df['label'].mean() * 100),
                'languages': test_df['language'].value_counts().head(5).to_dict(),
                'code_mixed': int(test_df['code_mixed'].sum())
            }
        },
        'stratification': {
            'method': 'sklearn.model_selection.train_test_split',
            'stratify_by': 'label_x_language_group_x_code_mixed',
            'reproducible': True
        },
        'source_datasets': list(train_df['source'].unique())
    }
    
    manifest_file = OUTPUT_DIR / 'split_manifest.json'
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✓ Manifest saved: {manifest_file}")
    
    return manifest

def main():
    """Main pipeline"""
    
    # Load labeled data
    print("\nLoading labeled data...")
    labeled_file = INPUT_DIR / 'all_labeled_data.csv'
    
    if not labeled_file.exists():
        print(f"❌ Error: {labeled_file} not found!")
        print("   Run scripts/5_preprocess_and_unify.py first")
        return 1
    
    df = pd.read_csv(labeled_file)
    print(f"✓ Loaded {len(df):,} samples")
    
    # Create splits
    train_df, dev_df, test_df = create_splits(df, train_size=0.7, dev_size=0.15, test_size=0.15)
    
    # Validate splits
    validate_splits(train_df, dev_df, test_df)
    
    # Save splits
    files = save_splits(train_df, dev_df, test_df)
    
    # Create manifest
    manifest = create_split_manifest(train_df, dev_df, test_df, files)
    
    # Final summary
    print("\n" + "=" * 80)
    print("SPLIT CREATION COMPLETE!")
    print("=" * 80)
    
    print(f"\n📊 Summary:")
    print(f"  Total samples:  {manifest['total_samples']:,}")
    print(f"  Train samples:  {manifest['splits']['train']['samples']:,} ({manifest['splits']['train']['toxic_pct']:.1f}% toxic)")
    print(f"  Dev samples:    {manifest['splits']['dev']['samples']:,} ({manifest['splits']['dev']['toxic_pct']:.1f}% toxic)")
    print(f"  Test samples:   {manifest['splits']['test']['samples']:,} ({manifest['splits']['test']['toxic_pct']:.1f}% toxic)")
    
    print(f"\n📁 Output files:")
    print(f"  {OUTPUT_DIR}/")
    print(f"    ├── train.csv")
    print(f"    ├── dev.csv")
    print(f"    ├── test.csv")
    print(f"    └── split_manifest.json")
    
    print(f"\n✓ Stratified splits ready for model training!")
    print(f"  Random seed: {RANDOM_SEED} (reproducible)")
    
    return 0

if __name__ == '__main__':
    import sys
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
