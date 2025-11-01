#!/usr/bin/env python3
"""
Export annotations from Label Studio and convert to final dataset format.

This script:
1. Loads Label Studio exports
2. Aggregates multiple annotations (voting/adjudication)
3. Validates against schema
4. Exports in JSONL and CSV formats
5. Generates batch manifests
"""

import pandas as pd
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter

def load_label_studio_export(export_file):
    """Load Label Studio export (same as IAA script)"""
    with open(export_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    annotations = []
    
    for task in data:
        task_id = task.get('data', {}).get('id', task.get('id'))
        text = task.get('data', {}).get('text', '')
        source_data = task.get('data', {})
        
        for ann in task.get('annotations', []):
            annotator = ann.get('created_by', {}).get('username', 'unknown')
            result = ann.get('result', [])
            
            binary_label = None
            subtypes = []
            confidence = None
            notes = None
            
            for item in result:
                value = item.get('value', {})
                
                if 'choices' in value:
                    choices = value.get('choices', [])
                    if choices:
                        if 'toxic' in choices:
                            binary_label = 1
                        elif 'non-toxic' in choices:
                            binary_label = 0
                        
                        # Check if this is subtypes
                        if 'toxic_types' in str(item.get('from_name', '')):
                            subtypes = choices
                        
                        # Check if this is confidence
                        if 'confidence' in value.get('from_name', '').lower():
                            confidence = choices[0] if choices else None
            
            annotations.append({
                'id': task_id,
                'text': text,
                'annotator': annotator,
                'label': binary_label,
                'subtypes': subtypes if isinstance(subtypes, list) else [],
                'confidence': confidence,
                'notes': notes,
                'source': source_data.get('source', 'unknown'),
                'language': source_data.get('language', 'unknown'),
                'code_mixed': source_data.get('code_mixed', 'False') == 'True'
            })
    
    return pd.DataFrame(annotations)

def aggregate_annotations(df, method='majority_vote'):
    """
    Aggregate multiple annotations per item.
    
    Methods:
    - majority_vote: Use most common label
    - adjudicated: Use adjudicator's label (if available)
    - confidence_weighted: Weight by confidence (high=3, medium=2, low=1)
    """
    aggregated = []
    
    for item_id in df['id'].unique():
        item_anns = df[df['id'] == item_id].copy()
        
        # Get first row for metadata
        first_row = item_anns.iloc[0]
        
        if method == 'majority_vote':
            # Binary label: majority vote
            labels = item_anns['label'].dropna().tolist()
            if labels:
                label_counts = Counter(labels)
                final_label = label_counts.most_common(1)[0][0]
                agreement = label_counts[final_label] / len(labels)
            else:
                final_label = None
                agreement = 0.0
            
            # Subtypes: union of all selected
            all_subtypes = []
            for subtypes in item_anns['subtypes']:
                if isinstance(subtypes, list):
                    all_subtypes.extend(subtypes)
            final_subtypes = list(set(all_subtypes))  # Unique
            
            # Confidence: average (convert to numeric)
            conf_map = {'high': 3, 'medium': 2, 'low': 1}
            confidences = [conf_map.get(c, 1) for c in item_anns['confidence'].dropna() if c]
            avg_confidence = np.mean(confidences) if confidences else None
            
            # Notes: combine (or use adjudicator's)
            notes = ' | '.join(item_anns['notes'].dropna().astype(str).unique())
        
        elif method == 'adjudicated':
            # Use adjudicator's annotation if available
            adjudicator_ann = item_anns[item_anns['annotator'].str.contains('adjudicator|expert|lead', case=False, na=False)]
            
            if len(adjudicator_ann) > 0:
                adjud_row = adjudicator_ann.iloc[0]
                final_label = adjud_row['label']
                final_subtypes = adjud_row['subtypes'] if isinstance(adjud_row['subtypes'], list) else []
                avg_confidence = 3  # Adjudicator is high confidence
                notes = str(adjud_row['notes']) if pd.notna(adjud_row['notes']) else ''
                agreement = 1.0
            else:
                # Fall back to majority vote
                return aggregate_annotations(item_anns, method='majority_vote')
        
        else:  # confidence_weighted
            # Weight by confidence
            conf_map = {'high': 3, 'medium': 2, 'low': 1}
            weights = []
            weighted_labels = []
            
            for _, row in item_anns.iterrows():
                if pd.notna(row['label']):
                    weight = conf_map.get(row['confidence'], 1)
                    weights.append(weight)
                    weighted_labels.append((row['label'], weight))
            
            if weighted_labels:
                label_scores = {}
                total_weight = sum(weights)
                for label, weight in weighted_labels:
                    label_scores[label] = label_scores.get(label, 0) + weight
                final_label = max(label_scores, key=label_scores.get)
                agreement = label_scores[final_label] / total_weight
            else:
                final_label = None
                agreement = 0.0
            
            # Subtypes: union
            all_subtypes = []
            for subtypes in item_anns['subtypes']:
                if isinstance(subtypes, list):
                    all_subtypes.extend(subtypes)
            final_subtypes = list(set(all_subtypes))
            
            avg_confidence = np.mean([conf_map.get(c, 1) for c in item_anns['confidence'].dropna() if c]) if item_anns['confidence'].notna().any() else None
            notes = ' | '.join(item_anns['notes'].dropna().astype(str).unique())
        
        aggregated.append({
            'id': item_id,
            'text': first_row['text'],
            'label': int(final_label) if final_label is not None else None,
            'toxic_types': final_subtypes,
            'confidence': avg_confidence,
            'agreement': agreement,
            'n_annotators': len(item_anns),
            'source': first_row['source'],
            'language': first_row['language'],
            'code_mixed': first_row['code_mixed'],
            'notes': notes
        })
    
    return pd.DataFrame(aggregated)

def validate_schema(df):
    """Validate exported data against schema"""
    errors = []
    warnings = []
    
    # Required columns
    required = ['id', 'text', 'label', 'source', 'language', 'code_mixed']
    for col in required:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
    
    # Check IDs are unique
    if 'id' in df.columns:
        if df['id'].duplicated().any():
            errors.append("Duplicate IDs found")
    
    # Check labels are 0 or 1
    if 'label' in df.columns:
        invalid_labels = df[~df['label'].isin([0, 1, None]) & df['label'].notna()]
        if len(invalid_labels) > 0:
            errors.append(f"Invalid label values: {len(invalid_labels)} items")
        
        null_labels = df['label'].isna().sum()
        if null_labels > 0:
            warnings.append(f"Null labels: {null_labels} items")
    
    # Check text is not empty
    if 'text' in df.columns:
        empty_text = df[df['text'].str.strip() == '']
        if len(empty_text) > 0:
            errors.append(f"Empty text: {len(empty_text)} items")
    
    return errors, warnings

def export_to_jsonl(df, output_file):
    """Export to JSONL format (one JSON object per line)"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            record = {
                'id': row['id'],
                'text': row['text'],
                'label': int(row['label']) if pd.notna(row['label']) else None,
                'source': row['source'],
                'language': row['language'],
                'split': 'train',  # Can be updated later
                'code_mixed': bool(row['code_mixed']),
                'metadata': {
                    'toxic_types': row.get('toxic_types', []),
                    'confidence': row.get('confidence'),
                    'agreement': row.get('agreement'),
                    'n_annotators': int(row.get('n_annotators', 1)),
                    'notes': row.get('notes', '')
                }
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"Exported JSONL: {output_file} ({len(df):,} items)")

def export_to_csv(df, output_file):
    """Export to CSV format (expanding metadata)"""
    # Flatten metadata for CSV
    export_df = df.copy()
    
    # Convert toxic_types list to comma-separated string
    if 'toxic_types' in export_df.columns:
        export_df['toxic_types'] = export_df['toxic_types'].apply(
            lambda x: ','.join(x) if isinstance(x, list) else ''
        )
    
    # Create metadata JSON string
    metadata_cols = ['toxic_types', 'confidence', 'agreement', 'n_annotators', 'notes']
    export_df['metadata'] = export_df.apply(
        lambda row: json.dumps({
            k: row.get(k) for k in metadata_cols if k in row
        }, ensure_ascii=False),
        axis=1
    )
    
    # Select final columns
    final_cols = ['id', 'text', 'label', 'source', 'language', 'split', 'code_mixed', 'metadata']
    export_df = export_df[[c for c in final_cols if c in export_df.columns]]
    
    # Set split column
    if 'split' not in export_df.columns:
        export_df['split'] = 'train'
    
    export_df.to_csv(output_file, index=False)
    print(f"Exported CSV: {output_file} ({len(export_df):,} items)")

def create_batch_manifest(df, batch_name, output_dir):
    """Create batch manifest with metadata"""
    manifest = {
        "batch_name": batch_name,
        "creation_date": datetime.now().isoformat(),
        "total_samples": int(len(df)),
        "label_distribution": {
            "non_toxic": int((df['label'] == 0).sum()),
            "toxic": int((df['label'] == 1).sum()),
            "unlabeled": int(df['label'].isna().sum())
        },
        "sources": df['source'].value_counts().to_dict(),
        "languages": df['language'].value_counts().head(10).to_dict(),
        "code_mixed_count": int(df['code_mixed'].sum()),
        "average_agreement": float(df['agreement'].mean()) if 'agreement' in df.columns else None,
        "annotation_method": "Label Studio",
        "schema_version": "1.0"
    }
    
    manifest_file = output_dir / f"{batch_name}_manifest.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"Created batch manifest: {manifest_file}")
    return manifest

def main():
    """Main execution"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python 10_export_annotations.py <label_studio_export.json> [aggregation_method]")
        print("\nAggregation methods:")
        print("  - majority_vote (default)")
        print("  - adjudicated (use adjudicator annotations)")
        print("  - confidence_weighted (weight by confidence)")
        print("\nExample:")
        print("  python 10_export_annotations.py annotation/exports/pilot_annotations.json majority_vote")
        sys.exit(1)
    
    export_file = Path(sys.argv[1])
    method = sys.argv[2] if len(sys.argv) > 2 else 'majority_vote'
    
    if not export_file.exists():
        print(f"Error: File not found: {export_file}")
        sys.exit(1)
    
    print("=" * 60)
    print("Annotation Export")
    print("=" * 60)
    print(f"Loading: {export_file}")
    print(f"Aggregation method: {method}")
    
    # Load annotations
    df = load_label_studio_export(export_file)
    print(f"Loaded {len(df):,} annotations for {df['id'].nunique():,} items")
    
    # Aggregate
    print(f"\nAggregating annotations...")
    aggregated = aggregate_annotations(df, method=method)
    print(f"Aggregated to {len(aggregated):,} items")
    
    # Validate
    print(f"\nValidating schema...")
    errors, warnings = validate_schema(aggregated)
    
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix errors before exporting")
        return
    
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    print("Schema validation passed")
    
    # Create output directory
    output_dir = export_file.parent / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate batch name
    batch_name = export_file.stem.replace('_annotations', '').replace('_export', '')
    
    # Export formats
    print(f"\nExporting...")
    jsonl_file = output_dir / f"{batch_name}.jsonl"
    csv_file = output_dir / f"{batch_name}.csv"
    
    export_to_jsonl(aggregated, jsonl_file)
    export_to_csv(aggregated, csv_file)
    
    # Create manifest
    manifest = create_batch_manifest(aggregated, batch_name, output_dir)
    
    print("\n" + "=" * 60)
    print("Export Complete!")
    print("=" * 60)
    print(f"JSONL: {jsonl_file}")
    print(f"CSV: {csv_file}")
    print(f"Manifest: {output_dir / f'{batch_name}_manifest.json'}")
    print(f"\nTotal items: {len(aggregated):,}")
    print(f"Toxic: {(aggregated['label'] == 1).sum():,}")
    print(f"Non-toxic: {(aggregated['label'] == 0).sum():,}")
    print("=" * 60)

if __name__ == "__main__":
    main()

