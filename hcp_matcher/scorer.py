"""
Version 2.0 Multi-Attribute Match Scorer & Name-First Pre-Detector aligned with PIMS ERP Schema.
Features Step-by-Step ERP Attribute Evaluation, Component-Level Linkage (Surname, First Name, Middle Name),
and Encoding Frequency Tracking across MedRep ERP submissions.
"""

import math
import re
from .normalizer import parse_erp_doctor_name, normalize_text, normalize_institution
from .algorithms import jaro_winkler_distance, token_set_ratio

class HCPMatchScorer:
    """
    Version 2.0 ERP-Aligned Multi-Attribute Matcher and Intelligent Name Detector.
    """

    HIGH_THRESHOLD = 0.88      # >= 88% High match (Auto-merge/Fast-track)
    MEDIUM_THRESHOLD = 0.50    # 50% - 87% Medium (50-50 Match) -> Managerial Escalation

    def calculate_name_score(self, cand_first: str, cand_mid: str, cand_last: str, mast_name: str) -> dict:
        """
        Multi-signal component linkage for ERP Doctor Name fields.
        Compares candidate structured components against master records.
        """
        # If candidate sends raw name string
        if not cand_first and not cand_last and cand_mid:
            cand_first, cand_last = cand_mid, ""

        erp_name = parse_erp_doctor_name(cand_first, cand_mid, cand_last)
        cand_canonical = erp_name.canonical_name or normalize_text(cand_first + " " + cand_last)

        mast_erp = parse_erp_doctor_name("", mast_name, "")
        mast_canonical = mast_erp.canonical_name or normalize_text(mast_name)

        if not cand_canonical or not mast_canonical:
            return {"score": 0.0, "jw": 0.0, "token_set": 0.0, "reason": "Empty name input"}

        if cand_canonical == mast_canonical:
            return {"score": 1.0, "jw": 1.0, "token_set": 1.0, "reason": "Exact normalized canonical match"}

        jw_score = jaro_winkler_distance(cand_canonical, mast_canonical)
        tok_set = token_set_ratio(cand_canonical, mast_canonical)

        # Surname check if provided
        surname_score = 0.0
        if erp_name.last_name:
            surname_score = jaro_winkler_distance(erp_name.last_name, mast_canonical)

        base_name_score = (jw_score * 0.40) + (tok_set * 0.40) + (surname_score * 0.20)

        # Zero-Match penalty rule
        cand_tokens = set(cand_canonical.split())
        mast_tokens = set(mast_canonical.split())
        if not cand_tokens.intersection(mast_tokens) and jw_score < 0.65:
            base_name_score = 0.0
        elif base_name_score < 0.55:
            base_name_score = 0.0

        return {
            "score": round(base_name_score, 4),
            "jw": round(jw_score, 4),
            "token_set": round(tok_set, 4),
            "canonical1": cand_canonical,
            "canonical2": mast_canonical
        }

    def detect_name_match(self, candidate_name: str, master_records: list) -> list:
        """
        ERP Standalone Name-First Pre-Detection Engine.
        Executes instant search as user types in HCP Search or Last/First Name box.
        """
        if not candidate_name or len(candidate_name.strip()) < 2:
            return []

        results = []
        for master in master_records:
            name_eval = self.calculate_name_score("", candidate_name, "", master.get("name", ""))
            score_pct = round(name_eval["score"] * 100, 1)
            encoded_count = master.get("encoded_count", 1)

            results.append({
                "master_id": master.get("id"),
                "master_name": master.get("name"),
                "canonical_name": master.get("canonical_name"),
                "specialty": master.get("specialty"),
                "hospital": master.get("hospital"),
                "city": master.get("city"),
                "name_score_pct": score_pct,
                "encoded_count": encoded_count,
                "details": name_eval
            })

        results.sort(key=lambda x: x["name_score_pct"], reverse=True)
        return results

    def score_pair(self, candidate: dict, master_record: dict) -> dict:
        """
        Version 2.0 ERP-Aligned Multi-Attribute Match Scorer.
        Evaluates First/Middle/Last Name, Specialization, Workplaces, Contacts, Account/Program.
        """
        cand_fn = candidate.get("first_name", "")
        cand_mn = candidate.get("middle_name", "")
        cand_ln = candidate.get("last_name", "")
        cand_full = candidate.get("name") or f"{cand_fn} {cand_mn} {cand_ln}".strip()

        field_scores = {}
        field_weights = {}

        # 1. Doctor Full Name (Weight ~ 36.4%)
        name_res = self.calculate_name_score(cand_fn, cand_mn, cand_ln, master_record.get("name", cand_full))
        field_scores["name"] = name_res["score"]
        field_weights["name"] = 0.364

        # 2. Specialty & Sub-Specialty (Weight ~ 18.2%)
        cand_spec = candidate.get("specialty") or candidate.get("specialty_name", "")
        mast_spec = master_record.get("specialty", "")
        spec_n1 = normalize_text(cand_spec)
        spec_n2 = normalize_text(mast_spec)
        if spec_n1 and spec_n2:
            field_scores["specialty"] = 1.0 if spec_n1 == spec_n2 else jaro_winkler_distance(spec_n1, spec_n2)
        else:
            field_scores["specialty"] = 0.0
        field_weights["specialty"] = 0.182

        # 3. Primary Hospital / Workplace Name (Weight ~ 18.2%)
        cand_hosp = candidate.get("hospital") or candidate.get("workplace_name", "")
        mast_hosp = master_record.get("hospital", "")
        h1 = normalize_institution(cand_hosp)
        h2 = normalize_institution(mast_hosp)
        if h1 and h2:
            field_scores["hospital"] = 1.0 if h1 == h2 else jaro_winkler_distance(h1, h2)
        else:
            field_scores["hospital"] = 0.0
        field_weights["hospital"] = 0.182

        # 4. City / Province Name (Weight ~ 9.1%)
        cand_city = candidate.get("city") or candidate.get("city_name", "")
        mast_city = master_record.get("city", "")
        c1 = normalize_text(cand_city)
        c2 = normalize_text(mast_city)
        if c1 and c2:
            field_scores["city"] = 1.0 if c1 == c2 else jaro_winkler_distance(c1, c2)
        else:
            field_scores["city"] = 0.0
        field_weights["city"] = 0.091

        # 5. Secondary Hospital / Clinic (Weight ~ 4.5%)
        cand_sec = candidate.get("secondary_hospital", "")
        mast_sec = master_record.get("secondary_hospital", "")
        if cand_sec or mast_sec:
            field_scores["secondary_hospital"] = jaro_winkler_distance(normalize_text(cand_sec), normalize_text(mast_sec))
            field_weights["secondary_hospital"] = 0.045

        # 6. Street Address (Weight ~ 4.5%)
        cand_addr = candidate.get("address", "")
        mast_addr = master_record.get("address", "")
        if cand_addr or mast_addr:
            field_scores["address"] = jaro_winkler_distance(normalize_text(cand_addr), normalize_text(mast_addr))
            field_weights["address"] = 0.045

        # 7. Contact / Mobile Phone Number (Weight ~ 4.5%)
        cand_phone = candidate.get("contact") or candidate.get("mobile_number", "")
        mast_phone = master_record.get("contact", "")
        p1 = re.sub(r'\D', '', str(cand_phone))
        p2 = re.sub(r'\D', '', str(mast_phone))
        if p1 and p2:
            field_scores["contact"] = 1.0 if p1 == p2 else (0.9 if p1[-7:] == p2[-7:] else 0.0)
        else:
            field_scores["contact"] = 0.0
        field_weights["contact"] = 0.045

        # 8. Email Address (Weight ~ 4.5%)
        cand_email = candidate.get("email") or candidate.get("email_address", "")
        mast_email = master_record.get("email", "")
        e1 = str(cand_email).strip().lower()
        e2 = str(mast_email).strip().lower()
        if e1 and e2:
            field_scores["email"] = 1.0 if e1 == e2 else jaro_winkler_distance(e1, e2)
        else:
            field_scores["email"] = 0.0
        field_weights["email"] = 0.045

        # Weight Normalization
        total_weight = sum(field_weights.values())
        raw_weighted = 0.0
        normalized_breakdown = {}

        for f, score in field_scores.items():
            if score < 0.40:
                score = 0.0
            w = field_weights[f] / total_weight
            raw_weighted += score * w
            
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

        # ML Calibration Sigmoid
        z = 6.5 * (raw_weighted - 0.52)
        prob_ml = 1.0 / (1.0 + math.exp(-z))
        
        # Name Anchoring Penalty
        if field_scores["name"] == 0.0:
            prob_ml = min(prob_ml, 0.25)
            confidence_pct = round(prob_ml * 100 * (raw_weighted / 0.60), 1)
            confidence_pct = min(confidence_pct, 25.0)
        else:
            confidence_pct = round(prob_ml * 100, 1)

        if confidence_pct >= 88.0:
            tier = "High Match (Fast-Track Merge)"
            action = "Merge records into canonical HCP Profile"
            badge_color = "#10B981"
        elif confidence_pct >= 50.0:
            tier = "Medium Tier (50-50 Match)"
            action = "Escalate to Manager Approval Queue"
            badge_color = "#F59E0B"
        else:
            tier = "Low Match Tier (<50%)"
            action = "Create New Doctor Candidate Queue"
            badge_color = "#EF4444"

        encoded_count = master_record.get("encoded_count", 1)

        return {
            "master_id": master_record.get("id"),
            "master_record": master_record,
            "confidence_pct": confidence_pct,
            "raw_weighted": round(raw_weighted, 4),
            "tier": tier,
            "action": action,
            "badge_color": badge_color,
            "encoded_count": encoded_count,
            "breakdown": normalized_breakdown
        }
