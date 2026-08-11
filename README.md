# PIMS Risk-Based HCP Identity Resolution Algorithm Engine

[![Data Privacy Act Compliant](https://img.shields.io/badge/DPA_2012-Compliant-success)](#) [![Governance](https://img.shields.io/badge/MDM_Governance-Fellegi--Sunter-blue)](#)

A risk-based Healthcare Professional (HCP) identity resolution engine designed for Master Data Management (MDM) platforms. It uses standardized names paired with weighted non-SPI (Sensitive Personal Information) supporting attributes to accurately detect duplicates and prevent false-positive merges.

---

## Guiding Principle

> **Guiding Principle**: *Favor preserving separate records over incorrectly merging two distinct physicians. Duplicate records can be merged later after additional evidence is available, whereas an incorrect merge can compromise HCP history, reporting, and engagement records and is significantly more difficult to reverse.*

---

## Features

1. **Name Normalization & Abbreviation Expansion**:
   - Strips honorific titles (`Dr.`, `MD`, `Dra.`, `Prof.`, `FPOA`, `FPCP`).
   - Normalizes local name variants (`Ma.` $\rightarrow$ `Maria`, `St.` $\rightarrow$ `Saint`, `Sta.` $\rightarrow$ `Santa`, `Dela` $\rightarrow$ `De La`).
   - Token-sorting for name order permutations.

2. **Weighted Attribute Similarity Model**:
   - **Standardized Name (40%)**: Jaro-Winkler + Double Metaphone / Token Jaro-Winkler.
   - **Specialty (20%)**: Taxonomy & sub-specialty token set similarity.
   - **Affiliated Institution (20%)**: Workplace / Hospital ID and Token Set Ratio.
   - **Geographic Location (10%)**: City, Province, and Zip Code match.
   - **Historical Interactions (10%)**: Shared email, phone, or interaction history.

3. **Mandatory Corroboration Requirement**:
   - Prevents auto-merging distinct physicians with identical/similar names (e.g. *Dr. Maria Santos*).
   - High-confidence auto-merging requires at least **one** verified supporting attribute match (institution, specialty, location, or interaction).

4. **Risk-Based Action Tiers**:
   - **High Confidence ($\ge 85\%$ Total Score + Corroboration)**: Merge records into a single HCP profile.
   - **Medium Confidence ($60\% - 84\%$ Total Score OR Uncorroborated)**: Flag for Data Steward manual review.
   - **Low Confidence ($< 60\%$ Total Score)**: Keep records separate.

5. **Data Steward Queue & Governance Audit Log**:
   - Built-in queue management (`APPROVE_MERGE`, `REJECT_SEPARATE`, `DEFER`) with immutable event logging.

---

## File Structure

- `HCP_Identity_Resolution_Specification.md`: Technical proposal and MDM governance design document.
- `src/hcp_identity_resolution.py`: Core Python implementation.
- `src/hcp_identity_resolution.js`: Standalone JavaScript implementation.
- `src/data_steward_queue.py`: Steward review queue and audit log manager.
- `tests/test_hcp_identity_resolution.py`: Pytest test suite.
- `demo_runner.py`: Interactive demonstration script.

---

## Quick Start Example (Python)

```python
from src.hcp_identity_resolution import HCPRecord, HCPMatcher, ActionTier

matcher = HCPMatcher()

doc_a = HCPRecord(
    id="HCP-001",
    full_name="Dr. Ma. Christina Dela Cruz, MD",
    specialty="Pediatrics",
    institution_name="St. Jude Hospital",
    city="Quezon City"
)

doc_b = HCPRecord(
    id="HCP-002",
    full_name="Maria Christina de la Cruz",
    specialty="Pediatrics",
    institution_name="Saint Jude Hospital",
    city="Quezon City"
)

result = matcher.evaluate_pair(doc_a, doc_b)
print(f"Action: {result.recommended_action.value}")  # Output: MERGE
print(f"Confidence: {result.confidence_tier.value}") # Output: HIGH
print(f"Explanation: {result.explanation}")
```
