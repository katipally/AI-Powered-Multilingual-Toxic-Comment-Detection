# Annotation Setup & Workflow

This directory contains all files needed for Person 2 annotation tasks.

## Quick Start

### 1. Start Label Studio (Docker)

```bash
cd annotation
docker-compose up -d
```

Label Studio will be available at: http://localhost:8080

**Default credentials:** (set on first login)
- Username: admin
- Password: (you'll be prompted to set this)

### 2. Prepare Pilot Data

```bash
python scripts/8_prepare_pilot_data.py
```

This creates:
- `annotation/data/pilot_annotation_tasks.json` - Import this into Label Studio
- `annotation/data/pilot_sample.csv` - Reference CSV
- `annotation/gold_questions.json` - Manually annotate these first!

### 3. Import Label Studio Template

1. Log into Label Studio
2. Create a new project
3. Go to Settings → Labeling Interface
4. Copy contents of `label_studio_template.xml` into the editor
5. Save

### 4. Import Pilot Tasks

1. Go to Import
2. Select "Upload JSON files"
3. Upload `annotation/data/pilot_annotation_tasks.json`

### 5. Annotate Pilot (~1,000 items)

- Assign to 2-3 annotators
- Each item should be annotated by at least 2 annotators
- Focus on quality over speed

### 6. Calculate IAA

After pilot annotation:

```bash
# Export from Label Studio (Settings → Export)
# Save as: annotation/exports/pilot_annotations.json

# Calculate IAA
python scripts/9_calculate_iaa.py annotation/exports/pilot_annotations.json
```

**Target:** Cohen's κ ≥ 0.70

If κ < 0.70:
- Review disagreements
- Refine guidelines
- Rerun pilot

### 7. Scale Annotation

Once κ ≥ 0.70:
- Import full dataset (20,072 items)
- Assign batches to annotators
- Monitor performance with dashboard

### 8. Export Annotations

```bash
python scripts/10_export_annotations.py annotation/exports/full_annotations.json
```

This creates:
- JSONL export
- CSV export
- Batch manifest

### 9. Monitor Annotators

```bash
python scripts/11_annotator_dashboard.py \
 annotation/exports/annotations.json \
 annotation/gold_questions.json
```

---

## Directory Structure

```
annotation/
├── docker-compose.yml # Docker setup for Label Studio
├── label_studio_template.xml # Label Studio interface template
├── ANNOTATION_GUIDELINES.md # Complete annotation guidelines
├── gold_questions.json # Gold standard questions (manually annotated)
├── README.md # This file
├── data/ # Annotation data
│ ├── pilot_annotation_tasks.json
│ ├── pilot_sample.csv
│ └── pilot_manifest.json
└── exports/ # Label Studio exports
 ├── pilot_annotations.json
 ├── iaa_reports/
 │ └── iaa_report.json
 └── exports/
 ├── pilot.jsonl
 └── pilot.csv
```

---

## Scripts Reference

### `scripts/8_prepare_pilot_data.py`
Creates pilot sample (~1,000 items) prioritizing code-mixed data.

### `scripts/9_calculate_iaa.py`
Calculates Cohen's kappa and generates IAA reports.

### `scripts/10_export_annotations.py`
Exports annotations from Label Studio to JSONL/CSV formats.

### `scripts/11_annotator_dashboard.py`
Generates performance dashboard for annotators based on gold questions.

---

## Success Criteria

- [ ] Pilot κ ≥ 0.70 achieved
- [ ] All 20,072 items annotated
- [ ] Exports pass schema validation
- [ ] IAA report attached
- [ ] Batch manifests generated
- [ ] Ready for Person 3 training

---

## Troubleshooting

### Label Studio won't start
- Check Docker is running: `docker ps`
- Check ports: `lsof -i :8080`
- View logs: `docker-compose logs`

### Import fails
- Check JSON format matches Label Studio expected format
- Verify file encoding (UTF-8)

### IAA too low
- Review disagreements: `annotation/exports/iaa_reports/disagreements.csv`
- Update guidelines based on patterns
- Retrain annotators

---

## Support

For questions or issues, see `ANNOTATION_GUIDELINES.md` or contact the annotation lead.

