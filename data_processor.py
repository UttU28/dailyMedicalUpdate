import json
from extract import extractClaimData
from backend import convertExtractedDataToStepFormat


def parseExtractedData(jsonOutput):
    if not jsonOutput:
        return None
    
    try:
        return json.loads(jsonOutput)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON: {e}")
        return None


def formatDataForDisplay(data):
    if not data:
        return False
    
    try:
        print("\nPATIENT INFORMATION:")
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  DOB: {data.get('dob', 'N/A')}")
        print(f"  Sex: {data.get('sex', 'N/A')}")
        print(f"  ID: {data.get('id', 'N/A')}")
        print(f"  Group: {data.get('group', 'N/A')}")
        
        print("\nADDRESS:")
        address = data.get('address', 'N/A')
        city = data.get('city', 'N/A')
        state = data.get('state', 'N/A')
        zipCode = data.get('zipCode', 'N/A')
        print(f"  {address}")
        print(f"  {city}, {state} {zipCode}")
        print(f"  Phone: {data.get('phone', 'N/A')}")
        
        diagnosisCodes = data.get('diagnosis_codes', [])
        if diagnosisCodes:
            print(f"\nDIAGNOSIS CODES ({len(diagnosisCodes)}):")
            for code in diagnosisCodes:
                print(f"  - {code}")
        
        procedures = data.get('procedures', [])
        if procedures:
            print(f"\nPROCEDURES ({len(procedures)}):")
            for i, proc in enumerate(procedures, 1):
                print(f"  {i}. Code: {proc.get('code', 'N/A')}")
                if proc.get('modifier'):
                    print(f"     Modifier: {proc['modifier']}")
                if proc.get('serviceDate'):
                    print(f"     Service Date: {proc['serviceDate']}")
                if proc.get('diagnosisPointer'):
                    print(f"     Diagnosis Pointer: {proc['diagnosisPointer']}")
                if proc.get('charges'):
                    print(f"     Charges: ${proc['charges']:.2f}")
                if proc.get('additionalInfo'):
                    print(f"     Additional Info: {proc['additionalInfo']}")
        
        print("\nFINANCIAL INFORMATION:")
        if data.get('account'):
            print(f"  Account: {data['account']}")
        if data.get('total') is not None:
            print(f"  Total Charge: ${data['total']:.2f}")
        if data.get('paid') is not None:
            print(f"  Amount Paid: ${data['paid']:.2f}")
        print(f"  Signature Date: {data.get('signatureDate', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to format data for display: {e}")
        return False


def extractAndParseClaimData(filepath):
    jsonOutput = extractClaimData(filepath)
    if not jsonOutput:
        return None
    
    return parseExtractedData(jsonOutput)


def processClaimDataForSteps(extractedData):
    try:
        return convertExtractedDataToStepFormat(extractedData)
    except Exception as e:
        print(f"[ERROR] Failed to convert data to step format: {e}")
        return None


def getDataSummary(data):
    if not data:
        return "No data"
    
    name = data.get('name', 'N/A')
    procedures = data.get('procedures', [])
    procedureCount = len(procedures)
    
    return f"{name} - {procedureCount} procedures"
