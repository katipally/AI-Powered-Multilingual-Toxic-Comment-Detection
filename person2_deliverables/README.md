# Person 2 Deliverables

This folder contains all Person 2 annotation infrastructure and tools.

## Structure

```
person2_deliverables/
├── annotation/              # Label Studio setup and templates
│   ├── docker-compose.yml
│   ├── label_studio_template.xml
│   ├── ANNOTATION_GUIDELINES.md
│   ├── README.md
│   └── data/               # Pilot data
│
├── scripts/                 # Person 2 annotation scripts
│   ├── 8_prepare_pilot_data.py
│   ├── 9_calculate_iaa.py
│   ├── 10_export_annotations.py
│   ├── 11_annotator_dashboard.py
│   └── 12_adjudicate_disagreements.py
│
└── docs/                    # Documentation
    ├── PERSON2_HANDOFF.md
    ├── PERSON2_TASKS_SUMMARY.md
    ├── PERSON2_REQUIREMENTS_VERIFICATION.md
    └── PERSON2_COMPLETION_CHECKLIST.md
```

## Quick Start

1. **Set up Label Studio:**
   ```bash
   cd annotation
   docker-compose up -d
   ```

2. **Prepare pilot data:**
   ```bash
   python scripts/8_prepare_pilot_data.py
   ```

3. **See `annotation/README.md` for complete workflow.**

## Files

All Person 2 deliverables are organized here to keep the original repository structure unchanged.

