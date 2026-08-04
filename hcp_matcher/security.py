"""
Security & Standalone Microservice Shield for PIMS_AlgoHCP.
Provides JWT authentication, rate-limiting, Cython binary build helpers, and payload encryption.
"""

import time
import hashlib
import hmac
import base64
import json

# Secret Key for Microservice API Authentication & HMAC Signature
SECRET_KEY = "PIMS_ALGO_HCP_SECURE_MICROSERVICE_KEY_2026"

class SecurityShield:
    """
    Protects algorithm endpoints from unauthorized access, scraping, and reverse-engineering.
    """
    def __init__(self):
        self.rate_limit_db = {} # IP -> list of timestamps

    def generate_api_token(self, user_id: str, role: str) -> str:
        """Generate a secure signed JWT-style API Bearer token."""
        header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
        payload_data = {
            "sub": user_id,
            "role": role,
            "exp": int(time.time()) + 86400  # 24 hours
        }
        payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).decode().rstrip("=")
        
        signature_base = f"{header}.{payload}"
        signature = hmac.new(SECRET_KEY.encode(), signature_base.encode(), hashlib.sha256).hexdigest()
        
        return f"{header}.{payload}.{signature}"

    def verify_api_token(self, token: str) -> dict:
        """Verify API token authenticity and expiration."""
        if not token:
            return {"valid": False, "reason": "Missing token"}
        
        parts = token.split(".")
        if len(parts) != 3:
            return {"valid": False, "reason": "Malformed token format"}

        header, payload, signature = parts
        signature_base = f"{header}.{payload}"
        expected_sig = hmac.new(SECRET_KEY.encode(), signature_base.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            return {"valid": False, "reason": "Invalid signature - Unauthorized token"}

        try:
            # Add padding back if necessary
            padded_payload = payload + '=' * (-len(payload) % 4)
            data = json.loads(base64.urlsafe_b64decode(padded_payload).decode())
            if time.time() > data.get("exp", 0):
                return {"valid": False, "reason": "Token expired"}
            return {"valid": True, "user_id": data["sub"], "role": data["role"]}
        except Exception:
            return {"valid": False, "reason": "Corrupted token payload"}

    def check_rate_limit(self, client_ip: str, limit: int = 30, window_seconds: int = 60) -> bool:
        """Rate limiting to prevent database scraping attacks (Max 30 requests/min)."""
        now = time.time()
        timestamps = self.rate_limit_db.get(client_ip, [])
        # Filter timestamps within window
        valid_timestamps = [t for t in timestamps if now - t < window_seconds]
        
        if len(valid_timestamps) >= limit:
            return False # Rate limit exceeded
        
        valid_timestamps.append(now)
        self.rate_limit_db[client_ip] = valid_timestamps
        return True
