# Person 2 → Person 3: Annotation & Quality Handoff

**Date:** 2025-10-30 
**From:** Person 2 - Annotation & Quality Lead 
**To:** Person 3 - Model Training Lead 
**Status:** ⏳ **IN PROGRESS**

---

## Executive Summary

This document details Person 2's annotation workflow, tools, and deliverables for producing reliable labels (toxicity binary + subtypes) with strong inter-annotator agreement.

### Deliverables Status

- [x] **Label Studio deployment** (Docker)
- [x] **Annotation guidelines** (with examples and edge cases)
- [x] **Pilot data preparation** (~1,000 items)
- [x] **IAA calculation scripts** (Cohen's κ, per-subtype analysis)
- [x] **Annotation export scripts** (JSONL/CSV with validation)
- [x] **Annotator dashboard** (performance tracking)
- [x] **Adjudication workflow** (for resolving disagreements)
- [ ] **Pilot annotation completed** (κ ≥ 0.70 target)
- [ ] **Full dataset annotated** (20,072 items)
- [ ] **Final IAA report** (attached)
- [ ] **Schema-consistent exports** (ready for training)

---

## Package Contents

```
annotation/
├── docker-compose.yml # Label Studio Docker setup
├── label_studio_template.xml # Annotation interface template
├── ANNOTATION_GUIDELINES.md # Complete annotation guidelines
├── gold_questions.json # Gold standard questions
├── README.md # Setup and workflow guide
├── data/ # Annotation data
│ ├── pilot_annotation_tasks.json
│ ├── pilot_sample.csv
│ └── pilot_manifest.json
└── exports/ # Label Studio exports
 ├── pilot_annotations.json
 ├── iaa_reports/
 │ ├── iaa_report.json
 │ └── disagreements.csv
 └── exports/
 ├── pilot.jsonl
 └── pilot.csv

scripts/
├── 8_prepare_pilot_data.py # Create pilot sample
├── 9_calculate_iaa.py # Calculate IAA metrics
├── 10_export_annotations.py # Export to JSONL/CSV
├── 11_annotator_dashboard.py # Performance dashboard
└── 12_adjudicate_disagreements.py # Adjudication workflow
```

---

## Quick Start Guide

### 1. Deploy Label Studio

```bash
cd annotation
docker-compose up -d
```

Access at: http://localhost:8080

### 2. Prepare Pilot Data

```bash
python scripts/8_prepare_pilot_data.py
```

This creates:
- `annotation/data/pilot_annotation_tasks.json` (import into Label Studio)
- `annotation/gold_questions.json` (annotate manually first!)

### 3. Import Label Studio Template

1. Log into Label Studio
2. Create project → Settings → Labeling Interface
3. Paste contents of `annotation/label_studio_template.xml`
4. Save

### 4. Import & Annotate Pilot

1. Import `annotation/data/pilot_annotation_tasks.json`
2. Assign to 2-3 annotators
3. Each item annotated by at least 2 annotators

### 5. Calculate IAA

```bash
# Export from Label Studio → Save as annotation/exports/pilot_annotations.json
python scripts/9_calculate_iaa.py annotation/exports/pilot_annotations.json
```

**Target:** Cohen's κ ≥ 0.70

If κ < 0.70:
- Review disagreements: `annotation/exports/iaa_reports/disagreements.csv`
- Refine guidelines
- Rerun pilot

### 6. Scale to Full Dataset

Once κ ≥ 0.70:
- Import full dataset (20,072 items)
- Assign batches
- Monitor with dashboard

### 7. Export Final Annotations

```bash
python scripts/10_export_annotations.py annotation/exports/full_annotations.json
```

This creates:
- JSONL export (for training)
- CSV export (for reference)
- Batch manifest (metadata)

---

## Annotation Schema

### Binary Toxicity

- **0** = Non-toxic
- **1** = Toxic

### Toxicity Subtypes (Multi-Label)

If toxic, select all applicable:

- `hate` - Hate speech (identity-based attacks)
- `threat` - Threats of violence
- `insult` - Severe insults/profanity
- `harassment` - Harassment/cyberbullying
- `self_harm` - Self-harm promotion

### Output Schema

```json
{
 "id": "reddit_nhqkwg1",
 "text": "...",
 "label": 0,
 "source": "reddit",
 "language": "en",
 "split": "train",
 "code_mixed": false,
 "metadata": {
 "toxic_types": [],
 "confidence": 2.5,
 "agreement": 1.0,
 "n_annotators": 2,
 "notes": ""
 }
}
```

---

## IAA Metrics

### Binary Toxicity (Cohen's κ)

| κ Value | Interpretation |
|---------|----------------|
| ≥ 0.75 | Excellent agreement |
| 0.60-0.74 | Good agreement |
| 0.40-0.59 | Moderate agreement |
| < 0.40 | Poor agreement |

**Target:** κ ≥ 0.70 before scaling

### Per-Subtype Agreement

Track agreement rate for each subtype:
- `hate`: % agreement
- `threat`: % agreement
- `insult`: % agreement
- `harassment`: % agreement
- `self_harm`: % agreement

---

## Annotation Guidelines Highlights

### Toxic (1) - Include if:
- Hate speech (identity-based attacks)
- Threats of violence
- Severe insults/profanity directed at person/group
- Harassment/cyberbullying
- Self-harm promotion

### Non-Toxic (0) - Include if:
- Constructive criticism
- Strong opinions (without targeting)
- Sarcasm (with clear indicators)
- Mild profanity (not directed)
- Casual code-mixed language ("yaar", "bhai")

### Code-Mixed Considerations

- Context matters! "bhenchod" can be toxic or casual
- Friendly terms ("yaar", "bhai") are non-toxic
- Direct insults in Hinglish are toxic

**See `annotation/ANNOTATION_GUIDELINES.md` for complete guidelines.**

---

## Tools & Scripts

### `scripts/8_prepare_pilot_data.py`
- Creates balanced pilot sample (~1,000 items)
- Prioritizes code-mixed samples
- Generates Label Studio import format

### `scripts/9_calculate_iaa.py`
- Calculates Cohen's kappa (binary)
- Per-subtype agreement rates
- Generates confusion matrices
- Identifies disagreements

### `scripts/10_export_annotations.py`
- Aggregates multiple annotations (majority vote/adjudicated)
- Validates against schema
- Exports JSONL and CSV formats
- Creates batch manifests

### `scripts/11_annotator_dashboard.py`
- Calculates accuracy on gold questions
- Performance metrics per annotator
- Identifies annotators needing review

### `scripts/12_adjudicate_disagreements.py`
- Creates adjudication templates
- Applies adjudicated labels
- Updates exports

---

## Success Criteria

Before handing off to Person 3:

- [ ] Pilot κ ≥ 0.70 achieved
- [ ] All 20,072 items annotated
- [ ] Final IAA report generated
- [ ] Exports pass schema validation
- [ ] Batch manifests created
- [ ] Gold questions accuracy ≥ 80%
- [ ] Documentation complete

---

## Workflow Summary

1. **Setup** → Deploy Label Studio, import template
2. **Pilot** → Annotate ~1,000 items with 2+ annotators
3. **IAA** → Calculate κ, target ≥ 0.70
4. **Refine** → If κ < 0.70, update guidelines, rerun pilot
5. **Scale** → Import full dataset, assign batches
6. **Monitor** → Track annotator performance via dashboard
7. **Adjudicate** → Resolve disagreements
8. **Export** → Generate JSONL/CSV with validation
9. **Validate** → Ensure schema consistency
10. **Handoff** → Deliver to Person 3

---

## 🚨 Important Notes

### DO:
- Annotate gold questions manually before pilot
- Target κ ≥ 0.70 before scaling
- Monitor annotator performance regularly
- Document edge cases and disagreements
- Validate exports before handoff

### DON'T:
- Skip pilot phase
- Scale if κ < 0.70
- Skip schema validation
- Export without checking quality

---

## Questions?

See:
- `annotation/ANNOTATION_GUIDELINES.md` - Complete guidelines
- `annotation/README.md` - Setup instructions
- `scripts/` - Script documentation

---

## Status Check

**Current Phase:** [Fill in: Pilot / Scaling / Export / Complete]

**Pilot Results:**
- κ = [Fill in]
- Status: [Fill in]

**Full Dataset:**
- Annotated: [Fill in] / 20,072
- Status: [Fill in]

**Exports:**
- Location: [Fill in]
- Validation: [Fill in]

---

**Person 2 Sign-Off:** [ ] 
**Ready for Person 3:** [ ] 
**Date:** [ ]

