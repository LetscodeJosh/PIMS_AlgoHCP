# Risk-Based HCP Identity Resolution Specification

## 1. Executive Summary & Regulatory Context

In healthcare master data management (MDM), identifying duplicate Healthcare Professional (HCP) profiles is critical for single customer view accuracy, engagement history tracking, and reporting. Under privacy frameworks such as the Philippine Data Privacy Act of 2012 (RA 10173), collecting mandatory unique government identifiers (e.g., PRC License Numbers, Birthdates) introduces compliance friction and data security risks as Sensitive Personal Information (SPI).

This specification outlines a **Risk-Based HCP Identity Resolution Process** that relies on standardized name matching paired with multiple non-SPI supporting attributes (specialty, institution/workplace, location, historical interactions). Rather than relying on rigid binary rules or aggressive deduplication, this system calculates multi-attribute confidence scores and enforces mandatory corroborating evidence before executing any consolidation.

---

## 2. Guiding Principle

> **Guiding Principle**: *Favor preserving separate records over incorrectly merging two distinct physicians. Duplicate records can be merged later after additional evidence is available, whereas an incorrect merge can compromise HCP history, reporting, and engagement records and is significantly more difficult to reverse.*

This principle prioritizes data integrity and governance compliance over aggressive deduplication.

---

## 3. Standardization & Natural Key Generation

Raw inputs often suffer from spelling variations, honorific prefixes, suffixes, and local name abbreviations. Before matching, attributes undergo a 4-stage standardization pipeline:

### 3.1 Text Normalization Pipeline
1. **Title & Suffix Stripping**: Remove prefixes (`Dr.`, `Doctor`, `Dra.`, `Prof.`) and professional suffixes (`MD`, `FPOA`, `FPCP`, `FPCS`, `DPBR`).
2. **Abbreviation Expansion**: Map regional abbreviations to canonical forms:
   - `Ma.` / `Ma` $\rightarrow$ `Maria`
   - `St.` / `St` $\rightarrow$ `Saint`
   - `Sta.` / `Sta` $\rightarrow$ `Santa`
   - `Dela` / `De La` $\rightarrow$ `De La`
3. **Punctuation & Case Standardization**: Convert string to lowercase, strip accents/diacritics, remove special characters except spaces.
4. **Token Sorting**: Create token-sorted name keys (e.g., `Juan Dela Cruz` $\rightarrow$ `cruz dela juan`) to handle name order permutations.

---

## 4. Multi-Attribute Scoring Engine

The matching engine compares candidate record pairs ($R_A, R_B$) across 5 key feature domains:

$$\text{Total Score} = w_{\text{name}} \cdot S_{\text{name}} + w_{\text{spec}} \cdot S_{\text{spec}} + w_{\text{inst}} \cdot S_{\text{inst}} + w_{\text{loc}} \cdot S_{\text{loc}} + w_{\text{hist}} \cdot S_{\text{hist}}$$

| Attribute Domain | Weight ($w_i$) | Matching Algorithm | Description |
| :--- | :---: | :--- | :--- |
| **Standardized Name** | **40%** | Jaro-Winkler Similarity + Double Metaphone (Phonetic) | Captures phonetic & typographical variations in full names |
| **Specialty / Sub-Specialty** | **20%** | Exact / Taxonomy Group Match | Evaluates medical specialty equivalence or sub-specialty overlap |
| **Affiliated Institution** | **20%** | Token Set Ratio / Normalized Hospital ID | Compares hospital, clinic, or medical center affiliation |
| **Geographic Location** | **10%** | City & Province / Zip Code Exact Match | Evaluates geographical workplace alignment |
| **Historical Interactions** | **10%** | Shared Phone / Email / Shared Patient Touchpoint | Evaluates overlapping contact details or interaction logs |

---

## 5. Corroboration Rules & Risk-Based Action Tiers

To prevent false-positive merges caused by common physician names (e.g., two distinct doctors named *Maria Santos* in different cities), high name similarity **alone** is insufficient to consolidate profiles.

### 5.1 Corroborating Evidence Requirement
An HCP pair is considered **Corroborated** if and only if **at least one** of the following supporting conditions is met:
- **Condition A**: Institution / Hospital Match ($S_{\text{inst}} \ge 0.80$)
- **Condition B**: Specialty Match ($S_{\text{spec}} \ge 0.90$)
- **Condition C**: Geographic Location Match ($S_{\text{loc}} \ge 0.85$)
- **Condition D**: Direct Interaction / Contact Detail Match ($S_{\text{hist}} \ge 0.90$)

### 5.2 Confidence Action Tiers

```
                             Total Score (0 - 100%)
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
      Score ≥ 85%                 60% ≤ Score < 85%            Score < 60%
     + Corroborated                      OR                        │
             │                    Uncorroborated                   │
             ▼                          │                          ▼
   ┌──────────────────┐                 ▼                 ┌──────────────────┐
   │ HIGH CONFIDENCE  │       ┌──────────────────┐        │  LOW CONFIDENCE  │
   ├──────────────────┤       │MEDIUM CONFIDENCE │        ├──────────────────┤
   │ Action: MERGE    │       ├──────────────────┤        │ Action: KEEP     │
   │ Records          │       │ Action: FLAG FOR │        │ SEPARATE         │
   └──────────────────┘       │ DATA STEWARD     │        └──────────────────┘
                              └──────────────────┘
```

1. **High Confidence** ($\ge 85\%$ Total Score **AND** Corroborated):
   - **Action**: Merge records into a single master HCP profile automatically.
   - **Rationale**: High probabilistic match with verified supporting operational evidence.

2. **Medium Confidence** ($60\% - 84\%$ Total Score, **OR** $\ge 85\%$ Total Score without Corroboration):
   - **Action**: Flag pair for manual review by a Data Steward. Place in ERP / MDM Steward Verification Queue.
   - **Rationale**: High risk of false-positive merge if uncorroborated; human judgment required.

3. **Low Confidence** ($< 60\%$ Total Score):
   - **Action**: Keep records separate.
   - **Rationale**: Insufficient evidence to suggest duplicate identity.

---

## 6. Data Steward Verification Workflow & Audit Trail

When a pair is queued for Medium Confidence review:
1. **Queue Metadata**: The system logs `candidate_id_1`, `candidate_id_2`, individual component scores, missing corroborations, and timestamp.
2. **Data Steward Actions**:
   - `APPROVE_MERGE`: Manually confirms records belong to the same physician; records are merged into a primary profile.
   - `REJECT_SEPARATE`: Confirms distinct physicians; pair is marked as explicit false-match to prevent future re-flagging.
   - `DEFER`: Leaves in queue pending further field agent verification.
3. **Auditability**: Every merge or split operation records the actor, decision rationale, timestamp, and snapshot of pre-merge attribute states for rollback safety.
