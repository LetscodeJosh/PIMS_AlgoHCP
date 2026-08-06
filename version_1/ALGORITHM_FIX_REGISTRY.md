# PIMS_AlgoHCP - Master Fix & Feature Registry

This file records all 8 major fixes, architectural decisions, and algorithm enhancements implemented in **PIMS_AlgoHCP**.

---

### 📋 Complete Fix & Feature Inventory

#### 1. Dynamic Origin API Resolution (Multi-Device LAN Access)
- **Problem**: Hardcoded API endpoints (`http://localhost:8080/api`) caused CORS errors and failed requests when accessing from external network devices (`192.168.0.96:8080`).
- **Fix**: Updated `web/app.js` to dynamically resolve `const API_BASE = window.location.origin + "/api";`.

#### 2. Mandatory Field Validation & Warning Pop-Up
- **Problem**: Blank inputs could previously be submitted accidentally.
- **Fix**: Enforced mandatory validation across all 8 fields + Digital Signature. Form submission is blocked if any field is blank, missing inputs outline in red (`#EF4444`), and a `⚠️ Mandatory Fields Missing Modal` pops up. `server.py` rejects incomplete API requests with `HTTP 400 Bad Request`.

#### 3. 8 Interactive Philippine Demo Presets & Expanded Dataset
- **Problem**: Needed comprehensive benchmark presets to test all algorithm tiers.
- **Fix**: Built 8 interactive preset buttons on the UI (High Match ≥88%, 50-50 Match 50-87%, Low Match <50%, Honorific Shift, Surname Compound, Santo/Sto. Shift, Suffix Shift, Delos/De Los Shift).

#### 4. Unthrottled Real-Time API Engine
- **Problem**: API rate-limiting caused request throttling as MedReps typed rapidly into form fields.
- **Fix**: Removed rate-limiting restrictions from `/api/match` to ensure smooth real-time background detection.

#### 5. Standalone Microservice Shield & Security Guard (`hcp_matcher/security.py`)
- **Problem**: Needed to protect algorithm weights and master database against unauthorized access or reverse-engineering.
- **Fix**: Built `security.py` providing HMAC-SHA256 JWT Bearer authentication tokens and Cython binary compilation readiness (`.so` / `.pyd`).

#### 6. New Doctor Canonical Verification Queue & Dictionary Auto-Commit
- **Problem**: When a brand new doctor (<50% score) is encoded, its canonical data needed managerial verification before becoming official reference data.
- **Fix**: New doctor submissions create a draft profile (`PENDING_MANAGERIAL_VERIFICATION`) routed to the Managerial Portal. Upon manager approval (`VERIFY_AND_LOCK_CANONICAL`), the profile status is updated to `VERIFIED_LOCKED` and automatically committed to the **100% Verified Master Dictionary** (`DICT-500X`).

#### 7. Doctor Digital Signature Pad & Immutable True-Only-One Signature Lock
- **Problem**: Need to capture and lock doctor signatures to prevent tampering or unauthorized changes.
- **Fix**: Integrated an interactive HTML5/Touch Digital Signature Pad. Upon managerial verification, the signature status is set to `LOCKED_TRUE_ONLY_ONE` and committed to the Verified Master Dictionary. Once locked, the signature is permanent and immutable.

#### 8. Socket Rebind Fix (`allow_reuse_address = True`)
- **Problem**: Restarting `server.py` quickly caused `OSError: [Errno 48] Address already in use`.
- **Fix**: Configured `socketserver.TCPServer.allow_reuse_address = True` in `server.py`.
