"""
Hierarchical Managerial Approval & Escalation Engine.
Handles review queue for 50-50 matches and new doctor canonical verification.
"""

from datetime import datetime

class EscalationWorkflowManager:
    """
    Manages the review queue, new doctor verification, and escalation chain:
    MedRep -> Level 1 District Manager -> Level 2 Regional Director / Data Steward.
    """

    def __init__(self):
        self.review_queue = []
        self.history = []
        self.counter = 100

    def add_to_queue(self, candidate_record: dict, match_results: list, review_type: str = "MATCH_REVIEW") -> dict:
        """Add a submission to the pending managerial review queue."""
        self.counter += 1
        review_id = f"REV-{self.counter}"
        
        top_match = match_results[0] if match_results else None

        stage_title = "Level 1 Review (District Manager)"
        if review_type == "NEW_DOCTOR_VERIFICATION":
            stage_title = "Level 1 Review - New Doctor Canonical Verification"

        item = {
            "review_id": review_id,
            "review_type": review_type,
            "submission_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "medrep_name": candidate_record.get("medrep_name", "MedRep User"),
            "candidate": candidate_record,
            "top_match": top_match,
            "all_matches": match_results,
            "confidence_pct": top_match["confidence_pct"] if top_match else 0.0,
            "current_stage": stage_title,
            "assigned_level": 1,
            "status": "PENDING",
            "escalation_history": [
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "action": "SUBMITTED_BY_MEDREP",
                    "actor": candidate_record.get("medrep_name", "MedRep User"),
                    "note": f"Submitted doctor entry ({review_type}). Match Score: {top_match['confidence_pct'] if top_match else 0.0}%"
                }
            ]
        }
        self.review_queue.append(item)
        return item

    def get_pending_reviews(self, level: int = None):
        """Fetch pending reviews, optionally filtered by manager level."""
        if level is None:
            return [item for item in self.review_queue if item["status"] == "PENDING"]
        return [item for item in self.review_queue if item["status"] == "PENDING" and item["assigned_level"] == level]

    def escalate(self, review_id: str, actor_name: str, reason: str = "") -> dict:
        """
        Escalate record to higher managerial position when Level 1 Manager doesn't know the record.
        """
        for item in self.review_queue:
            if item["review_id"] == review_id:
                if item["assigned_level"] < 2:
                    item["assigned_level"] += 1
                    item["current_stage"] = f"Level {item['assigned_level']} Review (Regional Director / Head Steward)"
                    item["escalation_history"].append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "action": "ESCALATED_TO_HIGHER_POSITION",
                        "actor": actor_name,
                        "note": reason or "Manager uncertain about record; passed up to higher position for final approval."
                    })
                    return {"success": True, "item": item, "message": "Record escalated to Level 2 Manager."}
                else:
                    return {"success": False, "message": "Record is already at the highest approval level."}
        return {"success": False, "message": "Review ID not found."}

    def resolve(self, review_id: str, action: str, actor_name: str, target_master_id: str = None, notes: str = "") -> dict:
        """
        Resolve review item with action: 'MERGE_RECORD', 'KEEP_SEPARATE', or 'VERIFY_AND_LOCK_CANONICAL'.
        """
        for item in self.review_queue:
            if item["review_id"] == review_id:
                item["status"] = "RESOLVED"
                item["resolution_action"] = action
                item["resolved_by"] = actor_name
                item["resolved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                item["target_master_id"] = target_master_id
                item["escalation_history"].append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "action": f"DECISION_{action}",
                    "actor": actor_name,
                    "note": notes or f"Decision finalized: {action}"
                })
                self.history.append(item)
                return {"success": True, "item": item, "message": f"Review {review_id} resolved with action {action}."}
        return {"success": False, "message": "Review ID not found."}
