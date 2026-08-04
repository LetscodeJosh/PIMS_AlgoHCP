"""
Sample Benchmark Dataset for Philippine HCP Masterlist & Verified Dictionary.
Contains realistic name variations, hospital affiliations, and specialties.
"""

SAMPLE_MASTERLIST = [
    {
        "id": "HCP-1001",
        "name": "Dr. Santa M. Cruz, M.D.",
        "canonical_name": "SANTA MARIA CRUZ",
        "specialty": "Cardiology",
        "hospital": "St. Luke's Medical Center - Global City",
        "address": "32nd St, Bonifacio Global City",
        "city": "Taguig City",
        "province": "Metro Manila",
        "contact": "09171234567",
        "status": "VERIFIED_ACTIVE"
    },
    {
        "id": "HCP-1002",
        "name": "Dr. Juan Dela Cruz",
        "canonical_name": "JUAN DE LA CRUZ",
        "specialty": "Pediatrics",
        "hospital": "Philippine General Hospital",
        "address": "Taft Avenue, Ermita",
        "city": "Manila",
        "province": "Metro Manila",
        "contact": "09189876543",
        "status": "VERIFIED_ACTIVE"
    },
    {
        "id": "HCP-1003",
        "name": "Dra. Maria Victoria Santos, FPCP",
        "canonical_name": "MARIA VICTORIA SANTOS",
        "specialty": "Internal Medicine",
        "hospital": "Makati Medical Center",
        "address": "Amorsolo St., Legazpi Village",
        "city": "Makati City",
        "province": "Metro Manila",
        "contact": "09201112233",
        "status": "VERIFIED_ACTIVE"
    },
    {
        "id": "HCP-1004",
        "name": "Dr. Sto. Tomas Reyes",
        "canonical_name": "SANTO TOMAS REYES",
        "specialty": "Orthopedic Surgery",
        "hospital": "Asian Hospital and Medical Center",
        "address": "2205 Civic Drive, Filinvest City",
        "city": "Muntinlupa City",
        "province": "Metro Manila",
        "contact": "09175554433",
        "status": "VERIFIED_ACTIVE"
    },
    {
        "id": "HCP-1005",
        "name": "Dr. Jose P. Rizal Jr.",
        "canonical_name": "JOSE PROTACIO RIZAL JUNIOR",
        "specialty": "Ophthalmology",
        "hospital": "Cardinal Santos Medical Center",
        "address": "10 Wilson St, Greenhills",
        "city": "San Juan City",
        "province": "Metro Manila",
        "contact": "09193332211",
        "status": "VERIFIED_ACTIVE"
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
    }
]
