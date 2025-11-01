#!/usr/bin/env python3
"""
Prepare pilot annotation data (~1,000 items) for inter-annotator agreement.

This script:
1. Samples ~1,000 items from unlabeled data
2. Prioritizes code-mixed samples
3. Creates balanced sample (toxic/non-toxic ratio based on labeled data)
4. Exports in Label Studio format (JSON)
"""

import pandas as pd
import json
import random
from pathlib import Path
from datetime import datetime

# Set random seed for reproducibility
random.seed(42)

def load_unlabeled_data():
    """Load unlabeled data for annotation"""
    data_path = Path(__file__).parent.parent / "data" / "unlabeled" / "for_annotation.csv"
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df):,} unlabeled samples")
    return df

def create_pilot_sample(df, n_samples=1000):
    """
    Create balanced pilot sample prioritizing code-mixed data.
    
    Target distribution (based on labeled data):
    - 70% non-toxic, 30% toxic (approximate)
    - Prioritize code-mixed samples
    """
    print(f"\nCreating pilot sample of {n_samples:,} items...")
    
    # Prioritize code-mixed samples (50% of pilot)
    code_mixed = df[df['code_mixed'] == True].copy()
    non_code_mixed = df[df['code_mixed'] == False].copy()
    
    n_code_mixed = min(len(code_mixed), n_samples // 2)
    n_regular = n_samples - n_code_mixed
    
    print(f"  - Code-mixed samples: {n_code_mixed:,}")
    print(f"  - Regular samples: {n_regular:,}")
    
    # Sample code-mixed (random)
    if len(code_mixed) > 0:
        code_mixed_sample = code_mixed.sample(
            n=min(n_code_mixed, len(code_mixed)), 
            random_state=42
        )
    else:
        code_mixed_sample = pd.DataFrame()
    
    # Sample regular (random)
    if len(non_code_mixed) > n_regular:
        regular_sample = non_code_mixed.sample(n=n_regular, random_state=42)
    else:
        regular_sample = non_code_mixed.copy()
        # If not enough, fill from code_mixed
        remaining = n_regular - len(regular_sample)
        if remaining > 0 and len(code_mixed) > n_code_mixed:
            additional = code_mixed.sample(n=min(remaining, len(code_mixed) - n_code_mixed), random_state=43)
            regular_sample = pd.concat([regular_sample, additional])
    
    # Combine
    pilot_sample = pd.concat([code_mixed_sample, regular_sample], ignore_index=True)
    pilot_sample = pilot_sample.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"  Created pilot sample: {len(pilot_sample):,} items")
    print(f"    - Code-mixed: {pilot_sample['code_mixed'].sum():,}")
    print(f"    - Reddit: {(pilot_sample['source'] == 'reddit').sum():,}")
    print(f"    - YouTube: {(pilot_sample['source'] == 'youtube').sum():,}")
    
    return pilot_sample

def convert_to_label_studio_format(df):
    """
    Convert DataFrame to Label Studio JSON format.
    
    Label Studio expects:
    {
        "data": {
            "text": "...",
            "id": "...",
            "metadata": {...}
        }
    }
    """
    tasks = []
    
    for idx, row in df.iterrows():
        # Parse metadata if it's a string
        if isinstance(row['metadata'], str):
            try:
                metadata = json.loads(row['metadata'])
            except:
                metadata = {"raw": row['metadata']}
        else:
            metadata = row['metadata'] if pd.notna(row['metadata']) else {}
        
        task = {
            "data": {
                "text": row['text'],
                "id": row['id'],
                "source": row['source'],
                "language": row['language'],
                "code_mixed": str(row['code_mixed']),
                "metadata": metadata
            },
            "id": idx + 1  # Label Studio task ID (1-indexed)
        }
        tasks.append(task)
    
    return tasks

def create_gold_questions(pilot_sample, n_gold=50):
    """
    Create gold standard questions for annotator quality monitoring.
    
    These should be manually labeled by expert annotator before pilot.
    For now, we'll create a template file.
    """
    gold_path = Path(__file__).parent.parent / "annotation" / "gold_questions.json"
    
    # Sample items for gold questions
    gold_sample = pilot_sample.sample(n=min(n_gold, len(pilot_sample)), random_state=999)
    
    gold_questions = []
    for idx, row in gold_sample.iterrows():
        gold_questions.append({
            "id": row['id'],
            "text": row['text'],
            "expected_label": None,  # To be filled by expert
            "expected_subtypes": [],  # To be filled by expert
            "notes": "To be annotated by expert before pilot"
        })
    
    with open(gold_path, 'w', encoding='utf-8') as f:
        json.dump(gold_questions, f, indent=2, ensure_ascii=False)
    
    print(f"\nCreated gold questions template: {len(gold_questions):,} items")
    print(f"  Location: {gold_path}")
    print(f"  IMPORTANT: Annotate these manually before running pilot!")
    
    return gold_path

def main():
    """Main execution"""
    print("=" * 60)
    print("Pilot Data Preparation for Annotation")
    print("=" * 60)
    
    # Load data
    df = load_unlabeled_data()
    
    # Create pilot sample
    pilot_sample = create_pilot_sample(df, n_samples=1000)
    
    # Convert to Label Studio format
    tasks = convert_to_label_studio_format(pilot_sample)
    
    # Save Label Studio import file
    output_dir = Path(__file__).parent.parent / "annotation" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "pilot_annotation_tasks.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved Label Studio import file:")
    print(f"  {output_file}")
    print(f"  Tasks: {len(tasks):,}")
    
    # Save pilot manifest
    manifest = {
        "creation_date": datetime.now().isoformat(),
        "total_samples": len(pilot_sample),
        "code_mixed_count": int(pilot_sample['code_mixed'].sum()),
        "sources": pilot_sample['source'].value_counts().to_dict(),
        "languages": pilot_sample['language'].value_counts().head(10).to_dict(),
        "random_seed": 42
    }
    
    manifest_file = output_dir / "pilot_manifest.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"Saved pilot manifest: {manifest_file}")
    
    # Create gold questions template
    create_gold_questions(pilot_sample, n_gold=50)
    
    # Also save as CSV for reference
    csv_file = output_dir / "pilot_sample.csv"
    pilot_sample.to_csv(csv_file, index=False)
    print(f"Saved CSV reference: {csv_file}")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("1. Review pilot_sample.csv")
    print("2. Manually annotate gold_questions.json")
    print("3. Import pilot_annotation_tasks.json into Label Studio")
    print("4. Run pilot annotation with 2+ annotators")
    print("5. Calculate IAA using scripts/9_calculate_iaa.py")
    print("=" * 60)

if __name__ == "__main__":
    main()

