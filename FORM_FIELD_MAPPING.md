# CMS-1500 Professional Claim Form Field Mapping

This document maps the extracted PDF data to the form fields on the Professional Claim page.

## Form Fields and Data Mapping

### General Info Section

#### Field 26: Patient's Account Number*
- **Form Field**: `profClaim.patCtrlNbr`
- **Extracted Data Source**: 
  - `billing_info.patient_account_number` (Primary)
  - `patient_info.account_number` (Fallback)
- **Example Value**: `PAT3311`
- **Required**: Yes
- **Max Length**: 20

#### Statement Dates*
- **Form Field From**: `profClaim.statementStartDate`
- **Form Field To**: `profClaim.statementEndDate`
- **Extracted Data Source**: 
  - `service_lines[].date_from` (earliest date)
  - `service_lines[].date_to` (latest date)
- **Format**: MM/DD/YYYY
- **Required**: Yes
- **Example**: From: `11/20/2025`, To: `11/20/2025`

#### Field 14: Date of current Illness, Injury, Pregnancy (LMP)
- **Form Field Qualifier**: `professionalClaim.professionalClaimDate.illnessLmpQual`
- **Form Field Date**: `professionalClaim.professionalClaimDate.illnessImpDate`
- **Extracted Data Source**: 
  - `patient_info.condition_related_to_employment` (if YES, use Current Illness or Injury)
  - `patient_info.condition_related_to_auto` (if YES, use Accident)
  - `patient_info.condition_related_to_other` (if YES, use Current Illness or Injury)
- **Options**: 
  - `431` - Current Illness or Injury
  - `484` - Last Menstrual Period
- **Status**: SKIP FOR NOW (Leave empty/default)
- **Required**: No

#### Field 15: Other Date
- **Form Field Qualifier**: `professionalClaim.professionalClaimDate.otherDateQual`
- **Form Field Date**: `professionalClaim.professionalClaimDate.otherDateValue`
- **Extracted Data Source**: TBD
- **Options**: 
  - `454` - Initial Treatment
  - `304` - Latest Visit or Consultation
  - `453` - Acute Manifestion of a Chronic Condition
  - `439` - Accident
  - `455` - Last X-ray
  - `471` - Prescription
  - `090` - Report Start (Assumed Care Date)
  - `091` - Report End (Relinquished Care Date)
  - `444` - First Visit or Consult
- **Status**: SKIP FOR NOW (Leave empty/default)
- **Required**: No

#### Field 18: Hospitalization
- **Form Field From**: `professionalClaim.professionalClaimDate.hospitalizedFrom`
- **Form Field To**: `professionalClaim.professionalClaimDate.hospitalizedTo`
- **Extracted Data Source**: TBD
- **Format**: MM/DD/YYYY
- **Status**: SKIP FOR NOW (Leave empty/default)
- **Required**: No

#### Field 19a: Additional Claim Information
- **Form Field**: `professionalClaim.remarks`
- **Extracted Data Source**: TBD
- **Current Value**: `TEST123456` (Dummy data for testing)
- **Max Length**: 80
- **Required**: No

#### Field 20: Outside Lab?
- **Form Field**: `professionalClaim.professionalClaimCondition.outsideLab`
- **Form Field Amount**: `professionalClaim.professionalClaimCondition.outsideLabAmount`
- **Extracted Data Source**: 
  - `billing_info.outside_lab` (YES/NO)
  - `billing_info.outside_lab_charges` (if YES)
- **Options**: 
  - `true` - Yes
  - `false` - No (default)
- **Status**: SKIP FOR NOW (Leave as default "No")
- **Required**: No

#### Referral Number
- **Form Field**: `referralNumber`
- **Extracted Data Source**: TBD
- **Current Value**: `REF123456789` (Dummy data for testing)
- **Max Length**: 12
- **Required**: No

#### Field 23a: Prior Authorization Number
- **Form Field**: `professionalClaim.priorAuthorization`
- **Extracted Data Source**: TBD (May be in form data)
- **Current Value**: `AUTH123456789` (Dummy data for testing)
- **Max Length**: 16
- **Required**: No

#### Field 23b: CLIA Number
- **Form Field**: `professionalClaim.cliaNbr`
- **Extracted Data Source**: TBD
- **Current Value**: `CLIA123456789` (Dummy data for testing)
- **Max Length**: 16
- **Required**: No

#### Field 29: Amount Paid
- **Form Field**: `professionalClaim.amountPaid`
- **Extracted Data Source**: 
  - `billing_info.amount_paid` (format: $X.XX)
- **Current Value**: `0.00` (Dummy data for testing)
- **Format**: XXXX.XX
- **Required**: No

## Fields to Skip (Leave Empty/Default)

1. **Date of current Illness, Injury, Pregnancy (LMP)** - Field 14
2. **Other Date** - Field 15
3. **Hospitalization** - Field 18
4. **Outside Lab?** - Field 20 (Keep as default "No")

## Fields with Dummy Data (For Testing)

1. **Additional Claim Information** - `TEST123456`
2. **Referral Number** - `REF123456789`
3. **Prior Authorization Number** - `AUTH123456789`
4. **CLIA Number** - `CLIA123456789`
5. **Amount Paid** - `0.00`

## Fields Filled from Extracted Data

1. **Patient's Account Number** - From `billing_info.patient_account_number`
2. **Statement Dates (From/To)** - From `service_lines[].date_from` and `service_lines[].date_to`

## Next Steps

1. Map remaining fields to extracted data sources
2. Replace dummy data with actual extracted values
3. Handle date format conversions
4. Add validation for required fields
5. Handle multiple service lines for date ranges


