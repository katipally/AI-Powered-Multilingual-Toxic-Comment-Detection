#!/usr/bin/env python3
"""
Automated annotation using pre-trained toxicity models.

This script:
1. Uses Transformers library with pre-trained toxicity models
2. Generates binary labels (0/1) and subtype classifications
3. Follows the label schema: binary toxicity + subtype taxonomy
4. Creates annotated CSV ready for review
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

# Set device
device = 0 if torch.cuda.is_available() else -1

def load_toxicity_classifier():
    """Load pre-trained toxicity classifier"""
    print("Loading toxicity classifier...")
    try:
        # Use a multilingual toxicity model
        classifier = pipeline(
            "text-classification",
            model="unitary/toxic-bert",
            device=device
        )
        print("Loaded: unitary/toxic-bert")
        return classifier
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Falling back to basic sentiment analysis...")
        return None

def classify_toxicity_binary(text, classifier):
    """Classify text as toxic (1) or non-toxic (0)"""
    if classifier is None:
        # Fallback: simple keyword-based detection
        toxic_keywords = ['hate', 'kill', 'stupid', 'idiot', 'die', 'damn', 'fuck']
        text_lower = text.lower()
        return 1 if any(keyword in text_lower for keyword in toxic_keywords) else 0
    
    try:
        result = classifier(text[:512])  # Limit length
        if isinstance(result, list):
            result = result[0]
        
        label = result.get('label', '').lower()
        score = result.get('score', 0.0)
        
        # Convert to binary
        if 'toxic' in label or 'hate' in label or score > 0.5:
            return 1
        else:
            return 0
    except:
        return 0

def classify_subtypes(text, label):
    """Classify toxicity subtypes if toxic"""
    if label == 0:
        return []
    
    subtypes = []
    text_lower = text.lower()
    
    # Hate speech indicators
    hate_keywords = ['race', 'religion', 'gender', 'sexual', 'identity', 'ethnic', 'dehumanize']
    if any(keyword in text_lower for keyword in hate_keywords):
        subtypes.append('hate')
    
    # Threat indicators
    threat_keywords = ['kill', 'hurt', 'harm', 'attack', 'violence', 'death', 'threat']
    if any(keyword in text_lower for keyword in threat_keywords):
        subtypes.append('threat')
    
    # Insult indicators
    insult_keywords = ['stupid', 'idiot', 'moron', 'fool', 'dumb', 'retard', 'chutiya', 'gandu']
    if any(keyword in text_lower for keyword in insult_keywords):
        subtypes.append('insult')
    
    # Harassment indicators
    harassment_keywords = ['harass', 'bully', 'stalk', 'repeated', 'target']
    if any(keyword in text_lower for keyword in harassment_keywords):
        subtypes.append('harassment')
    
    # Self-harm indicators
    self_harm_keywords = ['suicide', 'kill yourself', 'self-harm', 'end your life']
    if any(keyword in text_lower for keyword in self_harm_keywords):
        subtypes.append('self_harm')
    
    # If toxic but no specific subtype, default to insult
    if not subtypes:
        subtypes.append('insult')
    
    return subtypes

def determine_confidence(text, label, subtypes):
    """Determine confidence level"""
    # Simple heuristic based on text characteristics
    if len(text) < 20:
        return 'low'
    
    # High confidence if clear toxic keywords
    toxic_indicators = ['hate', 'kill', 'stupid', 'idiot', 'die', 'fuck', 'chutiya']
    has_clear_indicators = any(indicator in text.lower() for indicator in toxic_indicators)
    
    if has_clear_indicators and label == 1:
        return 'high'
    elif label == 0 and len(text) > 50:
        return 'high'
    else:
        return 'medium'

def annotate_batch(df, classifier, batch_size=100):
    """Annotate a batch of samples"""
    annotations = []
    
    for idx, row in df.iterrows():
        text = str(row['text'])
        
        # Binary classification
        binary_label = classify_toxicity_binary(text, classifier)
        
        # Subtype classification
        subtypes = classify_subtypes(text, binary_label)
        
        # Confidence
        confidence = determine_confidence(text, binary_label, subtypes)
        
        annotations.append({
            'id': row['id'],
            'text': text,
            'label': binary_label,
            'toxic_types': subtypes,
            'confidence': confidence,
            'annotator_id': 'automated_model',
            'notes': 'Auto-annotated using pre-trained model. Requires human review.'
        })
        
        if (idx + 1) % batch_size == 0:
            print(f"  Annotated {idx + 1:,} / {len(df):,} samples...")
    
    return pd.DataFrame(annotations)

def main():
    """Main execution"""
    print("=" * 60)
    print("Automated Annotation System")
    print("=" * 60)
    
    # Load data
    data_path = Path(__file__).parent.parent.parent / "data" / "unlabeled" / "for_annotation.csv"
    print(f"\nLoading data from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df):,} samples")
    
    # Load classifier
    classifier = load_toxicity_classifier()
    
    # Annotate
    print(f"\nAnnotating {len(df):,} samples...")
    print("This may take a while...")
    
    annotated_df = annotate_batch(df, classifier)
    
    print(f"\nAnnotation complete!")
    print(f"  Toxic: {(annotated_df['label'] == 1).sum():,}")
    print(f"  Non-toxic: {(annotated_df['label'] == 0).sum():,}")
    
    # Merge with original data
    result_df = df.copy()
    result_df['label'] = annotated_df['label'].values
    result_df['toxic_types'] = annotated_df['toxic_types'].apply(lambda x: ','.join(x) if x else '')
    result_df['confidence'] = annotated_df['confidence'].values
    result_df['annotator_id'] = annotated_df['annotator_id'].values
    result_df['notes'] = annotated_df['notes'].values
    
    # Save annotated data
    output_dir = Path(__file__).parent.parent.parent / "data" / "annotated"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "automated_annotations.csv"
    result_df.to_csv(output_file, index=False)
    print(f"\nSaved annotated data: {output_file}")
    
    # Create summary
    summary = {
        "annotation_date": datetime.now().isoformat(),
        "total_samples": len(result_df),
        "toxic_count": int((result_df['label'] == 1).sum()),
        "non_toxic_count": int((result_df['label'] == 0).sum()),
        "method": "automated_pre-trained_model",
        "annotator": "automated_model",
        "confidence_distribution": result_df['confidence'].value_counts().to_dict(),
        "subtype_counts": {
            "hate": int(result_df['toxic_types'].str.contains('hate', na=False).sum()),
            "threat": int(result_df['toxic_types'].str.contains('threat', na=False).sum()),
            "insult": int(result_df['toxic_types'].str.contains('insult', na=False).sum()),
            "harassment": int(result_df['toxic_types'].str.contains('harassment', na=False).sum()),
            "self_harm": int(result_df['toxic_types'].str.contains('self_harm', na=False).sum())
        },
        "note": "Auto-annotated. Requires human review and validation."
    }
    
    summary_file = output_dir / "automated_annotation_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Saved summary: {summary_file}")
    
    print("\n" + "=" * 60)
    print("IMPORTANT: These are automated annotations.")
    print("They MUST be reviewed by humans before use.")
    print("Use this as a starting point, not final labels.")
    print("=" * 60)

if __name__ == "__main__":
    main()

