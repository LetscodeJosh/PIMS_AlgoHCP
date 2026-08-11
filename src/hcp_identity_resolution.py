"""
Risk-Based HCP Identity Resolution Module
=========================================
Implements risk-based entity resolution for Healthcare Professionals (HCPs) using
standardized names, weighted supporting attributes, corroborating evidence checks,
and confidence-tiered action routing (Merge, Steward Review, Keep Separate).

Guiding Principle:
------------------
Favor preserving separate records over incorrectly merging two distinct physicians.
Duplicate records can be merged later after additional evidence is available, whereas
an incorrect merge compromises HCP history, reporting, and engagement records and
is significantly more difficult to reverse.
"""

from dataclasses import dataclass, field
from enum import Enum
import re
import unicodedata
from typing import List, Dict, Optional, Tuple, Set


class ConfidenceTier(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ActionTier(Enum):
    MERGE = "MERGE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    KEEP_SEPARATE = "KEEP_SEPARATE"


@dataclass
class HCPRecord:
    """Represents a Healthcare Professional (HCP) record."""
    id: str
    full_name: str
    specialty: Optional[str] = None
    sub_specialty: Optional[str] = None
    institution_id: Optional[str] = None
    institution_name: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    interaction_ids: List[str] = field(default_factory=list)


class NameStandardizer:
    """Standardizes names by stripping titles, expanding abbreviations, and cleaning formatting."""

    TITLES = {
        r'\bdr\b\.?', r'\bdra\b\.?', r'\bdoctor\b', r'\bdoctora\b', r'\bprof\b\.?',
        r'\bmd\b\.?', r'\bfpoa\b\.?', r'\bfpcp\b\.?', r'\bfpcs\b\.?', r'\bdpbr\b\.?'
    }

    ABBREVIATIONS = [
        (re.compile(r'\bma\b\.?', re.IGNORECASE), 'maria'),
        (re.compile(r'\bst\b\.?', re.IGNORECASE), 'saint'),
        (re.compile(r'\bsta\b\.?', re.IGNORECASE), 'santa'),
        (re.compile(r'\bdela\b', re.IGNORECASE), 'de la'),
    ]

    @classmethod
    def strip_accents(cls, text: str) -> str:
        """Removes diacritics/accents from unicode characters."""
        nfkd_form = unicodedata.normalize('NFKD', text)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    @classmethod
    def standardize_name(cls, name: str) -> str:
        """Normalizes a name string: lowercase, accent removal, title stripping, abbreviation expansion."""
        if not name:
            return ""

        cleaned = cls.strip_accents(name).lower()

        # Strip honorific titles and suffixes
        for title_pattern in cls.TITLES:
            cleaned = re.sub(title_pattern, '', cleaned, flags=re.IGNORECASE)

        # Expand abbreviations
        for pattern, replacement in cls.ABBREVIATIONS:
            cleaned = pattern.sub(replacement, cleaned)

        # Remove punctuation except whitespace
        cleaned = re.sub(r'[^a-z0-9\s]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    @classmethod
    def get_token_sorted_key(cls, name: str) -> str:
        """Returns a token-sorted key to handle name order variations (e.g. Last, First)."""
        standardized = cls.standardize_name(name)
        tokens = standardized.split()
        tokens.sort()
        return " ".join(tokens)


class SimilarityMetrics:
    """Provides string and attribute similarity metrics."""

    @staticmethod
    def jaro_winkler_similarity(s1: str, s2: str, p: float = 0.1) -> float:
        """Computes Jaro-Winkler similarity between two strings (0.0 to 1.0)."""
        if s1 == s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        len1, len2 = len(s1), len(s2)
        match_distance = max(len1, len2) // 2 - 1
        if match_distance < 0:
            match_distance = 0

        s1_matches = [False] * len1
        s2_matches = [False] * len2

        matches = 0
        transpositions = 0

        for i in range(len1):
            start = max(0, i - match_distance)
            end = min(i + match_distance + 1, len2)
            for j in range(start, end):
                if s2_matches[j]:
                    continue
                if s1[i] == s2[j]:
                    s1_matches[i] = True
                    s2_matches[j] = True
                    matches += 1
                    break

        if matches == 0:
            return 0.0

        k = 0
        for i in range(len1):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1

        jaro = (matches / len1 + matches / len2 + (matches - transpositions / 2) / matches) / 3.0

        # Winkler prefix scaling
        prefix_len = 0
        for i in range(min(4, min(len1, len2))):
            if s1[i] == s2[i]:
                prefix_len += 1
            else:
                break

        return jaro + prefix_len * p * (1.0 - jaro)

    @staticmethod
    def token_set_similarity(s1: str, s2: str) -> float:
        """Computes token set similarity ratio between two strings."""
        if not s1 or not s2:
            return 0.0

        tokens1 = set(s1.lower().split())
        tokens2 = set(s2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        return len(intersection) / len(union)


@dataclass
class MatchResult:
    """Result of identity matching between two HCP records."""
    candidate_a_id: str
    candidate_b_id: str
    name_score: float
    specialty_score: float
    institution_score: float
    location_score: float
    history_score: float
    total_score: float
    is_corroborated: bool
    confidence_tier: ConfidenceTier
    recommended_action: ActionTier
    explanation: str


class HCPMatcher:
    """Multi-attribute matching engine for HCP records."""

    def __init__(self,
                 weight_name: float = 0.40,
                 weight_specialty: float = 0.20,
                 weight_institution: float = 0.20,
                 weight_location: float = 0.10,
                 weight_history: float = 0.10,
                 high_confidence_threshold: float = 0.85,
                 medium_confidence_threshold: float = 0.60):
        self.w_name = weight_name
        self.w_specialty = weight_specialty
        self.w_institution = weight_institution
        self.w_location = weight_location
        self.w_history = weight_history

        self.high_threshold = high_confidence_threshold
        self.medium_threshold = medium_confidence_threshold

    def calculate_name_similarity(self, name_a: str, name_b: str) -> float:
        """Calculates combined name similarity using standardized Jaro-Winkler and token sorting."""
        std_a = NameStandardizer.standardize_name(name_a)
        std_b = NameStandardizer.standardize_name(name_b)

        jw_score = SimilarityMetrics.jaro_winkler_similarity(std_a, std_b)

        key_a = NameStandardizer.get_token_sorted_key(name_a)
        key_b = NameStandardizer.get_token_sorted_key(name_b)
        token_jw_score = SimilarityMetrics.jaro_winkler_similarity(key_a, key_b)

        return max(jw_score, token_jw_score)

    def calculate_specialty_similarity(self, spec_a: Optional[str], spec_b: Optional[str]) -> float:
        """Calculates specialty match score."""
        if not spec_a or not spec_b:
            return 0.0
        norm_a = spec_a.strip().lower()
        norm_b = spec_b.strip().lower()

        if norm_a == norm_b:
            return 1.0
        return SimilarityMetrics.token_set_similarity(norm_a, norm_b)

    def calculate_institution_similarity(self, rec_a: HCPRecord, rec_b: HCPRecord) -> float:
        """Calculates institution affiliation score."""
        if rec_a.institution_id and rec_b.institution_id:
            if rec_a.institution_id == rec_b.institution_id:
                return 1.0

        if rec_a.institution_name and rec_b.institution_name:
            norm_a = rec_a.institution_name.strip().lower()
            norm_b = rec_b.institution_name.strip().lower()
            return SimilarityMetrics.token_set_similarity(norm_a, norm_b)

        return 0.0

    def calculate_location_similarity(self, rec_a: HCPRecord, rec_b: HCPRecord) -> float:
        """Calculates geographic location match score."""
        matches = 0
        total_eval = 0

        if rec_a.city and rec_b.city:
            total_eval += 1
            if rec_a.city.strip().lower() == rec_b.city.strip().lower():
                matches += 1

        if rec_a.province and rec_b.province:
            total_eval += 1
            if rec_a.province.strip().lower() == rec_b.province.strip().lower():
                matches += 1

        if rec_a.zip_code and rec_b.zip_code:
            total_eval += 1
            if rec_a.zip_code.strip() == rec_b.zip_code.strip():
                matches += 1

        if total_eval == 0:
            return 0.0
        return matches / total_eval

    def calculate_history_similarity(self, rec_a: HCPRecord, rec_b: HCPRecord) -> float:
        """Calculates history/contact similarity (phone, email, shared interactions)."""
        if rec_a.email and rec_b.email and rec_a.email.strip().lower() == rec_b.email.strip().lower():
            return 1.0
        if rec_a.phone and rec_b.phone:
            p_a = re.sub(r'\D', '', rec_a.phone)
            p_b = re.sub(r'\D', '', rec_b.phone)
            if p_a and p_b and p_a == p_b:
                return 1.0

        set_a = set(rec_a.interaction_ids)
        set_b = set(rec_b.interaction_ids)

        if set_a and set_b:
            intersection = set_a.intersection(set_b)
            if intersection:
                return len(intersection) / max(len(set_a), len(set_b))

        return 0.0

    def evaluate_pair(self, rec_a: HCPRecord, rec_b: HCPRecord) -> MatchResult:
        """Evaluates candidate pair against weighted model, corroboration rules, and risk tiers."""
        s_name = self.calculate_name_similarity(rec_a.full_name, rec_b.full_name)
        s_spec = self.calculate_specialty_similarity(rec_a.specialty, rec_b.specialty)
        s_inst = self.calculate_institution_similarity(rec_a, rec_b)
        s_loc = self.calculate_location_similarity(rec_a, rec_b)
        s_hist = self.calculate_history_similarity(rec_a, rec_b)

        total_score = (
            self.w_name * s_name +
            self.w_specialty * s_spec +
            self.w_institution * s_inst +
            self.w_location * s_loc +
            self.w_history * s_hist
        )

        # Corroboration Rule Check:
        # Require at least one non-name supporting attribute match to corroborate high name score
        is_corroborated = (
            s_inst >= 0.80 or
            s_spec >= 0.90 or
            s_loc >= 0.85 or
            s_hist >= 0.90
        )

        # Action Routing logic:
        if total_score >= self.high_threshold:
            if is_corroborated:
                tier = ConfidenceTier.HIGH
                action = ActionTier.MERGE
                explanation = (
                    f"High confidence ({total_score:.1%}): Strong name match corroborated by supporting "
                    f"attributes (Inst: {s_inst:.2f}, Spec: {s_spec:.2f}, Loc: {s_loc:.2f}). Safe to auto-merge."
                )
            else:
                tier = ConfidenceTier.MEDIUM
                action = ActionTier.MANUAL_REVIEW
                explanation = (
                    f"Medium confidence ({total_score:.1%}): High name match ({s_name:.2f}) lacks mandatory "
                    f"corroborating supporting evidence (Inst/Spec/Loc). Flagged for Data Steward review to prevent false merge."
                )
        elif total_score >= self.medium_threshold:
            tier = ConfidenceTier.MEDIUM
            action = ActionTier.MANUAL_REVIEW
            explanation = (
                f"Medium confidence ({total_score:.1%}): Partial match across attributes. Flagged for Data Steward review."
            )
        else:
            tier = ConfidenceTier.LOW
            action = ActionTier.KEEP_SEPARATE
            explanation = (
                f"Low confidence ({total_score:.1%}): Insufficient attribute match. Records preserved separately."
            )

        return MatchResult(
            candidate_a_id=rec_a.id,
            candidate_b_id=rec_b.id,
            name_score=s_name,
            specialty_score=s_spec,
            institution_score=s_inst,
            location_score=s_loc,
            history_score=s_hist,
            total_score=total_score,
            is_corroborated=is_corroborated,
            confidence_tier=tier,
            recommended_action=action,
            explanation=explanation
        )
