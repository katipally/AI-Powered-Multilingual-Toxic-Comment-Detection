"""
Deduplication Utilities
Remove exact and near-duplicate samples using text hashing and cosine similarity

Requirements from Person 1:
- Deduplicate by normalized text hash
- Drop near-duplicates via cosine sim threshold if necessary
- Document dedup rate in quality report

Author: Person 1 - Data Collection & Preprocessing
Date: Oct 30, 2025
"""

import pandas as pd
import numpy as np
from typing import List, Set, Tuple
import hashlib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================================
# EXACT DEDUPLICATION
# ============================================================================

def compute_text_hash(text: str, algorithm: str = 'md5') -> str:
    """Compute hash of normalized text"""
    if not isinstance(text, str):
        return ""
    
    # Normalize text for hashing (lowercase, strip whitespace)
    normalized = ' '.join(text.lower().split())
    
    # Compute hash
    if algorithm == 'md5':
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

def remove_exact_duplicates(
    df: pd.DataFrame, 
    text_col: str = 'text',
    keep: str = 'first'
) -> Tuple[pd.DataFrame, int]:
    """
    Remove exact duplicate texts
    
    Args:
        df: DataFrame
        text_col: Column containing text
        keep: Which duplicate to keep ('first', 'last', False=remove all)
    
    Returns:
        Tuple of (deduplicated DataFrame, number of duplicates removed)
    """
    print(f"\nRemoving exact duplicates...")
    print(f"  Original size: {len(df):,}")
    
    # Add hash column
    df['_text_hash'] = df[text_col].apply(compute_text_hash)
    
    # Count duplicates before removal
    n_duplicates = df['_text_hash'].duplicated(keep=keep).sum()
    
    # Remove duplicates
    df_dedup = df.drop_duplicates(subset=['_text_hash'], keep=keep).copy()
    
    # Remove hash column
    df_dedup = df_dedup.drop(columns=['_text_hash'])
    
    print(f"  Duplicates removed: {n_duplicates:,}")
    print(f"  Final size: {len(df_dedup):,}")
    print(f"  Dedup rate: {(n_duplicates/len(df)*100):.2f}%")
    
    return df_dedup, n_duplicates

# ============================================================================
# NEAR-DUPLICATE DETECTION
# ============================================================================

def find_near_duplicates(
    texts: List[str],
    threshold: float = 0.95,
    n_gram_range: Tuple[int, int] = (1, 3),
    max_features: int = 10000
) -> List[Set[int]]:
    """
    Find near-duplicate text clusters using cosine similarity
    
    Args:
        texts: List of texts
        threshold: Cosine similarity threshold (0.95 = 95% similar)
        n_gram_range: N-gram range for TF-IDF
        max_features: Maximum TF-IDF features
    
    Returns:
        List of sets, where each set contains indices of near-duplicates
    """
    print(f"\nFinding near-duplicates (threshold={threshold})...")
    
    if len(texts) == 0:
        return []
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(
        ngram_range=n_gram_range,
        max_features=max_features,
        lowercase=True,
        stop_words='english'
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
    except ValueError:
        print("  ⚠️  Could not vectorize texts")
        return []
    
    print(f"  TF-IDF matrix: {tfidf_matrix.shape}")
    
    # Compute cosine similarity (only for upper triangle to save memory)
    n_samples = tfidf_matrix.shape[0]
    duplicate_clusters = []
    processed = set()
    
    # Process in batches to avoid memory issues
    batch_size = 1000
    n_comparisons = 0
    
    for i in range(0, n_samples, batch_size):
        end_i = min(i + batch_size, n_samples)
        batch = tfidf_matrix[i:end_i]
        
        # Compare batch with all documents
        similarities = cosine_similarity(batch, tfidf_matrix)
        
        for local_idx, global_idx in enumerate(range(i, end_i)):
            if global_idx in processed:
                continue
            
            # Find similar documents
            similar_indices = np.where(similarities[local_idx] >= threshold)[0]
            
            # Filter out self and already processed
            similar_indices = [idx for idx in similar_indices if idx != global_idx and idx not in processed]
            
            if similar_indices:
                cluster = {global_idx} | set(similar_indices)
                duplicate_clusters.append(cluster)
                processed.update(cluster)
                n_comparisons += len(similar_indices)
    
    print(f"  Comparisons made: {n_comparisons:,}")
    print(f"  Duplicate clusters found: {len(duplicate_clusters)}")
    
    return duplicate_clusters

def remove_near_duplicates(
    df: pd.DataFrame,
    text_col: str = 'text',
    threshold: float = 0.95,
    keep: str = 'first'
) -> Tuple[pd.DataFrame, int]:
    """
    Remove near-duplicate texts
    
    Args:
        df: DataFrame
        text_col: Column containing text
        threshold: Cosine similarity threshold
        keep: Which duplicate to keep ('first', 'last')
    
    Returns:
        Tuple of (deduplicated DataFrame, number of near-duplicates removed)
    """
    print(f"\nRemoving near-duplicates (threshold={threshold})...")
    print(f"  Original size: {len(df):,}")
    
    # Find near-duplicate clusters
    clusters = find_near_duplicates(
        df[text_col].tolist(),
        threshold=threshold
    )
    
    # Determine which indices to remove
    indices_to_remove = set()
    for cluster in clusters:
        sorted_cluster = sorted(cluster)
        if keep == 'first':
            # Keep first, remove rest
            indices_to_remove.update(sorted_cluster[1:])
        elif keep == 'last':
            # Keep last, remove rest
            indices_to_remove.update(sorted_cluster[:-1])
    
    print(f"  Near-duplicates to remove: {len(indices_to_remove):,}")
    
    # Remove near-duplicates
    mask = ~df.index.isin(indices_to_remove)
    df_dedup = df[mask].copy()
    
    print(f"  Final size: {len(df_dedup):,}")
    print(f"  Near-dedup rate: {(len(indices_to_remove)/len(df)*100):.2f}%")
    
    return df_dedup, len(indices_to_remove)

# ============================================================================
# COMBINED DEDUPLICATION
# ============================================================================

def deduplicate_dataframe(
    df: pd.DataFrame,
    text_col: str = 'text',
    exact: bool = True,
    near: bool = False,
    near_threshold: float = 0.95,
    keep: str = 'first'
) -> Tuple[pd.DataFrame, dict]:
    """
    Complete deduplication pipeline
    
    Args:
        df: DataFrame
        text_col: Column containing text
        exact: Remove exact duplicates
        near: Remove near-duplicates
        near_threshold: Cosine similarity threshold for near-duplicates
        keep: Which duplicate to keep
    
    Returns:
        Tuple of (deduplicated DataFrame, statistics dict)
    """
    print("=" * 80)
    print("DEDUPLICATION PIPELINE")
    print("=" * 80)
    
    stats = {
        'original_size': len(df),
        'exact_duplicates_removed': 0,
        'near_duplicates_removed': 0,
        'final_size': len(df),
        'total_removed': 0,
        'dedup_rate': 0.0
    }
    
    df_dedup = df.copy()
    
    # Exact deduplication
    if exact:
        df_dedup, n_exact = remove_exact_duplicates(df_dedup, text_col, keep)
        stats['exact_duplicates_removed'] = n_exact
    
    # Near-duplicate deduplication
    if near:
        df_dedup, n_near = remove_near_duplicates(df_dedup, text_col, near_threshold, keep)
        stats['near_duplicates_removed'] = n_near
    
    # Update final stats
    stats['final_size'] = len(df_dedup)
    stats['total_removed'] = stats['original_size'] - stats['final_size']
    stats['dedup_rate'] = (stats['total_removed'] / stats['original_size']) * 100
    
    print("\n" + "=" * 80)
    print("DEDUPLICATION COMPLETE")
    print("=" * 80)
    print(f"\n📊 Statistics:")
    print(f"  Original size:            {stats['original_size']:,}")
    print(f"  Exact duplicates removed: {stats['exact_duplicates_removed']:,}")
    print(f"  Near duplicates removed:  {stats['near_duplicates_removed']:,}")
    print(f"  Total removed:            {stats['total_removed']:,}")
    print(f"  Final size:               {stats['final_size']:,}")
    print(f"  Deduplication rate:       {stats['dedup_rate']:.2f}%")
    
    return df_dedup, stats

# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("DEDUPLICATION UTILITIES - TEST")
    print("=" * 80)
    
    # Create test data
    test_data = pd.DataFrame({
        'text': [
            'This is a test message',
            'This is a test message',  # Exact duplicate
            'This is a test message!!!',  # Near duplicate
            'Completely different text',
            'Another unique message',
            'This is a test message.',  # Near duplicate
        ],
        'label': [1, 1, 1, 0, 0, 1]
    })
    
    print(f"\nTest data:")
    for i, row in test_data.iterrows():
        print(f"  {i}: '{row['text']}'")
    
    # Test exact deduplication
    print("\n" + "-" * 80)
    print("TEST: Exact Deduplication")
    print("-" * 80)
    df_exact, stats_exact = deduplicate_dataframe(test_data, exact=True, near=False)
    
    # Test near-duplicate detection
    print("\n" + "-" * 80)
    print("TEST: Near-Duplicate Detection")
    print("-" * 80)
    df_near, stats_near = deduplicate_dataframe(test_data, exact=True, near=True, near_threshold=0.90)
    
    print("\n✓ Deduplication utilities ready for use!")
    print(f"\nImport in your code:")
    print(f"  from utils.deduplication import deduplicate_dataframe, remove_exact_duplicates")
