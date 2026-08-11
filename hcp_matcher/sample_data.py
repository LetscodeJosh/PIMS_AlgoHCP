"""
Sample Benchmark Dataset for Philippine HCP Masterlist & Verified Dictionary.
Contains realistic name variations, hospital affiliations, and specialties.
"""

BASE_MASTERLIST = [
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
        "birth_date": "1980-05-15",
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
        "birth_date": "1982-11-20",
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
        "birth_date": "1978-03-10",
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
        "birth_date": "1975-08-25",
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
        "birth_date": "1984-01-14",
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
        "emails": ["isabel.gonzales@csmc.ph"]
    }
]

def _generate_expanded_masterlist():
    records = [dict(r) for r in BASE_MASTERLIST]
    current_id = 1006

    middle_names_joshua_tan = [
        "Mariano", "Reyes", "Alonzo", "Santos", "Aquino", "Castro", "Garcia", "Dela Cruz",
        "Mendoza", "Ramos", "Flores", "Gonzales", "Bautista", "Villanueva", "Cruz", "Navarro",
        "Mercado", "Salcedo", "Roxas", "Soriano", "Corpuz", "Pascual", "Castillo", "Morales",
        "Valenzuela", "Rivera", "Guinto", "Tolentino", "Santiago", "Domingo"
    ]  # 30 records

    middle_names_joshua_chua = [
        "Lim", "Sy", "Go", "Tan", "Co", "King", "Yap", "Ty", "Ang", "Dee",
        "Cheng", "Uy", "Ong", "Chan", "Lee", "Ting", "Chiu", "Siy", "Yu", "Tiu",
        "Tan-Co", "Sy-Lim", "Go-King", "Ang-Dee", "Yap-Ty"
    ]  # 25 records

    middle_names_maria_cruz = [
        "Clara", "Isabel", "Teresa", "Sofia", "Luisa", "Elena", "Carmen", "Cristina",
        "Angela", "Patricia", "Beatris", "Victoria", "Aurora", "Rosa", "Esperanza",
        "Consuelo", "Dolores", "Mercedez", "Paloma", "Josefina", "Amalia", "Celia",
        "Ines", "Pilar", "Felicia"
    ]  # 25 records

    middle_names_jose_santos = [
        "Antonio", "Miguel", "Carlos", "Francisco", "Manuel", "Ramon", "Eduardo",
        "Fernando", "Roberto", "Gabriel", "Rafael", "Pedro", "Mario", "Alejandro",
        "Javier", "Luis", "Sergio", "Andres", "Diego", "Enrique"
    ]  # 20 records

    specialties_pool = [
        ("Cardiology", "Interventional Cardiology"),
        ("Pediatrics", "Pediatric Cardiology"),
        ("Internal Medicine", "Endocrinology"),
        ("Obstetrics & Gynecology", "Maternal & Fetal Medicine"),
        ("Orthopedic Surgery", "Spine Surgery"),
        ("Neurology", "Stroke Medicine"),
        ("Gastroenterology", "Hepatology"),
        ("Dermatology", "Cosmetic Dermatology"),
        ("Nephrology", "Transplant Nephrology"),
        ("Pulmonology", "Critical Care Medicine")
    ]

    hospitals_pool = [
        ("St. Luke's Medical Center - Global City", "St. Luke's Medical Center - Quezon City", "Taguig City", "Metro Manila", "32nd St, Bonifacio Global City"),
        ("The Medical City - Pasig", "TMC Ortigas Clinic", "Pasig City", "Metro Manila", "Ortigas Avenue"),
        ("Makati Medical Center", "Makati Med Annex Clinic", "Makati City", "Metro Manila", "Amorsolo St, Legazpi Village"),
        ("Philippine General Hospital", "PGH Faculty Medical Arts Building", "Manila", "Metro Manila", "Taft Avenue, Ermita"),
        ("Asian Hospital and Medical Center", "Alabang Medical Clinic", "Muntinlupa City", "Metro Manila", "2205 Civic Drive, Filinvest City"),
        ("Cardinal Santos Medical Center", "Greenhills Specialty Clinic", "San Juan City", "Metro Manila", "10 Wilson St, Greenhills"),
        ("UST Hospital", "UST Doctors Clinic", "Manila", "Metro Manila", "Espana Blvd, Sampaloc"),
        ("Chong Hua Hospital", "Chong Hua Mandaue Annex", "Cebu City", "Cebu", "Don Mariano Cui St, Fuente Osmena"),
        ("Davao Medical School Foundation Hospital", "DMSF Specialty Center", "Davao City", "Davao del Sur", "Medical School Drive, Bajada"),
        ("Capitol Medical Center", "Capitol Annex Clinic", "Quezon City", "Metro Manila", "Scout Magbanua St, Diliman")
    ]

    # 1. 30 "Joshua Tan"s with different middle names
    for idx, mn in enumerate(middle_names_joshua_tan):
        spec_pair = specialties_pool[idx % len(specialties_pool)]
        hosp_tuple = hospitals_pool[idx % len(hospitals_pool)]
        contact_num = f"0917123{current_id:04d}"
        email_addr = f"dr.joshua.{mn.lower().replace(' ', '')}.tan@stlukes.com.ph"
        birth_year = 1975 + (idx % 15)
        dob = f"{birth_year}-{(idx % 12) + 1:02d}-{(idx % 28) + 1:02d}"

        records.append({
            "id": f"HCP-{current_id}",
            "name": f"Dr. Joshua {mn} Tan, M.D., FPCP",
            "first_name": "Joshua",
            "middle_name": mn,
            "last_name": "Tan",
            "canonical_name": f"JOSHUA {mn.upper()} TAN",
            "specialty": spec_pair[0],
            "sub_specialty": spec_pair[1],
            "hcp_type": "Consultant",
            "practice": "Prescribing",
            "hospital": hosp_tuple[0],
            "secondary_hospital": hosp_tuple[1],
            "address": hosp_tuple[4],
            "city": hosp_tuple[2],
            "province": hosp_tuple[3],
            "contact": contact_num,
            "email": email_addr,
            "birth_date": dob,
            "account_program": "Abbott Cardiology Care",
            "territory_code": f"TERR-NCR-SOUTH-{(idx % 5) + 1:02d}",
            "status": "VERIFIED_LOCKED",
            "signature_status": "LOCKED_TRUE_ONLY_ONE",
            "has_merge_history": False,
            "encoded_count": 1,
            "specializations": [{
                "specialty": spec_pair[0],
                "sub_specialty": spec_pair[1],
                "type": "Consultant",
                "practice": "Prescribing",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Masterlist Baseline"
            }],
            "workplaces": [{
                "hospital": hosp_tuple[0],
                "secondary_hospital": hosp_tuple[1],
                "city": hosp_tuple[2],
                "province": hosp_tuple[3],
                "address": hosp_tuple[4],
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Masterlist Baseline"
            }],
            "contacts": [contact_num],
            "emails": [email_addr]
        })
        current_id += 1

    # 2. 25 "Joshua Chua"s with different middle names
    for idx, mn in enumerate(middle_names_joshua_chua):
        spec_pair = specialties_pool[(idx + 2) % len(specialties_pool)]
        hosp_tuple = hospitals_pool[(idx + 2) % len(hospitals_pool)]
        contact_num = f"0918234{current_id:04d}"
        email_addr = f"dr.joshua.{mn.lower().replace(' ', '').replace('-', '')}.chua@themedcity.com.ph"
        birth_year = 1978 + (idx % 12)
        dob = f"{birth_year}-{(idx % 12) + 1:02d}-{(idx % 28) + 1:02d}"

        records.append({
            "id": f"HCP-{current_id}",
            "name": f"Dr. Joshua {mn} Chua, M.D.",
            "first_name": "Joshua",
            "middle_name": mn,
            "last_name": "Chua",
            "canonical_name": f"JOSHUA {mn.upper().replace('-', ' ')} CHUA",
            "specialty": spec_pair[0],
            "sub_specialty": spec_pair[1],
            "hcp_type": "Consultant",
            "practice": "Prescribing",
            "hospital": hosp_tuple[0],
            "secondary_hospital": hosp_tuple[1],
            "address": hosp_tuple[4],
            "city": hosp_tuple[2],
            "province": hosp_tuple[3],
            "contact": contact_num,
            "email": email_addr,
            "birth_date": dob,
            "account_program": "Abbott Primary Care",
            "territory_code": f"TERR-NCR-EAST-{(idx % 5) + 1:02d}",
            "status": "VERIFIED_LOCKED",
            "signature_status": "LOCKED_TRUE_ONLY_ONE",
            "has_merge_history": False,
            "encoded_count": 1,
            "specializations": [{
                "specialty": spec_pair[0],
                "sub_specialty": spec_pair[1],
                "type": "Consultant",
                "practice": "Prescribing",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Masterlist Baseline"
            }],
            "workplaces": [{
                "hospital": hosp_tuple[0],
                "secondary_hospital": hosp_tuple[1],
                "city": hosp_tuple[2],
                "province": hosp_tuple[3],
                "address": hosp_tuple[4],
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Masterlist Baseline"
            }],
            "contacts": [contact_num],
            "emails": [email_addr]
        })
        current_id += 1

    # 3. 25 "Maria Dela Cruz"s with different middle names
    for idx, mn in enumerate(middle_names_maria_cruz):
        spec_pair = specialties_pool[(idx + 4) % len(specialties_pool)]
        hosp_tuple = hospitals_pool[(idx + 4) % len(hospitals_pool)]
        contact_num = f"0919345{current_id:04d}"
        email_addr = f"dra.maria.{mn.lower()}.cruz@pgh.gov.ph"
        birth_year = 1980 + (idx % 10)
        dob = f"{birth_year}-{(idx % 12) + 1:02d}-{(idx % 28) + 1:02d}"

        records.append({
            "id": f"HCP-{current_id}",
            "name": f"Dra. Maria {mn} Dela Cruz, FPOGS",
            "first_name": "Maria",
            "middle_name": mn,
            "last_name": "Dela Cruz",
            "canonical_name": f"MARIA {mn.upper()} DE LA CRUZ",
            "specialty": spec_pair[0],
            "sub_specialty": spec_pair[1],
            "hcp_type": "Consultant",
            "practice": "Prescribing",
            "hospital": hosp_tuple[0],
            "secondary_hospital": hosp_tuple[1],
            "address": hosp_tuple[4],
            "city": hosp_tuple[2],
            "province": hosp_tuple[3],
            "contact": contact_num,
            "email": email_addr,
            "birth_date": dob,
            "account_program": "Abbott Women's Health",
            "territory_code": f"TERR-NCR-CENTRAL-{(idx % 5) + 1:02d}",
            "status": "VERIFIED_LOCKED",
            "signature_status": "LOCKED_TRUE_ONLY_ONE",
            "has_merge_history": False,
            "encoded_count": 1,
            "specializations": [{
                "specialty": spec_pair[0],
                "sub_specialty": spec_pair[1],
                "type": "Consultant",
                "practice": "Prescribing",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Masterlist Baseline"
            }],
            "workplaces": [{
                "hospital": hosp_tuple[0],
                "secondary_hospital": hosp_tuple[1],
                "city": hosp_tuple[2],
                "province": hosp_tuple[3],
                "address": hosp_tuple[4],
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Masterlist Baseline"
            }],
            "contacts": [contact_num],
            "emails": [email_addr]
        })
        current_id += 1

    # 4. 20 "Jose Santos"s with different middle names
    for idx, mn in enumerate(middle_names_jose_santos):
        spec_pair = specialties_pool[(idx + 6) % len(specialties_pool)]
        hosp_tuple = hospitals_pool[(idx + 6) % len(hospitals_pool)]
        contact_num = f"0920456{current_id:04d}"
        email_addr = f"dr.jose.{mn.lower()}.santos@asianhospital.com"
        birth_year = 1976 + (idx % 14)
        dob = f"{birth_year}-{(idx % 12) + 1:02d}-{(idx % 28) + 1:02d}"

        records.append({
            "id": f"HCP-{current_id}",
            "name": f"Dr. Jose {mn} Santos, M.D.",
            "first_name": "Jose",
            "middle_name": mn,
            "last_name": "Santos",
            "canonical_name": f"JOSE {mn.upper()} SANTOS",
            "specialty": spec_pair[0],
            "sub_specialty": spec_pair[1],
            "hcp_type": "Consultant",
            "practice": "Both",
            "hospital": hosp_tuple[0],
            "secondary_hospital": hosp_tuple[1],
            "address": hosp_tuple[4],
            "city": hosp_tuple[2],
            "province": hosp_tuple[3],
            "contact": contact_num,
            "email": email_addr,
            "birth_date": dob,
            "account_program": "Abbott Pediatric Care",
            "territory_code": f"TERR-NCR-NORTH-{(idx % 5) + 1:02d}",
            "status": "VERIFIED_LOCKED",
            "signature_status": "LOCKED_TRUE_ONLY_ONE",
            "has_merge_history": False,
            "encoded_count": 1,
            "specializations": [{
                "specialty": spec_pair[0],
                "sub_specialty": spec_pair[1],
                "type": "Consultant",
                "practice": "Both",
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Masterlist Baseline"
            }],
            "workplaces": [{
                "hospital": hosp_tuple[0],
                "secondary_hospital": hosp_tuple[1],
                "city": hosp_tuple[2],
                "province": hosp_tuple[3],
                "address": hosp_tuple[4],
                "added_at": "2026-08-01 09:00:00",
                "added_by": "System Masterlist Baseline"
            }],
            "contacts": [contact_num],
            "emails": [email_addr]
        })
        current_id += 1

    return records

SAMPLE_MASTERLIST = _generate_expanded_masterlist()

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
