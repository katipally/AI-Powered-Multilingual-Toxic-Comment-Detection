# Dataset Card: Code-Mixed Toxic Comment Detection Corpus

**Version:** 1.0.0  
**Created:** October 30, 2025  
**Lead:** Person 1 - Data Collection & Preprocessing  
**License:** See individual dataset licenses below  
**Random Seed:** 42 (for reproducibility)

---

## Table of Contents
1. [Dataset Summary](#dataset-summary)
2. [Dataset Composition](#dataset-composition)
3. [Collection Methodology](#collection-methodology)
4. [Data Preprocessing](#data-preprocessing)
5. [Train/Dev/Test Splits](#traindevtest-splits)
6. [Known Limitations & Biases](#known-limitations--biases)
7. [Intended Use](#intended-use)
8. [Data Distribution](#data-distribution)
9. [Terms of Service Compliance](#terms-of-service-compliance)
10. [Removal Procedures](#removal-procedures)
11. [Appendix: Statistics](#appendix-statistics)

---

## 1. Dataset Summary

### Overview
This corpus combines 6 publicly available datasets focused on **toxic comment detection in multilingual and code-mixed text**, with special emphasis on Hindi-English (Hinglish) code-mixing. The dataset is specifically designed for training and evaluating models that can:

- Detect toxic/hateful content in English and 14+ other languages
- Handle code-mixed (Romanized Hindi-English) text
- Provide fairness evaluation through identity annotations
- Enable explainable AI through rationale annotations

### Key Statistics
| Metric | Count |
|--------|-------|
| **Total Samples** | 218,675 |
| **Labeled Samples** | 198,603 (90.8%) |
| **Unlabeled Samples (for annotation)** | 20,072 (9.2%) |
| **Languages** | 15+ languages |
| **Code-Mixed Samples** | 1,869 Hindi-English |
| **Training Samples** | 139,022 (70%) |
| **Dev Samples** | 29,790 (15%) |
| **Test Samples** | 29,791 (15%) |

### Label Distribution (Labeled Data)
- **Non-Toxic (0):** 143,536 samples (72.3%)
- **Toxic (1):** 55,067 samples (27.7%)
- **Balance Ratio:** 0.38 (reasonable for training)

---

## 2. Dataset Composition

### 2.1 Source Datasets

| # | Dataset | Samples | Purpose | License | URL |
|---|---------|---------|---------|---------|-----|
| 1 | **Jigsaw Unintended Bias** | 100,000 | Fairness evaluation | CC0 | [Kaggle](https://www.kaggle.com/c/jigsaw-unintended-bias-in-toxicity-classification) |
| 2 | **TextDetox** | 71,374 | Multilingual (15 langs) | Apache 2.0 | [HuggingFace](https://huggingface.co/datasets/textdetox/multilingual_toxicity_dataset) |
| 3 | **HateXplain** | 19,229 | Explainability (rationales) | MIT | [GitHub](https://github.com/hate-alert/HateXplain) |
| 4 | **Jigsaw Multilingual** | 8,000 | Multilingual baseline | CC0 | [Kaggle](https://www.kaggle.com/c/jigsaw-multilingual-toxic-comment-classification) |
| 5 | **Reddit** | 10,000 | Code-mixed (unlabeled) | Reddit API Terms | Collected via PRAW |
| 6 | **YouTube** | 10,072 | Code-mixed (unlabeled) | YouTube API Terms | Collected via Google API |

### 2.2 Schema

All datasets follow this unified schema:

| Column | Type | Description |
|--------|------|-------------|
| `id` | string | Unique identifier (format: `{source}_{original_id}`) |
| `text` | string | Cleaned comment/post text |
| `label` | int | 0 = non-toxic, 1 = toxic (null for unlabeled) |
| `source` | string | Dataset origin (hatexplain, jigsaw_bias, etc.) |
| `language` | string | ISO language code (en, hi, es, etc.) |
| `split` | string | train/dev/test/unlabeled |
| `code_mixed` | boolean | True if Hindi-English code-mixed |
| `metadata` | json | Source-specific fields (rationales, identities, etc.) |

### 2.3 Language Distribution (Labeled Data)

| Language | Samples | Percentage |
|----------|---------|------------|
| English (en) | 124,229 | 62.6% |
| Hindi (hi) | 9,363 | 4.7% |
| Spanish (es) | 7,500 | 3.8% |
| Italian (it) | 7,500 | 3.8% |
| Russian (ru) | 5,000 | 2.5% |
| Ukrainian (uk) | 5,000 | 2.5% |
| German (de) | 5,000 | 2.5% |
| Amharic (am) | 5,000 | 2.5% |
| Chinese (zh) | 5,000 | 2.5% |
| Arabic (ar) | 5,000 | 2.5% |
| **Others** | 23,011 | 11.6% |

---

## 3. Collection Methodology

### 3.1 Public Datasets (Labeled)
- **Downloaded:** October 28-30, 2025
- **Method:** Official APIs (Kaggle, HuggingFace)
- **Sampling:** 
  - Jigsaw Bias: Sampled 100,000 from 1.8M for efficiency
  - Jigsaw Multilingual: Sampled 8,000 from validation set
  - Others: Complete datasets

### 3.2 Reddit Collection (Unlabeled)
- **API:** PRAW (Python Reddit API Wrapper) v7.7.0
- **Time Period:** October 2025
- **Subreddits:** 28 Indian subreddits (r/india, r/bollywood, r/mumbai, etc.)
- **Sampling Strategy:** Hot, New, and Top posts from each subreddit
- **Rate Limiting:** 100 queries/minute (within API limits)
- **Filters Applied:**
  - Removed deleted/removed comments
  - Removed AutoModerator posts
  - Minimum length: 10 characters
- **Total Collected:** 10,000 comments
- **Code-Mixed Identified:** 927 (9.3%)

### 3.3 YouTube Collection (Unlabeled)
- **API:** YouTube Data API v3
- **Time Period:** October 2025
- **Video Sources:** 40 manually selected Bollywood/Indian content videos
- **Selection Criteria:** 
  - High engagement (>10k views)
  - Recent (2024-2025)
  - Likely to contain code-mixed comments
- **Quota Management:** <1% of daily quota used
- **Filters Applied:**
  - Minimum length: 10 characters
  - Duplicate removal
- **Total Collected:** 10,072 comments
- **Code-Mixed Identified:** 942 (9.4%)

### 3.4 Collection Scripts
All collection scripts are available in `scripts/` directory:
- `1_download_hatexplain.py` - Downloads HateXplain from GitHub
- `2_collect_reddit.py` - Collects Reddit comments via PRAW
- `3_collect_youtube.py` - Collects YouTube comments via API
- `4_download_textdetox.py` - Downloads TextDetox from HuggingFace
- `find_youtube_videos.py` - Helper to find relevant videos

---

## 4. Data Preprocessing

### 4.1 Text Cleaning Pipeline

All texts underwent the following normalization (implemented in `utils/text_normalization.py`):

1. **HTML Removal:** Stripped HTML tags and decoded entities
2. **URL Normalization:** Replaced URLs with `[URL]` token
3. **Email Normalization:** Replaced emails with `[EMAIL]` token
4. **Mention Normalization:** Replaced @mentions with `[MENTION]` token
5. **Hashtag Processing:** Kept text content, removed # symbol
6. **Punctuation Normalization:** Reduced excessive punctuation (e.g., "!!!" → "!")
7. **Whitespace Normalization:** Converted multiple spaces to single space
8. **Unicode Normalization:** NFKC normalization for consistency
9. **Romanized Hindi Normalization:** Standardized common Hindi words in Roman script
   - Examples: "bhaii" → "bhai", "nai" → "nahi", "kese" → "kaise"
   - 50+ common words normalized
10. **Emoji Handling:** Preserved emoji for sentiment context

### 4.2 Label Standardization

- **HateXplain:** 3-class (hate/offensive/normal) → binary (hate|offensive→1, normal→0)
- **Jigsaw Bias:** Continuous [0-1] → binary (≥0.5→1, <0.5→0)
- **TextDetox:** Already binary (0/1)
- **Jigsaw Multilingual:** Already binary (0/1)

### 4.3 Language Detection

- **Tool:** `langdetect` library (Google's language detection)
- **Fallback:** Character-set based detection for Devanagari, Arabic, Chinese
- **Code-Mixed Detection:** Pattern matching for Hindi words in Roman script
  - Keywords: yaar, bhai, hai, nahi, kya, mein, etc.
  - Threshold: ≥2 Hindi keywords + ≥5 total words

### 4.4 ID Generation

- **Format:** `{source}_{original_id}` or `{source}_{uuid}_{index}`
- **Uniqueness:** 100% unique IDs verified (no duplicates)
- **Consistency:** All 218,675 samples have valid IDs

### 4.5 Deduplication

**Exact Duplicates:**
- **Method:** MD5 hash of normalized text
- **Labeled Data:** 2,926 duplicates (1.47%) - acceptable
- **Unlabeled Data:** 2,819 duplicates (14.04%) - acceptable for social media

**Near-Duplicates:**
- **Method:** TF-IDF + Cosine similarity (threshold 0.95)
- **Status:** Not applied (preserves dataset diversity)
- **Utility Available:** `utils/deduplication.py` for future use

### 4.6 Quality Validation

All data passed the following checks:
- ✅ Schema validation (8 required columns)
- ✅ No null values in critical fields (id, text, source)
- ✅ Text length: 1-6,112 characters (mean: 216 for labeled, 100 for unlabeled)
- ✅ All labels valid (0 or 1)
- ✅ Metadata JSON parseable
- ✅ All IDs unique

---

## 5. Train/Dev/Test Splits

### 5.1 Methodology

- **Method:** Stratified splitting using `sklearn.model_selection.train_test_split`
- **Stratification Keys:**
  - Label (toxic/non-toxic)
  - Language group (English/Hindi/Other)
  - Code-mixed status
- **Random Seed:** 42 (frozen for reproducibility)
- **Split Ratio:** 70% train / 15% dev / 15% test

### 5.2 Split Statistics

| Split | Samples | Toxic % | English % | Hindi % | Other % | Code-Mixed |
|-------|---------|---------|-----------|---------|---------|------------|
| **Train** | 139,022 | 27.7% | 62.6% | 4.7% | 32.7% | 0 |
| **Dev** | 29,790 | 27.7% | 62.6% | 4.7% | 32.7% | 0 |
| **Test** | 29,791 | 27.7% | 62.6% | 4.7% | 32.7% | 0 |

**Validation:** All splits maintain consistent class balance and language distribution.

### 5.3 Split Files

Located in `Final_input/splits/`:
- `train.csv` - Training set (139,022 samples)
- `dev.csv` - Development/validation set (29,790 samples)
- `test.csv` - Test set (29,791 samples)
- `split_manifest.json` - Detailed split metadata

---

## 6. Known Limitations & Biases

### 6.1 Dataset Limitations

1. **English-Heavy:** 62.6% English content (reflects source datasets)
2. **Limited Code-Mixed Data:** Only 1,869 labeled code-mixed samples (0.9%)
3. **Temporal Bias:** Data collected in October 2025; may not reflect future language evolution
4. **Platform Bias:** Reddit and YouTube have platform-specific toxicity patterns
5. **Sampling Bias:** Jigsaw Bias sampled 100k/1.8M; may miss rare cases

### 6.2 Known Biases

1. **Identity Bias (from Jigsaw Bias dataset):**
   - Contains comments mentioning identities: gender, race, religion, sexual orientation
   - Use `metadata` field for fairness evaluation
   - Identity annotations available for bias mitigation

2. **Language Bias:**
   - Overrepresents English and major European languages
   - Underrepresents low-resource languages
   - Code-mixed data limited to Hindi-English

3. **Topic Bias:**
   - Reddit: Indian politics, Bollywood, cricket
   - YouTube: Bollywood, entertainment
   - May not generalize to all domains

4. **Labeling Bias:**
   - Different datasets use different annotation guidelines
   - Binary labels may miss nuanced toxicity
   - HateXplain has more hate speech due to targeted collection

### 6.3 PII (Personally Identifiable Information)

- **Removed:** URLs, emails replaced with tokens
- **Redacted:** @mentions replaced with `[MENTION]`
- **Remaining:** Public social media usernames in metadata (original collection)
- **Recommendation:** Do not expose metadata publicly; use for research only

---

## 7. Intended Use

### 7.1 Primary Use Cases

✅ **Recommended:**
- Training toxic comment detection models
- Multilingual toxicity research
- Code-mixed text analysis (Hindi-English)
- Fairness and bias research using identity annotations
- Explainable AI research using HateXplain rationales
- Benchmarking toxicity classifiers

### 7.2 Out-of-Scope Use

❌ **Not Recommended:**
- Production deployment without additional validation
- Identifying real individuals (PII scrubbed)
- Languages outside the 15 represented languages
- Domains significantly different from social media
- Real-time content moderation without human review

### 7.3 Ethical Considerations

- **Human Review Required:** For production deployment
- **Regular Retraining:** Language evolves; model drift expected
- **Bias Monitoring:** Use identity annotations for fairness metrics
- **User Impact:** False positives/negatives affect users; tune accordingly

---

## 8. Data Distribution

### 8.1 Access

**GitHub Repository:** [To be added by team]

**Files Included:**
```
Final_input/
├── labeled/
│   ├── all_labeled_data.csv (198,603 samples, 80 MB)
│   └── [individual source CSVs]
├── unlabeled/
│   └── for_annotation.csv (20,072 samples, 8 MB)
├── splits/
│   ├── train.csv (139,022 samples)
│   ├── dev.csv (29,790 samples)
│   ├── test.csv (29,791 samples)
│   └── split_manifest.json
└── reports/
    ├── processing_report.json
    └── validation_report.json
```

### 8.2 Citation

```bibtex
@dataset{code_mixed_toxic_2025,
  title={Code-Mixed Toxic Comment Detection Corpus},
  author={[Team Name]},
  year={2025},
  month={October},
  version={1.0.0},
  note={Combined corpus from Jigsaw, HateXplain, TextDetox, Reddit, and YouTube}
}
```

---

## 9. Terms of Service Compliance

### 9.1 Reddit API
- **Compliance:** ✅ Collected using official PRAW SDK
- **Rate Limits:** ✅ Stayed under 100 QPM limit
- **TOS:** ✅ Data for research purposes only
- **Attribution:** Required for Reddit-sourced data

### 9.2 YouTube API
- **Compliance:** ✅ Collected using official Google API
- **Quota:** ✅ Used <1% of daily quota
- **TOS:** ✅ Data for research purposes only
- **Attribution:** Required for YouTube-sourced data
- **No Storage of Videos:** Only comments stored

### 9.3 Public Datasets
- **Jigsaw (Kaggle):** CC0 license (public domain)
- **HateXplain:** MIT license
- **TextDetox:** Apache 2.0 license
- **All:** Properly attributed in this data card

### 9.4 License Summary

| Component | License |
|-----------|---------|
| Jigsaw Datasets | CC0-1.0 (Public Domain) |
| HateXplain | MIT |
| TextDetox | Apache-2.0 |
| Reddit Data | Research use (Reddit API Terms) |
| YouTube Data | Research use (YouTube API Terms) |
| Our Preprocessing Code | MIT |
| This Data Card | CC-BY-4.0 |

---

## 10. Removal Procedures

### 10.1 Content Removal Requests

If you are a content creator and want your content removed:

1. **Email:** [To be added by team]
2. **Subject:** "Data Removal Request - Toxic Comment Corpus"
3. **Include:**
   - Your Reddit username or YouTube channel ID
   - Comment text or comment ID
   - Proof of ownership
4. **Timeline:** We will respond within 5 business days

### 10.2 Automated Removal

For future updates, we will:
- Check for deleted Reddit comments via API
- Check for deleted YouTube comments via API
- Remove if original author deleted content

---

## 11. Appendix: Statistics

### 11.1 Full Language Breakdown

| Language | Code | Samples | Percentage |
|----------|------|---------|------------|
| English | en | 124,229 | 62.6% |
| Hindi | hi | 9,363 | 4.7% |
| Spanish | es | 7,500 | 3.8% |
| Italian | it | 7,500 | 3.8% |
| Russian | ru | 5,000 | 2.5% |
| Ukrainian | uk | 5,000 | 2.5% |
| German | de | 5,000 | 2.5% |
| Amharic | am | 5,000 | 2.5% |
| Chinese | zh | 5,000 | 2.5% |
| Arabic | ar | 5,000 | 2.5% |
| French | fr | 5,000 | 2.5% |
| Tatar | tt | 5,000 | 2.5% |
| Japanese | ja | 5,000 | 2.5% |
| Turkish | tr | 3,000 | 1.5% |
| Hebrew | he | 2,011 | 1.0% |

### 11.2 Text Length Distribution

| Metric | Labeled | Unlabeled |
|--------|---------|-----------|
| Mean | 216 chars | 100 chars |
| Median | 125 chars | 54 chars |
| Min | 1 char | 10 chars |
| Max | 3,691 chars | 6,112 chars |

### 11.3 Collection Timeline

- **Oct 28, 2025:** Jigsaw datasets acquired
- **Oct 29, 2025:** HateXplain and TextDetox downloaded
- **Oct 30, 2025:** Reddit and YouTube collection completed
- **Oct 30, 2025:** Preprocessing and unification completed
- **Oct 30, 2025:** Stratified splits created

### 11.4 Processing Statistics

- **Total processing time:** ~2 hours (including validation)
- **Preprocessing runtime:** 30 seconds
- **Validation runtime:** 10 seconds
- **Split creation runtime:** 5 seconds
- **Total cost:** $0 (all free tier APIs)

---

**Data Card Version:** 1.0.0  
**Last Updated:** October 30, 2025  
**Maintainer:** Person 1 - Data Collection & Preprocessing Team  
**Contact:** [To be added by team]
