"""
Preprocessing and Unification Script for Toxic Comment Detection
Standardizes all datasets into a unified format for model training

Handles:
- 6 different dataset formats
- Label standardization (binary 0/1)
- Text cleaning and normalization
- Language detection
- Metadata preservation
- Missing ID generation

Author: Person 1 - Data Collection & Preprocessing
Date: Oct 30, 2025
"""

import pandas as pd
import numpy as np
import json
import re
import uuid
from pathlib import Path
from datetime import datetime
import sys
import warnings
warnings.filterwarnings('ignore')

# Try to import langdetect, if not available, will use fallback
try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("⚠️  langdetect not installed. Using fallback language detection.")
    print("   Install with: pip install langdetect")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_DIR = PROJECT_ROOT / 'Input'
OUTPUT_DIR = PROJECT_ROOT / 'Final_input'

# Create output directory structure
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / 'labeled').mkdir(exist_ok=True)
(OUTPUT_DIR / 'unlabeled').mkdir(exist_ok=True)
(OUTPUT_DIR / 'metadata').mkdir(exist_ok=True)
(OUTPUT_DIR / 'reports').mkdir(exist_ok=True)

print("=" * 80)
print("DATA PREPROCESSING & UNIFICATION PIPELINE")
print("=" * 80)
print(f"\nInput:  {INPUT_DIR}")
print(f"Output: {OUTPUT_DIR}")
print(f"Date:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n" + "=" * 80)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def detect_language(text):
    """Detect language of text with fallback"""
    if not isinstance(text, str) or len(text.strip()) < 10:
        return 'unknown'
    
    if LANGDETECT_AVAILABLE:
        try:
            return detect(str(text))
        except LangDetectException:
            return 'unknown'
    else:
        # Fallback: Simple heuristic based on character sets
        text_lower = text.lower()
        
        # Check for Hindi characters (Devanagari)
        if any('\u0900' <= char <= '\u097F' for char in text):
            return 'hi'
        
        # Check for Arabic
        if any('\u0600' <= char <= '\u06FF' for char in text):
            return 'ar'
        
        # Check for Chinese
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            return 'zh'
        
        # Check for common Hindi romanization patterns
        hindi_words = ['hai', 'nahi', 'kya', 'bhai', 'yaar', 'kar', 'koi', 'mein', 'hoon']
        if any(word in text_lower for word in hindi_words):
            return 'hi'  # or 'hi-en' for code-mixed
        
        # Default to English
        return 'en'

def is_code_mixed(text):
    """Detect if text is code-mixed (Hindi-English)"""
    if not isinstance(text, str):
        return False
    
    text_lower = text.lower()
    
    # Common Hindi words in Roman script
    hindi_indicators = [
        'yaar', 'bhai', 'hai', 'nahi', 'kya', 'mein', 'hoon', 'kar', 
        'koi', 'bhi', 'toh', 'tha', 'kuch', 'bahut', 'acha', 'bura',
        'matlab', 'yeh', 'woh', 'kahan', 'kaise', 'kyun', 'abhi'
    ]
    
    # Check for Hindi words
    hindi_count = sum(1 for word in hindi_indicators if word in text_lower)
    
    # Check for English words (common ones)
    english_words = text_lower.split()
    
    # Code-mixed if has both Hindi indicators and reasonable length
    return hindi_count >= 2 and len(english_words) >= 5

def clean_text(text):
    """Clean and normalize text"""
    if not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove zero-width characters
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Remove control characters but keep newlines
    text = ''.join(char for char in text if char.isprintable() or char == '\n')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def generate_id(source, index):
    """Generate unique ID for records without IDs"""
    return f"{source}_{uuid.uuid4().hex[:12]}_{index}"

def standardize_label(value, label_type='binary'):
    """
    Standardize labels to binary 0/1
    
    Args:
        value: Original label value
        label_type: Type of label conversion
            - 'binary': 0 or 1
            - 'continuous': threshold at 0.5
            - 'multiclass': hate/offensive->1, normal->0
    """
    if pd.isna(value):
        return None
    
    if label_type == 'binary':
        # Already binary
        return int(value)
    
    elif label_type == 'continuous':
        # Threshold continuous scores
        return 1 if float(value) >= 0.5 else 0
    
    elif label_type == 'multiclass':
        # HateXplain: hate/offensive -> 1, normal -> 0
        value_lower = str(value).lower()
        if value_lower in ['hatespeech', 'offensive', 'hate']:
            return 1
        elif value_lower in ['normal', 'neither']:
            return 0
        else:
            return None
    
    return None

# ============================================================================
# DATASET PROCESSORS
# ============================================================================

def process_hatexplain():
    """Process HateXplain dataset"""
    print("\n" + "-" * 80)
    print("Processing HateXplain Dataset")
    print("-" * 80)
    
    data_list = []
    
    for split in ['train', 'validation', 'test']:
        file_path = INPUT_DIR / 'hatexplain' / f'{split}.csv'
        
        if not file_path.exists():
            print(f"⚠️  {split}.csv not found, skipping...")
            continue
        
        print(f"\nReading {split}.csv...")
        df = pd.read_csv(file_path)
        print(f"  Loaded: {len(df):,} rows")
        
        for idx, row in df.iterrows():
            # Extract clean data
            record = {
                'id': f"hatexplain_{row['post_id']}",
                'text': clean_text(row['text']),
                'label': standardize_label(row['label'], 'multiclass'),
                'source': 'hatexplain',
                'language': 'en',  # HateXplain is English-only
                'split': split,
                'code_mixed': False,
                'metadata': json.dumps({
                    'original_id': row['post_id'],
                    'num_annotators': row.get('num_annotators', 3),
                    'has_rationales': True
                })
            }
            
            # Only include if we have valid text and label
            if record['text'] and record['label'] is not None:
                data_list.append(record)
        
        print(f"  Processed: {len(data_list):,} total records so far")
    
    df_processed = pd.DataFrame(data_list)
    print(f"\n✓ HateXplain complete: {len(df_processed):,} samples")
    print(f"  Label distribution: {df_processed['label'].value_counts().to_dict()}")
    
    return df_processed

def process_jigsaw_multilingual():
    """Process Jigsaw Multilingual dataset"""
    print("\n" + "-" * 80)
    print("Processing Jigsaw Multilingual Dataset")
    print("-" * 80)
    
    data_list = []
    
    # Process validation set (test set doesn't have labels)
    for split in ['validation']:
        file_path = INPUT_DIR / 'jigsaw_multilingual' / f'{split}.csv'
        
        if not file_path.exists():
            print(f"⚠️  {split}.csv not found, skipping...")
            continue
        
        print(f"\nReading {split}.csv...")
        df = pd.read_csv(file_path)
        print(f"  Loaded: {len(df):,} rows")
        
        # Sample if too large (take subset for efficiency)
        if len(df) > 50000:
            print(f"  Sampling 50,000 rows for efficiency...")
            df = df.sample(n=50000, random_state=42)
        
        for idx, row in df.iterrows():
            text = clean_text(row.get('comment_text', ''))
            if not text:
                continue
            
            record = {
                'id': f"jigsaw_multi_{row['id']}",
                'text': text,
                'label': standardize_label(row['toxic'], 'binary'),
                'source': 'jigsaw_multilingual',
                'language': row.get('lang', 'unknown'),
                'split': split,
                'code_mixed': False,
                'metadata': json.dumps({
                    'original_id': row['id']
                })
            }
            
            if record['label'] is not None:
                data_list.append(record)
        
        print(f"  Processed: {len(data_list):,} records")
    
    df_processed = pd.DataFrame(data_list)
    print(f"\n✓ Jigsaw Multilingual complete: {len(df_processed):,} samples")
    if len(df_processed) > 0:
        print(f"  Languages: {df_processed['language'].value_counts().head(10).to_dict()}")
    
    return df_processed

def process_jigsaw_bias():
    """Process Jigsaw Unintended Bias dataset"""
    print("\n" + "-" * 80)
    print("Processing Jigsaw Unintended Bias Dataset")
    print("-" * 80)
    
    file_path = INPUT_DIR / 'jigsaw_unintended_bias' / 'train.csv'
    
    if not file_path.exists():
        print("⚠️  train.csv not found, skipping...")
        return pd.DataFrame()
    
    print(f"\nReading train.csv (large file, may take time)...")
    
    # Sample a subset due to size (1.8M rows is very large)
    print("  Sampling 100,000 rows for efficiency...")
    df = pd.read_csv(file_path, nrows=100000)
    print(f"  Loaded: {len(df):,} rows")
    
    data_list = []
    identity_columns = ['asian', 'atheist', 'bisexual', 'black', 'buddhist', 'christian', 
                        'female', 'heterosexual', 'hindu', 'homosexual_gay_or_lesbian',
                        'jewish', 'latino', 'male', 'muslim', 'transgender', 'white']
    
    for idx, row in df.iterrows():
        text = clean_text(row.get('comment_text', ''))
        if not text:
            continue
        
        # Extract identity mentions
        identities = {}
        for col in identity_columns:
            if col in row and pd.notna(row[col]) and row[col] >= 0.5:
                identities[col] = float(row[col])
        
        record = {
            'id': f"jigsaw_bias_{row['id']}",
            'text': text,
            'label': standardize_label(row['target'], 'continuous'),
            'source': 'jigsaw_unintended_bias',
            'language': 'en',  # Primarily English
            'split': 'train',
            'code_mixed': False,
            'metadata': json.dumps({
                'original_id': row['id'],
                'target_score': float(row['target']),
                'identities': identities,
                'has_fairness_annotations': bool(identities)
            })
        }
        
        if record['label'] is not None:
            data_list.append(record)
        
        # Progress indicator
        if (idx + 1) % 10000 == 0:
            print(f"  Processed: {idx + 1:,} / {len(df):,} rows...")
    
    df_processed = pd.DataFrame(data_list)
    print(f"\n✓ Jigsaw Bias complete: {len(df_processed):,} samples")
    
    return df_processed

def process_textdetox():
    """Process TextDetox multilingual dataset"""
    print("\n" + "-" * 80)
    print("Processing TextDetox Dataset")
    print("-" * 80)
    
    data_list = []
    
    # Language files
    lang_files = {
        'en': 'en', 'ru': 'ru', 'uk': 'uk', 'de': 'de', 'es': 'es',
        'am': 'am', 'zh': 'zh', 'ar': 'ar', 'hi': 'hi', 'it': 'it',
        'fr': 'fr', 'he': 'he', 'hin': 'hi', 'tt': 'tt', 'ja': 'ja'
    }
    
    for file_name, lang_code in lang_files.items():
        file_path = INPUT_DIR / 'textdetox' / f'{file_name}.csv'
        
        if not file_path.exists():
            continue
        
        print(f"\nReading {file_name}.csv...")
        df = pd.read_csv(file_path)
        print(f"  Loaded: {len(df):,} rows")
        
        for idx, row in df.iterrows():
            text = clean_text(row.get('text', ''))
            if not text:
                continue
            
            record = {
                'id': generate_id('textdetox', f"{file_name}_{idx}"),
                'text': text,
                'label': standardize_label(row.get('toxic', 0), 'binary'),
                'source': 'textdetox',
                'language': lang_code,
                'split': 'train',
                'code_mixed': False,
                'metadata': json.dumps({
                    'language_file': file_name
                })
            }
            
            if record['label'] is not None:
                data_list.append(record)
        
        print(f"  Processed: {len(data_list):,} total records so far")
    
    df_processed = pd.DataFrame(data_list)
    print(f"\n✓ TextDetox complete: {len(df_processed):,} samples")
    
    return df_processed

def process_reddit():
    """Process Reddit comments (unlabeled)"""
    print("\n" + "-" * 80)
    print("Processing Reddit Comments (Unlabeled)")
    print("-" * 80)
    
    file_path = INPUT_DIR / 'reddit' / 'raw_comments.csv'
    
    if not file_path.exists():
        print("⚠️  raw_comments.csv not found, skipping...")
        return pd.DataFrame()
    
    print(f"\nReading raw_comments.csv...")
    df = pd.read_csv(file_path)
    print(f"  Loaded: {len(df):,} rows")
    
    data_list = []
    seen_ids = set()
    
    for idx, row in df.iterrows():
        text = clean_text(row.get('text', ''))
        if not text or len(text) < 10:
            continue
        
        # Create unique ID (handle potential duplicates)
        original_id = str(row.get('id', ''))
        unique_id = f"reddit_{original_id}"
        
        # If ID already exists, append index
        if unique_id in seen_ids:
            unique_id = f"reddit_{original_id}_{idx}"
        seen_ids.add(unique_id)
        
        # Detect language and code-mixing
        lang = detect_language(text)
        is_cm = is_code_mixed(text)
        
        record = {
            'id': unique_id,
            'text': text,
            'label': None,  # Unlabeled
            'source': 'reddit',
            'language': lang,
            'split': 'unlabeled',
            'code_mixed': is_cm,
            'metadata': json.dumps({
                'original_id': original_id,
                'subreddit': row.get('subreddit', ''),
                'score': int(row.get('score', 0)),
                'created_utc': row.get('created_utc', ''),
                'comment_depth': int(row.get('comment_depth', 0))
            })
        }
        
        data_list.append(record)
    
    df_processed = pd.DataFrame(data_list)
    print(f"\n✓ Reddit complete: {len(df_processed):,} samples (unlabeled)")
    print(f"  Code-mixed: {df_processed['code_mixed'].sum():,} samples")
    
    return df_processed

def process_youtube():
    """Process YouTube comments (unlabeled)"""
    print("\n" + "-" * 80)
    print("Processing YouTube Comments (Unlabeled)")
    print("-" * 80)
    
    file_path = INPUT_DIR / 'youtube' / 'raw_comments.csv'
    
    if not file_path.exists():
        print("⚠️  raw_comments.csv not found, skipping...")
        return pd.DataFrame()
    
    print(f"\nReading raw_comments.csv...")
    df = pd.read_csv(file_path)
    print(f"  Loaded: {len(df):,} rows")
    
    data_list = []
    seen_ids = set()
    
    for idx, row in df.iterrows():
        text = clean_text(row.get('text', ''))
        if not text or len(text) < 10:
            continue
        
        # Create unique ID (handle potential duplicates)
        original_id = str(row.get('id', ''))
        unique_id = f"youtube_{original_id}"
        
        # If ID already exists, append index
        if unique_id in seen_ids:
            unique_id = f"youtube_{original_id}_{idx}"
        seen_ids.add(unique_id)
        
        # Detect language and code-mixing
        lang = detect_language(text)
        is_cm = is_code_mixed(text)
        
        record = {
            'id': unique_id,
            'text': text,
            'label': None,  # Unlabeled
            'source': 'youtube',
            'language': lang,
            'split': 'unlabeled',
            'code_mixed': is_cm,
            'metadata': json.dumps({
                'original_id': original_id,
                'video_id': row.get('video_id', ''),
                'video_title': row.get('video_title', ''),
                'author': row.get('author', ''),
                'likes': int(row.get('likes', 0)),
                'published_at': row.get('published_at', '')
            })
        }
        
        data_list.append(record)
    
    df_processed = pd.DataFrame(data_list)
    print(f"\n✓ YouTube complete: {len(df_processed):,} samples (unlabeled)")
    print(f"  Code-mixed: {df_processed['code_mixed'].sum():,} samples")
    
    return df_processed

# ============================================================================
# MAIN PROCESSING
# ============================================================================

def main():
    """Main processing pipeline"""
    
    print("\n" + "=" * 80)
    print("STEP 1: Processing Individual Datasets")
    print("=" * 80)
    
    # Process each dataset
    df_hatexplain = process_hatexplain()
    df_jigsaw_multi = process_jigsaw_multilingual()
    df_jigsaw_bias = process_jigsaw_bias()
    df_textdetox = process_textdetox()
    df_reddit = process_reddit()
    df_youtube = process_youtube()
    
    # ========================================================================
    # STEP 2: Combine datasets
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STEP 2: Combining Datasets")
    print("=" * 80)
    
    # Labeled data (has labels)
    labeled_dfs = [df_hatexplain, df_jigsaw_multi, df_jigsaw_bias, df_textdetox]
    labeled_dfs = [df for df in labeled_dfs if len(df) > 0]
    
    if labeled_dfs:
        df_labeled = pd.concat(labeled_dfs, ignore_index=True)
        df_labeled = df_labeled[df_labeled['label'].notna()]
        print(f"\n✓ Combined labeled data: {len(df_labeled):,} samples")
        print(f"  Sources: {df_labeled['source'].value_counts().to_dict()}")
    else:
        df_labeled = pd.DataFrame()
        print("\n⚠️  No labeled data found!")
    
    # Unlabeled data (for annotation)
    unlabeled_dfs = [df_reddit, df_youtube]
    unlabeled_dfs = [df for df in unlabeled_dfs if len(df) > 0]
    
    if unlabeled_dfs:
        df_unlabeled = pd.concat(unlabeled_dfs, ignore_index=True)
        print(f"\n✓ Combined unlabeled data: {len(df_unlabeled):,} samples")
        print(f"  Sources: {df_unlabeled['source'].value_counts().to_dict()}")
    else:
        df_unlabeled = pd.DataFrame()
        print("\n⚠️  No unlabeled data found!")
    
    # ========================================================================
    # STEP 3: Save processed data
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STEP 3: Saving Processed Data")
    print("=" * 80)
    
    # Save labeled data
    if len(df_labeled) > 0:
        labeled_file = OUTPUT_DIR / 'labeled' / 'all_labeled_data.csv'
        df_labeled.to_csv(labeled_file, index=False, encoding='utf-8')
        print(f"\n✓ Saved labeled data: {labeled_file}")
        print(f"  Rows: {len(df_labeled):,}")
        print(f"  Columns: {list(df_labeled.columns)}")
        
        # Save by source
        for source in df_labeled['source'].unique():
            source_df = df_labeled[df_labeled['source'] == source]
            source_file = OUTPUT_DIR / 'labeled' / f'{source}.csv'
            source_df.to_csv(source_file, index=False, encoding='utf-8')
            print(f"  • {source}: {len(source_df):,} samples → {source_file.name}")
    
    # Save unlabeled data
    if len(df_unlabeled) > 0:
        unlabeled_file = OUTPUT_DIR / 'unlabeled' / 'for_annotation.csv'
        df_unlabeled.to_csv(unlabeled_file, index=False, encoding='utf-8')
        print(f"\n✓ Saved unlabeled data: {unlabeled_file}")
        print(f"  Rows: {len(df_unlabeled):,}")
        
        # Save by source
        for source in df_unlabeled['source'].unique():
            source_df = df_unlabeled[df_unlabeled['source'] == source]
            source_file = OUTPUT_DIR / 'unlabeled' / f'{source}.csv'
            source_df.to_csv(source_file, index=False, encoding='utf-8')
            print(f"  • {source}: {len(source_df):,} samples → {source_file.name}")
    
    # ========================================================================
    # STEP 4: Generate statistics & reports
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STEP 4: Generating Reports")
    print("=" * 80)
    
    report = {
        'processing_date': datetime.now().isoformat(),
        'total_labeled_samples': int(len(df_labeled)) if len(df_labeled) > 0 else 0,
        'total_unlabeled_samples': int(len(df_unlabeled)) if len(df_unlabeled) > 0 else 0,
        'total_samples': int(len(df_labeled) + len(df_unlabeled)),
        'labeled_by_source': {},
        'unlabeled_by_source': {},
        'label_distribution': {},
        'language_distribution': {},
        'code_mixed_counts': {}
    }
    
    if len(df_labeled) > 0:
        report['labeled_by_source'] = df_labeled['source'].value_counts().to_dict()
        report['label_distribution'] = df_labeled['label'].value_counts().to_dict()
        report['language_distribution'] = df_labeled['language'].value_counts().to_dict()
    
    if len(df_unlabeled) > 0:
        report['unlabeled_by_source'] = df_unlabeled['source'].value_counts().to_dict()
        report['code_mixed_counts'] = {
            'reddit': int(df_unlabeled[df_unlabeled['source'] == 'reddit']['code_mixed'].sum()),
            'youtube': int(df_unlabeled[df_unlabeled['source'] == 'youtube']['code_mixed'].sum())
        }
    
    # Save report
    report_file = OUTPUT_DIR / 'reports' / 'processing_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✓ Saved processing report: {report_file}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE!")
    print("=" * 80)
    
    print(f"\n📊 Summary Statistics:")
    print(f"  Total labeled samples:   {report['total_labeled_samples']:,}")
    print(f"  Total unlabeled samples: {report['total_unlabeled_samples']:,}")
    print(f"  Total samples:           {report['total_samples']:,}")
    
    if report['labeled_by_source']:
        print(f"\n  Labeled by source:")
        for source, count in report['labeled_by_source'].items():
            print(f"    • {source:25s}: {count:,}")
    
    if report['label_distribution']:
        print(f"\n  Label distribution:")
        for label, count in report['label_distribution'].items():
            pct = (count / report['total_labeled_samples']) * 100
            print(f"    • {'Toxic' if label == 1 else 'Non-toxic':15s}: {count:,} ({pct:.1f}%)")
    
    if report['code_mixed_counts']:
        print(f"\n  Code-mixed samples:")
        for source, count in report['code_mixed_counts'].items():
            print(f"    • {source:10s}: {count:,}")
    
    print(f"\n📁 Output files:")
    print(f"  Labeled:   {OUTPUT_DIR / 'labeled'}")
    print(f"  Unlabeled: {OUTPUT_DIR / 'unlabeled'}")
    print(f"  Reports:   {OUTPUT_DIR / 'reports'}")
    
    print("\n✓ All datasets preprocessed and unified!")
    print("\nNext steps:")
    print("  1. Run validation: python scripts/6_data_quality_checks.py")
    print("  2. Review reports in Final_input/reports/")
    print("  3. Hand off to Person 2 for annotation")
    
    return report

if __name__ == '__main__':
    try:
        report = main()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
