#!/usr/bin/env python3
"""
Generate annotator performance dashboard.

This script:
1. Loads annotations and gold standard questions
2. Calculates accuracy per annotator
3. Generates performance statistics
4. Creates visualization-ready data
"""

import pandas as pd
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def load_gold_questions(gold_file):
    """Load gold standard questions"""
    with open(gold_file, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)
    
    # Convert to dict keyed by ID
    gold_dict = {}
    for item in gold_data:
        gold_dict[item['id']] = {
            'expected_label': item.get('expected_label'),
            'expected_subtypes': item.get('expected_subtypes', []),
            'text': item.get('text', '')
        }
    
    return gold_dict

def load_label_studio_export(export_file):
    """Load Label Studio export (same as script 10)"""
    import json
    import pandas as pd
    
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
                        
                        if 'toxic_types' in str(item.get('from_name', '')):
                            subtypes = choices
                        
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

def load_annotations(export_file):
    """Load Label Studio export"""
    return load_label_studio_export(export_file)

def calculate_annotator_performance(df, gold_dict):
    """Calculate performance metrics per annotator"""
    annotator_stats = {}
    
    for annotator in df['annotator'].unique():
        ann_data = df[df['annotator'] == annotator].copy()
        
        # Filter to gold questions only
        gold_items = ann_data[ann_data['id'].isin(gold_dict.keys())].copy()
        
        if len(gold_items) == 0:
            continue
        
        # Get expected and predicted labels
        gold_items['expected_label'] = gold_items['id'].map(lambda x: gold_dict[x]['expected_label'])
        gold_items = gold_items[gold_items['expected_label'].notna()].copy()
        
        if len(gold_items) == 0:
            continue
        
        # Calculate metrics
        y_true = gold_items['expected_label'].astype(int)
        y_pred = gold_items['label'].astype(int)
        
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        # Per-subtype accuracy (if applicable)
        subtype_accuracy = {}
        for _, row in gold_items.iterrows():
            expected_subs = set(gold_dict[row['id']].get('expected_subtypes', []))
            predicted_subs = set(row['subtypes'] if isinstance(row['subtypes'], list) else [])
            
            for subtype in ['hate', 'threat', 'insult', 'harassment', 'self_harm']:
                if subtype not in subtype_accuracy:
                    subtype_accuracy[subtype] = {'tp': 0, 'total': 0}
                
                expected = subtype in expected_subs
                predicted = subtype in predicted_subs
                
                if expected or predicted:
                    subtype_accuracy[subtype]['total'] += 1
                    if expected == predicted:
                        subtype_accuracy[subtype]['tp'] += 1
        
        subtype_scores = {
            k: v['tp'] / v['total'] if v['total'] > 0 else None
            for k, v in subtype_accuracy.items()
        }
        
        annotator_stats[annotator] = {
            'n_gold_annotated': len(gold_items),
            'n_total_annotated': len(ann_data),
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'subtype_accuracy': {k: float(v) if v is not None else 0.0 
                               for k, v in subtype_scores.items()},
            'average_confidence': ann_data['confidence'].value_counts().to_dict() if 'confidence' in ann_data.columns else {}
        }
    
    return annotator_stats

def generate_dashboard_data(annotator_stats, output_dir):
    """Generate dashboard-ready data"""
    
    # Summary statistics
    summary = {
        "generation_date": datetime.now().isoformat(),
        "n_annotators": len(annotator_stats),
        "average_accuracy": np.mean([s['accuracy'] for s in annotator_stats.values()]),
        "average_f1": np.mean([s['f1_score'] for s in annotator_stats.values()]),
        "annotator_performance": annotator_stats
    }
    
    # Create DataFrame for easy visualization
    df_rows = []
    for ann, stats in annotator_stats.items():
        df_rows.append({
            'annotator': ann,
            'accuracy': stats['accuracy'],
            'precision': stats['precision'],
            'recall': stats['recall'],
            'f1_score': stats['f1_score'],
            'n_gold': stats['n_gold_annotated'],
            'n_total': stats['n_total_annotated']
        })
    
    df_performance = pd.DataFrame(df_rows)
    
    # Save
    summary_file = output_dir / "annotator_performance.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    csv_file = output_dir / "annotator_performance.csv"
    df_performance.to_csv(csv_file, index=False)
    
    return summary, df_performance

def print_dashboard(annotator_stats, df_performance):
    """Print dashboard to console"""
    print("\n" + "=" * 60)
    print("Annotator Performance Dashboard")
    print("=" * 60)
    
    print(f"\nSummary:")
    print(f"  - Total annotators: {len(annotator_stats)}")
    print(f"  - Average accuracy: {df_performance['accuracy'].mean():.2%}")
    print(f"  - Average F1 score: {df_performance['f1_score'].mean():.2%}")
    
    print(f"\nPer-Annotator Performance:")
    print(f"{'Annotator':<20} {'Accuracy':<12} {'F1':<12} {'Gold':<8} {'Total':<8}")
    print("-" * 60)
    
    for _, row in df_performance.sort_values('accuracy', ascending=False).iterrows():
        print(f"{row['annotator']:<20} {row['accuracy']:>11.2%} {row['f1_score']:>11.2%} "
              f"{row['n_gold']:>7} {row['n_total']:>7}")
    
    # Identify annotators needing review
    threshold = 0.80
    low_performers = df_performance[df_performance['accuracy'] < threshold]
    
    if len(low_performers) > 0:
        print(f"\nAnnotators below {threshold:.0%} accuracy threshold:")
        for _, row in low_performers.iterrows():
            print(f"  - {row['annotator']}: {row['accuracy']:.2%} (Review needed)")
    
    print("\n" + "=" * 60)

def main():
    """Main execution"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python 11_annotator_dashboard.py <label_studio_export.json> <gold_questions.json>")
        print("\nExample:")
        print("  python 11_annotator_dashboard.py annotation/exports/pilot_annotations.json annotation/gold_questions.json")
        sys.exit(1)
    
    export_file = Path(sys.argv[1])
    gold_file = Path(sys.argv[2])
    
    if not export_file.exists():
        print(f"Error: File not found: {export_file}")
        sys.exit(1)
    
    if not gold_file.exists():
        print(f"Error: File not found: {gold_file}")
        sys.exit(1)
    
    print("=" * 60)
    print("Annotator Performance Dashboard")
    print("=" * 60)
    
    # Load data
    print(f"\nLoading annotations: {export_file}")
    df = load_annotations(export_file)
    print(f"Loaded {len(df):,} annotations from {df['annotator'].nunique()} annotators")
    
    print(f"\nLoading gold questions: {gold_file}")
    gold_dict = load_gold_questions(gold_file)
    print(f"Loaded {len(gold_dict):,} gold questions")
    
    # Calculate performance
    print(f"\nCalculating performance metrics...")
    annotator_stats = calculate_annotator_performance(df, gold_dict)
    
    if len(annotator_stats) == 0:
        print("No annotators found with gold question annotations")
        print("   Make sure gold questions are annotated in the export file")
        return
    
    # Generate dashboard
    output_dir = export_file.parent / "dashboards"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    summary, df_performance = generate_dashboard_data(annotator_stats, output_dir)
    
    # Print dashboard
    print_dashboard(annotator_stats, df_performance)
    
    print(f"\nDashboard saved:")
    print(f"  - JSON: {output_dir / 'annotator_performance.json'}")
    print(f"  - CSV: {output_dir / 'annotator_performance.csv'}")

if __name__ == "__main__":
    main()

