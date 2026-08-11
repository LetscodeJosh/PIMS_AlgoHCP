"""
Interactive Demo Runner for Risk-Based HCP Identity Resolution System
======================================================================
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from hcp_identity_resolution import HCPRecord, HCPMatcher, ConfidenceTier, ActionTier
from data_steward_queue import DataStewardQueueManager, StewardDecision


def run_demo():
    print("=" * 80)
    print("RISK-BASED HCP IDENTITY RESOLUTION DEMONSTRATION ENGINE")
    print("Guiding Principle: Favor preserving separate records over incorrectly merging.")
    print("=" * 80)
    print()

    matcher = HCPMatcher()
    queue_mgr = DataStewardQueueManager()

    scenarios = [
        (
            "Scenario 1: High Confidence Match (Auto-Merge)",
            HCPRecord(
                id="HCP-101",
                full_name="Dr. Ma. Christina Dela Cruz, MD",
                specialty="Pediatrics",
                institution_name="St. Jude Hospital",
                city="Quezon City",
                email="mcdelacruz@example.com"
            ),
            HCPRecord(
                id="HCP-102",
                full_name="Maria Christina de la Cruz",
                specialty="Pediatrics",
                institution_name="Saint Jude Hospital",
                city="Quezon City",
                email="mcdelacruz@example.com"
            )
        ),
        (
            "Scenario 2: Similar Name, Distinct Identity (Prevent False Merge)",
            HCPRecord(
                id="HCP-201",
                full_name="Dr. Maria Santos",
                specialty="Cardiology",
                institution_name="Manila Doctors Hospital",
                city="Manila"
            ),
            HCPRecord(
                id="HCP-202",
                full_name="Maria Santos, MD",
                specialty="Dermatology",
                institution_name="Cebu City Medical Center",
                city="Cebu City"
            )
        ),
        (
            "Scenario 3: Medium Confidence (Flagged for Data Steward)",
            HCPRecord(
                id="HCP-301",
                full_name="Dr. Jose Antonio Reyes",
                specialty="Internal Medicine"
            ),
            HCPRecord(
                id="HCP-302",
                full_name="Jose A. Reyes",
                specialty="Gastroenterology"
            )
        ),
        (
            "Scenario 4: Low Confidence (Distinct Records Preserved)",
            HCPRecord(
                id="HCP-401",
                full_name="Dr. Juan Abad",
                specialty="Ophthalmology",
                city="Pasig"
            ),
            HCPRecord(
                id="HCP-402",
                full_name="Dr. Gabriel Ramos",
                specialty="Oncology",
                city="Makati"
            )
        )
    ]

    for title, rec_a, rec_b in scenarios:
        print(f"--- {title} ---")
        print(f"  Record A: [{rec_a.id}] {rec_a.full_name} | {rec_a.specialty or 'N/A'} | {rec_a.institution_name or 'N/A'} | {rec_a.city or 'N/A'}")
        print(f"  Record B: [{rec_b.id}] {rec_b.full_name} | {rec_b.specialty or 'N/A'} | {rec_b.institution_name or 'N/A'} | {rec_b.city or 'N/A'}")

        res = matcher.evaluate_pair(rec_a, rec_b)
        print(f"  Scores  : Total: {res.total_score:.1%} | Name: {res.name_score:.2f} | Inst: {res.institution_score:.2f} | Spec: {res.specialty_score:.2f} | Loc: {res.location_score:.2f}")
        print(f"  Corroborated : {res.is_corroborated}")
        print(f"  Confidence   : {res.confidence_tier.value}")
        print(f"  Action       : {res.recommended_action.value}")
        print(f"  Explanation  : {res.explanation}")

        # Enqueue if steward review needed
        item = queue_mgr.enqueue_if_needed(res)
        if item:
            print(f"  [QUEUE LOG] Pair placed into Data Steward Queue -> Queue ID: {item.queue_id}")
        print()

    print("=" * 80)
    print("DATA STEWARD QUEUE SUMMARY")
    print("=" * 80)
    pending = queue_mgr.get_pending_items()
    print(f"Pending Items in Steward Queue: {len(pending)}")
    for p in pending:
        print(f"  - [{p.queue_id}] Candidates ({p.match_result.candidate_a_id} vs {p.match_result.candidate_b_id}) | Score: {p.match_result.total_score:.1%} | Status: {p.status.value}")

    print("\nSimulating Data Steward Action on STWD-0001:")
    if pending:
        resolved = queue_mgr.process_decision(
            queue_id=pending[0].queue_id,
            steward_id="STEWARD_ADMIN_01",
            decision=StewardDecision.REJECTED_SEPARATE,
            reason="Confirmed different physicians via hospital directory verification."
        )
        print(f"  - [{resolved.queue_id}] Updated Status: {resolved.status.value} | Reason: {resolved.decision_reason}")

    print("\nAudit Log Events:")
    for entry in queue_mgr.audit_log:
        print(f"  [{entry['timestamp']}] Event: {entry['event_type']} | Queue ID: {entry['queue_id']} | Details: {entry['details']}")

    print("\nDemo Completed Successfully.")


if __name__ == '__main__':
    run_demo()
