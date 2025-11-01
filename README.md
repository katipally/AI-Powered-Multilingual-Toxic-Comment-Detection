# Code-Mixed Toxic Comment Detection - Person 1 Deliverables

**Version:** 1.0.0  
**Status:** ✅ **COMPLETE** - Ready for Team  
**Person 1 Lead:** Data Collection & Preprocessing  
**Date:** October 30, 2025  

---

## 🎯 What's Included

This repository contains **all Person 1 deliverables** for the Code-Mixed Toxic Comment Detection project:

- ✅ **218,675 samples** collected & preprocessed
- ✅ **Train/dev/test splits** (70/15/15, stratified)
- ✅ **20,072 unlabeled samples** for Person 2 annotation  
- ✅ **Normalization utilities** (Romanized Hindi, URL/emoji handling)
- ✅ **Deduplication tools** (exact + near-duplicate)
- ✅ **Complete data card** with TOS compliance
- ✅ **Quality reports** (100% validation passed)
- ✅ **Reproducible pipeline** (DVC-ready)

---

## 📁 Repository Structure

```
toxic-comment-detection/
├── README.md                    ← YOU ARE HERE
├── PERSON1_HANDOFF.md           ← 🔥 START HERE FOR PERSON 2
├── DATA_CARD.md                 ← Complete documentation (must-read!)
├── requirements.txt             ← All dependencies
├── .gitignore                   ← Git ignore rules
│
├── data/                        ← All datasets
│   ├── splits/                  ← Train/dev/test (ready for training)
│   │   ├── train.csv           (139,022 samples)
│   │   ├── dev.csv             (29,790 samples)
│   │   ├── test.csv            (29,791 samples)
│   │   └── split_manifest.json
│   │
│   ├── unlabeled/               ← FOR PERSON 2 ANNOTATION ⭐
│   │   ├── for_annotation.csv  (20,072 samples)
│   │   ├── reddit.csv
│   │   └── youtube.csv
│   │
│   ├── reports/                 ← Quality & statistics
│   │   ├── processing_report.json
│   │   └── validation_report.json
│   │
│   └── all_labeled_data.csv     ← Combined labeled data (198,603)
│
├── scripts/                     ← Collection & preprocessing
│   ├── 1_download_hatexplain.py
│   ├── 2_collect_reddit.py
│   ├── 3_collect_youtube.py
│   ├── 4_download_textdetox.py
│   ├── 5_preprocess_and_unify.py
│   ├── 6_data_quality_checks.py
│   ├── 7_create_stratified_splits.py
│   └── find_youtube_videos.py
│
├── utils/                       ← Utility functions
│   ├── __init__.py
│   ├── text_normalization.py   ← Normalization + transliteration
│   └── deduplication.py         ← Dedup utilities
│
├── notebooks/                   ← Jupyter notebooks
│   └── (to be added)
│
└── docs/                        ← Additional documentation
    └── (to be added)
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Clone repository
git clone [your-repo-url]
cd toxic-comment-detection

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Data

```bash
# Check data quality
python scripts/6_data_quality_checks.py

# Should output: ✅ VALIDATION PASSED
```

### 3. Load Data

```python
import pandas as pd

# Load train/dev/test splits
train = pd.read_csv('data/splits/train.csv')
dev = pd.read_csv('data/splits/dev.csv')
test = pd.read_csv('data/splits/test.csv')

print(f"Train: {len(train):,} samples")
print(f"Dev:   {len(dev):,} samples")
print(f"Test:  {len(test):,} samples")

# For Person 2: Load unlabeled data
unlabeled = pd.read_csv('data/unlabeled/for_annotation.csv')
print(f"To annotate: {len(unlabeled):,} samples")
```

---

## 📊 Dataset Overview

| Component | Samples | Status |
|-----------|---------|--------|
| **Labeled (ready to use)** | 198,603 | ✅ Complete |
| - Train | 139,022 | 70% |
| - Dev | 29,790 | 15% |
| - Test | 29,791 | 15% |
| **Unlabeled (for annotation)** | 20,072 | ⏳ Person 2 |
| - Reddit | 10,000 | Needs labels |
| - YouTube | 10,072 | Needs labels |
| **Code-Mixed (priority)** | 1,869 | Hindi-English |

### Label Distribution (Labeled Data)

- **Non-Toxic (0):** 143,536 (72.3%)
- **Toxic (1):** 55,067 (27.7%)
- **Balance Ratio:** 0.38 (good for training)

### Languages (15+)

English (62.6%), Hindi (4.7%), Spanish (3.8%), Italian (3.8%), Russian, Ukrainian, German, Amharic, Chinese, Arabic, French, Japanese, Turkish, Hebrew, and more.

---

## 🎯 For Person 2 (Annotation Lead)

### 👉 **START HERE:** [PERSON1_HANDOFF.md](PERSON1_HANDOFF.md)

This document contains:
- Complete task overview
- Step-by-step annotation guide
- Tools & utilities documentation
- Quality checklist
- Success criteria

### Your Task

Annotate **20,072 unlabeled samples** as toxic (1) or non-toxic (0):

```python
# Load data
df = pd.read_csv('data/unlabeled/for_annotation.csv')

# Priority: Code-mixed samples
code_mixed = df[df['code_mixed'] == True]
print(f"Priority samples: {len(code_mixed):,}")  # 1,869 samples
```

### Time Estimate

- **Total:** ~117 hours (with 3 annotators: ~39 hours/person)
- **Code-mixed (priority):** ~16 hours
- **Timeline:** 1-2 weeks annotation + 1 week consensus

---

## 🛠️ Tools & Utilities

### Normalization (for clean text before annotation)

```python
from utils.text_normalization import get_normalizer

# Use code-mixed preset
normalizer = get_normalizer('code_mixed')
clean_text = normalizer(raw_text)

# Handles:
# - URL/email removal
# - Punctuation normalization
# - Romanized Hindi (yaar→yaar, bhaii→bhai)
# - Emoji preservation
```

### Deduplication (if needed)

```python
from utils.deduplication import remove_exact_duplicates

df_clean, n_removed = remove_exact_duplicates(df)
print(f"Removed {n_removed} duplicates")
```

---

## 📚 Documentation

### Must-Read Documents

1. **[PERSON1_HANDOFF.md](PERSON1_HANDOFF.md)** - Complete handoff guide for Person 2
2. **[DATA_CARD.md](DATA_CARD.md)** - Full dataset documentation (TOS, licenses, statistics)

### Key Information

- **Random Seed:** 42 (for reproducibility)
- **Validation:** 100% passed all quality checks
- **TOS Compliance:** ✅ All data collected legally via official APIs
- **Licenses:** Mix of CC0, MIT, Apache 2.0 (see DATA_CARD.md)

---

## ✅ Person 1 Completion Checklist

All requirements from official specification completed:

- [x] **Curated dataset with train/dev/test splits (DVC-tracked)**
  - Stratified by label + language + code-mixed
  - Random seed 42 frozen
  - Manifest with complete metadata

- [x] **Normalization & transliteration utilities**
  - Romanized Hindi normalization (50+ words)
  - URL/email/mention removal
  - Validated ≥95% accuracy on gold list

- [x] **Provenance logs, data card**
  - Complete 11-section data card
  - License & TOS compliance
  - Collection queries & sampling documented

- [x] **Quality report**
  - Dedup rates: 1.47% (labeled), 14.04% (unlabeled)
  - Language mix: 15+ languages
  - Class balance: 72.3% / 27.7%
  - PII scrubbed (URLs, emails removed)

---

## 📈 Statistics Summary

| Metric | Value |
|--------|-------|
| Total samples | 218,675 |
| Labeled samples | 198,603 (90.8%) |
| Unlabeled samples | 20,072 (9.2%) |
| Languages | 15+ |
| Code-mixed (Hinglish) | 1,869 (0.9%) |
| Sources | 6 datasets |
| Processing time | ~2 hours |
| Cost | $0 (all free tier) |
| Validation status | ✅ 100% passed |

---
