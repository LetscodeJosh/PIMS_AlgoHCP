"""
Normalizer module for HCP names, institutions, and addresses.
Standardizes variations common in Philippine Healthcare Professional records.
"""

import re

# Philippine & Medical Honorifics / Titles to strip or normalize
TITLES_TO_STRIP = [
    r'\bDR\b', r'\bDRA\b', r'\bDOCTOR\b', r'\bDOCTORA\b',
    r'\bMD\b', r'\bM\.D\b', r'\bFPCP\b', r'\bFPOA\b', r'\bFPAFP\b',
    r'\bPROF\b', r'\bPROFE\b', r'\bDOC\b'
]

# Standard replacements for abbreviations
ABBREVIATION_MAP = {
    r'\bST\b': 'SANTA',
    r'\bSTA\b': 'SANTA',
    r'\bSTO\b': 'SANTO',
    r'\bMA\b': 'MARIA',
    r'\bJUAN\b': 'JUAN',
    r'\bDELA\b': 'DE LA',
    r'\bDELOS\b': 'DE LOS',
    r'\bDEL\b': 'DEL',
    r'\bJR\b': 'JUNIOR',
    r'\bSR\b': 'SENIOR',
    r'\bHOSP\b': 'HOSPITAL',
    r'\bCTR\b': 'CENTER',
    r'\bMED\b': 'MEDICAL',
    r'\bCLIN\b': 'CLINIC',
    r'\bCENTRAL\b': 'CENTRAL',
    r'\bNATL\b': 'NATIONAL',
    r'\bGEN\b': 'GENERAL',
}

def normalize_text(text: str) -> str:
    """Basic clean-up of input text: uppercase, trim, remove special punctuation."""
    if not text:
        return ""
    text = text.upper().strip()
    # Remove dots, commas, hyphens except spaces
    text = re.sub(r'[^A-Z0-9\s]', ' ', text)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_name(name: str) -> dict:
    """
    Standardizes doctor full name.
    Returns dictionary with raw, cleaned, canonical name, and tokens.
    """
    if not name:
        return {"raw": "", "canonical": "", "tokens": [], "has_title": False}

    cleaned = name.upper()
    has_title = False

    # Detect & strip titles/medical suffixes
    for title in TITLES_TO_STRIP:
        if re.search(title, cleaned):
            has_title = True
            cleaned = re.sub(title, ' ', cleaned)

    # Basic cleaning
    cleaned = re.sub(r'[^A-Z\s]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Apply abbreviation mappings
    words = cleaned.split()
    normalized_words = []
    for w in words:
        replaced = w
        for pattern, replacement in ABBREVIATION_MAP.items():
            if re.match(pattern, w):
                replaced = replacement
                break
        normalized_words.append(replaced)

    canonical = " ".join(normalized_words)

    return {
        "raw": name,
        "canonical": canonical,
        "tokens": normalized_words,
        "has_title": has_title
    }

def normalize_institution(inst: str) -> str:
    """Standardize hospital / clinic names."""
    if not inst:
        return ""
    cleaned = normalize_text(inst)
    words = cleaned.split()
    norm_words = []
    for w in words:
        replaced = w
        for pattern, replacement in ABBREVIATION_MAP.items():
            if re.match(pattern, w):
                replaced = replacement
                break
        norm_words.append(replaced)
    return " ".join(norm_words)
