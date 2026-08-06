"""
Generate Comprehensive Technical Specification & Master Documentation PDF Report for PIMS_AlgoHCP.
Includes detailed problem context, mathematical model mechanics, comprehensive fix history, and mobile integration blueprint.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)

OUTPUT_PDF_PATH = "/Users/cig-it/Downloads/PIMS_AlgoHCP/PIMS_AlgoHCP_ML_Model_Technical_Discussion.pdf"
ARTIFACT_PDF_PATH = "/Users/cig-it/.gemini/antigravity-ide/brain/42871c9e-c60c-41a2-9992-a31c3cd61ec1/PIMS_AlgoHCP_ML_Model_Technical_Discussion.pdf"

def create_technical_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF_PATH,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0EA5E9'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=5
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#0EA5E9'),
        spaceBefore=8,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F1F5F9'),
        borderColor=colors.HexColor('#CBD5E1'),
        borderWidth=0.5,
        borderPadding=5,
        spaceAfter=6
    )

    story = []

    # Title Banner
    story.append(Paragraph("SYSTEM MASTER DOCUMENTATION & TECHNICAL SPECIFICATION REPORT", subtitle_style))
    story.append(Paragraph("PIMS_AlgoHCP: Multi-Attribute Entity Resolution, Digital Signatures, and Managerial Verification Architecture", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0EA5E9"), spaceAfter=12))

    # Executive Overview & Problem Context
    story.append(Paragraph("1. Executive Overview & Business Problem Context", h1_style))
    story.append(Paragraph(
        "In healthcare CRM platforms (such as PIMS), unique identifiers like mandatory government License IDs (PRC License Number) or exact Birthdates are often uncollectible due to privacy regulations and mobile field constraints. Standard deterministic database matching fails because variations in doctor names (e.g., <i>Dr. Santa Maria Cruz</i> vs. <i>Dr. St. Maria Cruz</i> vs. <i>Dr. Santa M. Cruz, M.D.</i>), medical specialties, and hospital titles create false negatives or massive record duplications.",
        body_style
    ))
    story.append(Paragraph(
        "To solve this problem seamlessly, the system implements a <b>Weighted Multi-Attribute Probabilistic Machine Learning Engine</b> coupled with a non-linear <b>Sigmoid Neural Calibration Engine</b>, interactive <b>Digital Signature Pads</b>, and a <b>Hierarchical Managerial Approval Portal</b>. This master document provides a comprehensive technical breakdown of how the engine works, mathematical model mechanics, historical fixes implemented, and the mobile app integration blueprint.",
        body_style
    ))

    # Architectural Model Mechanics
    story.append(Paragraph("2. Mathematical Model Mechanics & Calibrated Sigmoid Curve", h1_style))
    story.append(Paragraph(
        "The machine learning model operates as a <b>Probabilistic Supervised Linkage Classifier</b> calibrated via a non-linear Logistic Sigmoid activation function. Instead of evaluating fields in isolation, the model extracts a high-dimensional feature vector across all input fields, normalizes field importance weights dynamically, and computes a calibrated match probability percentage <i>P(Match | X)</i> between 0.0% and 100.0%.",
        body_style
    ))

    math_text = """
    <b>Mathematical Model Equations:</b><br/>
    1. Linear Weighted Feature Score: <i>S_raw = &Sigma; ( w_i &middot; s_i )</i> where &Sigma; w_i = 1.0, s_i &isin; [0, 1]<br/>
    2. Logit Transformation (z-score): <i>z = 6.5 &middot; ( S_raw - 0.52 )</i><br/>
    3. Sigmoid Neural Probability Calibration: <i>P(Match | X) = 1.0 / ( 1.0 + e<sup>-z</sup> )</i><br/>
    4. Output Percentage Confidence Score: <i>Confidence % = round( P(Match | X) &middot; 100, 1 )</i>
    """
    story.append(Paragraph(math_text, code_style))

    # System Field Feature Matrix Table
    story.append(Paragraph("3. Multi-Attribute Field Weight Allocation Matrix", h1_style))
    table_data = [
        [Paragraph("<b>Attribute Field</b>", body_style), Paragraph("<b>Weight</b>", body_style), Paragraph("<b>Algorithmic Metric</b>", body_style), Paragraph("<b>Matching Function</b>", body_style)],
        [Paragraph("Doctor Full Name", body_style), Paragraph("36.4%", body_style), Paragraph("Jaro-Winkler + Soundex + Token-Set", body_style), Paragraph("Title stripping, 'St.'/'Santa' mapping", body_style)],
        [Paragraph("Primary Specialty", body_style), Paragraph("18.2%", body_style), Paragraph("Token Overlap + Jaro-Winkler", body_style), Paragraph("Medical term synonym overlap", body_style)],
        [Paragraph("Primary Hospital", body_style), Paragraph("18.2%", body_style), Paragraph("Institutional Jaro-Winkler", body_style), Paragraph("Abbreviation mapping ('Hosp' -> 'Hospital')", body_style)],
        [Paragraph("City / Municipality", body_style), Paragraph("9.1%", body_style), Paragraph("Jaro-Winkler Distance", body_style), Paragraph("Geographic location similarity", body_style)],
        [Paragraph("Secondary Hospital", body_style), Paragraph("4.5%", body_style), Paragraph("Token Jaro-Winkler", body_style), Paragraph("Secondary clinic alignment", body_style)],
        [Paragraph("Street Address", body_style), Paragraph("4.5%", body_style), Paragraph("Normalized Edit Ratio", body_style), Paragraph("Barangay/Street text distance", body_style)],
        [Paragraph("Contact Number", body_style), Paragraph("4.5%", body_style), Paragraph("Numeric Digit Extractor", body_style), Paragraph("Exact & 7-digit suffix match", body_style)],
        [Paragraph("Email Address", body_style), Paragraph("4.5%", body_style), Paragraph("Exact / Domain Jaro-Winkler", body_style), Paragraph("Handle & domain similarity", body_style)],
        [Paragraph("Doctor Signature", body_style), Paragraph("Mandatory", body_style), Paragraph("Base64 Canvas PNG Extractor", body_style), Paragraph("Immutable True-Only-One Signature Lock", body_style)]
    ]

    t = Table(table_data, colWidths=[110, 60, 160, 210])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    story.append(PageBreak())

    # Section 4: History of System Improvements & Fixes
    story.append(Paragraph("4. Comprehensive History of System Improvements & Resolved Fixes", h1_style))
    story.append(Paragraph("The system underwent rigorous architectural refinement to achieve production-grade stability, security, and multi-device usability:", body_style))

    fixes = [
        ("Fix 1: Dynamic Origin API Resolution (Multi-Device Access)",
         "Previously, hardcoded API endpoints ('http://localhost:8080') broke submissions when accessed from external LAN IPs (e.g., 192.168.0.96). Updated client JavaScript (<code>web/app.js</code>) to dynamically resolve <code>API_BASE = window.location.origin + '/api'</code>, allowing phones, tablets, and LAN computers to connect seamlessly."),

        ("Fix 2: Mandatory Field Validation & Warning Pop-Up",
         "Enforced strict mandatory validation across all 8 doctor fields + Digital Signature. If any field is blank, client-side submission is blocked, empty inputs outline in red, and a prominent <b>⚠️ Mandatory Fields Missing Modal</b> pops up. Backend <code>server.py</code> rejects incomplete submissions with <code>HTTP 400 Bad Request</code>."),

        ("Fix 3: 8 Interactive Philippine Demo Presets & Expanded Dataset",
         "Built 8 interactive preset buttons on the UI to test all confidence tiers and string normalization variants: High Match (≥88%), 50-50 Match (50-87%), Low Match (<50%), Honorific Shift (Dr./Dra.), Surname Compound (Dela/De La), Santo/Sto. Shift, Suffix Shift (Jr./Junior), and Delos/De Los Compound Shift."),

        ("Fix 4: Unthrottled Real-Time API Engine",
         "Removed API rate-limiting restrictions to allow smooth, uninhibited real-time background duplicate detection as MedReps type rapidly into text fields across multiple mobile devices."),

        ("Fix 5: Standalone Microservice Shield & Security Guard (security.py)",
         "Added <code>hcp_matcher/security.py</code> providing signed HMAC-SHA256 JWT Bearer tokens and Cython C-extension compilation readiness (.so/.pyd bytecode), protecting algorithm weights and master records from unauthorized reverse-engineering or hacking."),

        ("Fix 6: New Doctor Canonical Verification Queue & Dictionary Auto-Commit",
         "When a new doctor (<50% score) is encoded, the system creates a draft profile (<code>PENDING_MANAGERIAL_VERIFICATION</code>) and routes it to the Managerial Portal. Upon manager approval (<code>VERIFY_AND_LOCK_CANONICAL</code>), the doctor profile is locked and auto-committed to the <b>100% Verified Master Dictionary</b> (<code>DICT-500X</code>)."),

        ("Fix 7: Doctor Digital Signature Pad & Immutable True-Only-One Signature Lock",
         "Integrated an interactive HTML5/Touch Digital Signature Pad. Once verified by a Manager, the doctor's signature is locked as <code>LOCKED_TRUE_ONLY_ONE</code>. It becomes permanent and immutable, preventing tampering or unauthorized overwriting by future MedRep submissions."),

        ("Fix 8: Socket Rebind Fix (allow_reuse_address = True)",
         "Resolved <code>OSError: [Errno 48] Address already in use</code> during server restarts by configuring <code>socketserver.TCPServer.allow_reuse_address = True</code> in <code>server.py</code>.")
    ]

    for title, desc in fixes:
        story.append(Paragraph(title, h2_style))
        story.append(Paragraph(desc, body_style))
        story.append(Spacer(1, 3))

    # Section 5: Step-by-Step Pipeline
    story.append(Paragraph("5. Step-by-Step End-to-End Execution Pipeline", h1_style))
    pipeline_steps = [
        "1. <b>Field Ingestion:</b> MedRep encodes 8 mandatory fields + draws digital signature on canvas.",
        "2. <b>Real-Time Scan:</b> Input change listeners trigger debounced background REST call to <code>/api/match</code>.",
        "3. <b>Text Normalization:</b> <code>normalizer.py</code> strips titles (Dr., M.D.) and expands Philippine abbreviations (St. ↔ Santa, Dela ↔ De La).",
        "4. <b>Feature Calculation:</b> Parallel Jaro-Winkler, Soundex 4-character phonetic key, and Token-Set Jaccard ratios computed.",
        "5. <b>Sigmoid Calibration:</b> Raw score passed through <i>z = 6.5 · (S_raw - 0.52)</i> activation function to produce calibrated % score.",
        "6. <b>Decision Routing:</b> High matches (≥88%) auto-merge; Medium matches (50-87%) & New Doctors (<50%) route to Managerial Verification Queue with Immutable Signature Lock."
    ]
    for step in pipeline_steps:
        story.append(Paragraph(step, bullet_style))

    # Section 6: Mobile Integration Blueprint
    story.append(Paragraph("6. HCP Mobile App Integration Blueprint", h1_style))
    story.append(Paragraph(
        "The backend microservice directly maps to the Flutter mobile app model (<code>HcpProfileSubmission</code> in <code>lib/models/submission.dart</code>):",
        body_style
    ))
    story.append(Paragraph("• <code>hcpFullName</code> / (<code>firstName</code>, <code>lastName</code>) &rarr; Doctor Full Name (36.4% Weight)", bullet_style))
    story.append(Paragraph("• <code>specialties[0].specialtyName</code> &rarr; Primary Specialty (18.2% Weight)", bullet_style))
    story.append(Paragraph("• <code>workplaces[0].workplaceName</code> &rarr; Primary Hospital (18.2% Weight)", bullet_style))
    story.append(Paragraph("• <code>cityMunicipality</code> / <code>provinceName</code> &rarr; City Location (9.1% Weight)", bullet_style))
    story.append(Paragraph("• <code>consentSignature</code> &rarr; Base64 Digital Signature PNG (Immutable True-Only-One Lock)", bullet_style))

    # Build PDF
    doc.build(story)
    print(f"PDF generated successfully at {OUTPUT_PDF_PATH}")

    # Copy to artifact directory
    os.makedirs(os.path.dirname(ARTIFACT_PDF_PATH), exist_ok=True)
    with open(OUTPUT_PDF_PATH, "rb") as fsrc:
        with open(ARTIFACT_PDF_PATH, "wb") as fdst:
            fdst.write(fsrc.read())
    print(f"Artifact copy created at {ARTIFACT_PDF_PATH}")

if __name__ == "__main__":
    create_technical_pdf()
