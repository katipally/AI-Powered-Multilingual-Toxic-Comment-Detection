"""
Data Quality Validation Script
Validates preprocessed data and generates comprehensive quality reports

Checks:
- Data integrity (no nulls in required fields)
- Text quality (length, encoding, duplicates)
- Label distribution and balance
- Language consistency
- Schema validation
- Statistical summaries

Author: Person 1 - Data Collection & Preprocessing
Date: Oct 30, 2025
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import sys
from collections import Counter

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_DIR = PROJECT_ROOT / 'Final_input'

print("=" * 80)
print("DATA QUALITY VALIDATION")
print("=" * 80)
print(f"\nValidating: {INPUT_DIR}")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n" + "=" * 80)

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_schema(df, expected_columns, dataset_name):
    """Validate that dataframe has expected columns"""
    print(f"\n📋 Schema Validation: {dataset_name}")
    
    missing = set(expected_columns) - set(df.columns)
    extra = set(df.columns) - set(expected_columns)
    
    if missing:
        print(f"  ❌ Missing columns: {missing}")
        return False
    
    if extra:
        print(f"  ⚠️  Extra columns: {extra}")
    
    print(f"  ✓ Schema valid: {len(df.columns)} columns")
    return True

def check_nulls(df, dataset_name):
    """Check for null values in critical columns"""
    print(f"\n🔍 Null Value Check: {dataset_name}")
    
    critical_columns = ['id', 'text', 'source']
    issues = []
    
    for col in critical_columns:
        if col in df.columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                pct = (null_count / len(df)) * 100
                print(f"  ❌ {col}: {null_count:,} nulls ({pct:.2f}%)")
                issues.append(col)
            else:
                print(f"  ✓ {col}: No nulls")
    
    return len(issues) == 0

def check_text_quality(df, dataset_name):
    """Check text field quality"""
    print(f"\n📝 Text Quality Check: {dataset_name}")
    
    if 'text' not in df.columns:
        print("  ⚠️  No 'text' column found")
        return False
    
    # Length statistics
    df['text_length'] = df['text'].astype(str).str.len()
    
    print(f"  Text length statistics:")
    print(f"    Mean:   {df['text_length'].mean():.1f} characters")
    print(f"    Median: {df['text_length'].median():.1f} characters")
    print(f"    Min:    {df['text_length'].min()} characters")
    print(f"    Max:    {df['text_length'].max()} characters")
    
    # Check for very short texts
    very_short = (df['text_length'] < 10).sum()
    if very_short > 0:
        pct = (very_short / len(df)) * 100
        print(f"  ⚠️  Very short texts (<10 chars): {very_short:,} ({pct:.2f}%)")
    else:
        print(f"  ✓ No very short texts")
    
    # Check for empty texts
    empty = df['text'].isna().sum() + (df['text'].astype(str).str.strip() == '').sum()
    if empty > 0:
        pct = (empty / len(df)) * 100
        print(f"  ❌ Empty texts: {empty:,} ({pct:.2f}%)")
    else:
        print(f"  ✓ No empty texts")
    
    return empty == 0

def check_duplicates(df, dataset_name):
    """Check for duplicate texts"""
    print(f"\n🔄 Duplicate Check: {dataset_name}")
    
    if 'text' not in df.columns:
        return True
    
    # Check exact duplicates
    exact_dupes = df['text'].duplicated().sum()
    if exact_dupes > 0:
        pct = (exact_dupes / len(df)) * 100
        # For social media data, up to 20% duplicates is acceptable
        threshold = 0.20 if 'unlabeled' in dataset_name else 0.05
        if pct / 100 > threshold:
            print(f"  ⚠️  High duplicate texts: {exact_dupes:,} ({pct:.2f}%)")
        else:
            print(f"  ⚠️  Some duplicate texts: {exact_dupes:,} ({pct:.2f}%) - acceptable for social media")
    else:
        print(f"  ✓ No exact duplicates")
    
    # Check duplicate IDs (CRITICAL - must be unique)
    if 'id' in df.columns:
        id_dupes = df['id'].duplicated().sum()
        if id_dupes > 0:
            print(f"  ❌ Duplicate IDs: {id_dupes:,} - CRITICAL ERROR")
            return False
        else:
            print(f"  ✓ All IDs unique")
    
    # Duplicates acceptable if within threshold
    threshold = 0.20 if 'unlabeled' in dataset_name else 0.05
    return exact_dupes < len(df) * threshold

def check_labels(df, dataset_name):
    """Check label distribution and validity"""
    print(f"\n🏷️  Label Check: {dataset_name}")
    
    if 'label' not in df.columns:
        print("  ⚠️  No 'label' column (unlabeled data)")
        return True
    
    # Check for nulls in labeled data
    null_labels = df['label'].isna().sum()
    if null_labels > 0:
        if null_labels == len(df):
            print(f"  ℹ️  All samples unlabeled (for annotation)")
            return True
        else:
            pct = (null_labels / len(df)) * 100
            print(f"  ⚠️  Null labels: {null_labels:,} ({pct:.2f}%)")
    
    # Label distribution
    labeled = df[df['label'].notna()]
    if len(labeled) > 0:
        label_counts = labeled['label'].value_counts().sort_index()
        print(f"  Label distribution:")
        for label, count in label_counts.items():
            pct = (count / len(labeled)) * 100
            label_name = 'Toxic' if label == 1 else 'Non-toxic'
            print(f"    • {label_name:12s} ({label}): {count:,} ({pct:.1f}%)")
        
        # Check balance
        if len(label_counts) == 2:
            ratio = label_counts.min() / label_counts.max()
            if ratio < 0.1:
                print(f"  ⚠️  Highly imbalanced (ratio: {ratio:.2f})")
            elif ratio < 0.3:
                print(f"  ⚠️  Moderately imbalanced (ratio: {ratio:.2f})")
            else:
                print(f"  ✓ Reasonably balanced (ratio: {ratio:.2f})")
    
    # Check valid values (should be 0 or 1)
    invalid = labeled[~labeled['label'].isin([0, 1])]
    if len(invalid) > 0:
        print(f"  ❌ Invalid label values: {len(invalid):,} (not 0 or 1)")
        return False
    else:
        print(f"  ✓ All labels are valid (0 or 1)")
    
    return True

def check_language(df, dataset_name):
    """Check language distribution"""
    print(f"\n🌍 Language Check: {dataset_name}")
    
    if 'language' not in df.columns:
        print("  ⚠️  No 'language' column")
        return True
    
    lang_counts = df['language'].value_counts()
    print(f"  Languages detected: {len(lang_counts)}")
    print(f"  Top 10 languages:")
    for lang, count in lang_counts.head(10).items():
        pct = (count / len(df)) * 100
        print(f"    • {lang:10s}: {count:,} ({pct:.1f}%)")
    
    # Check for unknown languages
    unknown = df[df['language'] == 'unknown']
    if len(unknown) > 0:
        pct = (len(unknown) / len(df)) * 100
        print(f"  ⚠️  Unknown language: {len(unknown):,} ({pct:.2f}%)")
    
    return True

def check_code_mixed(df, dataset_name):
    """Check code-mixed content"""
    print(f"\n🔀 Code-Mixed Check: {dataset_name}")
    
    if 'code_mixed' not in df.columns:
        print("  ⚠️  No 'code_mixed' column")
        return True
    
    cm_count = df['code_mixed'].sum()
    if cm_count > 0:
        pct = (cm_count / len(df)) * 100
        print(f"  ✓ Code-mixed samples: {cm_count:,} ({pct:.1f}%)")
        
        # By source
        if 'source' in df.columns:
            print(f"  Code-mixed by source:")
            for source in df['source'].unique():
                source_df = df[df['source'] == source]
                cm_in_source = source_df['code_mixed'].sum()
                if cm_in_source > 0:
                    pct = (cm_in_source / len(source_df)) * 100
                    print(f"    • {source:15s}: {cm_in_source:,} ({pct:.1f}%)")
    else:
        print(f"  ℹ️  No code-mixed samples detected")
    
    return True

def check_metadata(df, dataset_name):
    """Check metadata field"""
    print(f"\n📦 Metadata Check: {dataset_name}")
    
    if 'metadata' not in df.columns:
        print("  ⚠️  No 'metadata' column")
        return True
    
    # Check if metadata is valid JSON
    invalid_json = 0
    for idx, meta in df['metadata'].head(100).items():
        if pd.notna(meta):
            try:
                json.loads(meta)
            except json.JSONDecodeError:
                invalid_json += 1
    
    if invalid_json > 0:
        print(f"  ❌ Invalid JSON in metadata: {invalid_json} / 100 samples checked")
        return False
    else:
        print(f"  ✓ Metadata JSON valid (checked 100 samples)")
    
    return True

def generate_quality_report(df, dataset_name):
    """Generate comprehensive quality report"""
    
    report = {
        'dataset': dataset_name,
        'validation_date': datetime.now().isoformat(),
        'total_samples': int(len(df)),
        'columns': list(df.columns),
        'checks': {}
    }
    
    # Run all checks
    report['checks']['schema'] = bool(validate_schema(
        df, 
        ['id', 'text', 'label', 'source', 'language', 'split', 'code_mixed', 'metadata'],
        dataset_name
    ))
    report['checks']['nulls'] = bool(check_nulls(df, dataset_name))
    report['checks']['text_quality'] = bool(check_text_quality(df, dataset_name))
    report['checks']['duplicates'] = bool(check_duplicates(df, dataset_name))
    report['checks']['labels'] = bool(check_labels(df, dataset_name))
    report['checks']['language'] = bool(check_language(df, dataset_name))
    report['checks']['code_mixed'] = bool(check_code_mixed(df, dataset_name))
    report['checks']['metadata'] = bool(check_metadata(df, dataset_name))
    
    # Overall status
    report['all_checks_passed'] = bool(all(report['checks'].values()))
    
    return report

# ============================================================================
# MAIN VALIDATION
# ============================================================================

def main():
    """Main validation pipeline"""
    
    reports = {}
    all_passed = True
    
    # ========================================================================
    # Validate labeled data
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("VALIDATING LABELED DATA")
    print("=" * 80)
    
    labeled_file = INPUT_DIR / 'labeled' / 'all_labeled_data.csv'
    
    if labeled_file.exists():
        print(f"\nReading: {labeled_file}")
        df_labeled = pd.read_csv(labeled_file)
        print(f"Loaded: {len(df_labeled):,} rows")
        
        report = generate_quality_report(df_labeled, 'labeled_data')
        reports['labeled'] = report
        
        if not report['all_checks_passed']:
            print(f"\n⚠️  Some checks failed for labeled data")
            all_passed = False
        else:
            print(f"\n✓ All checks passed for labeled data")
    else:
        print(f"\n⚠️  Labeled data file not found: {labeled_file}")
        all_passed = False
    
    # ========================================================================
    # Validate unlabeled data
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("VALIDATING UNLABELED DATA")
    print("=" * 80)
    
    unlabeled_file = INPUT_DIR / 'unlabeled' / 'for_annotation.csv'
    
    if unlabeled_file.exists():
        print(f"\nReading: {unlabeled_file}")
        df_unlabeled = pd.read_csv(unlabeled_file)
        print(f"Loaded: {len(df_unlabeled):,} rows")
        
        report = generate_quality_report(df_unlabeled, 'unlabeled_data')
        reports['unlabeled'] = report
        
        if not report['all_checks_passed']:
            print(f"\n⚠️  Some checks failed for unlabeled data")
            all_passed = False
        else:
            print(f"\n✓ All checks passed for unlabeled data")
    else:
        print(f"\n⚠️  Unlabeled data file not found: {unlabeled_file}")
    
    # ========================================================================
    # Save validation reports
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("SAVING VALIDATION REPORTS")
    print("=" * 80)
    
    report_file = INPUT_DIR / 'reports' / 'validation_report.json'
    with open(report_file, 'w') as f:
        json.dump(reports, f, indent=2)
    
    print(f"\n✓ Validation report saved: {report_file}")
    
    # ========================================================================
    # Generate summary
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    for dataset_name, report in reports.items():
        print(f"\n{dataset_name.upper()}:")
        print(f"  Total samples: {report['total_samples']:,}")
        print(f"  Checks passed: {sum(report['checks'].values())} / {len(report['checks'])}")
        
        failed_checks = [k for k, v in report['checks'].items() if not v]
        if failed_checks:
            print(f"  ❌ Failed checks: {', '.join(failed_checks)}")
        else:
            print(f"  ✓ All checks passed")
    
    # Overall status
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ VALIDATION PASSED - Data ready for next phase!")
    else:
        print("⚠️  VALIDATION ISSUES DETECTED - Review reports above")
    print("=" * 80)
    
    print(f"\n📁 Reports saved in: {INPUT_DIR / 'reports'}")
    print("\nNext steps:")
    if all_passed:
        print("  1. ✓ Data quality validated")
        print("  2. Review Final_input/reports/ for detailed statistics")
        print("  3. Hand off to Person 2 for annotation")
        print("  4. Update data card with preprocessing details")
    else:
        print("  1. Review validation issues above")
        print("  2. Fix data quality problems")
        print("  3. Re-run: python scripts/5_preprocess_and_unify.py")
        print("  4. Re-validate: python scripts/6_data_quality_checks.py")
    
    return all_passed

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
