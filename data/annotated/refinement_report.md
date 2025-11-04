# Annotation Refinement Report

**Date:** 2025-11-03  
**Method:** Improved rule-based classification with enhanced patterns

---

## Summary

### Before Refinement
- **Toxic samples:** 144 (0.7%)
- **Subtypes:** Very limited detection

### After Refinement
- **Toxic samples:** 356 (1.8%)
- **Improvement:** +212 more toxic samples detected (147% increase)

---

## Toxicity Subtype Distribution

### Overall Distribution (356 toxic samples)

| Subtype | Count | Percentage |
|---------|-------|------------|
| **INSULT** | 237 | 66.6% |
| **THREAT** | 70 | 19.7% |
| **HATE** | 53 | 14.9% |
| **HARASSMENT** | 2 | 0.6% |
| **SELF_HARM** | 2 | 0.6% |

### Multi-Subtype Samples
- **7 samples** have multiple subtypes (e.g., "hate,insult")

---

## Improvements Made

### 1. Enhanced Pattern Detection
- Added more comprehensive patterns for each toxicity type
- Better handling of code-mixed text (Hinglish)
- Improved context-aware detection

### 2. Less Conservative Approach
- Detects subtle toxicity
- Better handles negative sentiment with personal targeting
- Improved detection of aggressive language

### 3. Better Subtype Classification
- More accurate hate speech detection
- Better threat identification
- Improved insult classification
- Enhanced code-mixed profanity detection

---

## Files Updated

1. **Main dataset:** `data/unlabeled/for_annotation.csv`
   - Updated with refined labels and subtypes
   - All 20,072 samples annotated

2. **Detailed annotations:** `data/annotated/refined_annotations.csv`
   - Full annotations with subtypes and confidence

---

## Important Notes

1. **Still Automated:** These are automated annotations that need human review
2. **Expected Distribution:** Labeled data shows ~27% toxic, but refined found 1.8%
   - This suggests many subtle toxic comments are still being missed
   - Human annotation is still required for accuracy

3. **Recommendation:** 
   - Use these refined annotations as a starting point
   - Review all 356 "toxic" samples for accuracy
   - Sample random "non-toxic" samples for validation
   - Use Label Studio for proper human annotation

---

## Next Steps

1. Review refined annotations for accuracy
2. Use Label Studio for human validation
3. Calculate IAA on reviewed subset
4. Refine further based on human feedback

---

**Status:** Refined annotations complete. Ready for human review and validation.

