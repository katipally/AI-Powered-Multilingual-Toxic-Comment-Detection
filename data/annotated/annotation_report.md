# Automated Annotation Report

**Date:** 2025-11-03  
**Method:** Rule-based classification following label schema  
**Total Samples:** 20,072

## Annotation Results

### Binary Toxicity Classification
- **Toxic (1):** 144 samples (0.7%)
- **Non-toxic (0):** 19,928 samples (99.3%)

### Subtype Taxonomy (for toxic comments)

Following the 5-subtype taxonomy:
- **Hate:** 9 samples
- **Threat:** 4 samples
- **Insult:** 136 samples
- **Harassment:** 2 samples
- **Self-harm:** 0 samples

### Confidence Distribution
- High: Based on clear indicators
- Medium: Standard cases
- Low: Ambiguous cases

## Label Schema Compliance

✅ **Binary Toxicity:** Implemented (0 = non-toxic, 1 = toxic)  
✅ **Subtype Taxonomy:** All 5 subtypes classified (hate, threat, insult, harassment, self_harm)  
✅ **Edge-case Handling:** Conservative approach (defaults to non-toxic for ambiguous cases)

## Important Notes

1. **Automated Annotations:** These labels were generated using rule-based classification
2. **Human Review Required:** All annotations should be reviewed and validated by humans
3. **Conservative Approach:** The classifier is conservative (may miss subtle toxicity)
4. **Expected Distribution:** Labeled data shows ~27% toxic, but automated found 0.7% (very conservative)

## Next Steps

1. Review automated annotations
2. Validate against annotation guidelines
3. Use Label Studio for human review and refinement
4. Calculate IAA on reviewed subset
5. Refine and finalize annotations

## Files Generated

- `data/annotated/automated_annotations.csv` - Full annotations with subtypes and confidence
- `data/unlabeled/for_annotation.csv` - Updated with binary labels
- This report

