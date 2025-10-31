"""
Utility Functions for Text Processing
Includes normalization, transliteration, and deduplication

Author: Person 1 - Data Collection & Preprocessing
Date: Oct 30, 2025
"""

from .text_normalization import (
    normalize_text,
    get_normalizer,
    normalize_romanized_hindi,
    remove_urls,
    remove_html,
    normalize_punctuation
)

from .deduplication import (
    deduplicate_dataframe,
    remove_exact_duplicates,
    remove_near_duplicates,
    compute_text_hash
)

__all__ = [
    # Normalization
    'normalize_text',
    'get_normalizer',
    'normalize_romanized_hindi',
    'remove_urls',
    'remove_html',
    'normalize_punctuation',
    
    # Deduplication
    'deduplicate_dataframe',
    'remove_exact_duplicates',
    'remove_near_duplicates',
    'compute_text_hash',
]

__version__ = '1.0.0'
