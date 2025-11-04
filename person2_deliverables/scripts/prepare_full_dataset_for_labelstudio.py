#!/usr/bin/env python3
"""
Prepare full dataset (20,072 items) for Label Studio import.

This script converts the unlabeled CSV to Label Studio JSON format.
"""

import pandas as pd
import json
from pathlib import Path

def main():
    """Convert full dataset to Label Studio format"""
    print("=" * 60)
    print("Preparing Full Dataset for Label Studio")
    print("=" * 60)
    
    # Load unlabeled data
    data_path = Path(__file__).parent.parent.parent / "data" / "unlabeled" / "for_annotation.csv"
    print(f"\nLoading: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df):,} samples")
    
    # Convert to Label Studio format
    tasks = []
    
    for idx, row in df.iterrows():
        # Parse metadata if it's a string
        if isinstance(row.get('metadata'), str):
            try:
                metadata = json.loads(row['metadata'])
            except:
                metadata = {"raw": row.get('metadata', {})}
        else:
            metadata = row.get('metadata', {}) if pd.notna(row.get('metadata')) else {}
        
        task = {
            "data": {
                "text": str(row['text']),
                "id": row['id'],
                "source": row.get('source', 'unknown'),
                "language": row.get('language', 'unknown'),
                "code_mixed": str(row.get('code_mixed', False)),
                "metadata": metadata
            },
            "id": idx + 1
        }
        tasks.append(task)
    
    # Save Label Studio import file
    output_dir = Path(__file__).parent.parent / "annotation" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "full_annotation_tasks.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved Label Studio import file:")
    print(f"  {output_file}")
    print(f"  Tasks: {len(tasks):,}")
    print(f"\nYou can now import this file into Label Studio!")
    print(f"  File size: {output_file.stat().st_size / (1024*1024):.1f} MB")

if __name__ == "__main__":
    main()

