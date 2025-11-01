#!/usr/bin/env python3
"""
Calculate Inter-Annotator Agreement (IAA) metrics.

This script:
1. Loads annotations from Label Studio exports
2. Calculates Cohen's kappa for binary toxicity labels
3. Calculates per-subtype agreement
4. Generates IAA reports
5. Identifies disagreements for adjudication
"""

import pandas as pd
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.metrics import cohen_kappa_score, confusion_matrix, classification_report
from collections import defaultdict

def load_label_studio_export(export_file):
    """
    Load Label Studio export file (JSON format).
    
    Expected format:
    [
        {
            "id": 1,
            "data": {"text": "...", "id": "..."},
            "annotations": [
                {
                    "created_by": {"username": "annotator1"},
                    "result": [
                        {"value": {"choices": ["toxic"]}},
                        {"value": {"choices": ["hate", "insult"]}},
                        ...
                    ]
                }
            ]
        }
    ]
    """
    with open(export_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    annotations = []
    
    for task in data:
        task_id = task.get('data', {}).get('id', task.get('id'))
        text = task.get('data', {}).get('text', '')
        
        for ann in task.get('annotations', []):
            annotator = ann.get('created_by', {}).get('username', 'unknown')
            result = ann.get('result', [])
            
            # Extract binary label
            binary_label = None
            subtypes = []
            confidence = None
            notes = None
            
            for item in result:
                value = item.get('value', {})
                
                # Binary toxicity (from Choices)
                if 'choices' in value:
                    choices = value.get('choices', [])
                    if choices:
                        if 'toxic' in choices:
                            binary_label = 1
                        elif 'non-toxic' in choices:
                            binary_label = 0
                
                # Subtypes (from multi-choice)
                if 'toxic_types' in str(item.get('from_name', '')):
                    if 'choices' in value:
                        subtypes = value.get('choices', [])
                
                # Confidence
                if 'confidence' in value.get('from_name', '').lower():
                    if 'choices' in value:
                        conf_choices = value.get('choices', [])
                        if conf_choices:
                            confidence = conf_choices[0]
                
                # Notes (from TextArea)
                if 'notes' in value.get('from_name', '').lower():
                    notes = value.get('value', {}).get('text', '')
            
            annotations.append({
                'task_id': task_id,
                'text': text,
                'annotator': annotator,
                'label': binary_label,
                'subtypes': subtypes,
                'confidence': confidence,
                'notes': notes
            })
    
    return pd.DataFrame(annotations)

def calculate_binary_kappa(df):
    """Calculate Cohen's kappa for binary toxicity labels"""
    # Get items annotated by multiple annotators
    multi_annotated = df.groupby('task_id').filter(lambda x: len(x) > 1)
    
    if len(multi_annotated) == 0:
        return None, "No items with multiple annotations"
    
    # Pivot to get annotations side-by-side
    pivot = multi_annotated.pivot(index='task_id', columns='annotator', values='label')
    
    # Calculate pairwise kappa for all annotator pairs
    annotators = pivot.columns.tolist()
    kappa_results = {}
    
    for i, ann1 in enumerate(annotators):
        for ann2 in annotators[i+1:]:
            # Get common annotations (non-null for both)
            common = pivot[[ann1, ann2]].dropna()
            
            if len(common) < 2:
                continue
            
            kappa = cohen_kappa_score(common[ann1], common[ann2])
            kappa_results[f"{ann1}_vs_{ann2}"] = {
                'kappa': kappa,
                'n_common': len(common)
            }
    
    # Calculate average kappa
    if kappa_results:
        avg_kappa = np.mean([v['kappa'] for v in kappa_results.values()])
        return avg_kappa, kappa_results
    else:
        return None, "No overlapping annotations"

def calculate_subtype_agreement(df):
    """Calculate agreement for each toxicity subtype"""
    # Get items annotated by multiple annotators
    multi_annotated = df.groupby('task_id').filter(lambda x: len(x) > 1)
    
    if len(multi_annotated) == 0:
        return {}
    
    subtype_results = {}
    subtypes = ['hate', 'threat', 'insult', 'harassment', 'self_harm']
    
    for subtype in subtypes:
        # For each task, check if subtype was selected by annotators
        agreement_data = []
        
        for task_id in multi_annotated['task_id'].unique():
            task_anns = multi_annotated[multi_annotated['task_id'] == task_id]
            
            if len(task_anns) < 2:
                continue
            
            # Get subtype selections for each annotator
            selections = []
            for _, ann in task_anns.iterrows():
                ann_subtypes = ann.get('subtypes', []) if isinstance(ann.get('subtypes'), list) else []
                selected = 1 if subtype in ann_subtypes else 0
                selections.append(selected)
            
            # Agreement: all selected or all not selected
            if len(set(selections)) == 1:
                agreement_data.append(1)  # Agreed
            else:
                agreement_data.append(0)  # Disagreed
        
        if agreement_data:
            subtype_results[subtype] = {
                'agreement_rate': np.mean(agreement_data),
                'n_items': len(agreement_data)
            }
    
    return subtype_results

def generate_confusion_analysis(df):
    """Generate confusion matrix and detailed analysis"""
    multi_annotated = df.groupby('task_id').filter(lambda x: len(x) > 1)
    
    if len(multi_annotated) == 0:
        return None
    
    # Get first two annotators for each task (if available)
    confusion_data = []
    
    for task_id in multi_annotated['task_id'].unique():
        task_anns = multi_annotated[multi_annotated['task_id'] == task_id]
        
        if len(task_anns) >= 2:
            annotators = task_anns['annotator'].unique()[:2]
            ann1_data = task_anns[task_anns['annotator'] == annotators[0]].iloc[0]
            ann2_data = task_anns[task_anns['annotator'] == annotators[1]].iloc[0]
            
            confusion_data.append({
                'task_id': task_id,
                'text': ann1_data['text'],
                'annotator1': annotators[0],
                'label1': ann1_data['label'],
                'annotator2': annotators[1],
                'label2': ann2_data['label'],
                'agree': ann1_data['label'] == ann2_data['label']
            })
    
    confusion_df = pd.DataFrame(confusion_data)
    
    if len(confusion_df) == 0:
        return None
    
    # Create confusion matrix
    cm = confusion_matrix(confusion_df['label1'], confusion_df['label2'], labels=[0, 1])
    
    return {
        'confusion_matrix': cm.tolist(),
        'agreement_rate': confusion_df['agree'].mean(),
        'disagreements': confusion_df[~confusion_df['agree']].to_dict('records')
    }

def generate_iaa_report(df, output_dir):
    """Generate comprehensive IAA report"""
    print("\n" + "=" * 60)
    print("Inter-Annotator Agreement (IAA) Analysis")
    print("=" * 60)
    
    # Basic statistics
    n_annotators = df['annotator'].nunique()
    n_tasks = df['task_id'].nunique()
    n_annotations = len(df)
    
    print(f"\nBasic Statistics:")
    print(f"  - Annotators: {n_annotators}")
    print(f"  - Tasks: {n_tasks}")
    print(f"  - Total annotations: {n_annotations}")
    print(f"  - Avg annotations per task: {n_annotations / n_tasks:.2f}")
    
    # Binary kappa
    avg_kappa, kappa_details = calculate_binary_kappa(df)
    
    print(f"\nBinary Toxicity Agreement (Cohen's κ):")
    if avg_kappa is not None:
        print(f"  - Average κ: {avg_kappa:.4f}")
        print(f"  - Interpretation: ", end="")
        if avg_kappa >= 0.75:
            print("Excellent agreement")
        elif avg_kappa >= 0.60:
            print("Good agreement")
        elif avg_kappa >= 0.40:
            print("Moderate agreement")
        else:
            print("Poor agreement")
        
        print(f"\n  Pairwise κ scores:")
        for pair, details in kappa_details.items():
            print(f"    - {pair}: {details['kappa']:.4f} (n={details['n_common']})")
    else:
        print(f"  - {kappa_details}")
    
    # Subtype agreement
    subtype_agreement = calculate_subtype_agreement(df)
    
    if subtype_agreement:
        print(f"\nSubtype Agreement:")
        for subtype, details in subtype_agreement.items():
            rate = details['agreement_rate']
            print(f"  - {subtype}: {rate:.2%} agreement (n={details['n_items']})")
    
    # Confusion analysis
    confusion_analysis = generate_confusion_analysis(df)
    
    if confusion_analysis:
        print(f"\nConfusion Analysis:")
        print(f"  - Overall agreement rate: {confusion_analysis['agreement_rate']:.2%}")
        print(f"  - Disagreements: {len(confusion_analysis['disagreements'])}")
        
        cm = np.array(confusion_analysis['confusion_matrix'])
        print(f"\n  Confusion Matrix (Annotator1 vs Annotator2):")
        print(f"                 Non-Toxic  Toxic")
        print(f"    Non-Toxic    {cm[0,0]:8d}  {cm[0,1]:5d}")
        print(f"    Toxic        {cm[1,0]:8d}  {cm[1,1]:5d}")
    
    # Save report
    report = {
        "generation_date": datetime.now().isoformat(),
        "basic_stats": {
            "n_annotators": int(n_annotators),
            "n_tasks": int(n_tasks),
            "n_annotations": int(n_annotations)
        },
        "binary_kappa": {
            "average_kappa": float(avg_kappa) if avg_kappa is not None else None,
            "pairwise": {k: {"kappa": float(v['kappa']), "n": int(v['n_common'])} 
                        for k, v in (kappa_details.items() if isinstance(kappa_details, dict) else {})}
        },
        "subtype_agreement": {k: {"agreement_rate": float(v['agreement_rate']), "n": int(v['n_items'])}
                             for k, v in subtype_agreement.items()},
        "confusion_analysis": confusion_analysis
    }
    
    report_file = output_dir / "iaa_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved IAA report: {report_file}")
    
    # Save disagreements for adjudication
    if confusion_analysis and confusion_analysis['disagreements']:
        disagreements_df = pd.DataFrame(confusion_analysis['disagreements'])
        disagreements_file = output_dir / "disagreements.csv"
        disagreements_df.to_csv(disagreements_file, index=False)
        print(f"Saved disagreements: {disagreements_file}")
        print(f"  Total disagreements: {len(disagreements_df)}")
    
    return report

def main():
    """Main execution"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python 9_calculate_iaa.py <label_studio_export.json>")
        print("\nExample:")
        print("  python 9_calculate_iaa.py annotation/exports/pilot_annotations.json")
        sys.exit(1)
    
    export_file = Path(sys.argv[1])
    
    if not export_file.exists():
        print(f"Error: File not found: {export_file}")
        sys.exit(1)
    
    print("=" * 60)
    print("IAA Calculation")
    print("=" * 60)
    print(f"Loading annotations from: {export_file}")
    
    # Load annotations
    df = load_label_studio_export(export_file)
    print(f"Loaded {len(df):,} annotations")
    
    # Create output directory
    output_dir = export_file.parent / "iaa_reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate report
    report = generate_iaa_report(df, output_dir)
    
    print("\n" + "=" * 60)
    if report and report['binary_kappa']['average_kappa']:
        kappa = report['binary_kappa']['average_kappa']
        if kappa >= 0.70:
            print("SUCCESS: Pilot κ ≥ 0.70 - Ready to scale annotation!")
        else:
            print("WARNING: Pilot κ < 0.70 - Refine guidelines and rerun pilot")
    print("=" * 60)

if __name__ == "__main__":
    main()

