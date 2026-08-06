"""
PIMS_AlgoHCP Standalone Microservice Server v2.0 - ERP Schema Aligned.
Supports Step 1 (Privacy/Signature), Step 2 (Doctor & Workplace Info),
Step 3 (Survey Questionnaire), and Others (Territory & MedRep Details).
"""

import http.server
import socketserver
import json
import os
import urllib.parse
from datetime import datetime

from hcp_matcher.scorer import HCPMatchScorer
from hcp_matcher.dictionary import MasterDictionary
from hcp_matcher.workflow import EscalationWorkflowManager
from hcp_matcher.sample_data import SAMPLE_MASTERLIST, SAMPLE_DICTIONARY
from hcp_matcher.security import SecurityShield

PORT = 8080
WEB_DIR = os.path.join(os.path.dirname(__file__), "web")

# Clean Slate Data Stores (Simulates real-world production day-1 entry)
masterlist = []
dictionary_mgr = MasterDictionary([])
scorer = HCPMatchScorer()
workflow_mgr = EscalationWorkflowManager()
security_shield = SecurityShield()

class AlgoHCPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def _send_json(self, data, code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        if path == "/api/masterlist":
            self._send_json({"status": "success", "masterlist": masterlist})

        elif path == "/api/dictionary":
            self._send_json({"status": "success", "dictionary": dictionary_mgr.get_all()})

        elif path == "/api/reviews":
            reviews = workflow_mgr.get_pending_reviews()
            self._send_json({"status": "success", "reviews": reviews, "history": workflow_mgr.history})

        elif path == "/api/merge-history":
            self._send_json({"status": "success", "history": workflow_mgr.history})

        elif path == "/api/version":
            self._send_json({
                "status": "success",
                "version": "2.0-ERP",
                "engine_name": "PIMS_AlgoHCP ERP Matcher Engine v2.0",
                "features": [
                    "Step-by-Step PIMS ERP Wizard Alignment",
                    "Privacy Consent & Signature Lock Verification",
                    "Component Doctor Name Linkage (First, Middle, Last)",
                    "Workplace, Specialty & Account/Program Deduplication",
                    "Clean Slate Real-World Simulation Mode"
                ]
            })

        elif path == "/api/detect-name":
            name_query = query.get("name", [""])[0]
            name_matches = scorer.detect_name_match(name_query, masterlist)
            self._send_json({"status": "success", "name_query": name_query, "matches": name_matches})

        elif path == "/api/token":
            token = security_shield.generate_api_token("medrep_user_1", "MEDREP")
            self._send_json({"status": "success", "token": token})

        elif path.startswith("/api/"):
            self._send_json({"error": "Endpoint not found"}, 404)

        else:
            if path == "/" or path == "":
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)
        payload = {}
        if body_bytes:
            try:
                payload = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                pass

        if path == "/api/reset-data":
            global masterlist, dictionary_mgr, workflow_mgr
            masterlist.clear()
            dictionary_mgr.dictionary_db.clear()
            workflow_mgr.review_queue.clear()
            workflow_mgr.history.clear()
            workflow_mgr.counter = 100
            self._send_json({"status": "success", "message": "System reset to Clean Slate. Masterlist and Dictionary cleared."})

        elif path == "/api/seed-data":
            masterlist.clear()
            for item in SAMPLE_MASTERLIST:
                item_copy = dict(item)
                item_copy["encoded_count"] = item_copy.get("encoded_count", 1)
                masterlist.append(item_copy)

            dictionary_mgr.dictionary_db.clear()
            dictionary_mgr.dictionary_db.extend(list(SAMPLE_DICTIONARY))
            
            sample_cand = {
                "medrep_name": "MedRep Santos",
                "medrep_email": "medrep.santos@pims.com",
                "first_name": "Santa Maria",
                "middle_name": "Dela",
                "last_name": "Cruz",
                "name": "Dr. Santa Maria Cruz",
                "specialty": "Cardiology",
                "sub_specialty": "Interventional Cardiology",
                "hcp_type": "Physician",
                "practice": "Private",
                "hospital": "St. Lukes Hospital BGC",
                "secondary_hospital": "Makati Med Annex",
                "address": "32nd St, BGC",
                "city": "Taguig City",
                "province": "Metro Manila",
                "contact": "09171234567",
                "email": "dr.cruz@stlukes.ph",
                "account_program": "Abbott Diabetes Care",
                "territory_code": "NCR-TAGUIG-01",
                "consent_given": True
            }
            matches = [scorer.score_pair(sample_cand, masterlist[0])]
            workflow_mgr.add_to_queue(sample_cand, matches)
            self._send_json({"status": "success", "message": "ERP Benchmark dataset loaded successfully."})

        elif path == "/api/detect-name":
            name_query = payload.get("name", "")
            name_matches = scorer.detect_name_match(name_query, masterlist)
            self._send_json({"status": "success", "name_query": name_query, "matches": name_matches})

        elif path == "/api/match":
            candidate = payload.get("candidate", {})
            results = []
            for master_rec in masterlist:
                res = scorer.score_pair(candidate, master_rec)
                results.append(res)
            results.sort(key=lambda x: x["confidence_pct"], reverse=True)
            self._send_json({"status": "success", "matches": results})

        elif path == "/api/submit":
            candidate = payload.get("candidate", {})

            # ERP Mandatory Fields Check
            mandatory_keys = [
                ("first_name", "First Name"),
                ("last_name", "Last Name"),
                ("specialty", "Specialty Name"),
                ("hcp_type", "Type"),
                ("practice", "Practice"),
                ("hospital", "Workplace Name"),
                ("city", "City Name"),
                ("province", "Province Name"),
                ("contact", "Mobile/Phone Number"),
                ("email", "Email Address"),
                ("account_program", "Account/Program"),
                ("territory_code", "Territory Code"),
                ("medrep_email", "Medrep Email Address")
            ]

            missing_fields = []
            for k, label in mandatory_keys:
                val = candidate.get(k, "")
                if not val or not str(val).strip():
                    missing_fields.append(label)

            if not candidate.get("consent_given"):
                missing_fields.append("Privacy Notice & Consent Checkbox")

            if not candidate.get("signature_png"):
                missing_fields.append("Doctor Digital Signature")

            if missing_fields:
                self._send_json({
                    "status": "error",
                    "action_taken": "SUBMISSION_BLOCKED",
                    "message": f"Submission Rejected! Mandatory fields are blank: {', '.join(missing_fields)}",
                    "missing_fields": missing_fields
                }, 400)
                return

            # Construct full name if absent
            fn = candidate.get("first_name", "").strip()
            mn = candidate.get("middle_name", "").strip()
            ln = candidate.get("last_name", "").strip()
            full_name = f"Dr. {fn} {mn} {ln}".replace("  ", " ").strip()
            candidate["name"] = full_name

            matches = []
            for master_rec in masterlist:
                matches.append(scorer.score_pair(candidate, master_rec))
            matches.sort(key=lambda x: x["confidence_pct"], reverse=True)

            top_match = matches[0] if matches else None
            score_pct = top_match["confidence_pct"] if top_match else 0.0

            if score_pct >= 88.0:
                action_taken = "AUTO_MERGED"
                for m in masterlist:
                    if m["id"] == top_match["master_id"]:
                        m["has_merge_history"] = True
                        m["encoded_count"] = m.get("encoded_count", 1) + 1
                        enc_count = m["encoded_count"]
                msg = f"High Confidence Match ({score_pct}%). Candidate linked automatically to Master Record ({top_match['master_id']}). Encoded {enc_count}x."
            elif score_pct >= 50.0:
                review_item = workflow_mgr.add_to_queue(candidate, matches, "MATCH_REVIEW")
                action_taken = "PENDING_MANAGER_REVIEW"
                msg = f"Medium/50-50 Match ({score_pct}%). Sent to Level 1 Manager Review Queue ({review_item['review_id']})."
            else:
                new_id = f"HCP-{1000 + len(masterlist) + 1}"
                new_rec = {
                    "id": new_id,
                    "name": full_name,
                    "first_name": fn,
                    "middle_name": mn,
                    "last_name": ln,
                    "birth_date": candidate.get("birth_date", ""),
                    "canonical_name": f"{fn} {mn} {ln}".upper(),
                    "specialty": candidate.get("specialty"),
                    "sub_specialty": candidate.get("sub_specialty", ""),
                    "hcp_type": candidate.get("hcp_type"),
                    "practice": candidate.get("practice"),
                    "hospital": candidate.get("hospital"),
                    "secondary_hospital": candidate.get("secondary_hospital", ""),
                    "address": candidate.get("address", ""),
                    "city": candidate.get("city"),
                    "province": candidate.get("province", ""),
                    "contact": candidate.get("contact"),
                    "email": candidate.get("email"),
                    "account_program": candidate.get("account_program"),
                    "territory_code": candidate.get("territory_code"),
                    "medrep_email": candidate.get("medrep_email"),
                    "signature_png": candidate.get("signature_png", ""),
                    "signature_status": "PENDING_VERIFICATION",
                    "status": "PENDING_MANAGERIAL_VERIFICATION",
                    "has_merge_history": False,
                    "encoded_count": 1
                }
                masterlist.append(new_rec)
                
                review_item = workflow_mgr.add_to_queue(candidate, [{"master_id": new_id, "master_record": new_rec, "confidence_pct": score_pct, "tier": "Low Match (New Profile)", "badge_color": "#EF4444"}], "NEW_DOCTOR_VERIFICATION")
                
                action_taken = "NEW_DOCTOR_QUEUED_FOR_VERIFICATION"
                msg = f"New Doctor Profile Created ({new_id}). Queued for Managerial Verification ({review_item['review_id']}) to commit to Master Dictionary."

            self._send_json({
                "status": "success",
                "action_taken": action_taken,
                "message": msg,
                "submitted_candidate": candidate,
                "top_match": top_match,
                "all_matches": matches[:5]
            })

        elif path == "/api/link-existing":
            candidate = payload.get("candidate", {})
            master_id = payload.get("master_id")
            target_rec = next((m for m in masterlist if m["id"] == master_id), None)
            if target_rec:
                target_rec["has_merge_history"] = True
                target_rec["encoded_count"] = target_rec.get("encoded_count", 1) + 1
            
            log_item = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": "LINKED_TO_EXISTING_RECORD",
                "candidate": candidate,
                "linked_master_id": master_id,
                "master_record": target_rec
            }
            workflow_mgr.history.append(log_item)
            
            self._send_json({
                "status": "success",
                "action_taken": "LINKED_TO_EXISTING_RECORD",
                "message": f"Candidate doctor record linked to existing Master Profile ({master_id}). Duplicate prevented!",
                "target_record": target_rec
            })

        elif path == "/api/escalate":
            review_id = payload.get("review_id")
            actor = payload.get("actor_name", "District Manager")
            reason = payload.get("reason", "Manager uncertain about 50-50 match; passed to higher position.")
            res = workflow_mgr.escalate(review_id, actor, reason)
            self._send_json(res)

        elif path == "/api/resolve":
            review_id = payload.get("review_id")
            action = payload.get("action")
            actor = payload.get("actor_name", "Approver")
            target_id = payload.get("target_master_id")
            notes = payload.get("notes", "")

            review_item = next((item for item in workflow_mgr.review_queue if item["review_id"] == review_id), None)
            cand = review_item["candidate"] if review_item else {}
            
            master_before = {}
            m_id = target_id or (review_item.get("top_match", {}).get("master_id") if review_item else None)
            for m in masterlist:
                if m["id"] == m_id:
                    master_before = dict(m)

            if action == "VERIFY_AND_LOCK_CANONICAL" or action == "MERGE_RECORD":
                for m in masterlist:
                    if m["id"] == m_id:
                        m["status"] = "VERIFIED_LOCKED"
                        m["signature_status"] = "LOCKED_TRUE_ONLY_ONE"
                        if action == "MERGE_RECORD":
                            m["has_merge_history"] = True
                            m["encoded_count"] = m.get("encoded_count", 1) + 1
                        
                        # Merge all new/missing attributes into master profile
                        for k in ["birth_date", "sub_specialty", "hcp_type", "practice", "secondary_hospital", "address", "province", "contact", "email", "account_program", "territory_code"]:
                            if cand.get(k) and not m.get(k):
                                m[k] = cand.get(k)
                                
                        if cand.get("signature_png"):
                            m["signature_png"] = cand.get("signature_png")
                        m["verified_by"] = actor
                        m["verified_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                dict_id = f"DICT-{5000 + len(dictionary_mgr.dictionary_db) + 1}"
                new_dict_entry = {
                    "id": dict_id,
                    "full_canonical_name": cand.get("name", "").upper(),
                    "first_name": cand.get("first_name"),
                    "middle_name": cand.get("middle_name"),
                    "last_name": cand.get("last_name"),
                    "specialty": cand.get("specialty"),
                    "sub_specialty": cand.get("sub_specialty", ""),
                    "hcp_type": cand.get("hcp_type", ""),
                    "practice": cand.get("practice", ""),
                    "primary_hospital": cand.get("hospital"),
                    "city": cand.get("city"),
                    "province": cand.get("province", ""),
                    "official_contact": cand.get("contact", ""),
                    "email": cand.get("email", ""),
                    "account_program": cand.get("account_program", ""),
                    "signature_png": cand.get("signature_png", ""),
                    "signature_status": "LOCKED_TRUE_ONLY_ONE",
                    "dictionary_notes": f"100% Verified Canonical Baseline Record & True-Only-One Signature approved by Managerial Position ({actor}) on {datetime.now().strftime('%Y-%m-%d')}."
                }
                dictionary_mgr.dictionary_db.append(new_dict_entry)
                notes = f"Verified by Managerial Position ({actor}). Profile & Signature committed to Verified Dictionary ({dict_id})."

            master_after = next((dict(m) for m in masterlist if m["id"] == m_id), {})

            snapshot = {
                "master_id": m_id,
                "candidate_submitted": cand,
                "master_before": master_before,
                "master_after": master_after,
                "resolved_action": action,
                "resolved_by": actor,
                "resolved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            res = workflow_mgr.resolve(review_id, action, actor, target_id, notes, merge_snapshot=snapshot)
            self._send_json(res)

        elif path == "/api/test-score":
            rec1 = payload.get("record1", {})
            rec2 = payload.get("record2", {})
            result = scorer.score_pair(rec1, rec2)
            self._send_json({"status": "success", "result": result})

        else:
            self._send_json({"error": "Endpoint not found"}, 404)

def run_server():
    os.makedirs(WEB_DIR, exist_ok=True)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), AlgoHCPRequestHandler) as httpd:
        print(f"PIMS_AlgoHCP Standalone ERP Protected Microservice v2.0 running on http://0.0.0.0:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
