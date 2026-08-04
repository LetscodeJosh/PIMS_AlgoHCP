"""
Generate Comprehensive Technical Discussion PDF on the Probabilistic ML Model & Pipeline.
Uses ReportLab to create a beautifully formatted PDF document.
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
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0EA5E9'),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=14,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0EA5E9'),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F1F5F9'),
        borderColor=colors.HexColor('#CBD5E1'),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=8
    )

    story = []

    # Title Banner
    story.append(Paragraph("TECHNICAL SPECIFICATION & DISCUSSION REPORT", subtitle_style))
    story.append(Paragraph("Probabilistic Machine Learning Model & Entity Resolution Pipeline for Healthcare Professional (HCP) Deduplication", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0EA5E9"), spaceAfter=15))

    # Executive Overview
    story.append(Paragraph("1. Executive Overview & Problem Context", h1_style))
    story.append(Paragraph(
        "In healthcare CRM platforms (such as PIMS), unique identifiers like mandatory government License IDs (PRC License Number) or exact Birthdates are often uncollectible or unavailable during mobile field entry by Medical Representatives (MedReps). Standard deterministic database matching fails in these scenarios because variations in doctor names (e.g., <i>Dr. Santa Maria Cruz</i> vs. <i>Dr. St. Maria Cruz</i> vs. <i>Dr. Santa M. Cruz, M.D.</i>), medical specialties, and hospital titles create false negatives or massive record duplications.",
        body_style
    ))
    story.append(Paragraph(
        "To solve this problem seamlessly without requiring rigid exact-string matches, the system implements a <b>Weighted Multi-Attribute Probabilistic Machine Learning Model</b> coupled with a non-linear <b>Sigmoid Neural Calibration Engine</b>. This technical document provides an in-depth breakdown of how the machine learning model works, its mathematical foundations, dynamic feature scaling, and the step-by-step end-to-end execution pipeline.",
        body_style
    ))

    # Architectural Model Mechanics
    story.append(Paragraph("2. Deep Dive: Machine Learning Model Architecture & Mechanics", h1_style))
    story.append(Paragraph(
        "The machine learning model operates as a <b>Probabilistic Supervised Linkage Classifier</b> calibrated via a non-linear Logistic Sigmoid activation function. Instead of evaluating fields in isolation, the model extracts a high-dimensional feature vector across all input fields, normalizes field importance weights dynamically, and computes a calibrated match probability percentage <i>P(Duplicate | X)</i> between 0.0% and 100.0%.",
        body_style
    ))

    # Mathematical Formula Table Box
    math_text = """
    <b>Mathematical Model Equations:</b><br/><br/>
    <b>1. Linear Feature Vector Aggregation:</b><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;<i>S_raw = &Sigma; ( w_i &middot; s_i )</i> &nbsp;&nbsp;&nbsp;&nbsp; where &Sigma; w_i = 1.0, &nbsp; s_i &isin; [0, 1]<br/><br/>
    <b>2. Logit Log-Odds Transformation (z-score):</b><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;<i>z = 6.5 &middot; ( S_raw - 0.52 )</i><br/><br/>
    <b>3. Sigmoid Neural Probability Calibration:</b><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;<i>P(Match | X) = 1.0 / ( 1.0 + e<sup>-z</sup> )</i><br/><br/>
    <b>4. Output Percentage Confidence Score:</b><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;<i>Confidence % = round( P(Match | X) &middot; 100, 1 )</i>
    """
    story.append(Paragraph(math_text, code_style))

    story.append(Paragraph("Key Pointers of the ML Model:", h2_style))
    story.append(Paragraph("• <b>Sigmoid Curve Smoothing:</b> Linear weighted sums often create abrupt threshold jumps. The sigmoid function maps scores near the 50% decision boundary onto a smooth, realistic probability curve.", bullet_style))
    story.append(Paragraph("• <b>Multi-Metric Feature Extraction:</b> Uses Jaro-Winkler string distance, Soundex 4-character phonetic encoding, Token-Set Jaccard indices, and edit distance ratios simultaneously.", bullet_style))
    story.append(Paragraph("• <b>Dynamic Weight Normalization:</b> Automatically redistributes attribute weights when optional fields (e.g., secondary clinic, email, street address) are present or absent.", bullet_style))

    # System Field Feature Matrix Table
    story.append(Paragraph("3. Multi-Attribute Field Weight Allocation Matrix", h1_style))
    table_data = [
        [Paragraph("<b>Attribute Field</b>", body_style), Paragraph("<b>Base Weight</b>", body_style), Paragraph("<b>Algorithmic Metric Used</b>", body_style), Paragraph("<b>Matching Function</b>", body_style)],
        [Paragraph("Doctor Full Name", body_style), Paragraph("40.0%", body_style), Paragraph("Jaro-Winkler + Soundex + Token-Set", body_style), Paragraph("Title stripping, 'St.'/'Santa' mapping", body_style)],
        [Paragraph("Primary Specialty", body_style), Paragraph("20.0%", body_style), Paragraph("Token Overlap + Jaro-Winkler", body_style), Paragraph("Medical term synonym overlap", body_style)],
        [Paragraph("Primary Hospital", body_style), Paragraph("20.0%", body_style), Paragraph("Institutional Jaro-Winkler", body_style), Paragraph("Abbreviation mapping ('Hosp' -> 'Hospital')", body_style)],
        [Paragraph("City / Municipality", body_style), Paragraph("10.0%", body_style), Paragraph("Jaro-Winkler Distance", body_style), Paragraph("Geographic location similarity", body_style)],
        [Paragraph("Contact Number", body_style), Paragraph("5.0%", body_style), Paragraph("Numeric Digit Extractor", body_style), Paragraph("Exact & 7-digit suffix match", body_style)],
        [Paragraph("Secondary Hospital", body_style), Paragraph("5.0% (Optional)", body_style), Paragraph("Token Jaro-Winkler", body_style), Paragraph("Secondary clinic alignment", body_style)],
        [Paragraph("Street Address", body_style), Paragraph("5.0% (Optional)", body_style), Paragraph("Normalized Edit Ratio", body_style), Paragraph("Barangay/Street text distance", body_style)],
        [Paragraph("Email Address", body_style), Paragraph("5.0% (Optional)", body_style), Paragraph("Exact / Domain Jaro-Winkler", body_style), Paragraph("Handle & domain similarity", body_style)]
    ]

    t = Table(table_data, colWidths=[110, 75, 160, 185])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Page Break for Pipeline Section
    story.append(PageBreak())

    # Step-by-Step Pipeline
    story.append(Paragraph("4. Precise Step-by-Step Execution Pipeline", h1_style))
    story.append(Paragraph("The system executes a deterministic 6-stage end-to-end data processing pipeline for every candidate doctor record entered by a MedRep or submitted via REST API:", body_style))

    pipeline_stages = [
        ("Stage 1: Multi-Field Ingestion & Field Capture", 
         "The user enters doctor details across all fields in the UI (or via mobile API). Form input fields include Name, Specialty, Primary Hospital, Secondary Clinic, Street Address, City, Contact, and Email. Input change listeners trigger real-time background detection automatically as fields are typed."),

        ("Stage 2: Text Standardization & Honorific Normalization", 
         "Raw text undergoes cleanup in <b>normalizer.py</b>: Medical titles (<i>Dr., Dra., M.D., FPCP, Doc</i>) are detected and stripped. Philippine geographic/cultural honorifics and abbreviations are expanded using canonical dictionary rules (e.g., <i>'St.' / 'Sta.' &rarr; 'SANTA'</i>, <i>'Sto.' &rarr; 'SANTO'</i>, <i>'Ma.' &rarr; 'MARIA'</i>, <i>'Dela' &rarr; 'DE LA'</i>, <i>'Jr.' &rarr; 'JUNIOR'</i>)."),

        ("Stage 3: Multi-Algorithmic Feature Vector Generation", 
         "The engine evaluates candidate attributes against every master record using parallel distance metrics: 1) Jaro-Winkler calculates string distance; 2) Soundex converts surnames to 4-character phonetic keys to capture sound-alike surnames (e.g., <i>Cruz</i> vs. <i>Kruz</i>); 3) Token-Set Ratio checks token reordering; 4) Digit extractor cleans phone numbers."),

        ("Stage 4: Dynamic Attribute Weight Normalization", 
         "The scorer checks which optional fields (secondary clinic, street address, email) are supplied. Active attribute weights are dynamically normalized so that total weight equals exactly 1.0 (100.0%). Individual field similarity scores <i>s_i</i> are assigned granular match status tags: <b>EXACT_MATCH</b> (&ge;95%), <b>HIGH_FUZZY_MATCH</b> (70%-94%), <b>PARTIAL_MATCH</b> (40%-69%), or <b>NO_MATCH</b> (<40%)."),

        ("Stage 5: ML Probabilistic Inference & Sigmoid Calibration", 
         "The linear sum <i>S_raw</i> is calculated and passed into the logit calibration function <i>z = 6.5 &middot; (S_raw - 0.52)</i>. The Sigmoid activation transforms <i>z</i> into the calibrated confidence percentage score <i>P(Match | X)</i>."),

        ("Stage 6: Decision Tier Routing & Workflow Action Logic", 
         "The calculated percentage score determines system action according to strict business logic:<br/>" +
         "• <b>High Confidence Tier (&ge; 88.0%):</b> Auto-merges or fast-track links record to existing HCP Profile.<br/>" +
         "• <b>Medium / 50-50 Match Tier (50.0% - 87.9%):</b> Triggers the <b>Algorithm Recognizer Pop-Up Detector Modal</b> for MedRep side-by-side comparison, and routes the submission to the <b>Managerial Review & Escalation Queue</b>.<br/>" +
         "• <b>Low Confidence Tier (< 50.0%):</b> Keeps record separate and creates a new distinct HCP Profile.")
    ]

    for title, desc in pipeline_stages:
        story.append(Paragraph(title, h2_style))
        story.append(Paragraph(desc, body_style))
        story.append(Spacer(1, 4))

    # Managerial Review & Escalation Flow Section
    story.append(Paragraph("5. Hierarchical Managerial Escalation Queue & 100% Verified Dictionary", h1_style))
    story.append(Paragraph(
        "When a submission falls into the <b>50-50 Medium Confidence threshold (50% - 87%)</b>, it enters the Managerial Approval Queue. The process workflow enforces a hierarchical audit trail:",
        body_style
    ))
    story.append(Paragraph("1. <b>Level 1 Review (District Sales Manager):</b> The District Manager reviews the submitted candidate against the master candidate record side-by-side.", bullet_style))
    story.append(Paragraph("2. <b>Verified Master Dictionary Reference:</b> The approver can open the <b>100% Verified Canonical Dictionary Drawer</b> to read true benchmark doctor details (official hospitals, verified board certifications, canonical names) before making a decision.", bullet_style))
    story.append(Paragraph("3. <b>Escalation to Higher Position:</b> If the Level 1 Manager does not know the doctor record, they click <b>'Pass / Escalate to Higher Position'</b>. The item ascends to Level 2 (Regional Sales Director / Data Steward) who serves as the final binding approver.", bullet_style))

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
