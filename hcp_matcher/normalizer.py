"""
Version 2.0 Normalizer module matching exact PIMS ERP HCP Submission schema.
Handles First Name, Middle Name, Last Name, Birth Date, Specialties, Practice Type,
Workplaces, Cities, Provinces, Accounts/Programs, Territory, and MedRep details.
"""

import re
from dataclasses import dataclass

TITLES_TO_STRIP = [
    r'\bDR\b\.?', r'\bDRA\b\.?', r'\bDOCTOR\b\.?', r'\bDOCTORA\b\.?',
    r'\bMD\b\.?', r'\bM\.D\b\.?', r'\bFPCP\b\.?', r'\bFPOA\b\.?', r'\bFPAFP\b\.?',
    r'\bPROF\b\.?', r'\bPROFE\b\.?', r'\bDOC\b\.?'
]

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

@dataclass(frozen=True)
class ERPDoctorName:
    first_name: str
    middle_name: str
    last_name: str
    full_name: str
    canonical_name: str

def normalize_text(text: str) -> str:
    """Basic clean-up of input text: uppercase, trim, remove special punctuation."""
    if not text:
        return ""
    text = text.upper().strip()
    text = re.sub(r'[^A-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def strip_titles(text: str) -> str:
    if not text:
        return ""
    cleaned = text.upper()
    for title in TITLES_TO_STRIP:
        cleaned = re.sub(title, ' ', cleaned)
    return normalize_text(cleaned)

def parse_erp_doctor_name(first_name: str, middle_name: str, last_name: str) -> ERPDoctorName:
    """Construct full & canonical doctor name from ERP structured components."""
    fn = strip_titles(first_name)
    mn = strip_titles(middle_name)
    ln = strip_titles(last_name)

    parts = [p for p in [fn, mn, ln] if p]
    full_name = " ".join(parts)

    norm_parts = []
    for p in parts:
        words = p.split()
        for w in words:
            replaced = w
            for pattern, replacement in ABBREVIATION_MAP.items():
                if re.match(pattern, w):
                    replaced = replacement
                    break
            norm_parts.append(replaced)

    canonical_name = " ".join(norm_parts)
    return ERPDoctorName(
        first_name=fn,
        middle_name=mn,
        last_name=ln,
        full_name=full_name,
        canonical_name=canonical_name
    )

def normalize_name(name: str) -> dict:
    """Standardizes doctor full name for backwards compatibility."""
    cleaned = normalize_text(name)
    words = cleaned.split()
    norm_words = []
    for w in words:
        replaced = w
        for pattern, replacement in ABBREVIATION_MAP.items():
            if re.match(pattern, w):
                replaced = replacement
                break
        norm_words.append(replaced)

    canonical = " ".join(norm_words)
    return {
        "raw": name,
        "canonical": canonical,
        "tokens": norm_words,
        "has_title": False
    }

def normalize_institution(inst: str) -> str:
    """Standardize workplace hospital / clinic names."""
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
