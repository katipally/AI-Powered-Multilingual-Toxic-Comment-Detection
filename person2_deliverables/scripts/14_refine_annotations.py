#!/usr/bin/env python3
"""
Refined annotation system with improved toxicity detection.

This script:
1. Uses more sophisticated patterns for toxicity detection
2. Better handles code-mixed text
3. Less conservative (detects subtle toxicity)
4. Improved subtype classification
"""

import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime

def classify_toxicity_binary_improved(text):
    """
    Improved binary toxicity classification.
    More comprehensive patterns, less conservative.
    """
    if pd.isna(text) or not isinstance(text, str) or len(text.strip()) < 3:
        return 0
    
    text_lower = text.lower()
    
    # Strong toxic indicators (high confidence)
    strong_toxic_patterns = [
        # Hate speech patterns
        r'\b(all|every|most)\s+\w+\s+(are|is)\s+(criminals|animals|worthless|trash|stupid|idiots|scum)',
        r'\b(racist|sexist|homophobic|transphobic|bigot|nazi|fascist)\b',
        r'\b(pakis|chinks|niggers|kikes|wetbacks|retards)\b',  # Slurs
        r'\b(casteism|communalism|religious\s+bigotry)\b',
        
        # Threats
        r'\b(kill|hurt|harm|attack|violence|destroy|eliminate)\s+(you|them|your|their|him|her)',
        r'\b(i\s+will|i\'ll|gonna|going\s+to)\s+(kill|hurt|attack|destroy|harm)',
        r'\b(you\s+should\s+die|end\s+your\s+life|commit\s+suicide)',
        r'\b(threat|threaten|threatening|violence|violent)\b',
        
        # Severe insults/profanity
        r'\b(fuck|shit|damn|bastard|asshole|bitch|cunt|motherfucker)\s+(you|your|them|their)',
        r'\b(chutiya|gandu|bhenchod|madarchod|harami|bewakoof)\s+(you|your|tu|tum)',  # Hindi profanity directed
        r'\b(you\'re|you\s+are)\s+(a\s+)?(stupid|idiot|moron|fool|dumb|retard|imbecile|pathetic)',
        r'\b(disgusting|vile|repulsive|despicable|contemptible)\b',
        
        # Self-harm promotion
        r'\b(kill\s+yourself|end\s+your\s+life|commit\s+suicide|just\s+die|no\s+one\s+would\s+miss)',
        
        # Harassment patterns
        r'\b(harass|bully|stalk|target|intimidate|threaten)\s+(you|them|him|her)',
    ]
    
    # Check strong patterns
    for pattern in strong_toxic_patterns:
        if re.search(pattern, text_lower):
            return 1
    
    # Moderate toxic indicators
    moderate_patterns = [
        # Profanity in context
        r'\b(fuck|shit|damn)\b.*\b(you|your|them|government|system)\b',
        r'\b(incompetent|useless|worthless|pathetic)\s+(as\s+)?(fuck|hell|shit)',
        
        # Personal attacks
        r'\b(you\'re|you\s+are)\s+(so|really|very)\s+(stupid|dumb|ignorant|clueless)',
        r'\b(what\s+a|such\s+a)\s+(idiot|moron|fool|stupid|dumb)',
        
        # Code-mixed toxic patterns
        r'\b(chutiya|gandu|bhenchod)\b',  # Hindi profanity (standalone)
        r'\b(tum|tu)\s+(sab|log)\s+(chutiye|gandu|bewakoof)\b',
        
        # Dehumanizing language
        r'\b(these|those)\s+(people|ones)\s+(are|is)\s+(animals|vermin|scum)',
        
        # Aggressive language
        r'\b(shut\s+up|fuck\s+off|get\s+lost|go\s+to\s+hell)\b',
    ]
    
    # Check moderate patterns
    for pattern in moderate_patterns:
        if re.search(pattern, text_lower):
            return 1
    
    # Context-based detection (negative sentiment with personal targeting)
    negative_words = ['hate', 'disgusting', 'pathetic', 'terrible', 'awful', 'horrible']
    personal_pronouns = ['you', 'your', 'yours', 'them', 'their', 'he', 'she']
    
    has_negative = any(word in text_lower for word in negative_words)
    has_personal = any(pronoun in text_lower for pronoun in personal_pronouns)
    
    if has_negative and has_personal and len(text) > 20:
        # Check if it's constructive (has "because", "since", etc.)
        if not re.search(r'\b(because|since|due\s+to|reason|why|explain)\b', text_lower):
            return 1
    
    # Non-toxic indicators (override)
    non_toxic_patterns = [
        r'\b(/s|sarcasm|sarcastic|joke|joking|lol|haha|😂|😏)\b',  # Sarcasm
        r'\b(i\s+disagree|i\s+think|in\s+my\s+opinion|constructive)\b',  # Constructive
        r'\b(yaar|bhai|dost|friend)\b',  # Friendly Hindi
        r'\b(self\s+deprecating|self\s+deprecat)\b',  # Self-deprecation
    ]
    
    has_non_toxic = any(re.search(pattern, text_lower) for pattern in non_toxic_patterns)
    if has_non_toxic:
        # Only override if no strong toxic patterns
        return 0
    
    # Default: non-toxic (conservative)
    return 0

def classify_subtypes_improved(text, label):
    """Improved subtype classification"""
    if label == 0:
        return []
    
    subtypes = []
    text_lower = text.lower()
    
    # 1. HATE - Identity-based attacks
    hate_patterns = [
        r'\b(all|every|most)\s+\w+\s+(are|is)\s+(criminals|animals|worthless|trash)',
        r'\b(racist|sexist|homophobic|transphobic|bigot|discriminate)\b',
        r'\b(pakis|chinks|niggers|kikes|wetbacks)\b',  # Slurs
        r'\b(casteism|communalism|religious\s+bigotry)\b',
        r'\b(painting|stereotyping)\s+all\s+\w+\s+as',
        r'\b(misogyny|misogynistic|sexist|patriarchal)\b',
    ]
    if any(re.search(pattern, text_lower) for pattern in hate_patterns):
        subtypes.append('hate')
    
    # 2. THREAT - Threats of violence
    threat_patterns = [
        r'\b(kill|hurt|harm|attack|violence|destroy|eliminate)\s+(you|them|your|their)',
        r'\b(i\s+will|i\'ll|gonna|going\s+to)\s+(kill|hurt|attack|destroy|harm)',
        r'\b(you\s+should\s+die|end\s+your\s+life|commit\s+suicide)',
        r'\b(coming\s+for|find\s+you|get\s+you|target)',
        r'\b(threat|threaten|threatening|violent|violence)\b',
    ]
    if any(re.search(pattern, text_lower) for pattern in threat_patterns):
        subtypes.append('threat')
    
    # 3. INSULT - Severe personal attacks
    insult_patterns = [
        r'\b(you\'re|you\s+are)\s+(a\s+)?(stupid|idiot|moron|fool|dumb|retard|imbecile|pathetic|disgusting)',
        r'\b(what\s+a|such\s+a)\s+(idiot|moron|fool|stupid|dumb|pathetic)',
        r'\b(fuck|shit|damn|bastard|asshole|bitch|cunt)\s+(you|your|them|their)',
        r'\b(chutiya|gandu|bhenchod|madarchod|harami|bewakoof)\s+(you|tu|tum|sab)',
        r'\b(disgusting|vile|repulsive|despicable|contemptible)\b',
        r'\b(incompetent|useless|worthless|pathetic)\s+(as\s+)?(fuck|hell)',
    ]
    if any(re.search(pattern, text_lower) for pattern in insult_patterns):
        subtypes.append('insult')
    
    # 4. HARASSMENT - Repeated targeting
    harassment_patterns = [
        r'\b(harass|bully|stalk|cyberbully|intimidate)\b',
        r'\b(repeatedly|over\s+and\s+over|again\s+and\s+again)\s+(target|attack|harass)',
        r'\b(targeting|targeted|stalking|harassing)\s+(you|them|him|her)',
    ]
    if any(re.search(pattern, text_lower) for pattern in harassment_patterns):
        subtypes.append('harassment')
    
    # 5. SELF-HARM - Self-harm promotion
    self_harm_patterns = [
        r'\b(kill\s+yourself|end\s+your\s+life|commit\s+suicide|just\s+die)',
        r'\b(you\s+should\s+die|end\s+it\s+all|no\s+one\s+would\s+miss)',
        r'\b(self\s+harm|self\s+harm|suicide|end\s+yourself)',
    ]
    if any(re.search(pattern, text_lower) for pattern in self_harm_patterns):
        subtypes.append('self_harm')
    
    # If toxic but no specific subtype, default to insult
    if not subtypes:
        subtypes.append('insult')
    
    return subtypes

def determine_confidence_improved(text, label, subtypes):
    """Improved confidence determination"""
    if len(text) < 10:
        return 'low'
    
    text_lower = text.lower()
    
    # High confidence indicators
    strong_indicators = [
        'kill', 'hate', 'racist', 'sexist', 'stupid', 'idiot', 
        'chutiya', 'gandu', 'bhenchod', 'fuck', 'die', 'threat'
    ]
    
    has_strong = any(indicator in text_lower for indicator in strong_indicators)
    
    if label == 1 and has_strong and len(subtypes) > 0:
        return 'high'
    elif label == 0 and len(text) > 50 and not has_strong:
        return 'high'
    elif label == 1 or label == 0:
        return 'medium'
    else:
        return 'low'

def refine_annotations(df):
    """Refine annotations for entire dataset"""
    print(f"Refining annotations for {len(df):,} samples...")
    
    annotations = []
    for idx, row in df.iterrows():
        text = str(row['text']) if pd.notna(row['text']) else ''
        
        # Binary classification (improved)
        binary_label = classify_toxicity_binary_improved(text)
        
        # Subtype classification (improved)
        subtypes = classify_subtypes_improved(text, binary_label)
        
        # Confidence (improved)
        confidence = determine_confidence_improved(text, binary_label, subtypes)
        
        annotations.append({
            'id': row['id'],
            'text': text,
            'label': binary_label,
            'toxic_types': subtypes,
            'confidence': confidence,
            'annotator_id': 'refined_automated',
            'notes': 'Refined automated annotation with improved patterns'
        })
        
        if (idx + 1) % 2000 == 0:
            print(f"  Progress: {idx + 1:,} / {len(df):,} ({100*(idx+1)/len(df):.1f}%)")
    
    return pd.DataFrame(annotations)

def main():
    """Main execution"""
    print("=" * 80)
    print("REFINED ANNOTATION SYSTEM")
    print("Improved toxicity detection with better patterns")
    print("=" * 80)
    
    # Load data
    data_path = Path(__file__).parent.parent.parent / "data" / "unlabeled" / "for_annotation.csv"
    print(f"\nLoading: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df):,} samples")
    
    # Refine annotations
    print(f"\nRefining annotations...")
    annotated_df = refine_annotations(df)
    
    # Statistics
    print(f"\n" + "=" * 80)
    print("REFINED ANNOTATION RESULTS")
    print("=" * 80)
    print(f"\nTotal samples: {len(annotated_df):,}")
    print(f"Toxic (1): {(annotated_df['label'] == 1).sum():,} ({(annotated_df['label'] == 1).sum()/len(annotated_df)*100:.1f}%)")
    print(f"Non-toxic (0): {(annotated_df['label'] == 0).sum():,} ({(annotated_df['label'] == 0).sum()/len(annotated_df)*100:.1f}%)")
    
    # Subtype distribution
    print(f"\nSubtype Distribution (for toxic comments):")
    for subtype in ['hate', 'threat', 'insult', 'harassment', 'self_harm']:
        count = annotated_df['toxic_types'].apply(lambda x: subtype in x if isinstance(x, list) else False).sum()
        pct = (count / (annotated_df['label'] == 1).sum() * 100) if (annotated_df['label'] == 1).sum() > 0 else 0
        print(f"  {subtype}: {count:,} ({pct:.1f}%)")
    
    # Merge with original
    result_df = df.copy()
    result_df['label'] = annotated_df['label'].values
    result_df['toxic_types'] = annotated_df['toxic_types'].apply(lambda x: ','.join(x) if x else '')
    result_df['confidence'] = annotated_df['confidence'].values
    result_df['annotator_id'] = annotated_df['annotator_id'].values
    result_df['notes'] = annotated_df['notes'].values
    
    # Update metadata
    for idx, row in result_df.iterrows():
        if pd.notna(row.get('metadata')):
            try:
                meta = json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
            except:
                meta = {}
        else:
            meta = {}
        
        if row['toxic_types']:
            meta['toxic_types'] = row['toxic_types'].split(',')
        meta['confidence'] = row['confidence']
        meta['annotator_id'] = row['annotator_id']
        
        result_df.at[idx, 'metadata'] = json.dumps(meta)
    
    # Save updated file
    result_df.to_csv(data_path, index=False)
    print(f"\nUpdated: {data_path}")
    
    # Save detailed annotations
    output_dir = Path(__file__).parent.parent.parent / "data" / "annotated"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "refined_annotations.csv"
    annotated_df.to_csv(output_file, index=False)
    print(f"Saved detailed: {output_file}")
    
    print("\n" + "=" * 80)
    print("Refinement complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()

