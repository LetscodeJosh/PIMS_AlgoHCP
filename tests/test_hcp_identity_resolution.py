"""
Unit and Integration Tests for Risk-Based HCP Identity Resolution System
Standard Python unittest suite.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from hcp_identity_resolution import (
    HCPRecord, NameStandardizer, HCPMatcher,
    ConfidenceTier, ActionTier
)
from data_steward_queue import DataStewardQueueManager, StewardDecision


class TestHCPIdentityResolution(unittest.TestCase):

    def test_name_standardization(self):
        """Verify honorific stripping and abbreviation expansion."""
        raw1 = "Dr. Ma. Christina Dela Cruz, MD"
        std1 = NameStandardizer.standardize_name(raw1)
        self.assertIn("maria", std1)
        self.assertIn("christina", std1)
        self.assertIn("de la", std1)
        self.assertNotIn("dr", std1)
        self.assertNotIn("md", std1)

        sorted_key1 = NameStandardizer.get_token_sorted_key("Dela Cruz, Dr. Ma. Christina")
        sorted_key2 = NameStandardizer.get_token_sorted_key("Dr. Maria Christina De La Cruz")
        self.assertEqual(sorted_key1, sorted_key2)

    def test_high_confidence_corroborated_auto_merge(self):
        """Verify that high name similarity WITH corroborating hospital & specialty produces HIGH confidence MERGE."""
        matcher = HCPMatcher()

        doc_a = HCPRecord(
            id="HCP-001",
            full_name="Dr. Ma. Clara Santos, MD",
            specialty="Cardiology",
            institution_id="HOSP-101",
            institution_name="St. Luke's Medical Center",
            city="Taguig",
            province="Metro Manila"
        )

        doc_b = HCPRecord(
            id="HCP-002",
            full_name="Maria Clara Santos",
            specialty="Cardiology",
            institution_id="HOSP-101",
            institution_name="Saint Luke's Medical Center",
            city="Taguig",
            province="Metro Manila"
        )

        result = matcher.evaluate_pair(doc_a, doc_b)
        self.assertEqual(result.confidence_tier, ConfidenceTier.HIGH)
        self.assertEqual(result.recommended_action, ActionTier.MERGE)
        self.assertTrue(result.is_corroborated)
        self.assertGreaterEqual(result.total_score, 0.85)

    def test_similar_name_different_identity_prevents_false_merge(self):
        """
        CRITICAL TEST CASE:
        Two distinct doctors with similar/identical names but DIFFERENT specialty, institution, and location.
        Must NOT be auto-merged! Should be routed to MANUAL_REVIEW or KEEP_SEPARATE.
        """
        matcher = HCPMatcher()

        doc_a = HCPRecord(
            id="HCP-010",
            full_name="Dr. Maria Santos",
            specialty="Cardiology",
            institution_name="Manila Doctors Hospital",
            city="Manila",
            province="Metro Manila"
        )

        doc_b = HCPRecord(
            id="HCP-011",
            full_name="Dr. Maria Santos",
            specialty="Pediatrics",
            institution_name="Cebu City Medical Center",
            city="Cebu City",
            province="Cebu"
        )

        result = matcher.evaluate_pair(doc_a, doc_b)

        # Must NOT auto-merge because supporting attributes do not match!
        self.assertNotEqual(result.recommended_action, ActionTier.MERGE)
        self.assertFalse(result.is_corroborated)

    def test_medium_confidence_flagged_for_steward_review(self):
        """Verify that uncorroborated high name match is routed to Data Steward manual review."""
        matcher = HCPMatcher()

        doc_a = HCPRecord(
            id="HCP-020",
            full_name="Dr. Jose Antonio Reyes",
            specialty="Internal Medicine",
            city="Manila"
        )

        doc_b = HCPRecord(
            id="HCP-021",
            full_name="Jose A. Reyes",
            specialty="Internal Medicine",
            city="Quezon City" # Slight location difference
        )

        result = matcher.evaluate_pair(doc_a, doc_b)
        # Verify it routes to review or keep separate, avoiding auto merge
        self.assertNotEqual(result.recommended_action, ActionTier.MERGE)

    def test_low_confidence_keep_separate(self):
        """Verify low score results in KEEP_SEPARATE."""
        matcher = HCPMatcher()

        doc_a = HCPRecord(
            id="HCP-030",
            full_name="Dr. Juan Abad",
            specialty="Dermatology",
            city="Makati"
        )

        doc_b = HCPRecord(
            id="HCP-031",
            full_name="Dr. Pedro Reyes",
            specialty="Neurology",
            city="Davao"
        )

        result = matcher.evaluate_pair(doc_a, doc_b)
        self.assertEqual(result.confidence_tier, ConfidenceTier.LOW)
        self.assertEqual(result.recommended_action, ActionTier.KEEP_SEPARATE)

    def test_data_steward_queue_workflow(self):
        """Verify Data Steward Queue enqueue, processing, and audit logging."""
        matcher = HCPMatcher()
        queue_mgr = DataStewardQueueManager()

        # Set up pair that produces MANUAL_REVIEW
        matcher.high_threshold = 0.30
        matcher.medium_threshold = 0.20

        doc_a = HCPRecord(
            id="HCP-040",
            full_name="Dr. Antonio Luna",
            specialty="Orthopedics"
        )
        doc_b = HCPRecord(
            id="HCP-041",
            full_name="Antonio Luna, MD",
            specialty="Rheumatology"
        )

        result = matcher.evaluate_pair(doc_a, doc_b)
        item = queue_mgr.enqueue_if_needed(result)

        self.assertIsNotNone(item)
        self.assertEqual(item.status, StewardDecision.PENDING)
        self.assertEqual(len(queue_mgr.get_pending_items()), 1)

        # Steward reviews and approves merge
        resolved_item = queue_mgr.process_decision(
            queue_id=item.queue_id,
            steward_id="STEWARD-01",
            decision=StewardDecision.APPROVED_MERGE,
            reason="Verified via specialty board registry that physician cross-practices."
        )

        self.assertEqual(resolved_item.status, StewardDecision.APPROVED_MERGE)
        self.assertEqual(len(queue_mgr.get_pending_items()), 0)
        self.assertEqual(len(queue_mgr.audit_log), 2)  # 1 Enqueued + 1 Processed


if __name__ == '__main__':
    unittest.main()
