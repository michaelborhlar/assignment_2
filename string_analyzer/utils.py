import hashlib
from collections import Counter

def analyze_string(value: str):
    # Remove leading/trailing whitespace
    value = value.strip()

    # SHA-256 hash for unique ID
    sha_hash = hashlib.sha256(value.encode()).hexdigest()

    # Properties
    length = len(value)
    is_palindrome = value.lower() == value[::-1].lower()
    unique_characters = len(set(value))
    word_count = len(value.split())
    character_frequency_map = dict(Counter(value))

    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha_hash,
        "character_frequency_map": character_frequency_map,
    }
