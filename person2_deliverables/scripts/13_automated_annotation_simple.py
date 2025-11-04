#!/usr/bin/env python3
"""
Simplified automated annotation using rule-based and keyword detection.

This script:
1. Uses rule-based classification following the label schema
2. Generates binary labels (0/1) and subtype classifications
3. Follows toxicity binary + subtype taxonomy
4. Creates annotated CSV ready for review
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import re

def classify_toxicity_binary(text):
    """
    Classify text as toxic (1) or non-toxic (0) using rule-based approach.
    Follows the annotation guidelines schema.
    """
    if pd.isna(text) or not isinstance(text, str):
        return 0
    
    text_lower = text.lower()
    
    # Toxic indicators (following guidelines)
    toxic_patterns = [
        # Hate speech
        r'\b(all|every)\s+\w+\s+(are|is)\s+(criminals|animals|worthless|trash)',
        r'\b(racist|sexist|homophobic|transphobic)\b',
        
        # Threats
        r'\b(kill|hurt|harm|attack|violence|death|threat|destroy)\s+(you|them|your|their)',
        r'\b(i\s+will|i\'ll|gonna)\s+(find|hurt|kill|attack)',
        
        # Severe insults/profanity
        r'\b(stupid|idiot|moron|fool|dumb|retard|asshole|bastard)\b',
        r'\b(chutiya|gandu|bhenchod|madarchod|harami)\b',  # Hindi profanity
        
        # Self-harm
        r'\b(kill\s+yourself|end\s+your\s+life|commit\s+suicide|self-harm)\b',
        
        # Harassment patterns
        r'\b(repeatedly|over\s+and\s+over|again\s+and\s+again)\s+\w+\s+(you|them)',
    ]
    
    # Check for toxic patterns
    for pattern in toxic_patterns:
        if re.search(pattern, text_lower):
            return 1
    
    # Non-toxic indicators (constructive, sarcasm markers)
    non_toxic_indicators = [
        r'\b(/s|sarcasm|lol|haha|😂|😏)\b',  # Sarcasm markers
        r'\b(i\s+disagree|i\s+think|in\s+my\s+opinion|constructive)\b',  # Constructive
        r'\b(yaar|bhai|dost)\b',  # Friendly Hindi terms
    ]
    
    # If has sarcasm markers and no toxic patterns, likely non-toxic
    has_sarcasm = any(re.search(pattern, text_lower) for pattern in non_toxic_indicators)
    if has_sarcasm:
        return 0
    
    # Default: non-toxic (conservative approach)
    return 0

def classify_subtypes(text, label):
    """
    Classify toxicity subtypes following the taxonomy.
    Returns list of applicable subtypes.
    """
    if label == 0:
        return []
    
    subtypes = []
    text_lower = text.lower()
    
    # 1. Hate (hate)
    hate_patterns = [
        r'\b(race|religion|gender|sexual\s+orientation|identity|ethnic|dehumanize)\b',
        r'\b(all|every)\s+\w+\s+(are|is)\s+(criminals|animals|worthless)',
        r'\b(racist|sexist|homophobic|transphobic|discriminate)\b',
    ]
    if any(re.search(pattern, text_lower) for pattern in hate_patterns):
        subtypes.append('hate')
    
    # 2. Threat (threat)
    threat_patterns = [
        r'\b(kill|hurt|harm|attack|violence|death|threat|destroy)\s+(you|them|your|their)',
        r'\b(i\s+will|i\'ll|gonna)\s+(find|hurt|kill|attack|destroy)',
        r'\b(coming\s+for\s+you|find\s+you|get\s+you)',
    ]
    if any(re.search(pattern, text_lower) for pattern in threat_patterns):
        subtypes.append('threat')
    
    # 3. Insult (insult)
    insult_patterns = [
        r'\b(stupid|idiot|moron|fool|dumb|retard|asshole|bastard|trash|garbage)\b',
        r'\b(chutiya|gandu|bhenchod|madarchod|harami|bewakoof)\b',  # Hindi insults
        r'\b(you\'re\s+an|you\s+are\s+an)\s+\w+\s+(idiot|moron|fool)',
    ]
    if any(re.search(pattern, text_lower) for pattern in insult_patterns):
        subtypes.append('insult')
    
    # 4. Harassment (harassment)
    harassment_patterns = [
        r'\b(harass|bully|stalk|repeatedly\s+target|cyberbully)\b',
        r'\b(over\s+and\s+over|again\s+and\s+again)\s+\w+\s+(you|them)',
    ]
    if any(re.search(pattern, text_lower) for pattern in harassment_patterns):
        subtypes.append('harassment')
    
    # 5. Self-Harm (self_harm)
    self_harm_patterns = [
        r'\b(kill\s+yourself|end\s+your\s+life|commit\s+suicide|self-harm|just\s+die)\b',
        r'\b(you\s+should\s+die|end\s+it\s+all|no\s+one\s+would\s+miss)',
    ]
    if any(re.search(pattern, text_lower) for pattern in self_harm_patterns):
        subtypes.append('self_harm')
    
    # If toxic but no specific subtype, default to insult
    if not subtypes:
        subtypes.append('insult')
    
    return subtypes

def determine_confidence(text, label, subtypes):
    """
    Determine confidence level following guidelines.
    High: Clear indicators, Medium: Some indicators, Low: Ambiguous
    """
    if len(text) < 10:
        return 'low'
    
    text_lower = text.lower()
    
    # High confidence indicators
    strong_toxic_indicators = ['kill', 'hate', 'stupid', 'idiot', 'chutiya', 'gandu', 'die']
    strong_non_toxic_indicators = ['i disagree', 'i think', '/s', 'lol', 'yaar', 'bhai']
    
    has_strong_toxic = any(indicator in text_lower for indicator in strong_toxic_indicators)
    has_strong_non_toxic = any(indicator in text_lower for indicator in strong_non_toxic_indicators)
    
    if label == 1 and has_strong_toxic and len(subtypes) > 0:
        return 'high'
    elif label == 0 and has_strong_non_toxic and len(text) > 30:
        return 'high'
    elif label == 1 or label == 0:
        return 'medium'
    else:
        return 'low'

def annotate_dataset(df):
    """Annotate entire dataset"""
    print(f"Annotating {len(df):,} samples...")
    
    annotations = []
    for idx, row in df.iterrows():
        text = str(row['text']) if pd.notna(row['text']) else ''
        
        # Binary classification
        binary_label = classify_toxicity_binary(text)
        
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
            'annotator_id': 'automated_rule_based',
            'notes': 'Auto-annotated using rule-based classification. Requires human review.'
        })
        
        if (idx + 1) % 1000 == 0:
            print(f"  Progress: {idx + 1:,} / {len(df):,} ({100*(idx+1)/len(df):.1f}%)")
    
    return pd.DataFrame(annotations)

def main():
    """Main execution"""
    print("=" * 60)
    print("Automated Annotation - Rule-Based Classification")
    print("Following Label Schema: Binary + Subtypes")
    print("=" * 60)
    
    # Load data
    data_path = Path(__file__).parent.parent.parent / "data" / "unlabeled" / "for_annotation.csv"
    print(f"\nLoading: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df):,} samples")
    
    # Annotate
    annotated_df = annotate_dataset(df)
    
    # Merge with original
    result_df = df.copy()
    result_df['label'] = annotated_df['label'].values
    result_df['toxic_types'] = annotated_df['toxic_types'].apply(lambda x: ','.join(x) if x else '')
    result_df['confidence'] = annotated_df['confidence'].values
    result_df['annotator_id'] = annotated_df['annotator_id'].values
    result_df['notes'] = annotated_df['notes'].values
    
    # Statistics
    print(f"\n" + "=" * 60)
    print("Annotation Results:")
    print(f"  Total samples: {len(result_df):,}")
    print(f"  Toxic (1): {(result_df['label'] == 1).sum():,} ({(result_df['label'] == 1).sum()/len(result_df)*100:.1f}%)")
    print(f"  Non-toxic (0): {(result_df['label'] == 0).sum():,} ({(result_df['label'] == 0).sum()/len(result_df)*100:.1f}%)")
    
    # Subtype distribution
    print(f"\nSubtype Distribution (for toxic comments):")
    for subtype in ['hate', 'threat', 'insult', 'harassment', 'self_harm']:
        count = result_df['toxic_types'].str.contains(subtype, na=False).sum()
        print(f"  {subtype}: {count:,}")
    
    # Save
    output_dir = Path(__file__).parent.parent.parent / "data" / "annotated"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "automated_annotations.csv"
    result_df.to_csv(output_file, index=False)
    print(f"\nSaved: {output_file}")
    
    # Update original file
    original_file = data_path
    result_df[['id', 'text', 'label', 'source', 'language', 'split', 'code_mixed', 'metadata']].to_csv(
        original_file, index=False
    )
    print(f"Updated original file: {original_file}")
    
    print("\n" + "=" * 60)
    print("Annotation complete!")
    print("NOTE: These are automated annotations.")
    print("Please review and validate before final use.")
    print("=" * 60)

if __name__ == "__main__":
    main()

