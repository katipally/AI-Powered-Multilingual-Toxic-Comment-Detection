# Person 1 → Person 2: Handoff Document

**Date:** October 30, 2025  
**From:** Person 1 - Data Collection & Preprocessing Lead  
**To:** Person 2 - Annotation Lead  
**Status:** ✅ **COMPLETE** - All Person 1 deliverables ready

---

## 🎯 Executive Summary

Person 1 tasks are **100% complete**. This package includes:

✅ **218,675 total samples** collected and preprocessed  
✅ **198,603 labeled samples** (70/15/15 train/dev/test splits)  
✅ **20,072 unlabeled samples** ready for Person 2 annotation  
✅ **Normalization & transliteration utilities** (validated ≥95% accuracy)  
✅ **Deduplication utilities** (exact + near-duplicate detection)  
✅ **Complete data card** with TOS compliance  
✅ **Quality reports** (100% validation passed)  
✅ **DVC-ready structure** for reproducibility  
✅ **All code documented** and tested

**What Person 2 Needs to Do:**
1. Annotate 20,072 unlabeled samples (Reddit + YouTube)
2. Focus on 1,869 code-mixed samples (priority)
3. Calculate inter-annotator agreement
4. Merge annotations and create final dataset

---

## 📁 Package Contents

```
Github_upload/
├── PERSON1_HANDOFF.md          ← YOU ARE HERE
├── README.md                    ← Quick start guide
├── DATA_CARD.md                 ← Complete dataset documentation
├── requirements.txt             ← All dependencies
├── .gitignore                   ← Git ignore rules
│
├── data/                        ← All data files
│   ├── splits/                  ← Train/dev/test splits
│   │   ├── train.csv           (139,022 samples)
│   │   ├── dev.csv             (29,790 samples)
│   │   ├── test.csv            (29,791 samples)
│   │   └── split_manifest.json
│   │
│   ├── labeled/                 ← Pre-labeled data
│   │   ├── all_labeled_data.csv (198,603 samples)
│   │   ├── hatexplain.csv
│   │   ├── jigsaw_bias.csv
│   │   ├── jigsaw_multilingual.csv
│   │   └── textdetox.csv
│   │
│   ├── unlabeled/               ← FOR PERSON 2 ANNOTATION
│   │   ├── for_annotation.csv  (20,072 samples) ⭐
│   │   ├── reddit.csv          (10,000 samples)
│   │   └── youtube.csv         (10,072 samples)
│   │
│   └── reports/                 ← Quality & statistics
│       ├── processing_report.json
│       └── validation_report.json
│
├── scripts/                     ← All collection & preprocessing scripts
│   ├── 1_download_hatexplain.py
│   ├── 2_collect_reddit.py
│   ├── 3_collect_youtube.py
│   ├── 4_download_textdetox.py
│   ├── 5_preprocess_and_unify.py
│   ├── 6_data_quality_checks.py
│   ├── 7_create_stratified_splits.py
│   └── find_youtube_videos.py
│
├── utils/                       ← Normalization & deduplication
│   ├── __init__.py
│   ├── text_normalization.py   ← Romanized Hindi normalization
│   └── deduplication.py         ← Exact + near-duplicate detection
│
├── notebooks/                   ← Jupyter notebooks
│   └── collection_walkthrough.ipynb
│
└── docs/                        ← Additional documentation
    ├── COLLECTION_METHODOLOGY.md
    ├── PREPROCESSING_GUIDE.md
    └── TOS_COMPLIANCE.md
```

---

## ✅ Person 1 Checklist: Completed Deliverables

### Required Outputs (from official requirements)

- [x] **Curated dataset with train/dev/test splits**
  - ✅ 70/15/15 stratified splits
  - ✅ Balanced by label + language + code-mixed status
  - ✅ Random seed 42 (frozen for reproducibility)
  - ✅ Split manifest with complete metadata
  
- [x] **Normalization & transliteration utilities**
  - ✅ Romanized Hindi word normalization (50+ words)
  - ✅ URL/email/mention removal
  - ✅ Punctuation & whitespace normalization
  - ✅ Validated on gold list (≥95% accuracy)
  - ✅ Multiple presets (default, strict, code_mixed)
  
- [x] **Provenance logs, data card**
  - ✅ Complete data card with all 11 sections
  - ✅ License & TOS compliance documented
  - ✅ Collection queries & sampling recorded
  - ✅ Source attribution for all datasets
  
- [x] **Quality report**
  - ✅ Dedup rate: 1.47% (labeled), 14.04% (unlabeled)
  - ✅ Language mix: 15+ languages documented
  - ✅ Class balance: 72.3% non-toxic, 27.7% toxic
  - ✅ PII scrub: URLs, emails, mentions removed
  
- [x] **DVC-tracked structure**
  - ✅ DVC configuration ready
  - ✅ Reproducible from raw to processed
  - ✅ No credential leakage (.env excluded)

### Detailed Responsibilities

- [x] **Implement collectors with official SDKs/APIs**
  - ✅ PRAW for Reddit (rate-limited to 100 QPM)
  - ✅ Google API for YouTube (quota-safe)
  - ✅ HuggingFace datasets for public corpora
  - ✅ Raw JSONL saved with query params
  
- [x] **Code-mix detection pipeline**
  - ✅ Script ratio detection (Latin vs Devanagari)
  - ✅ Token-level language ID (langdetect)
  - ✅ Pattern matching for Romanized Hindi
  - ✅ 1,869 code-mixed samples identified
  
- [x] **Cleaning pipeline**
  - ✅ Strip URLs/HTML (replaced with tokens)
  - ✅ Normalize punctuation/emoji
  - ✅ Transliteration normalization (Romanized Hindi)
  - ✅ Unicode normalization (NFKC)
  
- [x] **Deduplicate**
  - ✅ By normalized text hash (MD5)
  - ✅ Near-duplicate detection available (cosine sim)
  - ✅ Dedup rates documented in quality report
  
- [x] **Stratified splits**
  - ✅ By toxicity label AND language mix
  - ✅ Frozen random seed (42)
  - ✅ Split manifest stored
  
- [x] **Data card + collection notebook**
  - ✅ 11-section data card (5,000+ words)
  - ✅ Collection notebook with examples
  - ✅ All artifacts DVC-ready

---

## 📊 Dataset Statistics for Person 2

### What You're Receiving

| Dataset | Samples | Purpose |
|---------|---------|---------|
| **Labeled (ready to use)** | 198,603 | Train/dev/test your models |
| **Unlabeled (your work)** | 20,072 | Annotate as toxic (1) or non-toxic (0) |
| **Code-mixed (priority)** | 1,869 | Focus annotation here first |

### Label Distribution (Labeled Data)

- Non-toxic (0): 143,536 (72.3%)
- Toxic (1): 55,067 (27.7%)
- **Target for unlabeled:** Maintain similar distribution

### Splits (Labeled Data)

| Split | Samples | Toxic % | Use |
|-------|---------|---------|-----|
| Train | 139,022 | 27.7% | Model training |
| Dev | 29,790 | 27.7% | Hyperparameter tuning |
| Test | 29,791 | 27.7% | Final evaluation |

### Unlabeled Breakdown

| Source | Total | Code-Mixed | Notes |
|--------|-------|------------|-------|
| Reddit | 10,000 | 927 (9.3%) | Indian subreddits |
| YouTube | 10,072 | 942 (9.4%) | Bollywood videos |

---

## 🚀 Quick Start for Person 2

### 1. Setup Environment

```bash
# Clone repository
git clone [repo_url]
cd toxic-comment-detection

# Install dependencies
pip install -r requirements.txt

# Verify data
python scripts/6_data_quality_checks.py
```

### 2. Load Data for Annotation

```python
import pandas as pd

# Load unlabeled data
df = pd.read_csv('data/unlabeled/for_annotation.csv')

# Priority: code-mixed samples
code_mixed = df[df['code_mixed'] == True]
print(f"Code-mixed samples to annotate: {len(code_mixed)}")

# Filter by source if needed
reddit = df[df['source'] == 'reddit']
youtube = df[df['source'] == 'youtube']
```

### 3. Annotation Schema

```python
# Each sample needs:
{
    'id': '[existing id]',
    'text': '[existing text]',
    'label': 0 or 1,  # YOUR ANNOTATION
    'annotator_id': '[your id]',
    'confidence': 'low'|'medium'|'high',
    'toxic_types': ['hate', 'threat', 'insult'],  # if toxic
    'notes': '[optional notes]'
}
```

### 4. Use Normalization Utilities

```python
from utils.text_normalization import normalize_text, get_normalizer

# Normalize text before showing to annotators
normalizer = get_normalizer('code_mixed')
cleaned_text = normalizer(raw_text)

# Or use full pipeline
normalized = normalize_text(
    text,
    normalize_hindi=True,
    remove_url=True,
    keep_emoji=True
)
```

---

## 🎯 Person 2 Action Items

### Immediate (Week 1)

1. **Review this handoff document** ✓
2. **Install environment** and verify data loads
3. **Read DATA_CARD.md** for dataset details
4. **Explore `data/unlabeled/for_annotation.csv`**
5. **Create annotation guidelines** for your team
6. **Set up annotation interface** (Label Studio, Prodigy, etc.)

### Annotation Phase (Weeks 2-4)

7. **Annotate code-mixed samples first** (1,869 samples - priority!)
8. **Annotate remaining samples** (18,203 samples)
9. **Calculate inter-annotator agreement** (Kappa, F1)
10. **Resolve disagreements** through consensus

### Integration Phase (Week 5)

11. **Merge annotations** with existing data
12. **Update splits** if needed
13. **Run quality checks** on annotated data
14. **Update DATA_CARD.md** with annotation details
15. **Hand off to Persons 3-4** for model training

---

## 📝 Annotation Guidelines Recommendations

### Toxicity Definition

Consider these categories (customize as needed):

1. **Toxic (1):**
   - Hate speech (targeting identity)
   - Threats of violence
   - Severe insults / profanity
   - Harassment
   - Self-harm promotion

2. **Non-Toxic (0):**
   - Constructive criticism
   - Sarcasm (without harm intent)
   - Strong opinions (without targeting)
   - Mild profanity (not directed)

### Code-Mixed Considerations

- Hindi profanity in Roman script (e.g., "gandu", "chutiya")
- Contextual toxicity (Hindi insults may be playful)
- Transliterate if needed: "bhenchod" is toxic
- Consider cultural context: "yaar" (buddy) is not toxic

### Edge Cases

- **Reclaimed slurs:** Check context and speaker identity
- **Quotes:** Is the poster endorsing or denouncing?
- **Sarcasm:** Look for obvious indicators (/s, LOL, emoji)
- **Political discourse:** Strong ≠ toxic; focus on personal attacks

---

## 🔧 Tools & Utilities Available

### Normalization (utils/text_normalization.py)

```python
# Presets
get_normalizer('default')     # Standard cleaning
get_normalizer('strict')      # Aggressive (lowercase, no emoji)
get_normalizer('code_mixed')  # Optimized for Hinglish
get_normalizer('minimal')     # Light touch

# Functions
normalize_text(text, **options)
normalize_romanized_hindi(text)
remove_urls(text)
normalize_punctuation(text)
```

### Deduplication (utils/deduplication.py)

```python
# Remove exact duplicates
df_clean, n_removed = remove_exact_duplicates(df)

# Remove near-duplicates
df_clean, n_removed = remove_near_duplicates(df, threshold=0.95)

# Full pipeline
df_clean, stats = deduplicate_dataframe(
    df, 
    exact=True, 
    near=True,
    near_threshold=0.95
)
```

---

## 📈 Expected Annotation Effort

### Time Estimates (Conservative)

| Task | Samples | Time/Sample | Total Time |
|------|---------|-------------|------------|
| Code-mixed (priority) | 1,869 | 30 sec | 15.6 hours |
| Reddit (remaining) | 8,131 | 20 sec | 45.2 hours |
| YouTube (remaining) | 10,072 | 20 sec | 55.9 hours |
| **TOTAL** | **20,072** | **~21 sec** | **~117 hours** |

### With 3 Annotators

- **Per annotator:** ~39 hours (1 week full-time)
- **With overlap for IAA:** Add 20% = ~47 hours/person
- **Total timeline:** 1-2 weeks for annotation + 1 week for consensus

---

## ✅ Quality Checklist for Person 2

Before handing off to Persons 3-4, ensure:

- [ ] All 20,072 samples annotated
- [ ] Inter-annotator agreement ≥0.7 (Kappa)
- [ ] Annotation guidelines documented
- [ ] Edge cases and disagreements resolved
- [ ] Final dataset has same schema as labeled data
- [ ] Data card updated with annotation details
- [ ] Quality report generated
- [ ] Train/dev/test splits updated (if needed)
- [ ] DVC pipeline updated

---

## 🚨 Important Notes

### DO:
- ✅ Use normalization utilities before annotation (cleaner text)
- ✅ Focus on code-mixed samples first (highest value)
- ✅ Track disagreements for guideline improvement
- ✅ Use metadata (subreddit, video_title) for context
- ✅ Update DATA_CARD.md with your work

### DON'T:
- ❌ Change schema (keep columns consistent)
- ❌ Delete any existing fields
- ❌ Expose PII (emails, names already removed)
- ❌ Share raw data publicly (TOS compliance)
- ❌ Skip quality validation before handoff

---

## 📞 Contact & Support

**Person 1 Lead:** [Add your contact]  
**Team Channel:** [Add Slack/Discord]  
**Issues:** [GitHub Issues URL]  
**Documentation:** See `docs/` folder

---

## 🎓 Additional Resources

1. **DATA_CARD.md** - Complete dataset documentation (must-read!)
2. **PREPROCESSING_GUIDE.md** - How preprocessing was done
3. **TOS_COMPLIANCE.md** - Legal compliance details
4. **notebooks/collection_walkthrough.ipynb** - Interactive examples

---

## 🏁 Success Criteria for Person 2

You're done when:

1. ✅ All 20,072 samples have labels (0 or 1)
2. ✅ Inter-annotator agreement documented (≥0.7 Kappa)
3. ✅ Final dataset passes quality validation
4. ✅ DATA_CARD.md updated with annotation section
5. ✅ Persons 3-4 can load and use the data without issues

---

**Status:** Ready for annotation! 🚀  
**Last Updated:** October 30, 2025  
**Next Steps:** Person 2 begins annotation phase

---

## 📦 Appendix: File Manifest

### Critical Files (Must Include in GitHub)

```
✅ README.md                    - Quick start
✅ DATA_CARD.md                  - Complete documentation (5,000+ words)
✅ PERSON1_HANDOFF.md            - This document
✅ requirements.txt              - All dependencies
✅ .gitignore                    - Don't commit .env, data/

✅ data/splits/                  - Train/dev/test (198,603 samples)
✅ data/unlabeled/               - For annotation (20,072 samples)
✅ data/reports/                 - Quality & stats

✅ scripts/*.py                  - All 7 collection/preprocessing scripts
✅ utils/*.py                    - Normalization & deduplication
✅ notebooks/*.ipynb             - Collection walkthrough

✅ .dvc/                         - DVC configuration
✅ .dvc/.gitignore               - DVC ignore rules
```

### Excluded from GitHub (Too Large)

```
❌ data/labeled/*.csv            - Too large (80 MB)
   → Use DVC to track
   → Or use Git LFS
   → Or host on HuggingFace/Kaggle

❌ Input/                        - Raw data (not needed by team)
❌ Final_input/                  - Duplicate of data/ (already organized)
❌ .env                          - Credentials (never commit!)
```

---

**Person 1 Sign-Off:** ✅ Complete  
**Ready for Person 2:** ✅ Yes  
**Date:** October 30, 2025
