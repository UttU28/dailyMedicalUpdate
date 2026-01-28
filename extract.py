import re
import json
import sys
import argparse

def extractInsuranceId(line7):
    xPos = line7.find('X')
    if xPos != -1:
        afterX = line7[xPos + 1:].strip()
        idMatch = re.search(r'([A-Z0-9]+)', afterX)
        if idMatch:
            return idMatch.group(1)
    return None

def formatDob(dob):
    if dob and len(dob) == 8:
        return f"{dob[0:2]}/{dob[2:4]}/{dob[4:8]}"
    return dob

def extractPatientInfo(line9):
    dobMatch = re.search(r'(\d{8})', line9)
    if not dobMatch:
        return None, None, None
    
    dob = dobMatch.group(1)
    dobStart = dobMatch.start()
    dobEnd = dobMatch.end()
    
    name = line9[:dobStart].strip()
    
    xMatch = re.search(r'X', line9[dobEnd:])
    if not xMatch:
        return None, None, None
    
    textAfterDob = line9[dobEnd:dobEnd + xMatch.start()]
    spacesBetween = textAfterDob.count(' ')
    
    if spacesBetween <= 3:
        gender = "M"
    else:
        gender = "F"
    
    return name, dob, gender

def extractAddress(line11):
    xPos = line11.find('X')
    if xPos != -1:
        address = line11[:xPos].strip()
        return address
    return None

def extractCityState(line13):
    stateMatch = re.search(r'\b([A-Z]{2})\b', line13)
    if stateMatch:
        state = stateMatch.group(1)
        statePos = stateMatch.start()
        city = line13[:statePos].strip()
        return city, state
    return None, None

def extractZipPhone(line15):
    xPos = line15.find('X')
    if xPos == -1:
        xPos = len(line15)
    
    firstPart = line15[:xPos].strip()
    zipMatch = re.search(r'^(\d{5})', firstPart)
    if zipMatch:
        zipCode = zipMatch.group(1)
        phoneMatch = re.search(r'(\d{3})\s*-?\s*(\d{3})\s*-?\s*(\d{4})', firstPart)
        if phoneMatch:
            phone = f"{phoneMatch.group(1)}-{phoneMatch.group(2)}-{phoneMatch.group(3)}"
            return zipCode, phone
        return zipCode, None
    return None, None

def extractInsurancePolicyNo(line17):
    xPos = line17.find('X')
    if xPos == -1:
        xPos = len(line17)
    
    firstPart = line17[:xPos].strip()
    policyMatch = re.search(r'(\d+)', firstPart)
    if policyMatch:
        return policyMatch.group(1)
    
    afterX = line17[xPos + 1:].strip() if xPos < len(line17) else ""
    if afterX:
        policyMatch = re.search(r'(\d+)', afterX)
        if policyMatch:
            return policyMatch.group(1)
    return None

def isPriorAuthNumber(text):
    priorAuthPattern = re.compile(r'^\d+[A-Z]\d+$')
    return bool(priorAuthPattern.match(text.strip()))

def extractDiagnosisCodes(line37, line38, line39):
    diagnosisCodes = {
        'A': None, 'B': None, 'C': None, 'D': None,
        'E': None, 'F': None, 'G': None, 'H': None,
        'I': None, 'J': None, 'K': None, 'L': None
    }
    
    codeIndex = 0
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    
    if line37:
        line37 = line37.strip()
        codes = re.split(r'\s{2,}', line37)
        codes = [c.strip() for c in codes if c.strip()]
        
        for code in codes[:4]:
            if code and not isPriorAuthNumber(code):
                if codeIndex < len(labels):
                    diagnosisCodes[labels[codeIndex]] = code
                    codeIndex += 1
    
    if line38:
        line38 = line38.strip()
        if line38:
            codes = re.split(r'\s{2,}', line38)
            codes = [c.strip() for c in codes if c.strip()]
            
            for code in codes[:4]:
                if code and not isPriorAuthNumber(code):
                    if codeIndex < len(labels):
                        diagnosisCodes[labels[codeIndex]] = code
                        codeIndex += 1
    
    if line39:
        line39 = line39.strip()
        if line39:
            codes = re.split(r'\s{2,}', line39)
            codes = [c.strip() for c in codes if c.strip()]
            
            for code in codes[:4]:
                if code and not isPriorAuthNumber(code):
                    if codeIndex < len(labels):
                        diagnosisCodes[labels[codeIndex]] = code
                        codeIndex += 1
    
    return diagnosisCodes

def extractProcedures(lines42to54):
    procedures = []
    pendingAdditionalInfo = None
    
    i = 0
    while i < len(lines42to54) and len(procedures) < 6:
        line = lines42to54[i]
        lineStripped = line.strip()
        
        # Check if this is an additional info line (doesn't start with date, has content and "0B R1006")
        if not re.match(r'^\d{8}', lineStripped) and lineStripped and not re.match(r'^\s*$', lineStripped):
            obPattern = re.search(r'0B\s+R\d+', lineStripped)
            if obPattern:
                additionalInfo = lineStripped[:obPattern.start()].strip()
                if additionalInfo and len(additionalInfo) > 0:
                    # Extract only the first two parts (space-separated)
                    parts = additionalInfo.split()
                    if len(parts) >= 2:
                        # Take only first two parts and join them
                        pendingAdditionalInfo = ' '.join(parts[:2])
                    else:
                        # If less than 2 parts, use what we have
                        pendingAdditionalInfo = additionalInfo
                    i += 1
                    continue
        
        # Check if this is a procedure line (starts with date)
        datePattern = re.match(r'^\s*(\d{8})\s+(\d{8})\s+(\d+)', line)
        if datePattern:
            fromDate = datePattern.group(1)
            toDate = datePattern.group(2)
            placeOfService = datePattern.group(3)
            
            line = line.strip()
            parts = re.split(r'\s{2,}', line)
            parts = [p.strip() for p in parts if p.strip()]
            
            if len(parts) >= 3:
                procedureCode = parts[1] if len(parts) > 1 else None
                modifier = None
                diagnosisPointer = None
                charges = None
                
                if len(parts) > 2:
                    part2 = parts[2]
                    if re.match(r'^\d{1,2}$', part2) or re.match(r'^[A-Z]{1,2}\d{1,2}$', part2) or re.match(r'^[A-Z]{2}$', part2):
                        modifier = part2
                        if len(parts) > 3:
                            potentialPointer = parts[3]
                            if re.match(r'^[A-Z]{1,4}$', potentialPointer):
                                diagnosisPointer = potentialPointer
                            if len(parts) > 4:
                                chargePart = parts[4]
                                chargeMatch = re.match(r'^(\d+)\s+(\d{2})', chargePart)
                                if chargeMatch:
                                    dollars = chargeMatch.group(1)
                                    cents = chargeMatch.group(2)
                                    charges = f"{dollars}.{cents}"
                    elif re.match(r'^[A-Z]{1,4}$', part2):
                        diagnosisPointer = part2
                        if len(parts) > 3:
                            chargePart = parts[3]
                            chargeMatch = re.match(r'^(\d+)\s+(\d{2})', chargePart)
                            if chargeMatch:
                                dollars = chargeMatch.group(1)
                                cents = chargeMatch.group(2)
                                charges = f"{dollars}.{cents}"
                
                if procedureCode and re.match(r'^[A-Z0-9]{4,}$', procedureCode):
                    procedure = {
                        'procedureCode': procedureCode,
                        'modifier': modifier,
                        'diagnosisPointer': diagnosisPointer,
                        'charges': charges,
                        'additionalInfo': pendingAdditionalInfo,  # Use pending additional info
                        'fromDate': fromDate,
                        'toDate': toDate,
                        'placeOfService': placeOfService
                    }
                    
                    # Clear pending additional info after using it
                    pendingAdditionalInfo = None
                    
                    procedures.append(procedure)
        
        i += 1
    
    return procedures

def extractPatientAccountAndTotal(line55):
    patientAccountNo = None
    totalCharge = None
    amountPaid = None
    
    if line55:
        line = line55.strip()
        
        patMatch = re.search(r'PAT\w+', line)
        if patMatch:
            patientAccountNo = patMatch.group(0)
        
        parts = re.split(r'\s{2,}', line)
        parts = [p.strip() for p in parts if p.strip()]
        
        for i, part in enumerate(parts):
            if 'PAT' in part:
                if i + 1 < len(parts):
                    nextPart = parts[i + 1]
                    if nextPart == 'X' and i + 2 < len(parts):
                        chargePart = parts[i + 2]
                        chargeMatch = re.match(r'^(\d+)\s+(\d{2})$', chargePart)
                        if chargeMatch:
                            dollars = chargeMatch.group(1)
                            cents = chargeMatch.group(2)
                            totalCharge = f"{dollars}.{cents}"
                            
                            if i + 3 < len(parts):
                                paidPart = parts[i + 3]
                                paidMatch = re.match(r'^(\d+)\s+(\d{2})$', paidPart)
                                if paidMatch:
                                    paidDollars = paidMatch.group(1)
                                    paidCents = paidMatch.group(2)
                                    amountPaid = f"{paidDollars}.{paidCents}"
                            break
    
    return patientAccountNo, totalCharge, amountPaid

def extractSignatureDate(line60):
    if line60:
        line = line60.strip()
        dateMatch = re.search(r'(\d{8})', line)
        if dateMatch:
            return dateMatch.group(1)
    return None

def parseClaimFile(filePath):
    try:
        with open(filePath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) < 17:
            print(f"Error: File {filePath} has fewer than 17 lines")
            return None
        
        line7 = lines[6]
        insuranceId = extractInsuranceId(line7)
        
        line9 = lines[8]
        name, dob, gender = extractPatientInfo(line9)
        formattedDob = formatDob(dob) if dob else None
        
        line11 = lines[10]
        address = extractAddress(line11)
        
        line13 = lines[12]
        city, state = extractCityState(line13)
        
        line15 = lines[14]
        zipCode, phone = extractZipPhone(line15)
        
        line17 = lines[16]
        insurancePolicyNo = extractInsurancePolicyNo(line17)
        
        line37 = lines[36] if len(lines) > 36 else ""
        line38 = lines[37] if len(lines) > 37 else ""
        line39 = lines[38] if len(lines) > 38 else ""
        diagnosisCodes = extractDiagnosisCodes(line37, line38, line39)
        
        lines42to54 = lines[41:54] if len(lines) > 41 else []
        procedures = extractProcedures(lines42to54)
        
        line55 = lines[54] if len(lines) > 54 else ""
        patientAccountNo, totalCharge, amountPaid = extractPatientAccountAndTotal(line55)
        
        line60 = lines[59] if len(lines) > 59 else ""
        signatureDate = extractSignatureDate(line60)
        
        return {
            'insuranceId': insuranceId,
            'name': name,
            'dob': formattedDob,
            'gender': gender,
            'address': address,
            'city': city,
            'state': state,
            'zipCode': zipCode,
            'phone': phone,
            'insurancePolicyNo': insurancePolicyNo,
            'diagnosisCodes': diagnosisCodes,
            'procedures': procedures,
            'patientAccountNo': patientAccountNo,
            'totalCharge': totalCharge,
            'amountPaid': amountPaid,
            'signatureDate': signatureDate
        }
    except Exception as e:
        return None

def formatPhone(phone):
    if phone:
        phone = phone.replace('-', '')
        if len(phone) == 10:
            return f"({phone[0:3]})-{phone[3:6]}-{phone[6:10]}"
    return phone

def formatOutput(result):
    if not result:
        return None
    
    diagnosisCodesList = []
    for label in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
        code = result['diagnosisCodes'][label]
        if code:
            diagnosisCodesList.append(code)
    
    proceduresList = []
    for proc in result['procedures']:
        procedure = {
            'code': proc['procedureCode']
        }
        if proc['modifier']:
            procedure['modifier'] = proc['modifier']
        if proc['charges']:
            procedure['charges'] = float(proc['charges'])
        if proc.get('diagnosisPointer'):
            procedure['diagnosisPointer'] = proc['diagnosisPointer']
        if proc.get('additionalInfo'):
            procedure['additionalInfo'] = proc['additionalInfo']
        proceduresList.append(procedure)
    
    signatureDate = result.get('signatureDate')
    formattedSignatureDate = None
    if signatureDate:
        try:
            from datetime import datetime
            dateObj = datetime.strptime(signatureDate, '%m%d%Y')
            formattedSignatureDate = dateObj.strftime('%m/%d/%Y')
        except:
            formattedSignatureDate = signatureDate
    
    
    output = {
        'name': result['name'],
        'dob': result['dob'],
        'sex': result['gender'],
        'address': result['address'],
        'city': result['city'],
        'state': result['state'],
        'zipCode': result['zipCode'],
        'phone': formatPhone(result['phone']),
        'id': result['insuranceId'],
        'group': result['insurancePolicyNo'],
        'diagnosis_codes': diagnosisCodesList,
        'procedures': proceduresList,
        'account': result['patientAccountNo'],
        'total': float(result['totalCharge']) if result['totalCharge'] else None,
        'paid': float(result['amountPaid']) if result['amountPaid'] else None,
        'signatureDate': formattedSignatureDate
    }
    
    return output

def extractClaimData(filePath):
    result = parseClaimFile(filePath)
    output = formatOutput(result)
    
    if output:
        return json.dumps(output, indent=2)
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract claim data from text file and output as JSON')
    parser.add_argument('filename', help='Path to the claim text file to process')
    args = parser.parse_args()
    
    result = parseClaimFile(args.filename)
    output = formatOutput(result)
    
    if output:
        print(json.dumps(output, indent=2))
    else:
        sys.exit(1)
