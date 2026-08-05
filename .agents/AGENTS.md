# PIMS_AlgoHCP - Master Algorithm & Architectural Fix Registry

This file documents all architectural rules, algorithm weights, and historical fixes established for the **PIMS_AlgoHCP Recognizer Engine**. All AI agents and developers working on this project must strictly adhere to these rules.

---

## 📌 Core Architectural Rules & Directives

### 1. Mandatory Field Validation Rule
- **Rule**: All 8 doctor attributes (`Doctor Full Name`, `Specialty`, `Primary Hospital`, `Secondary Hospital`, `Street Address`, `City`, `Contact Number`, `Email Address`) AND `Doctor Digital Signature` are **MANDATORY**.
- **Enforcement**: Submissions with any blank field MUST be blocked on both client-side (`web/app.js`) and server-side (`server.py` returning `HTTP 400 Bad Request`).
- **UI Behavior**: Empty fields outline in red (`#EF4444`) and trigger the `⚠️ Mandatory Fields Missing` pop-up warning modal.

### 2. Immutable True-Only-One Signature Rule
- **Rule**: Each verified doctor profile in the Masterlist and Dictionary possesses exactly **one canonical signature**.
- **Enforcement**: Once approved by a Managerial Position (`VERIFY_AND_LOCK_CANONICAL`), the signature status becomes `LOCKED_TRUE_ONLY_ONE`.
- **Immutability**: Locked signatures CANNOT be overwritten, edited, or tampered with by any MedRep or subsequent submission.

### 3. Dynamic Origin API Resolution
- **Rule**: Never hardcode `http://localhost:8080/api` in client scripts.
- **Implementation**: Client code MUST resolve `const API_BASE = window.location.origin + "/api";` so that external network IPs (`http://192.168.0.96:8080`), mobile apps, and public tunnels work seamlessly without CORS or loopback errors.

### 4. Unthrottled Real-Time Background Detection
- **Rule**: Do NOT apply rate-limiting restrictions on the API endpoint `/api/match`.
- **Rationale**: Real-time debounced (300ms) background auto-detection requires uninhibited API responses as MedReps type rapidly into form fields across multiple mobile devices.

### 5. New Doctor Verification & Master Dictionary Auto-Commit Flow
- **Rule**: When a low match (< 50%) entry is submitted:
  1. Profile status set to `PENDING_MANAGERIAL_VERIFICATION`.
  2. Queued to Managerial Approval Portal under `NEW DOCTOR VERIFICATION`.
  3. Upon Manager approval (`VERIFY_AND_LOCK_CANONICAL`), profile status updates to `VERIFIED_LOCKED`, signature locks as `LOCKED_TRUE_ONLY_ONE`, and canonical record automatically commits to the **100% Verified Reference Dictionary** (`DICT-500X`).

---

## 📊 Calibrated Multi-Attribute Weight Matrix

| Attribute Field | Weight Percentage | Primary Matching Logic |
| :--- | :---: | :--- |
| **Doctor Full Name** | **36.4%** | Strips titles (`Dr.`, `M.D.`, `FPCP`), expands Philippine prefixes (`St.` $\leftrightarrow$ `Santa`, `Dela` $\leftrightarrow$ `De La`), Jaro-Winkler + Soundex 4-character phonetic distance. |
| **Primary Specialty** | **18.2%** | Canonical specialty dictionary token set ratio. |
| **Primary Hospital** | **18.2%** | Token-Set Jaccard index for hospital abbreviations (`St. Lukes BGC` vs `St. Luke's Medical Center`). |
| **City / Municipality** | **9.1%** | Geographic municipality fuzzy distance. |
| **Secondary Hospital** | **4.5%** | Secondary clinic/annex matching. |
| **Street Address** | **4.5%** | Barangay & street text distance ratio. |
| **Contact Number** | **4.5%** | Standardized 11-digit Philippine phone number match. |
| **Email Address** | **4.5%** | Lowercase email handle & domain similarity. |
| **Doctor Digital Signature** | **Required** | **Immutable True-Only-One Signature Lock** upon managerial approval. |

---

## 🧮 ML Sigmoid Calibration Formula

$$S_{\text{raw}} = \sum (w_i \cdot s_i), \quad z = 6.5 \cdot (S_{\text{raw}} - 0.52), \quad P(\text{Match}) = \frac{1}{1 + e^{-z}}$$

- **High Match Tier ($\ge 88.0\%$)**: Fast-track auto-merge with existing Master Profile.
- **Medium 50-50 Match Tier ($50.0\% - 87.9\%$)**: Pop-up recognizer detector & route to Manager Review Queue.
- **Low Match Tier ($< 50.0\%$)**: Create draft profile & queue for Managerial Position Verification & Signature Lock.

---

## 🛠️ Master Fix Registry History

- **Fix 1**: Dynamic Origin API Resolution (`window.location.origin + "/api"`).
- **Fix 2**: Mandatory Field Validation & Warning Pop-Up (`HTTP 400 Bad Request`).
- **Fix 3**: 8 Interactive Philippine Demo Presets & Benchmark Datasets.
- **Fix 4**: Unthrottled Real-Time API Engine (Removed rate-limiting).
- **Fix 5**: Standalone Microservice Shield & Security Guard (`hcp_matcher/security.py`).
- **Fix 6**: New Doctor Verification Queue & Automatic Master Dictionary Auto-Commit (`DICT-500X`).
- **Fix 7**: Doctor Digital Signature Pad & Immutable True-Only-One Signature Lock (`LOCKED_TRUE_ONLY_ONE`).
- **Fix 8**: TCPServer `allow_reuse_address = True` Socket Rebind Fix.
