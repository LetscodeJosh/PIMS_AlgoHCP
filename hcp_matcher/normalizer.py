"""
Version 2.0 Normalizer module for HCP names, institutions, and addresses.
Standardizes variations common in Philippine Healthcare Professional records with component-level name parsing.
"""

import re
from dataclasses import dataclass, asdict

# Philippine & Medical Honorifics / Titles to strip
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

COMMON_NAME_PARTICLES = {"DE", "LA", "LOS", "SAN", "SANTA", "SANTO", "DEL", "VDA"}

@dataclass(frozen=True)
class ParsedNameComponents:
    first_name: str
    middle_names: tuple[str, ...]
    surname: str
    tokens: tuple[str, ...]
    initials: str
    canonical: str
    has_title: bool

def normalize_text(text: str) -> str:
    """Basic clean-up of input text: uppercase, trim, remove special punctuation."""
    if not text:
        return ""
    text = text.upper().strip()
    text = re.sub(r'[^A-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_name_components(name: str) -> ParsedNameComponents:
    """
    Component-level name parsing for Version 2.0 Name-First Intelligent Detection.
    Infers First Name, Middle Name, Surname, Initials, and Canonical string.
    """
    if not name:
        return ParsedNameComponents("", (), "", (), "", "", False)

    cleaned = name.upper()
    has_title = False

    for title in TITLES_TO_STRIP:
        if re.search(title, cleaned):
            has_title = True
            cleaned = re.sub(title, ' ', cleaned)

    cleaned = re.sub(r'[^A-Z\s,]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Check for explicit 'Surname, Given' comma format
    if "," in cleaned:
        surname_part, given_part = cleaned.split(",", 1)
        surname_words = [ABBREVIATION_MAP.get(r'\b' + w + r'\b', w) for w in surname_part.split()]
        given_words = [ABBREVIATION_MAP.get(r'\b' + w + r'\b', w) for w in given_part.split()]
        
        first_name = given_words[0] if given_words else ""
        middle_names = tuple(given_words[1:]) if len(given_words) > 1 else ()
        surname = " ".join(surname_words)
        all_tokens = tuple(given_words + surname_words)
    else:
        words = cleaned.split()
        norm_words = []
        for w in words:
            replaced = w
            for pattern, replacement in ABBREVIATION_MAP.items():
                if re.match(pattern, w):
                    replaced = replacement
                    break
            norm_words.append(replaced)
        
        if not norm_words:
            return ParsedNameComponents("", (), "", (), "", "", has_title)

        if len(norm_words) == 1:
            first_name = norm_words[0]
            middle_names = ()
            surname = norm_words[0]
        elif len(norm_words) == 2:
            first_name = norm_words[0]
            middle_names = ()
            surname = norm_words[1]
        else:
            first_name = norm_words[0]
            middle_names = tuple(norm_words[1:-1])
            surname = norm_words[-1]
        
        all_tokens = tuple(norm_words)

    initials = "".join([t[0] for t in all_tokens if t])
    canonical = " ".join(all_tokens)

    return ParsedNameComponents(
        first_name=first_name,
        middle_names=middle_names,
        surname=surname,
        tokens=all_tokens,
        initials=initials,
        canonical=canonical,
        has_title=has_title
    )

def normalize_name(name: str) -> dict:
    """Standardizes doctor full name and returns serialization dictionary."""
    parsed = parse_name_components(name)
    return {
        "raw": name,
        "canonical": parsed.canonical,
        "first_name": parsed.first_name,
        "middle_names": list(parsed.middle_names),
        "surname": parsed.surname,
        "tokens": list(parsed.tokens),
        "initials": parsed.initials,
        "has_title": parsed.has_title
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
