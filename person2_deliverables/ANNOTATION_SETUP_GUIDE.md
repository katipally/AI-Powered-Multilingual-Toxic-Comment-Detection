# Annotation Setup Guide - Label Studio

This guide will help you set up Label Studio to annotate the 20,072 unlabeled samples.

---

## Step 1: Start Label Studio

```bash
cd person2_deliverables/annotation
docker-compose up -d
```

**Access Label Studio:** http://localhost:8080

**First time setup:**
- Create admin account
- Set password
- Log in

---

## Step 2: Create New Project

1. Click "Create Project"
2. Project Name: "Toxic Comment Detection"
3. Description: "Annotate 20,072 comments as toxic (1) or non-toxic (0) with subtypes"

---

## Step 3: Configure Labeling Interface

1. Go to **Settings** → **Labeling Interface**
2. Copy and paste the contents of `label_studio_template.xml`
3. Click **Save**

This template includes:
- Binary toxicity classification (toxic/non-toxic)
- Multi-label subtypes (hate, threat, insult, harassment, self_harm)
- Optional rationale spans
- Confidence levels
- Notes field

---

## Step 4: Import Data

You have two options:

### Option A: Start with Pilot (Recommended)
1. Go to **Import**
2. Select "Upload JSON files"
3. Upload: `person2_deliverables/annotation/data/pilot_annotation_tasks.json`
4. This imports ~1,000 items for pilot annotation

### Option B: Import Full Dataset
1. First, prepare full dataset:
   ```bash
   python person2_deliverables/scripts/prepare_full_dataset_for_labelstudio.py
   ```
2. Go to **Import** in Label Studio
3. Upload the generated JSON file

---

## Step 5: Assign Annotators

1. Go to **Settings** → **Members**
2. Add annotators (create accounts for each)
3. Assign tasks to annotators
4. **Important:** Each item should be annotated by at least 2 annotators for IAA

---

## Step 6: Annotate Following Schema

### Binary Classification
- **0 (Non-toxic):** Constructive criticism, strong opinions, sarcasm, mild profanity
- **1 (Toxic):** Hate speech, threats, severe insults, harassment, self-harm promotion

### Subtypes (if toxic)
Select all applicable:
- **hate** - Identity-based attacks
- **threat** - Threats of violence
- **insult** - Severe insults/profanity
- **harassment** - Cyberbullying/repeated targeting
- **self_harm** - Self-harm promotion

### Confidence
- **High:** Clear case, follows guidelines directly
- **Medium:** Generally clear with some nuance
- **Low:** Edge case, requires interpretation

### Guidelines
See `person2_deliverables/annotation/ANNOTATION_GUIDELINES.md` for:
- Complete guidelines
- Examples
- Edge case handling
- Code-mixed considerations

---

## Step 7: Export Annotations

After annotation:

1. Go to **Export**
2. Select "JSON" format
3. Download export file
4. Save as: `person2_deliverables/annotation/exports/annotations.json`

---

## Step 8: Calculate IAA (Inter-Annotator Agreement)

```bash
python person2_deliverables/scripts/9_calculate_iaa.py \
  person2_deliverables/annotation/exports/annotations.json
```

**Target:** Cohen's κ ≥ 0.70

If κ < 0.70:
- Review disagreements
- Refine guidelines
- Retrain annotators
- Rerun pilot

---

## Step 9: Export Final Annotations

```bash
python person2_deliverables/scripts/10_export_annotations.py \
  person2_deliverables/annotation/exports/annotations.json
```

This creates:
- JSONL export (for training)
- CSV export (for reference)
- Batch manifest

---

## Step 10: Monitor Annotator Performance

```bash
python person2_deliverables/scripts/11_annotator_dashboard.py \
  person2_deliverables/annotation/exports/annotations.json \
  person2_deliverables/annotation/gold_questions.json
```

---

## Quick Start Summary

```bash
# 1. Start Label Studio
cd person2_deliverables/annotation
docker-compose up -d

# 2. Access: http://localhost:8080
# 3. Create project and import pilot data
# 4. Configure template (paste label_studio_template.xml)
# 5. Annotate!
```

---

## Important Notes

1. **Pilot First:** Start with ~1,000 items to calibrate annotators
2. **IAA Target:** Achieve κ ≥ 0.70 before scaling
3. **Priority:** Focus on code-mixed samples first (1,869 items)
4. **Review Guidelines:** Read `ANNOTATION_GUIDELINES.md` before starting
5. **Gold Questions:** Manually annotate 50 gold questions first for quality control

---

## Troubleshooting

**Label Studio won't start:**
```bash
docker-compose logs
docker-compose down
docker-compose up -d
```

**Port 8080 already in use:**
- Edit `docker-compose.yml` to change port
- Or: `lsof -ti:8080 | xargs kill`

**Need to reset:**
```bash
docker-compose down -v  # Removes volumes
docker-compose up -d
```

---

## Files You'll Need

- `person2_deliverables/annotation/docker-compose.yml` - Docker setup
- `person2_deliverables/annotation/label_studio_template.xml` - Interface template
- `person2_deliverables/annotation/ANNOTATION_GUIDELINES.md` - Complete guidelines
- `person2_deliverables/annotation/data/pilot_annotation_tasks.json` - Pilot data

---

Ready to start annotating!

