"""
Sample Benchmark Dataset for Philippine HCP Masterlist & Verified Dictionary.
Contains realistic name variations, hospital affiliations, and specialties.
"""

SAMPLE_MASTERLIST = [
    {
        "id": "HCP-1001",
        "name": "Dr. Joshua Mariano Tan, M.D., FPCP",
        "first_name": "Joshua",
        "middle_name": "Mariano",
        "last_name": "Tan",
        "canonical_name": "JOSHUA MARIANO TAN",
        "specialty": "Cardiology",
        "sub_specialty": "Interventional Cardiology",
        "hcp_type": "Consultant",
        "practice": "Prescribing",
        "hospital": "St. Luke's Medical Center - Global City",
        "secondary_hospital": "St. Luke's Medical Center - Quezon City",
        "address": "32nd St, Bonifacio Global City",
        "city": "Taguig City",
        "province": "Metro Manila",
        "contact": "09171234567",
        "email": "dr.joshua.tan@stlukes.com.ph",
        "account_program": "Abbott Cardiology Care",
        "territory_code": "TERR-NCR-SOUTH-01",
        "status": "VERIFIED_LOCKED",
        "signature_status": "LOCKED_TRUE_ONLY_ONE",
        "has_merge_history": False,
        "encoded_count": 1,
        "specializations": [
            {
                "specialty": "Cardiology",
                "sub_specialty": "Interventional Cardiology",
                "type": "Consultant",
                "practice": "Prescribing",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Baseline"
            }
        ],
        "workplaces": [
            {
                "hospital": "St. Luke's Medical Center - Global City",
                "secondary_hospital": "St. Luke's Medical Center - Quezon City",
                "city": "Taguig City",
                "province": "Metro Manila",
                "address": "32nd St, Bonifacio Global City",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Baseline"
            }
        ],
        "contacts": ["09171234567"],
        "emails": ["dr.joshua.tan@stlukes.com.ph"]
    },
    {
        "id": "HCP-1002",
        "name": "Dra. Maria Clara De La Cruz, FPOGS",
        "first_name": "Maria",
        "middle_name": "Clara",
        "last_name": "Dela Cruz",
        "canonical_name": "MARIA CLARA DE LA CRUZ",
        "specialty": "Obstetrics & Gynecology",
        "sub_specialty": "Maternal & Fetal Medicine",
        "hcp_type": "Consultant",
        "practice": "Prescribing",
        "hospital": "Philippine General Hospital",
        "secondary_hospital": "Makati Medical Center Annex",
        "address": "Taft Avenue, Ermita",
        "city": "Manila",
        "province": "Metro Manila",
        "contact": "09189876543",
        "email": "dra.claradelacruz@pgh.gov.ph",
        "account_program": "Abbott Women's Health",
        "territory_code": "TERR-NCR-CENTRAL-02",
        "status": "VERIFIED_LOCKED",
        "signature_status": "LOCKED_TRUE_ONLY_ONE",
        "has_merge_history": False,
        "encoded_count": 1,
        "specializations": [
            {
                "specialty": "Obstetrics & Gynecology",
                "sub_specialty": "Maternal & Fetal Medicine",
                "type": "Consultant",
                "practice": "Prescribing",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Baseline"
            }
        ],
        "workplaces": [
            {
                "hospital": "Philippine General Hospital",
                "secondary_hospital": "Makati Medical Center Annex",
                "city": "Manila",
                "province": "Metro Manila",
                "address": "Taft Avenue, Ermita",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Baseline"
            }
        ],
        "contacts": ["09189876543"],
        "emails": ["dra.claradelacruz@pgh.gov.ph"]
    },
    {
        "id": "HCP-1003",
        "name": "Dr. Antonio Jose Santos Jr., M.D.",
        "first_name": "Antonio",
        "middle_name": "Jose",
        "last_name": "Santos",
        "canonical_name": "ANTONIO JOSE SANTOS JUNIOR",
        "specialty": "Pediatrics",
        "sub_specialty": "Pediatric Cardiology",
        "hcp_type": "Consultant",
        "practice": "Both",
        "hospital": "The Medical City - Pasig",
        "secondary_hospital": "TMC Ortigas Clinic",
        "address": "Ortigas Avenue",
        "city": "Pasig City",
        "province": "Metro Manila",
        "contact": "09201112233",
        "email": "dr.antonio.santos@themedcity.com.ph",
        "account_program": "Abbott Pediatric Care",
        "territory_code": "TERR-NCR-EAST-03",
        "status": "VERIFIED_LOCKED",
        "signature_status": "LOCKED_TRUE_ONLY_ONE",
        "has_merge_history": False,
        "encoded_count": 1,
        "specializations": [
            {
                "specialty": "Pediatrics",
                "sub_specialty": "Pediatric Cardiology",
                "type": "Consultant",
                "practice": "Both",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Baseline"
            }
        ],
        "workplaces": [
            {
                "hospital": "The Medical City - Pasig",
                "secondary_hospital": "TMC Ortigas Clinic",
                "city": "Pasig City",
                "province": "Metro Manila",
                "address": "Ortigas Avenue",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Baseline"
            }
        ],
        "contacts": ["09201112233"],
        "emails": ["dr.antonio.santos@themedcity.com.ph"]
    },
    {
        "id": "HCP-1004",
        "name": "Dr. Santo Tomas Reyes, FPOA",
        "first_name": "Santo",
        "middle_name": "Tomas",
        "last_name": "Reyes",
        "canonical_name": "SANTO TOMAS REYES",
        "specialty": "Orthopedic Surgery",
        "sub_specialty": "Spine Surgery",
        "hcp_type": "Consultant",
        "practice": "Prescribing",
        "hospital": "Asian Hospital and Medical Center",
        "secondary_hospital": "Alabang Medical Clinic",
        "address": "2205 Civic Drive, Filinvest City",
        "city": "Muntinlupa City",
        "province": "Metro Manila",
        "contact": "09175554433",
        "email": "dr.reyes@asianhospital.com",
        "account_program": "Abbott Ortho Line",
        "territory_code": "TERR-NCR-SOUTH-04",
        "status": "VERIFIED_LOCKED",
        "signature_status": "LOCKED_TRUE_ONLY_ONE",
        "has_merge_history": False,
        "encoded_count": 1,
        "specializations": [
            {
                "specialty": "Orthopedic Surgery",
                "sub_specialty": "Spine Surgery",
                "type": "Consultant",
                "practice": "Prescribing",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Baseline"
            }
        ],
        "workplaces": [
            {
                "hospital": "Asian Hospital and Medical Center",
                "secondary_hospital": "Alabang Medical Clinic",
                "city": "Muntinlupa City",
                "province": "Metro Manila",
                "address": "2205 Civic Drive, Filinvest City",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Baseline"
            }
        ],
        "contacts": ["09175554433"],
        "emails": ["dr.reyes@asianhospital.com"]
    },
    {
        "id": "HCP-1005",
        "name": "Dra. Santa Isabel Gonzales, FPCP",
        "first_name": "Santa",
        "middle_name": "Isabel",
        "last_name": "Gonzales",
        "canonical_name": "SANTA ISABEL GONZALES",
        "specialty": "Internal Medicine",
        "sub_specialty": "Endocrinology",
        "hcp_type": "Consultant",
        "practice": "Prescribing",
        "hospital": "Cardinal Santos Medical Center",
        "secondary_hospital": "Greenhills Endocrinology Clinic",
        "address": "10 Wilson St, Greenhills",
        "city": "San Juan City",
        "province": "Metro Manila",
        "contact": "09193332211",
        "email": "isabel.gonzales@csmc.ph",
        "account_program": "Abbott Diabetes Care",
        "territory_code": "TERR-NCR-NORTH-05",
        "status": "VERIFIED_LOCKED",
        "signature_status": "LOCKED_TRUE_ONLY_ONE",
        "has_merge_history": False,
        "encoded_count": 1,
        "specializations": [
            {
                "specialty": "Internal Medicine",
                "sub_specialty": "Endocrinology",
                "type": "Consultant",
                "practice": "Prescribing",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Baseline"
            }
        ],
        "workplaces": [
            {
                "hospital": "Cardinal Santos Medical Center",
                "secondary_hospital": "Greenhills Endocrinology Clinic",
                "city": "San Juan City",
                "province": "Metro Manila",
                "address": "10 Wilson St, Greenhills",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Baseline"
            }
        ],
        "contacts": ["09193332211"],
    }
]

SAMPLE_DICTIONARY = [
    {
        "id": "DICT-5001",
        "full_canonical_name": "DR. SANTA MARIA CRUZ, M.D.",
        "name": "Dr. Santa Maria Cruz",
        "specialty": "Cardiology / Interventional Cardiology",
        "primary_hospital": "St. Luke's Medical Center - Global City",
        "secondary_hospital": "Makati Medical Center",
        "city": "Taguig City",
        "province": "Metro Manila",
        "official_contact": "(02) 8789-7700 ext 5012",
        "dictionary_notes": "100% Verified Canonical Benchmark Record. Board Certified Fellow in Cardiology."
    },
    {
        "id": "DICT-5002",
        "full_canonical_name": "DR. JUAN DE LA CRUZ, M.D.",
        "name": "Dr. Juan De La Cruz",
        "specialty": "Pediatrics & Pediatric Pulmonology",
        "primary_hospital": "Philippine General Hospital",
        "secondary_hospital": "Manila Doctors Hospital",
        "city": "Manila",
        "province": "Metro Manila",
        "official_contact": "(02) 8554-8400",
        "dictionary_notes": "100% Verified Canonical Benchmark Record. Senior Consultant."
    },
    {
        "id": "DICT-5003",
        "full_canonical_name": "DRA. MARIA VICTORIA SANTOS, FPCP",
        "name": "Dra. Maria Victoria Santos",
        "specialty": "Internal Medicine - Endocrinology",
        "primary_hospital": "Makati Medical Center",
        "secondary_hospital": "The Medical City - Pasig",
        "city": "Makati City",
        "province": "Metro Manila",
        "official_contact": "(02) 8888-8999",
        "dictionary_notes": "100% Verified Canonical Benchmark Record. Department Chair."
    },
    {
        "id": "DICT-5004",
        "full_canonical_name": "DR. SANTO TOMAS REYES, FPOA",
        "name": "Dr. Santo Tomas Reyes",
        "specialty": "Orthopedic Surgery - Joint Replacement",
        "primary_hospital": "Asian Hospital and Medical Center",
        "secondary_hospital": "Medical Center Muntinlupa",
        "city": "Muntinlupa City",
        "province": "Metro Manila",
        "official_contact": "(02) 8771-9000",
        "dictionary_notes": "100% Verified Canonical Benchmark Record. Orthopedic Specialist."
    },
    {
        "id": "DICT-5005",
        "full_canonical_name": "DR. JOSE PROTACIO RIZAL JUNIOR, M.D.",
        "name": "Dr. Jose Protacio Rizal Jr.",
        "specialty": "Ophthalmology & Cataract Surgery",
        "primary_hospital": "Cardinal Santos Medical Center",
        "secondary_hospital": "VRC Eye Center",
        "city": "San Juan City",
        "province": "Metro Manila",
        "official_contact": "(02) 8727-0001",
        "dictionary_notes": "100% Verified Canonical Benchmark Record. Fellow in Ophthalmology."
    },
    {
        "id": "DICT-5006",
        "full_canonical_name": "DR. ANTONIO DE LOS REYES, M.D.",
        "name": "Dr. Antonio De Los Reyes",
        "specialty": "Dermatology & Cosmetic Surgery",
        "primary_hospital": "The Medical City - Pasig",
        "secondary_hospital": "St. Luke's QC",
        "city": "Pasig City",
        "province": "Metro Manila",
        "official_contact": "(02) 8988-1000",
        "dictionary_notes": "100% Verified Canonical Benchmark Record. Dermatology Department Chair."
    }
]
