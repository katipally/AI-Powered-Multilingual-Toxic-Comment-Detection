#!/usr/bin/env python3
"""
Adjudicate disagreements between annotators.

This script:
1. Loads disagreements from IAA report
2. Allows manual review and adjudication
3. Updates annotations with adjudicated labels
4. Exports final adjudicated dataset
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def load_disagreements(disagreements_file):
    """Load disagreements CSV"""
    df = pd.read_csv(disagreements_file)
    return df

def load_gold_questions(gold_file):
    """Load gold questions (if available)"""
    if not gold_file.exists():
        return {}
    
    with open(gold_file, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)
    
    return {item['id']: item for item in gold_data}

def adjudicate_manually(disagreements_df, output_file):
    """
    Create adjudication file for manual review.
    
    Returns DataFrame with adjudication template.
    """
    # Create adjudication template
    adjudication = []
    
    for _, row in disagreements_df.iterrows():
        adjudication.append({
            'task_id': row['task_id'],
            'text': row['text'],
            'annotator1': row['annotator1'],
            'label1': row['label1'],
            'annotator2': row['annotator2'],
            'label2': row['label2'],
            'adjudicated_label': None,  # To be filled
            'adjudicator': None,
            'adjudication_date': None,
            'notes': ''
        })
    
    adj_df = pd.DataFrame(adjudication)
    adj_df.to_csv(output_file, index=False)
    
    print(f"Created adjudication template: {output_file}")
    print(f"  Total disagreements: {len(adj_df)}")
    print(f"\n  Next steps:")
    print(f"  1. Review each disagreement")
    print(f"  2. Fill in 'adjudicated_label' (0 or 1)")
    print(f"  3. Add your name to 'adjudicator'")
    print(f"  4. Add notes if needed")
    print(f"  5. Run this script again with --apply flag")
    
    return adj_df

def apply_adjudications(original_export, adjudication_file, output_file):
    """
    Apply adjudications to original Label Studio export.
    
    Replaces annotations with adjudicated labels.
    """
    # Load original export
    with open(original_export, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # Load adjudications
    adj_df = pd.read_csv(adjudication_file)
    adj_df = adj_df[adj_df['adjudicated_label'].notna()]  # Only completed
    
    # Create lookup
    adjudications = {}
    for _, row in adj_df.iterrows():
        adjudications[row['task_id']] = {
            'label': int(row['adjudicated_label']),
            'adjudicator': row['adjudicator'],
            'date': row['adjudication_date'],
            'notes': row.get('notes', '')
        }
    
    # Update original data
    updated_count = 0
    for task in original_data:
        task_id = task.get('data', {}).get('id', task.get('id'))
        
        if task_id in adjudications:
            adj = adjudications[task_id]
            
            # Add adjudicated annotation
            adjudicated_ann = {
                "created_by": {"username": adj['adjudicator'] or "adjudicator"},
                "created_at": adj['date'] or datetime.now().isoformat(),
                "result": [
                    {
                        "value": {
                            "choices": ["toxic" if adj['label'] == 1 else "non-toxic"]
                        },
                        "from_name": "toxicity",
                        "to_name": "text"
                    }
                ],
                "adjudicated": True
            }
            
            task['annotations'].append(adjudicated_ann)
            updated_count += 1
    
    # Save updated export
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(original_data, f, indent=2, ensure_ascii=False)
    
    print(f"Applied {updated_count} adjudications")
    print(f"Saved updated export: {output_file}")
    
    return updated_count

def main():
    """Main execution"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  # Create adjudication template:")
        print("  python 12_adjudicate_disagreements.py <disagreements.csv>")
        print("\n  # Apply adjudications:")
        print("  python 12_adjudicate_disagreements.py <disagreements.csv> --apply <original_export.json> <adjudication_file.csv>")
        sys.exit(1)
    
    disagreements_file = Path(sys.argv[1])
    
    if not disagreements_file.exists():
        print(f"Error: File not found: {disagreements_file}")
        sys.exit(1)
    
    if '--apply' in sys.argv:
        # Apply mode
        if len(sys.argv) < 5:
            print("Error: Need original export and adjudication file")
            sys.exit(1)
        
        original_export = Path(sys.argv[3])
        adjudication_file = Path(sys.argv[4])
        
        if not original_export.exists():
            print(f"Error: File not found: {original_export}")
            sys.exit(1)
        
        if not adjudication_file.exists():
            print(f"Error: File not found: {adjudication_file}")
            sys.exit(1)
        
        output_file = original_export.parent / f"{original_export.stem}_adjudicated.json"
        
        print("=" * 60)
        print("Applying Adjudications")
        print("=" * 60)
        
        apply_adjudications(original_export, adjudication_file, output_file)
        
    else:
        # Create template mode
        print("=" * 60)
        print("Create Adjudication Template")
        print("=" * 60)
        
        disagreements_df = load_disagreements(disagreements_file)
        print(f"Loaded {len(disagreements_df)} disagreements")
        
        output_file = disagreements_file.parent / f"{disagreements_file.stem}_adjudication_template.csv"
        adjudicate_manually(disagreements_df, output_file)

if __name__ == "__main__":
    main()

