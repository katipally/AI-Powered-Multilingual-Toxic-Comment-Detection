# START HERE: Annotation Guide

## Your Main Task

**Annotate 20,072 unlabeled samples with:**
1. **Binary toxicity** (0 = non-toxic, 1 = toxic)
2. **Subtype taxonomy** (if toxic: hate, threat, insult, harassment, self_harm)

---

## Quick Start (5 Steps)

### Step 1: Start Label Studio

```bash
cd person2_deliverables/annotation
docker-compose up -d
```

Open: **http://localhost:8080**

### Step 2: Create Project & Configure Template

1. Create new project in Label Studio
2. Go to **Settings** → **Labeling Interface**
3. Copy/paste contents of `label_studio_template.xml`
4. Save

### Step 3: Import Data

**Option A: Start with Pilot (Recommended)**
- Import: `person2_deliverables/annotation/data/pilot_annotation_tasks.json` (~1,000 items)

**Option B: Import Full Dataset**
- Import: `person2_deliverables/annotation/data/full_annotation_tasks.json` (20,072 items)

### Step 4: Annotate Following Schema

For each comment:
1. **Binary:** Toxic (1) or Non-toxic (0)
2. **If Toxic:** Select all applicable subtypes:
   - hate
   - threat
   - insult
   - harassment
   - self_harm
3. **Confidence:** High/Medium/Low
4. **Notes:** Add if edge case

### Step 5: Export & Validate

After annotation:
```bash
# Export from Label Studio → Save as JSON
# Then run:
python person2_deliverables/scripts/10_export_annotations.py <export_file.json>
```

---

## Important Files

- **Template:** `person2_deliverables/annotation/label_studio_template.xml`
- **Guidelines:** `person2_deliverables/annotation/ANNOTATION_GUIDELINES.md`
- **Pilot Data:** `person2_deliverables/annotation/data/pilot_annotation_tasks.json`
- **Full Data:** `person2_deliverables/annotation/data/full_annotation_tasks.json`

---

## Current Status

- **Total samples:** 20,072
- **Preliminary automated labels:** 20,072 (very conservative, needs human review)
- **Proper human annotation:** 0 (needs to be done)

**You need to annotate all 20,072 samples properly using Label Studio!**

---

## Next Steps

1. Start Label Studio
2. Import data
3. Begin annotation following guidelines
4. Export annotations
5. Calculate IAA
6. Refine if needed

**See `ANNOTATION_SETUP_GUIDE.md` for detailed instructions.**

