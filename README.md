MetriQ

Intelligent Packaged-Commodity Compliance Inspection System

MetriQ is an evidence-first compliance inspection system designed to simplify the inspection of packaged commodities under India's Legal Metrology framework.

It takes package images, extracts relevant declarations, maps the evidence against applicable legal requirements, and produces an explainable compliance decision instead of treating the inspection as a simple OCR task.

---

The Problem

Checking a packaged commodity for compliance involves more than reading the text printed on a package.

An inspector may need to verify:

- Maximum Retail Price (MRP)
- Net quantity
- Manufacturer / packer / importer details
- Country of origin
- Product name
- Manufacturing / packing information
- Best Before / Use By
- Consumer-care information
- Principal Display Panel requirements
- Declaration visibility and legibility
- Sticker-related declarations
- Applicable standard pack sizes
- E-commerce declarations
- Category-specific legal requirements

The challenge becomes harder when different commodities, package types, exemptions and amendments have to be considered.

MetriQ is built to bring these checks into one structured inspection workflow.

---

What MetriQ Does

Package Image
      ↓
OCR & Evidence Extraction
      ↓
Evidence Structuring
      ↓
Conditional Legal Rules
      ↓
Legal Version & Amendment Check
      ↓
Compliance Evaluation
      ↓
Evidence Chain
      ↓
Inspection Report

Instead of simply answering:

«"Was this text detected?"»

the system aims to answer:

«"What was detected, which legal requirement does it relate to, does that requirement apply, and why was the final decision made?"»

---

Key Features

1. Evidence-First Inspection

Every compliance decision is intended to be backed by identifiable evidence extracted from the package.

This makes the system more transparent and easier to review.

2. Legal Rule Matrix

Legal requirements are maintained in a centralized rule matrix containing:

- Rule ID
- Legal provision
- Requirement description
- Applicability
- Required evidence
- Validation logic
- Failure reason

This keeps legal logic separate from the application code.

3. Conditional Rule Engine

Not every requirement applies to every package.

MetriQ evaluates conditions such as:

IF product is imported
→ Country of Origin requirement applies

IF package contains multiple products
→ Component declarations must be checked

IF package is sold through e-commerce
→ Online declarations must be checked

IF sticker is detected
→ Sticker compliance must be evaluated

IF commodity is time-sensitive
→ Best Before / Use By requirement may apply

This prevents the system from treating every missing declaration as an automatic violation.

4. Legal Versioning

The system maintains an amendment registry with effective dates.

An inspection can therefore be evaluated against the legal framework applicable on the inspection date rather than relying on hard-coded rules alone.

5. Explainable Decisions

Each rule produces a structured result:

Rule
Legal Provision
Status
Confidence
Reason

Possible outcomes include:

- "PASS"
- "FAIL"
- "REVIEW"
- "N/A"

6. Principal Display Panel Analysis

The system includes a legal layer for Principal Display Panel requirements, including package geometry and declaration placement.

7. Evidence Chain

The planned evidence-chain layer connects extracted evidence to the corresponding legal decision, creating an auditable path from:

Image → Evidence → Rule → Decision

8. Compliance Scoring

The engine calculates an overall compliance score and status based on applicable rules.

---

Current Legal Coverage

The current rule matrix includes checks for:

Rule ID| Area
PCR-01| Manufacturer / Packer / Importer
PCR-02| Country of Origin
PCR-03| Common / Generic Name
PCR-04| Multiple Product Declaration
PCR-05| Net Quantity
PCR-06| Manufacturing / Packing Date
PCR-07| Best Before / Use By
PCR-08| MRP
PCR-09| Consumer Care
PCR-10| Standard Pack Size
PCR-11| Principal Display Panel
PCR-12| Declaration Visibility
PCR-13| Sticker Compliance
PCR-14| E-Commerce Declarations
PCR-15| Category-Specific Requirements
PCR-16| PDP Area

The legal layer is designed so additional rules and amendments can be added without restructuring the entire application.

---

Technology Stack

Core

- Python
- Rule-based compliance engine
- Structured evidence model

Planned / Integrated Components

- OCR
- Image processing
- Evidence extraction
- Legal rule engine
- Amendment/version management
- Evidence chain
- Compliance report generation

---

Project Structure

compliance_engine/
│
├── main.py
├── rules.py
├── models.py
├── evidence.py
├── evidence_chain.py
├── ocr.py
│
└── legal/
    ├── legal_matrix.py
    ├── amendments.py
    ├── versions.py
    └── conditions.py

---

Design Philosophy

Evidence before decision.

MetriQ is not designed to blindly trust an OCR result.

The intended decision pipeline is:

DETECT
  ↓
VERIFY
  ↓
APPLY LEGAL CONDITION
  ↓
EVALUATE
  ↓
EXPLAIN

Low-confidence or ambiguous evidence can be routed for REVIEW rather than forcing an unreliable automatic decision.

---

Example Decision

A simplified inspection may produce:

MRP
Rule: PCR-08
Status: PASS
Confidence: 0.98

Legal Provision:
Rule 6(1)(e)

Reason:
Required declaration found with sufficient confidence.

While another requirement could produce:

Country of Origin
Rule: PCR-02
Status: N/A

Reason:
This requirement is not applicable to the inspected commodity.

This distinction is important because:

Missing evidence ≠ legal violation when the requirement itself does not apply.

---

Why MetriQ?

Traditional inspection can involve manually reading packages, checking multiple requirements and referring to changing legal provisions.

MetriQ aims to reduce that workload by combining:

Computer Vision + OCR + Evidence + Legal Rules + Explainable Decisions

into a single inspection pipeline.

The goal is not to replace legal authority or human inspectors.

The goal is to provide them with a faster, structured and evidence-backed inspection assistant.

---

Future Scope

MetriQ can be extended with:

- Automated package image analysis
- Advanced OCR
- Multi-image package inspection
- Computer-vision based PDP detection
- Automated declaration localization
- Improved confidence scoring
- Category-specific legal modules
- Digital inspection reports
- Evidence visualization
- Inspector review dashboard
- E-commerce listing inspection
- Continuous legal amendment updates

---

Project Status

🚧 Active Development

The core legal rule engine, legal matrix, amendment registry, version resolver and conditional applicability layer are currently being developed as part of the SIH prototype.

---

Built For

Smart India Hackathon 2026

Problem Statement: Intelligent Packaged-Commodity Compliance Inspection System

---

MetriQ

Inspect with evidence. Decide with rules. Explain every result.