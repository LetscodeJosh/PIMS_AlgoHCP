"""
Multi-Attribute Match Scorer & ML Probabilistic Classifier.
Calculates confidence score across ALL system fields without mandatory License ID or Birthdate.
Enforces Strict Zero-Match Penalty Rule (If a field does not match, returns 0.0% fuzzy match score).
"""

import math
import re
from .normalizer import normalize_name, normalize_text, normalize_institution
from .algorithms import jaro_winkler_distance, levenshtein_ratio, soundex, token_set_ratio

class HCPMatchScorer:
    """
    Intelligent Multi-Attribute Matcher and Probabilistic Classifier.
    Evaluates ALL doctor fields dynamically with string standardization and weighted linkage.
    
    Supported Fields:
    - Doctor Name (Jaro-Winkler + Soundex + Token Set)
    - Specialty / Subspecialty
    - Primary Hospital / Institution
    - Secondary Hospital / Clinic
    - Street / Barangay Address
    - City / Municipality / Province
    - Phone / Mobile Contact
    - Email Address
    """

    # Tiers
    HIGH_THRESHOLD = 0.88      # >= 88% High match (Auto-merge/Fast-track)
    MEDIUM_THRESHOLD = 0.50    # 50% - 87% Medium (50-50 Match) -> Managerial Escalation

    def calculate_name_score(self, name1: str, name2: str) -> dict:
        """Calculate multi-algorithm name similarity."""
        norm1 = normalize_name(name1)
        norm2 = normalize_name(name2)

        c1 = norm1["canonical"]
        c2 = norm2["canonical"]

        if not c1 or not c2:
            return {"score": 0.0, "jw": 0.0, "token": 0.0, "soundex_match": False, "canonical1": "", "canonical2": ""}

        jw_score = jaro_winkler_distance(c1, c2)
        token_score = token_set_ratio(c1, c2)

        # Soundex check for primary surname token
        t1 = norm1["tokens"]
        t2 = norm2["tokens"]
        sx_match = False
        if t1 and t2:
            sx1 = soundex(t1[-1])
            sx2 = soundex(t2[-1])
            if sx1 == sx2:
                sx_match = True

        base_name_score = (jw_score * 0.55) + (token_score * 0.45)
        if sx_match:
            base_name_score = min(1.0, base_name_score + 0.05)

        # Strict Zero-Match Threshold for Name
        if base_name_score < 0.40:
            base_name_score = 0.0

        return {
            "score": round(base_name_score, 4),
            "jw": round(jw_score, 4),
            "token": round(token_score, 4),
            "soundex_match": sx_match,
            "canonical1": c1,
            "canonical2": c2
        }

    def calculate_text_score(self, val1: str, val2: str) -> float:
        """Calculate similarity for textual attributes."""
        if not val1 or not val2:
            return 0.0
        n1 = normalize_text(val1)
        n2 = normalize_text(val2)
        if n1 == n2:
            return 1.0

        tokens1 = set(n1.split())
        tokens2 = set(n2.split())
        if tokens1 and tokens2:
            overlap = len(tokens1.intersection(tokens2)) / len(tokens1.union(tokens2))
            if overlap >= 0.8:
                return 1.0

        score = jaro_winkler_distance(n1, n2)
        # Strict Zero-Match Threshold for text fields
        if score < 0.40:
            return 0.0
        return score

    def calculate_contact_score(self, c1: str, c2: str) -> float:
        """Standardize and compare phone/contact numbers."""
        if not c1 or not c2:
            return 0.0
        d1 = re.sub(r'\D', '', str(c1))
        d2 = re.sub(r'\D', '', str(c2))
        if not d1 or not d2:
            return 0.0
        if d1 == d2:
            return 1.0
        if d1[-7:] == d2[-7:]:  # Last 7 digits match
            return 0.9
        return 0.0

    def calculate_email_score(self, e1: str, e2: str) -> float:
        """Standardize and compare email addresses."""
        if not e1 or not e2:
            return 0.0
        clean1 = e1.strip().lower()
        clean2 = e2.strip().lower()
        if clean1 == clean2:
            return 1.0
        score = jaro_winkler_distance(clean1, clean2)
        if score < 0.40:
            return 0.0
        return score

    def score_pair(self, candidate: dict, master_record: dict) -> dict:
        """
        Intelligently evaluate candidate record against a masterlist record across ALL system fields.
        Enforces Strict Zero-Match Penalty Rule (If a field does not match, returns 0.0% in fuzzy matching).
        """
        field_scores = {}
        field_weights = {}

        # 1. Doctor Name (Weight ~ 40%)
        name_res = self.calculate_name_score(candidate.get("name", ""), master_record.get("name", ""))
        field_scores["name"] = name_res["score"]
        field_weights["name"] = 0.40

        # 2. Medical Specialty (Weight ~ 20%)
        spec_score = self.calculate_text_score(candidate.get("specialty", ""), master_record.get("specialty", ""))
        field_scores["specialty"] = spec_score
        field_weights["specialty"] = 0.20

        # 3. Primary Hospital / Institution (Weight ~ 20%)
        hosp_cand = normalize_institution(candidate.get("hospital", ""))
        hosp_mast = normalize_institution(master_record.get("hospital", ""))
        inst_score = self.calculate_text_score(hosp_cand, hosp_mast)
        field_scores["hospital"] = inst_score
        field_weights["hospital"] = 0.20

        # 4. Secondary Hospital / Clinic (Weight ~ 5% if provided)
        sec_cand = candidate.get("secondary_hospital", "")
        sec_mast = master_record.get("secondary_hospital", "")
        if sec_cand or sec_mast:
            sec_score = self.calculate_text_score(normalize_institution(sec_cand), normalize_institution(sec_mast))
            field_scores["secondary_hospital"] = sec_score
            field_weights["secondary_hospital"] = 0.05

        # 5. Street / Barangay Address (Weight ~ 5% if provided)
        addr_cand = candidate.get("address", "")
        addr_mast = master_record.get("address", "")
        if addr_cand or addr_mast:
            addr_score = self.calculate_text_score(addr_cand, addr_mast)
            field_scores["address"] = addr_score
            field_weights["address"] = 0.05

        # 6. City / Province (Weight ~ 10%)
        city_score = self.calculate_text_score(candidate.get("city", ""), master_record.get("city", ""))
        field_scores["city"] = city_score
        field_weights["city"] = 0.10

        # 7. Contact Phone Number (Weight ~ 5%)
        phone_score = self.calculate_contact_score(candidate.get("contact", ""), master_record.get("contact", ""))
        field_scores["contact"] = phone_score
        field_weights["contact"] = 0.05

        # 8. Email Address (Weight ~ 5% if provided)
        email_cand = candidate.get("email", "")
        email_mast = master_record.get("email", "")
        if email_cand or email_mast:
            email_score = self.calculate_email_score(email_cand, email_mast)
            field_scores["email"] = email_score
            field_weights["email"] = 0.05

        # Normalize Weights to 1.0 (100%)
        total_weight = sum(field_weights.values())
        raw_weighted = 0.0
        normalized_breakdown = {}

        for f, score in field_scores.items():
            # Zero-Match Adjustment: If field is present but score < 0.40, force strictly 0.0
            if score < 0.40:
                score = 0.0

            w = field_weights[f] / total_weight
            raw_weighted += score * w
            
            # Status classification for each field
            status = "ZERO_MATCH (0%)"
            if score >= 0.95:
                status = "EXACT_MATCH"
            elif score >= 0.70:
                status = "HIGH_FUZZY_MATCH"
            elif score >= 0.40:
                status = "PARTIAL_MATCH"

            normalized_breakdown[f] = {
                "score": round(score * 100, 1),
                "weight_pct": f"{round(w * 100, 1)}%",
                "status": status
            }

        normalized_breakdown["name"]["details"] = name_res

        # ML Classifier Sigmoid Calibration
        z = 6.5 * (raw_weighted - 0.52)
        prob_ml = 1.0 / (1.0 + math.exp(-z))
        confidence_pct = round(prob_ml * 100, 1)

        # Determine Tier and Action according to process flow
        if prob_ml >= self.HIGH_THRESHOLD:
            tier = "High"
            action = "Merge records into single HCP Profile (Auto/Fast-Track)"
            badge_color = "#10B981"
        elif prob_ml >= self.MEDIUM_THRESHOLD:
            tier = "Medium (50-50 Match)"
            action = "Flag for Managerial Review & Escalation Workflow"
            badge_color = "#F59E0B"
        else:
            tier = "Low"
            action = "Keep records separate (Create New Record)"
            badge_color = "#EF4444"

        return {
            "master_id": master_record.get("id"),
            "master_record": master_record,
            "confidence_pct": confidence_pct,
            "raw_weighted": round(raw_weighted, 4),
            "tier": tier,
            "action": action,
            "badge_color": badge_color,
            "breakdown": normalized_breakdown
        }
