"""
Text Normalization & Transliteration Utilities for Code-Mixed Text
Handles Romanized Indic scripts, emoji, URLs, and punctuation normalization

Requirements from Person 1:
- Normalization utilities for Romanized words (Indic NLP tools)
- Strip URLs/HTML, normalize punctuation/emoji
- Transliteration normalization where appropriate
- Validated on gold list (≥95% exact matches)

Author: Person 1 - Data Collection & Preprocessing
Date: Oct 30, 2025
"""

import re
import unicodedata
from typing import Dict, List, Tuple
import html

# ============================================================================
# NORMALIZATION CONSTANTS
# ============================================================================

# Common Romanized Hindi words and their normalized forms
HINDI_ROMANIZED_NORMALIZATIONS = {
    # Greetings & Common phrases
    'namaste': 'namaste', 'namaskar': 'namaskar',
    'dhanyavaad': 'dhanyavad', 'dhanyavad': 'dhanyavad', 'thanks': 'thanks',
    'shukriya': 'shukriya', 'shukria': 'shukriya',
    
    # Common words (various spellings -> standardized)
    'bhai': 'bhai', 'bhaii': 'bhai', 'bhaiya': 'bhaiya', 'bhaiyya': 'bhaiya',
    'yaar': 'yaar', 'yar': 'yaar', 'yaara': 'yara',
    'hai': 'hai', 'he': 'hai', 'hain': 'hain',
    'hoon': 'hoon', 'hun': 'hoon', 'hu': 'hoon',
    'nahi': 'nahi', 'nahin': 'nahi', 'nai': 'nahi', 'nhi': 'nahi',
    'kya': 'kya', 'kia': 'kya', 'kyaa': 'kya',
    'mein': 'mein', 'main': 'mein', 'me': 'mein',
    'aap': 'aap', 'aapka': 'aapka', 'aapki': 'aapki',
    'kar': 'kar', 'karo': 'karo', 'karna': 'karna', 'karta': 'karta',
    'tha': 'tha', 'thi': 'thi', 'the': 'the', 'thee': 'the',
    'koi': 'koi', 'kisi': 'kisi', 'kisiko': 'kisiko',
    'bhi': 'bhi', 'b': 'bhi',
    'toh': 'toh', 'to': 'toh',
    'kuch': 'kuch', 'kuchh': 'kuch', 'kucch': 'kuch',
    'bahut': 'bahut', 'bohot': 'bahut', 'bhot': 'bahut',
    'acha': 'acha', 'accha': 'acha', 'achha': 'acha', 'achchha': 'acha',
    'bura': 'bura', 'buraa': 'bura',
    'matlab': 'matlab', 'mtlb': 'matlab', 'matlb': 'matlab',
    'yeh': 'yeh', 'ye': 'yeh', 'yee': 'yeh',
    'woh': 'woh', 'wo': 'woh', 'vo': 'woh',
    'kahan': 'kahan', 'kaha': 'kaha', 'kahaan': 'kahan',
    'kaise': 'kaise', 'kese': 'kaise', 'kaese': 'kaise',
    'kyun': 'kyun', 'kyu': 'kyun', 'kyon': 'kyun', 'why': 'kyun',
    'abhi': 'abhi', 'abi': 'abhi', 'abhee': 'abhi',
    'log': 'log', 'lok': 'log', 'loog': 'log', 'loag': 'log',
    'sahi': 'sahi', 'sahee': 'sahi', 'shi': 'sahi',
    'galat': 'galat', 'ghalat': 'galat', 'glat': 'galat',
    'dekho': 'dekho', 'dekh': 'dekh', 'dekhna': 'dekhna',
    'suno': 'suno', 'sun': 'sun', 'sunna': 'sunna', 'sunna': 'sunna',
    'samjho': 'samajho', 'samajh': 'samajh', 'smjho': 'samajho',
    'dost': 'dost', 'dosth': 'dost', 'doost': 'dost',
    'pakka': 'pakka', 'paka': 'pakka', 'pukka': 'pakka',
    'chalo': 'chalo', 'chal': 'chal', 'chlo': 'chalo',
    'theek': 'theek', 'thik': 'theek', 'thek': 'theek',
    'accha': 'acha', 'achha': 'acha',
}

# URL patterns
URL_PATTERN = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    r'|www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)

# Email pattern
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# Mention patterns
MENTION_PATTERN = re.compile(r'@\w+')

# Hashtag pattern
HASHTAG_PATTERN = re.compile(r'#\w+')

# Multiple punctuation
MULTI_PUNCT_PATTERN = re.compile(r'([!?.;,]){2,}')

# Multiple spaces/whitespace
MULTI_SPACE_PATTERN = re.compile(r'\s+')

# ============================================================================
# CORE NORMALIZATION FUNCTIONS
# ============================================================================

def remove_html(text: str) -> str:
    """Remove HTML tags and decode HTML entities"""
    # Decode HTML entities
    text = html.unescape(text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return text

def remove_urls(text: str, replace_with: str = '[URL]') -> str:
    """Remove or replace URLs"""
    return URL_PATTERN.sub(replace_with, text)

def remove_emails(text: str, replace_with: str = '[EMAIL]') -> str:
    """Remove or replace email addresses"""
    return EMAIL_PATTERN.sub(replace_with, text)

def remove_mentions(text: str, replace_with: str = '[MENTION]') -> str:
    """Remove or replace @mentions"""
    return MENTION_PATTERN.sub(replace_with, text)

def remove_hashtags(text: str, keep_text: bool = True) -> str:
    """Remove hashtags or keep just the text"""
    if keep_text:
        return re.sub(r'#(\w+)', r'\1', text)
    else:
        return HASHTAG_PATTERN.sub('', text)

def normalize_punctuation(text: str) -> str:
    """Normalize excessive punctuation"""
    # Replace multiple punctuation with single
    text = MULTI_PUNCT_PATTERN.sub(r'\1', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Normalize dashes
    text = text.replace('–', '-').replace('—', '-')
    
    # Normalize ellipsis
    text = text.replace('…', '...')
    
    return text

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace to single spaces"""
    return MULTI_SPACE_PATTERN.sub(' ', text).strip()

def normalize_unicode(text: str) -> str:
    """Normalize Unicode characters"""
    # NFKC normalization (compatibility decomposition + canonical composition)
    return unicodedata.normalize('NFKC', text)

def remove_control_characters(text: str) -> str:
    """Remove control characters but keep printable ones"""
    return ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\r\t')

def normalize_romanized_hindi(text: str, word_dict: Dict[str, str] = None) -> str:
    """
    Normalize Romanized Hindi words to standard spellings
    
    Args:
        text: Input text
        word_dict: Custom word normalization dictionary (optional)
    
    Returns:
        Normalized text
    """
    if word_dict is None:
        word_dict = HINDI_ROMANIZED_NORMALIZATIONS
    
    # Split into words
    words = text.split()
    
    # Normalize each word
    normalized_words = []
    for word in words:
        # Remove punctuation for lookup
        clean_word = re.sub(r'[^\w]', '', word.lower())
        
        if clean_word in word_dict:
            # Get normalized form
            normalized = word_dict[clean_word]
            
            # Preserve original punctuation/capitalization pattern
            if word[0].isupper():
                normalized = normalized.capitalize()
            
            # Re-attach punctuation
            punct = re.findall(r'[^\w]+', word)
            if punct:
                normalized = normalized + punct[0]
            
            normalized_words.append(normalized)
        else:
            normalized_words.append(word)
    
    return ' '.join(normalized_words)

def normalize_emoji(text: str, keep: bool = True) -> str:
    """
    Normalize or remove emoji
    
    Args:
        text: Input text
        keep: If True, keep emoji; if False, remove them
    
    Returns:
        Normalized text
    """
    if keep:
        return text
    else:
        # Remove emoji using Unicode ranges
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", 
            flags=re.UNICODE
        )
        return emoji_pattern.sub('', text)

# ============================================================================
# COMBINED NORMALIZATION PIPELINE
# ============================================================================

def normalize_text(
    text: str,
    remove_html_tags: bool = True,
    remove_url: bool = True,
    remove_email: bool = True,
    remove_mention: bool = True,
    normalize_hashtag: bool = True,
    normalize_punct: bool = True,
    normalize_ws: bool = True,
    normalize_unicode_chars: bool = True,
    normalize_hindi: bool = True,
    keep_emoji: bool = True,
    lowercase: bool = False
) -> str:
    """
    Complete text normalization pipeline
    
    Args:
        text: Input text
        remove_html_tags: Remove HTML tags
        remove_url: Remove URLs
        remove_email: Remove email addresses
        remove_mention: Remove @mentions
        normalize_hashtag: Normalize hashtags (keep text)
        normalize_punct: Normalize punctuation
        normalize_ws: Normalize whitespace
        normalize_unicode_chars: Normalize Unicode
        normalize_hindi: Normalize Romanized Hindi
        keep_emoji: Keep or remove emoji
        lowercase: Convert to lowercase
    
    Returns:
        Normalized text
    """
    if not isinstance(text, str):
        return ""
    
    # HTML
    if remove_html_tags:
        text = remove_html(text)
    
    # URLs and emails
    if remove_url:
        text = remove_urls(text)
    if remove_email:
        text = remove_emails(text)
    
    # Mentions and hashtags
    if remove_mention:
        text = remove_mentions(text)
    if normalize_hashtag:
        text = remove_hashtags(text, keep_text=True)
    
    # Unicode
    if normalize_unicode_chars:
        text = normalize_unicode(text)
        text = remove_control_characters(text)
    
    # Emoji
    text = normalize_emoji(text, keep=keep_emoji)
    
    # Punctuation
    if normalize_punct:
        text = normalize_punctuation(text)
    
    # Romanized Hindi
    if normalize_hindi:
        text = normalize_romanized_hindi(text)
    
    # Whitespace
    if normalize_ws:
        text = normalize_whitespace(text)
    
    # Lowercase
    if lowercase:
        text = text.lower()
    
    return text

# ============================================================================
# VALIDATION & TESTING
# ============================================================================

def validate_normalizations(gold_list: List[Tuple[str, str]] = None) -> float:
    """
    Validate normalizations against gold standard list
    
    Args:
        gold_list: List of (input, expected_output) tuples
    
    Returns:
        Accuracy percentage
    """
    if gold_list is None:
        # Default gold list for testing
        gold_list = [
            # Hindi words
            ('bhai', 'bhai'),
            ('bhaii', 'bhai'),
            ('yar', 'yaar'),
            ('nai', 'nahi'),
            ('kia', 'kya'),
            ('main', 'mein'),
            ('bohot', 'bahut'),
            ('achha', 'acha'),
            ('kese', 'kaise'),
            ('kyu', 'kyun'),
            
            # URLs
            ('Check https://example.com here', 'Check [URL] here'),
            ('www.example.com is good', '[URL] is good'),
            
            # Punctuation
            ('What!!!!!', 'What!'),
            ('Really???', 'Really?'),
            
            # Hashtags
            ('#bollywood rocks', 'bollywood rocks'),
            
            # Whitespace
            ('Too   many    spaces', 'Too many spaces'),
            
            # Mixed
            ('Yar  kya   baat  hai!!!', 'yaar kya baat hai!'),
        ]
    
    correct = 0
    total = len(gold_list)
    
    print("\nValidating normalizations:")
    print("-" * 80)
    
    for input_text, expected in gold_list:
        normalized = normalize_text(input_text)
        is_correct = normalized == expected
        correct += is_correct
        
        status = "✓" if is_correct else "✗"
        print(f"{status} '{input_text}' -> '{normalized}' {'(expected: ' + expected + ')' if not is_correct else ''}")
    
    accuracy = (correct / total) * 100
    print(f"\n{'✓' if accuracy >= 95 else '✗'} Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    print(f"   Target: ≥95% (Person 1 requirement)")
    
    return accuracy

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_normalizer(preset: str = 'default'):
    """
    Get pre-configured normalizer function
    
    Presets:
        - 'default': Standard normalization
        - 'strict': Aggressive cleaning
        - 'minimal': Light normalization
        - 'code_mixed': Optimized for code-mixed text
    """
    presets = {
        'default': {
            'remove_html_tags': True,
            'remove_url': True,
            'remove_email': True,
            'remove_mention': True,
            'normalize_hashtag': True,
            'normalize_punct': True,
            'normalize_ws': True,
            'normalize_unicode_chars': True,
            'normalize_hindi': True,
            'keep_emoji': True,
            'lowercase': False
        },
        'strict': {
            'remove_html_tags': True,
            'remove_url': True,
            'remove_email': True,
            'remove_mention': True,
            'normalize_hashtag': False,  # Remove completely
            'normalize_punct': True,
            'normalize_ws': True,
            'normalize_unicode_chars': True,
            'normalize_hindi': True,
            'keep_emoji': False,  # Remove emoji
            'lowercase': True
        },
        'minimal': {
            'remove_html_tags': True,
            'remove_url': False,
            'remove_email': False,
            'remove_mention': False,
            'normalize_hashtag': False,
            'normalize_punct': True,
            'normalize_ws': True,
            'normalize_unicode_chars': True,
            'normalize_hindi': False,
            'keep_emoji': True,
            'lowercase': False
        },
        'code_mixed': {
            'remove_html_tags': True,
            'remove_url': True,
            'remove_email': True,
            'remove_mention': True,
            'normalize_hashtag': True,
            'normalize_punct': True,
            'normalize_ws': True,
            'normalize_unicode_chars': True,
            'normalize_hindi': True,  # Important for code-mixed
            'keep_emoji': True,
            'lowercase': False
        }
    }
    
    config = presets.get(preset, presets['default'])
    
    def normalizer(text: str) -> str:
        return normalize_text(text, **config)
    
    return normalizer

# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("TEXT NORMALIZATION & TRANSLITERATION UTILITIES")
    print("=" * 80)
    
    # Run validation
    accuracy = validate_normalizations()
    
    # Examples
    print("\n" + "=" * 80)
    print("USAGE EXAMPLES")
    print("=" * 80)
    
    examples = [
        "Yar  kya   baat  hai!!! Check https://example.com",
        "Bohot achha hai bhaii @username #bollywood",
        "Main nai janta kese karu   ye   kaam",
        "Kia  aap  samjho  yeh  baat???",
    ]
    
    print("\nDefault normalizer:")
    normalizer = get_normalizer('default')
    for ex in examples:
        print(f"  Input:  '{ex}'")
        print(f"  Output: '{normalizer(ex)}'")
        print()
    
    print("\n" + "✓" + " Utilities ready for use!")
    print(f"\nImport in your code:")
    print(f"  from utils.text_normalization import normalize_text, get_normalizer")
