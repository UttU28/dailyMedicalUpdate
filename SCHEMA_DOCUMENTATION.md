# CMS-1500 Claim Data Schema Documentation

## Overview

This document describes the comprehensive JSON schema for extracting and structuring data from CMS-1500 Health Insurance Claim Forms using Ollama OCR or other extraction methods.

## Schema Files

1. **`sample.json`** - Complete example with all fields populated
2. **`claim_data_schema.json`** - JSON Schema for validation
3. **`SCHEMA_DOCUMENTATION.md`** - This documentation file

## Architecture

### Design Principles

1. **Dual Format Storage**: Each field stores both `raw` (original extracted value) and `formatted` (normalized/cleaned value)
2. **Structured Data**: Complex fields (names, addresses, dates) are broken down into components
3. **Confidence Scoring**: OCR confidence scores are included for quality assessment
4. **Validation Metadata**: Built-in validation results and error tracking
5. **Extensibility**: Schema supports optional fields and future additions

### Key Features

- **Raw + Processed Data**: Preserves original OCR output while providing cleaned data
- **Type Safety**: JSON Schema enforces data types and patterns
- **Confidence Tracking**: OCR confidence scores for quality control
- **Error Handling**: Validation section tracks missing fields and errors
- **Multi-Provider Support**: Handles Referring, Rendering, Billing, and Service Facility providers

## Schema Structure

### 1. Metadata (`metadata`)

Tracks extraction process information:
- `extraction_date`: When the extraction occurred
- `extraction_method`: OCR method used (ollama_ocr, pymupdf, etc.)
- `pdf_filename`: Source PDF file name
- `form_version`: CMS-1500 form version
- `confidence_score`: Overall extraction confidence (0-1)
- `extraction_notes`: Any notes or warnings from extraction

### 2. Form Information (`form_info`)

Basic form identification:
- `carrier`: Insurance carrier name
- `form_type`: Form type (e.g., "CMS-1500 (02-12)")
- `form_number`: Form number if present

### 3. Patient Information (`patient_info`)

Complete patient demographics:
- `name`: Structured name (last, first, middle, full)
- `date_of_birth`: Date with components (raw, formatted, month, day, year)
- `sex`: Gender (M/F)
- `address`: Full address breakdown
- `telephone`: Phone number with components
- `relationship_to_insured`: Relationship type
- `condition_related_to`: Employment/accident flags

### 4. Insured Information (`insured_info`)

Primary insured person details:
- `id_number`: Member/ID number with type
- `name`: Full name structure
- `date_of_birth`: Date components
- `address`: Address details
- `policy_group_number`: Policy/group number

### 5. Provider Information (`provider_info`)

Four provider types with complete details:

#### Referring Provider
- `qualifier`: Provider qualifier code (DN, etc.)
- `name`: Provider name
- `id`: Provider ID with type
- `npi`: National Provider Identifier

#### Rendering Provider
- `npi`: NPI number
- `taxonomy`: Taxonomy code
- `name`: Provider name
- `id`: Provider ID with qualifier

#### Billing Provider
- `name`: Provider name
- `npi`: NPI number
- `taxonomy`: Taxonomy code
- `address`: Full address
- `phone`: Phone number
- `federal_tax_id`: Tax ID (SSN/EIN)

#### Service Facility Location
- `name`: Facility name
- `npi`: Facility NPI
- `taxonomy`: Taxonomy code
- `address`: Facility address

### 6. Diagnosis (`diagnosis`)

Diagnosis codes with ICD indicator:
- `icd_indicator`: ICD version (0=ICD-10, 1=ICD-9)
- `codes`: Array of diagnosis codes
  - `pointer`: Letter pointer (A-L)
  - `code`: Diagnosis code (e.g., "Z00.01")
  - `raw`: Original extracted value
  - `confidence`: OCR confidence score

### 7. Service Lines (`service_lines`)

Array of service line items, each containing:
- `line_number`: Sequential line number
- `dates_of_service`: From/To dates with components
- `place_of_service`: POS code with description
- `procedure_code`: CPT/HCPCS code with modifier
- `diagnosis_pointer`: Diagnosis pointers (A-L)
- `charges`: Charge amount (raw, formatted, numeric)
- `days_units`: Units with type (UN, etc.)
- `amount_paid`: Amount paid if applicable
- `rendering_provider`: Provider NPI and ID
- `confidence`: OCR confidence for this line

### 8. Billing Information (`billing_info`)

Financial and billing details:
- `patient_account_number`: Account number
- `federal_tax_id`: Tax ID with type
- `accept_assignment`: Assignment acceptance flag
- `outside_lab`: Outside lab flag with charges
- `total_charge`: Total charge amount
- `amount_paid`: Amount already paid
- `balance_due`: Calculated balance

### 9. Dates (`dates`)

Additional date fields:
- `current_illness_injury_pregnancy`: Illness date with qualifier
- `other_date`: Other date with qualifier
- `patient_unable_to_work`: Work disability dates
- `hospitalization`: Hospitalization dates

### 10. Additional Information (`additional_info`)

Optional claim information:
- `prior_authorization_number`: Prior auth number
- `clia_number`: CLIA number
- `referral_number`: Referral number
- `resubmission_code`: Resubmission code
- `original_reference_number`: Original ref number
- `additional_claim_information`: Free text field

### 11. Signatures (`signatures`)

Signature information:
- `patient_signature`: Patient signature status
- `insured_signature`: Insured signature status
- `provider_signature`: Provider signature with date

### 12. Validation (`validation`)

Data quality and validation:
- `is_valid`: Overall validation status
- `errors`: Array of validation errors
- `warnings`: Array of warnings
- `missing_fields`: List of missing required fields
- `confidence_threshold`: Minimum confidence threshold

## Data Extraction Workflow

### Using Ollama OCR

1. **PDF Input**: Load PDF file
2. **OCR Processing**: Extract text using Ollama OCR
3. **Field Mapping**: Map extracted text to schema fields
4. **Data Normalization**: Clean and format extracted values
5. **Validation**: Validate against schema
6. **Output**: Generate JSON following schema

### Field Extraction Patterns

#### Dates
- Pattern: `MM/DD/YYYY` or `MM DD YY`
- Normalize to: `MM/DD/YYYY`
- Store components: month, day, year

#### Phone Numbers
- Pattern: Various formats `(XXX)XXX-XXXX`, `XXX-XXX-XXXX`, etc.
- Normalize to: `(XXX)-XXX-XXXX`
- Extract: area_code, number

#### Names
- Pattern: `Last, First Middle`
- Parse into: last_name, first_name, middle_initial
- Store: full_name

#### Addresses
- Pattern: `Street, City, State ZIP`
- Parse into: street, city, state, zip_code
- Validate: State (2 letters), ZIP (5 or 9 digits)

#### Diagnosis Codes
- Pattern: Letter pointer + Code (e.g., "A. Z00.01")
- Extract: pointer (A-L), code value
- Validate: ICD-10 format

#### Service Lines
- Pattern: Tabular data with multiple fields
- Extract: dates, POS, procedure, diagnosis pointers, charges, units
- Validate: All required fields present

## Usage Examples

### Python Validation

```python
import json
import jsonschema

# Load schema
with open('claim_data_schema.json', 'r') as f:
    schema = json.load(f)

# Load extracted data
with open('extracted_data.json', 'r') as f:
    data = json.load(f)

# Validate
try:
    jsonschema.validate(instance=data, schema=schema)
    print("✓ Data is valid")
except jsonschema.exceptions.ValidationError as e:
    print(f"✗ Validation error: {e.message}")
```

### Data Access Patterns

```python
# Access patient name
patient_name = data['patient_info']['name']['full_name']

# Access diagnosis codes
for code in data['diagnosis']['codes']:
    print(f"{code['pointer']}: {code['code']}")

# Access service lines
for line in data['service_lines']:
    charge = line['charges']['amount']
    procedure = line['procedure_code']['code']
    print(f"{procedure}: ${charge}")

# Check validation
if data['validation']['is_valid']:
    print("Data is valid")
else:
    print(f"Errors: {data['validation']['errors']}")
```

## Compatibility

This schema is designed to work with:
- **ex2.pdf**: Multiple service lines, complete provider info
- **ex3.pdf**: Multiple diagnosis codes, various procedure codes
- **example.pdf**: Standard single service line claim

All PDFs should extract to the same schema structure, with optional fields left empty if not present.

## Best Practices

1. **Always store raw values**: Preserve original OCR output for debugging
2. **Normalize consistently**: Use same formatting rules across all extractions
3. **Validate early**: Check data quality during extraction
4. **Track confidence**: Use confidence scores to flag low-quality extractions
5. **Handle missing fields**: Use empty strings or null for missing optional fields
6. **Document exceptions**: Add notes in `extraction_notes` for unusual cases

## Future Enhancements

- Support for ICD-9 codes
- Enhanced validation rules
- Support for additional form versions
- Multi-page form handling
- Image quality assessment
- Automated field correction suggestions
