"""
Unit tests for PIMS_AlgoHCP ERP algorithm core, multi-field intelligence, and workflow.
"""

import unittest
from hcp_matcher.normalizer import parse_erp_doctor_name, normalize_name, normalize_text
from hcp_matcher.algorithms import jaro_winkler_distance, soundex, token_set_ratio
from hcp_matcher.scorer import HCPMatchScorer
from hcp_matcher.workflow import EscalationWorkflowManager

class TestAlgoHCP(unittest.TestCase):

    def test_normalizer(self):
        erp1 = parse_erp_doctor_name("Santa Maria", "", "Cruz")
        erp2 = parse_erp_doctor_name("St. Maria", "", "Cruz")
        self.assertEqual(erp1.canonical_name, "SANTA MARIA CRUZ")
        self.assertEqual(erp2.canonical_name, "SANTA MARIA CRUZ")

    def test_name_similarity(self):
        scorer = HCPMatchScorer()
        res = scorer.calculate_name_score("Santa Maria", "", "Cruz", "Dr. St. Maria Cruz")
        self.assertGreater(res["score"], 0.90)

    def test_multi_field_intelligent_scoring(self):
        scorer = HCPMatchScorer()
        cand = {
            "first_name": "Santa Maria",
            "last_name": "Cruz",
            "name": "Dr. Santa Maria Cruz",
            "specialty": "Cardiology",
            "hospital": "St Lukes Hospital BGC",
            "secondary_hospital": "Makati Med Annex",
            "address": "32nd St, BGC",
            "city": "Taguig City",
            "contact": "09171234567",
            "email": "dr.cruz@stlukes.ph"
        }
        mast = {
            "id": "HCP-1001",
            "name": "Dr. Santa M. Cruz, M.D.",
            "specialty": "Cardiology",
            "hospital": "St. Luke's Medical Center - Global City",
            "secondary_hospital": "Makati Medical Center",
            "address": "32nd St, Bonifacio Global City",
            "city": "Taguig City",
            "contact": "09171234567",
            "email": "dr.cruz@stlukes.ph"
        }
        score = scorer.score_pair(cand, mast)
        self.assertGreater(score["confidence_pct"], 80.0)
        self.assertIn("name", score["breakdown"])
        self.assertIn("hospital", score["breakdown"])
        self.assertIn("email", score["breakdown"])
        self.assertIn("contact", score["breakdown"])
        self.assertEqual(score["breakdown"]["contact"]["status"], "EXACT_MATCH")
        self.assertEqual(score["breakdown"]["email"]["status"], "EXACT_MATCH")

    def test_escalation_workflow(self):
        wf = EscalationWorkflowManager()
        cand = {"medrep_name": "Test MedRep", "name": "Dr. Santa Maria Cruz"}
        matches = [{"confidence_pct": 65.0, "tier": "Medium (50-50 Match)", "master_record": {"name": "Dr. Santa M. Cruz"}}]
        
        item = wf.add_to_queue(cand, matches)
        self.assertEqual(item["assigned_level"], 1)

        res = wf.escalate(item["review_id"], "District Manager", "Uncertain match score")
        self.assertTrue(res["success"])
        self.assertEqual(res["item"]["assigned_level"], 2)

if __name__ == "__main__":
    unittest.main()
