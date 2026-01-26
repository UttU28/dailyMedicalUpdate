import pymupdf
import re
import json

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def extract_date(text):
    if not text:
        return ""
    date_match = re.search(r'(\d{1,2})\s+(\d{1,2})\s+(\d{2,4})', text)
    if date_match:
        month, day, year = date_match.groups()
        if len(year) == 2:
            year = "20" + year if int(year) < 50 else "19" + year
        return f"{month.zfill(2)}/{day.zfill(2)}/{year}"
    date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', text)
    if date_match:
        month, day, year = date_match.groups()
        if len(year) == 2:
            year = "20" + year if int(year) < 50 else "19" + year
        return f"{month.zfill(2)}/{day.zfill(2)}/{year}"
    return ""

def extract_phone(text):
    if not text:
        return ""
    phone_match = re.search(r'\(?(\d{3})\)?[-\s.]?(\d{3})[-\s.]?(\d{4})', text)
    if phone_match:
        area, first, last = phone_match.groups()
        return f"({area})-{first}-{last}"
    return ""

def extract_name_after_label(text, label_pattern):
    match = re.search(label_pattern, text, re.IGNORECASE)
    if match:
        after_label = text[match.end():match.end()+200]
        name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})', after_label)
        if name_match:
            return name_match.group(1).strip()
    return ""

def extract_address_components(text):
    address_match = re.search(r'(\d+\s+[A-Za-z0-9\s]+(?:St|Street|Ave|Avenue|Rd|Road|Dr|Drive|Ct|Court|Ln|Lane|Blvd|Boulevard|Way|Pl|Place)\.?)\s*,?\s*([A-Za-z\s]+),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)', text, re.IGNORECASE)
    if address_match:
        street = address_match.group(1).strip()
        city = address_match.group(2).strip()
        state = address_match.group(3).strip()
        zip_code = address_match.group(4).strip()
        return street, city, state, zip_code
    return "", "", "", ""

def extract_structured_data(pdf_path, print_raw=False):
    import os
    raw_text_file = pdf_path.replace('.pdf', '_raw_text.txt')
    
    if os.path.exists(raw_text_file):
        with open(raw_text_file, 'r', encoding='utf-8') as f:
            full_text = f.read()
    else:
        doc = pymupdf.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text("text") + "\n"
        doc.close()
        
        with open(raw_text_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
    
    if print_raw:
        print("=" * 100)
        print("RAW EXTRACTED TEXT FROM PDF:")
        print("=" * 100)
        print(full_text)
        print("=" * 100)
        print(f"\nTotal characters: {len(full_text)}")
        print(f"Total lines: {len(full_text.splitlines())}")
        print("=" * 100)
        print("\n")
    
    data = {
        "form_info": {},
        "patient_info": {},
        "insured_info": {},
        "provider_info": {},
        "diagnosis": {},
        "service_lines": [],
        "billing_info": {}
    }
    
    if re.search(r'CMS[\s-]?1500|CMS[\s-]?1500[\s(]02[\s-]?12|FORM 1500 \(02-12\)', full_text, re.IGNORECASE):
        data["form_info"]["form_type"] = "CMS-1500 (02-12)"
    else:
        data["form_info"]["form_type"] = ""
    
    carrier_match = re.search(r'Superior Health Plan', full_text, re.IGNORECASE)
    if carrier_match:
        data["form_info"]["carrier"] = "Superior Health Plan"
    else:
        carrier_match = re.search(r'Medicare|Medicaid|Blue Cross|Blue Shield|Aetna|Cigna|UnitedHealth|Anthem', full_text, re.IGNORECASE)
        data["form_info"]["carrier"] = carrier_match.group(0) if carrier_match else ""
    
    lines = full_text.split('\n')
    carrier_idx = -1
    for i, line in enumerate(lines):
        if 'CARRIER' in line.upper():
            carrier_idx = i
            break
    
    if carrier_idx >= 0:
        data_section = lines[carrier_idx:carrier_idx+20]
        data_text = '\n'.join(data_section)
        
        name_pattern = r'^([A-Z][a-z]+\s+[A-Z][a-z]+)$'
        for line in data_section:
            name_match = re.match(name_pattern, line.strip())
            if name_match and 'Health' not in line and 'Plan' not in line and 'Name' not in line:
                data["patient_info"]["name"] = name_match.group(1)
                break
        
        dob_match = re.search(r'(\d{1,2})\s+(\d{1,2})\s+(\d{4})', data_text)
        if dob_match:
            month, day, year = dob_match.groups()
            data["patient_info"]["date_of_birth"] = f"{month.zfill(2)}/{day.zfill(2)}/{year}"
        
        street_match = re.search(r'(\d+\s+[A-Za-z\s]+(?:ct|st|street|dr|drive|ave|avenue|rd|road|blvd|boulevard|ln|lane|way|pl|place)\.?)', data_text, re.IGNORECASE)
        if street_match:
            data["patient_info"]["street"] = street_match.group(1).strip()
        
        city_state_zip = re.search(r'([A-Z][a-z]+)\s+([A-Z]{2})\s+(\d{5})', data_text)
        if city_state_zip:
            data["patient_info"]["city"] = city_state_zip.group(1)
            data["patient_info"]["state"] = city_state_zip.group(2)
            data["patient_info"]["zip_code"] = city_state_zip.group(3)
        
        phone_match = re.search(r'(\d{3})\s*[-]?\s*(\d{3})\s*[-]?\s*(\d{4})', data_text)
        if phone_match:
            area = phone_match.group(1)
            first = phone_match.group(2)
            last = phone_match.group(3)
            phone_digits = area + first + last
            insured_id = data["insured_info"].get("id_number", "")
            if not (insured_id and phone_digits in insured_id.replace("U", "").replace("-", "").replace(" ", "")):
                data["patient_info"]["telephone"] = f"({area})-{first}-{last}"
        
        sex_match = re.search(r'(\d{1,2}\s+\d{1,2}\s+\d{4})\s+[^\n]*?([MF])\s+[X✓]', data_text, re.IGNORECASE)
        if sex_match:
            data["patient_info"]["sex"] = sex_match.group(2).upper()
    
    if not data["patient_info"].get("sex"):
        dob_text = data["patient_info"].get("date_of_birth", "").replace("/", " ")
        if dob_text:
            dob_pos = full_text.find(dob_text)
            if dob_pos >= 0:
                sex_context = full_text[dob_pos:dob_pos + 200]
                sex_match = re.search(r'([MF])\s+[X✓☑]', sex_context, re.IGNORECASE)
                if sex_match:
                    data["patient_info"]["sex"] = sex_match.group(1).upper()
    
    if not data["patient_info"].get("telephone"):
        patient_phone_section = re.search(r"5\.\s*PATIENT['']?S\s+ADDRESS[^\n]{0,500}TELEPHONE[^\n]{0,300}", full_text, re.IGNORECASE)
        if patient_phone_section:
            phone_match = re.search(r'(\d{3})\s*[-]?\s*(\d{3})\s*[-]?\s*(\d{4})', patient_phone_section.group(0))
            if phone_match:
                area = phone_match.group(1)
                first = phone_match.group(2)
                last = phone_match.group(3)
                phone_digits = area + first + last
                insured_id = data["insured_info"].get("id_number", "")
                if not (insured_id and phone_digits in insured_id.replace("U", "").replace("-", "").replace(" ", "")):
                    data["patient_info"]["telephone"] = f"({area})-{first}-{last}"
    
    if not data["patient_info"].get("sex"):
        sex_context = re.search(r'(\d{1,2}\s+\d{1,2}\s+\d{4})\s+[^\n]{0,50}([MF])\s+[X✓]', full_text, re.IGNORECASE)
        if sex_context:
            data["patient_info"]["sex"] = sex_context.group(2).upper()
    
    insured_id_section = re.search(r"(?:1a\.\s*)?INSURED['']?S\s+ID\s+NUMBER[^\n]{0,200}", full_text, re.IGNORECASE)
    if insured_id_section:
        id_match = re.search(r'\b([A-Z]\d{8,15}|[A-Z0-9]{9,15})\b', insured_id_section.group(0))
        if id_match and id_match.group(1).upper() not in ['INSURANCE', 'INSURED', 'NUMBER']:
            data["insured_info"]["id_number"] = id_match.group(1)
    else:
        insured_id_match = re.search(r'\b([A-Z]\d{10,15})\b', full_text)
        if insured_id_match:
            data["insured_info"]["id_number"] = insured_id_match.group(1)
    
    if not data["insured_info"].get("name"):
        data["insured_info"]["name"] = data["patient_info"]["name"]
    
    if not data["insured_info"].get("date_of_birth"):
        data["insured_info"]["date_of_birth"] = data["patient_info"]["date_of_birth"]
    
    if data["patient_info"].get("street"):
        data["insured_info"]["address"] = data["patient_info"]["street"]
        data["insured_info"]["city"] = data["patient_info"]["city"]
        data["insured_info"]["state"] = data["patient_info"]["state"]
        data["insured_info"]["zip_code"] = data["patient_info"]["zip_code"]
    
    insured_phone_section = re.search(r"7\.\s*INSURED['']?S\s+ADDRESS[^\n]{0,500}TELEPHONE[^\n]{0,300}|INSURED['']?S\s+TELEPHONE[^\n]{0,300}", full_text, re.IGNORECASE)
    if insured_phone_section:
        insured_phone_match = re.search(r'(\d{3})\s*[-]?\s*(\d{3})\s*[-]?\s*(\d{4})|(\d{3})\s+(\d{7})', insured_phone_section.group(0))
        if insured_phone_match:
            if insured_phone_match.group(3):
                area = insured_phone_match.group(1)
                first = insured_phone_match.group(2)
                last = insured_phone_match.group(3)
                phone_digits = area + first + last
            else:
                area = insured_phone_match.group(4)
                number = insured_phone_match.group(5)
                phone_digits = area + number
                first = number[:3]
                last = number[3:]
            
            insured_id = data["insured_info"].get("id_number", "")
            patient_phone_clean = data["patient_info"].get("telephone", "").replace("-", "").replace("(", "").replace(")", "").replace(" ", "")
            
            if insured_id and phone_digits in insured_id.replace("U", "").replace("-", "").replace(" ", ""):
                data["insured_info"]["telephone"] = data["patient_info"].get("telephone", "")
            elif phone_digits != patient_phone_clean:
                if insured_phone_match.group(3):
                    data["insured_info"]["telephone"] = f"({area}){first}{last}"
                else:
                    data["insured_info"]["telephone"] = f"({area}){first}{last}"
            else:
                data["insured_info"]["telephone"] = data["patient_info"].get("telephone", "")
        else:
            data["insured_info"]["telephone"] = data["patient_info"].get("telephone", "")
    else:
        all_phones = list(re.finditer(r'(\d{3})\s*[-]?\s*(\d{3})\s*[-]?\s*(\d{4})|(\d{3})\s+(\d{7})', full_text))
        if len(all_phones) >= 2:
            patient_phone_clean = data["patient_info"].get("telephone", "").replace("-", "").replace("(", "").replace(")", "").replace(" ", "")
            insured_id = data["insured_info"].get("id_number", "")
            for phone_match in all_phones:
                if phone_match.group(3):
                    area = phone_match.group(1)
                    first = phone_match.group(2)
                    last = phone_match.group(3)
                    phone_clean = area + first + last
                else:
                    area = phone_match.group(4)
                    number = phone_match.group(5)
                    phone_clean = area + number
                    first = number[:3]
                    last = number[3:]
                
                if phone_clean != patient_phone_clean and not (insured_id and phone_clean in insured_id.replace("U", "").replace("-", "").replace(" ", "")):
                    if phone_match.group(3):
                        data["insured_info"]["telephone"] = f"({area}){first}{last}"
                    else:
                        data["insured_info"]["telephone"] = f"({area}){first}{last}"
                    break
        else:
            data["insured_info"]["telephone"] = data["patient_info"].get("telephone", "")
    
    relationship_match = re.search(r'Self\s+[X✓]|Self\s+X\b', full_text)
    if relationship_match:
        data["patient_info"]["relationship_to_insured"] = "Self"
    elif re.search(r'Spouse\s+[X✓]|Spouse\s+X\b', full_text):
        data["patient_info"]["relationship_to_insured"] = "Spouse"
    elif re.search(r'Child\s+[X✓]|Child\s+X\b', full_text):
        data["patient_info"]["relationship_to_insured"] = "Child"
    elif re.search(r'Other\s+[X✓]|Other\s+X\b', full_text):
        data["patient_info"]["relationship_to_insured"] = "Other"
    
    policy_match = re.search(r'\b(\d{8})\b', full_text)
    if policy_match and len(policy_match.group(1)) == 8:
        data["insured_info"]["policy_group_number"] = policy_match.group(1)
    
    diagnosis_codes = []
    icd10_pattern = r'\b([A-Z]\d{2,3}\.\d{1,2})\b'
    all_diag_matches = list(re.finditer(icd10_pattern, full_text))
    seen_codes = set()
    code_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    for match in all_diag_matches:
        code = match.group(1)
        if code not in seen_codes and len(diagnosis_codes) < len(code_letters):
            diagnosis_codes.append({"code": code_letters[len(diagnosis_codes)], "value": code})
            seen_codes.add(code)
    
    data["diagnosis"]["codes"] = diagnosis_codes
    data["diagnosis"]["icd_indicator"] = "0" if diagnosis_codes else "0"
    
    service_line = {}
    
    service_date_flexible = re.search(r'(\d{1,2})\s+(\d{1,2})\s+(\d{2})\s+\1\s+\2\s+\3\s+(\d{1,2})', full_text)
    if service_date_flexible:
        month, day, year, pos = service_date_flexible.group(1), service_date_flexible.group(2), service_date_flexible.group(3), service_date_flexible.group(4)
        if int(year) >= 20 and int(month) <= 12 and int(day) <= 31 and int(pos) <= 99:
            date_start = service_date_flexible.start()
            date_end = service_date_flexible.end()
            date_context = full_text[max(0, date_start-200):min(len(full_text), date_end+200)]
            
            has_procedure = re.search(r'\b\d{5}\b', date_context)
            has_diag_pointer = re.search(r'\b[A-Z]{1,4}\b', date_context)
            has_charge = re.search(r'\d{3}\s+\d{2}', date_context)
            
            if has_procedure or has_diag_pointer or has_charge:
                year_full = "20" + year
                service_line["date_from"] = f"{month.zfill(2)}/{day.zfill(2)}/{year_full}"
                service_line["date_to"] = f"{month.zfill(2)}/{day.zfill(2)}/{year_full}"
                service_line["place_of_service"] = pos
    else:
        all_date_patterns = list(re.finditer(r'(\d{1,2})\s+(\d{1,2})\s+(\d{2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{2})\s+(\d{1,2})', full_text))
        best_match = None
        best_priority = 0
        
        for date_match in all_date_patterns:
            month1, day1, year1 = date_match.group(1), date_match.group(2), date_match.group(3)
            month2, day2, year2 = date_match.group(4), date_match.group(5), date_match.group(6)
            pos = date_match.group(7)
            
            if int(year1) >= 20 and int(year2) >= 20 and int(month1) <= 12 and int(month2) <= 12 and int(day1) <= 31 and int(day2) <= 31 and int(pos) <= 99:
                date_start = date_match.start()
                date_end = date_match.end()
                date_context = full_text[max(0, date_start-200):min(len(full_text), date_end+200)]
                
                has_procedure = re.search(r'\b\d{5}\b', date_context)
                has_diag_pointer = re.search(r'\b[A-Z]{1,4}\b', date_context)
                has_charge = re.search(r'\d{3}\s+\d{2}', date_context)
                
                if has_procedure or has_diag_pointer or has_charge:
                    priority = 3 if (month1 == month2 and day1 == day2 and year1 == year2) else (2 if (month1 == month2 and day1 == day2) else 1)
                    if priority > best_priority:
                        best_priority = priority
                        year_full = "20" + year1
                        best_match = {
                            "date_from": f"{month1.zfill(2)}/{day1.zfill(2)}/{year_full}",
                            "date_to": f"{month2.zfill(2)}/{day2.zfill(2)}/{year_full}",
                            "place_of_service": pos
                        }
        
        if best_match:
            service_line.update(best_match)
    
    if service_line.get("date_from"):
        date_str = service_line["date_from"].replace("/", " ").replace("20", "")
        date_pos = full_text.find(date_str)
        if date_pos >= 0:
            proc_context = full_text[date_pos:date_pos + 400]
            proc_match = re.search(r'\b([A-Z0-9]{5})\b', proc_context)
            if proc_match:
                proc_code = proc_match.group(1)
                if proc_code.upper() not in ['PROCEDURES', 'SERVICES', 'SUPPLIES', 'CPT/HCPCS', 'DATE', 'PLACE']:
                    service_line["procedure_code"] = proc_code
    else:
        service_section = re.search(r'24\.\s*A\.\s*DATE|PROCEDURES[^\n]{0,300}|CPT/HCPCS[^\n]{0,300}', full_text, re.IGNORECASE)
        if service_section:
            proc_match = re.search(r'\b([A-Z0-9]{5})\b', service_section.group(0))
            if proc_match:
                proc_code = proc_match.group(1)
                if proc_code.upper() not in ['PROCEDURES', 'SERVICES', 'SUPPLIES', 'CPT/HCPCS']:
                    service_line["procedure_code"] = proc_code
    
    if service_line.get("procedure_code"):
        proc_pos = full_text.find(service_line["procedure_code"])
        if proc_pos >= 0:
            pointer_context = full_text[max(0, proc_pos-100):min(len(full_text), proc_pos+100)]
            diag_pointer_match = re.search(r'\b([A-Z]{1,4})\b', pointer_context)
            if diag_pointer_match:
                pointer_value = diag_pointer_match.group(1)
                if pointer_value.upper() not in ['FORM', 'NUCC', 'PICA', 'DATE', 'FILE', 'SIGN', 'POINTER', 'CPT', 'HCPCS', 'PROCEDURES', 'SERVICES']:
                    service_line["diagnosis_pointer"] = pointer_value
    else:
        diag_pointer_section = re.search(r'DIAGNOSIS\s+POINTER[^\n]{0,100}|24\.\s*E\.\s*DIAGNOSIS', full_text, re.IGNORECASE)
        if diag_pointer_section:
            diag_pointer_match = re.search(r'\b([A-Z]{1,4})\b', diag_pointer_section.group(0))
            if diag_pointer_match:
                pointer_value = diag_pointer_match.group(1)
                if pointer_value.upper() not in ['FORM', 'NUCC', 'PICA', 'DATE', 'FILE', 'SIGN', 'POINTER']:
                    service_line["diagnosis_pointer"] = pointer_value
    
    charge_match = re.search(r'(\d{3})\s+(\d{2})\s+(\d{1})\b', full_text)
    if charge_match and int(charge_match.group(1)) > 100:
        service_line["charges"] = f"${charge_match.group(1)}.{charge_match.group(2)}"
        service_line["days_units"] = charge_match.group(3)
    
    if service_line.get("procedure_code"):
        proc_pos = full_text.find(service_line["procedure_code"])
        if proc_pos >= 0:
            npi_context = full_text[max(0, proc_pos-100):min(len(full_text), proc_pos+300)]
            npi_match = re.search(r'\b(\d{10})\b', npi_context)
            if npi_match:
                service_line["rendering_provider_npi"] = npi_match.group(1)
    else:
        npi_section = re.search(r'RENDERING\s+PROVIDER.*NPI|NPI[^\n]{0,100}', full_text, re.IGNORECASE)
        if npi_section:
            npi_match = re.search(r'\b(\d{10})\b', npi_section.group(0))
            if npi_match:
                service_line["rendering_provider_npi"] = npi_match.group(1)
    
    provider_id_section = re.search(r'ID\.\s*QUAL[^\n]{0,100}|RENDERING\s+PROVIDER\s+ID[^\n]{0,200}', full_text, re.IGNORECASE)
    if provider_id_section:
        provider_id_match = re.search(r'\b([A-Z0-9]{2})\s+([A-Z0-9]{4,10})\b', provider_id_section.group(0))
        if provider_id_match:
            qual = provider_id_match.group(1)
            provider_id = provider_id_match.group(2)
            if qual.upper() not in ['ID', 'QUAL', 'BY'] and provider_id.upper() not in ['RENDERING', 'PROVIDER', 'NATIONAL']:
                service_line["rendering_provider_id_qual"] = qual
                service_line["rendering_provider_id"] = provider_id
    else:
        if service_line.get("procedure_code"):
            proc_pos = full_text.find(service_line["procedure_code"])
            if proc_pos >= 0:
                id_context = full_text[max(0, proc_pos-100):min(len(full_text), proc_pos+200)]
                provider_id_match = re.search(r'\b([A-Z0-9]{2})\s+([A-Z0-9]{4,10})\b', id_context)
                if provider_id_match:
                    qual = provider_id_match.group(1)
                    provider_id = provider_id_match.group(2)
                    if qual.upper() not in ['ID', 'QUAL', 'BY'] and provider_id.upper() not in ['RENDERING', 'PROVIDER', 'NATIONAL']:
                        service_line["rendering_provider_id_qual"] = qual
                        service_line["rendering_provider_id"] = provider_id
    
    if service_line.get("date_from"):
        data["service_lines"] = [service_line]
    
    provider_section = re.search(r'PHYSICIAN OR SUPPLIER INFORMATION[^\n]*(?:\n[^\n]*){0,100}', full_text, re.IGNORECASE)
    if provider_section:
        section_text = provider_section.group(0)
    else:
        section_text = full_text
    
    provider_name_section = re.search(r'PHYSICIAN[^\n]{0,200}|SUPPLIER[^\n]{0,200}|BILLING\s+PROVIDER[^\n]{0,200}', section_text, re.IGNORECASE)
    if provider_name_section:
        provider_name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}(?:\s+[A-Z])?(?:,\s*MD)?)', provider_name_section.group(0))
        if provider_name_match:
            name = provider_name_match.group(1).strip()
            if 'Health' not in name and 'Plan' not in name and 'Information' not in name and name != data["patient_info"].get("name", ""):
                if ', MD' in name:
                    data["provider_info"]["name"] = name.split(',')[0].strip()
                else:
                    data["provider_info"]["name"] = name
    else:
        provider_name_match = re.search(r'([A-Z][a-z]+\s+[A-Z]\s+[A-Z][a-z]+,\s+MD)', section_text)
        if provider_name_match:
            name = provider_name_match.group(1).strip()
            if 'Health' not in name and 'Plan' not in name and name != data["patient_info"].get("name", ""):
                data["provider_info"]["name"] = name.split(',')[0].strip()
    
    referring_match = re.search(r'DN\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', section_text)
    if referring_match:
        data["provider_info"]["referring_provider_name"] = referring_match.group(0).strip()
    
    referring_id_match = re.search(r'17a\.\s*([A-Z0-9]{6,10})', section_text, re.IGNORECASE)
    if referring_id_match:
        id_value = referring_id_match.group(1)
        if id_value.upper() not in ['REFERRING', 'PROVIDER', 'SOURCE']:
            data["provider_info"]["referring_provider_id"] = id_value
    
    provider_address_section = re.search(r'33\.\s*BILLING\s+PROVIDER[^\n]{0,500}|32\.\s*SERVICE\s+FACILITY[^\n]{0,500}', full_text, re.IGNORECASE)
    if provider_address_section:
        provider_address_match = re.search(r'(\d+\s+[A-Za-z0-9\s]+(?:Dr|DR|Dr\.|Street|St|Ave|Avenue|Rd|Road|Blvd|Boulevard|Ct|Court|Ln|Lane|Way|Pl|Place)\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)', provider_address_section.group(0), re.IGNORECASE)
        if provider_address_match:
            street = provider_address_match.group(1).strip()
            city = provider_address_match.group(2).strip()
            state = provider_address_match.group(3).strip()
            zip_code = provider_address_match.group(4).strip()
            
            patient_street = data["patient_info"].get("street", "")
            patient_city = data["patient_info"].get("city", "")
            
            if street != patient_street and city != patient_city and len(city.split()) <= 3 and len(street.split()) <= 5:
                data["provider_info"]["address"] = street
                data["provider_info"]["city"] = city.split('\n')[-1].strip() if '\n' in city else city
                data["provider_info"]["state"] = state
                data["provider_info"]["zip_code"] = zip_code
    
    provider_phone_match = re.search(r'\((\d{3})\)\s*(\d{7})', section_text)
    if provider_phone_match:
        data["provider_info"]["phone"] = f"({provider_phone_match.group(1)}) {provider_phone_match.group(2)}"
    
    if not data["provider_info"].get("address"):
        provider_address_section = re.search(r'33\.\s*BILLING\s+PROVIDER[^\n]{0,500}|32\.\s*SERVICE\s+FACILITY[^\n]{0,500}', full_text, re.IGNORECASE)
        if provider_address_section:
            all_addresses = list(re.finditer(r'(\d+\s+[A-Za-z0-9\s]+(?:Dr|DR|Dr\.|Street|St|Ave|Avenue|Rd|Road|Blvd|Boulevard|Ct|Court|Ln|Lane|Way|Pl|Place)\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)', provider_address_section.group(0), re.IGNORECASE))
            patient_street = data["patient_info"].get("street", "")
            patient_city = data["patient_info"].get("city", "")
            
            for addr_match in all_addresses:
                street = addr_match.group(1).strip()
                city = addr_match.group(2).strip()
                if street != patient_street and city != patient_city and len(city.split()) <= 3 and len(street.split()) <= 5:
                    data["provider_info"]["address"] = street
                    data["provider_info"]["city"] = city.split('\n')[-1].strip() if '\n' in city else city
                    data["provider_info"]["state"] = addr_match.group(3).strip()
                    data["provider_info"]["zip_code"] = addr_match.group(4).strip()
                    break
    
    if not data["provider_info"].get("phone"):
        provider_phone_section = re.search(r'BILLING\s+PROVIDER[^\n]{0,200}|PH\s*#[^\n]{0,200}', full_text, re.IGNORECASE)
        if provider_phone_section:
            provider_phone_match = re.search(r'\((\d{3})\)\s*(\d{7})', provider_phone_section.group(0))
            if provider_phone_match:
                data["provider_info"]["phone"] = f"({provider_phone_match.group(1)}) {provider_phone_match.group(2)}"
            else:
                provider_phone_match = re.search(r'(\d{3})\s+(\d{7})', provider_phone_section.group(0))
                if provider_phone_match:
                    data["provider_info"]["phone"] = f"({provider_phone_match.group(1)}) {provider_phone_match.group(2)}"
        else:
            all_phones = list(re.finditer(r'\((\d{3})\)\s*(\d{7})|(\d{3})\s+(\d{7})', full_text))
            patient_phone = data["patient_info"].get("telephone", "").replace("-", "").replace("(", "").replace(")", "").replace(" ", "")
            insured_phone = data["insured_info"].get("telephone", "").replace("-", "").replace("(", "").replace(")", "").replace(" ", "")
            
            for phone_match in all_phones:
                area = phone_match.group(1) or phone_match.group(3)
                number = phone_match.group(2) or phone_match.group(4)
                phone_clean = area + number
                if phone_clean != patient_phone and phone_clean != insured_phone:
                    data["provider_info"]["phone"] = f"({area}) {number}"
                    break
    
    if not data["provider_info"].get("name"):
        provider_sig_section = re.search(r'SIGNATURE\s+OF\s+PHYSICIAN[^\n]{0,300}', full_text, re.IGNORECASE)
        if provider_sig_section:
            provider_name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})', provider_sig_section.group(0))
            if provider_name_match:
                name = provider_name_match.group(1).strip()
                if 'Health' not in name and 'Plan' not in name and 'Information' not in name and name != data["patient_info"].get("name", ""):
                    data["provider_info"]["name"] = name
    
    if not data["provider_info"].get("referring_provider_name"):
        referring_match = re.search(r'DN\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', full_text)
        if referring_match:
            data["provider_info"]["referring_provider_name"] = referring_match.group(0).strip()
    
    if not data["provider_info"].get("referring_provider_id"):
        referring_section = re.search(r'17a\.\s*([A-Z0-9]{6,10})', full_text, re.IGNORECASE)
        if referring_section:
            id_value = referring_section.group(1)
            if id_value.upper() not in ['REFERRING', 'PROVIDER', 'SOURCE']:
                data["provider_info"]["referring_provider_id"] = id_value
    
    npi_section = re.search(r'17b\.\s*NPI|PROVIDER.*NPI|NPI[^\n]{0,50}', full_text, re.IGNORECASE)
    if npi_section:
        npi_match = re.search(r'\b(\d{10})\b', npi_section.group(0))
        if npi_match:
            data["provider_info"]["npi"] = npi_match.group(1)
    else:
        all_npis = list(re.finditer(r'\b(\d{10})\b', full_text))
        if len(all_npis) > 0:
            data["provider_info"]["npi"] = all_npis[0].group(1)
    
    tax_id_section = re.search(r'FEDERAL\s+TAX\s+ID[^\n]{0,100}|25\.\s*FEDERAL[^\n]{0,100}', full_text, re.IGNORECASE)
    if tax_id_section:
        tax_id_match = re.search(r'\b(\d{9})\b', tax_id_section.group(0))
        if tax_id_match:
            data["billing_info"]["federal_tax_id"] = tax_id_match.group(1)
            ein_match = re.search(r'EIN\s+[X✓☑]', tax_id_section.group(0), re.IGNORECASE)
            if ein_match:
                data["billing_info"]["tax_id_type"] = "EIN"
            else:
                ssn_match = re.search(r'SSN\s+[X✓☑]', tax_id_section.group(0), re.IGNORECASE)
                if ssn_match:
                    data["billing_info"]["tax_id_type"] = "SSN"
    
    account_section = re.search(r"26\.\s*PATIENT['']?S\s+ACCOUNT[^\n]{0,200}|PATIENT['']?S\s+ACCOUNT\s+NO[^\n]{0,200}", full_text, re.IGNORECASE)
    if account_section:
        account_match = re.search(r'\b([A-Z0-9]{4,20})\b', account_section.group(0))
        if account_match:
            account_value = account_match.group(1)
            if account_value.upper() not in ['PATIENT', 'ACCOUNT', 'NUMBER', 'NO']:
                data["billing_info"]["patient_account_number"] = account_value
    
    total_charge_match = re.search(r'(\d{3})\s+(\d{2})\s*$', full_text, re.MULTILINE)
    if total_charge_match and int(total_charge_match.group(1)) >= 100:
        data["billing_info"]["total_charge"] = f"${total_charge_match.group(1)}.{total_charge_match.group(2)}"
    
    amount_paid_match = re.search(r'0\s+00', full_text)
    if amount_paid_match:
        data["billing_info"]["amount_paid"] = "$0.00"
    
    accept_assignment_match = re.search(r'ACCEPT\s+ASSIGNMENT[^\n]*[X✓☑]\s+YES|ACCEPT\s+ASSIGNMENT[^\n]*YES\s+[X✓☑]', full_text, re.IGNORECASE)
    if accept_assignment_match:
        data["billing_info"]["accept_assignment"] = "YES"
    elif re.search(r'ACCEPT\s+ASSIGNMENT[^\n]*[X✓☑]\s+NO|ACCEPT\s+ASSIGNMENT[^\n]*NO\s+[X✓☑]', full_text, re.IGNORECASE):
        data["billing_info"]["accept_assignment"] = "NO"
    
    outside_lab_match = re.search(r'OUTSIDE\s+LAB[^\n]*[X✓☑]\s+YES|OUTSIDE\s+LAB[^\n]*YES\s+[X✓☑]', full_text, re.IGNORECASE)
    if outside_lab_match:
        data["billing_info"]["outside_lab"] = "YES"
        lab_charge_match = re.search(r'OUTSIDE\s+LAB[^\n]*\$?\s*(\d+)\s+(\d{2})', full_text, re.IGNORECASE)
        if lab_charge_match:
            data["billing_info"]["outside_lab_charges"] = f"${lab_charge_match.group(1)}.{lab_charge_match.group(2)}"
    elif re.search(r'OUTSIDE\s+LAB[^\n]*[X✓☑]\s+NO|OUTSIDE\s+LAB[^\n]*NO\s+[X✓☑]', full_text, re.IGNORECASE):
        data["billing_info"]["outside_lab"] = "NO"
        data["billing_info"]["outside_lab_charges"] = ""
    
    if re.search(r'EMPLOYMENT[^\n]*NO\s+[X✓]', full_text, re.IGNORECASE):
        data["patient_info"]["condition_related_to_employment"] = "NO"
    if re.search(r'AUTO\s+ACCIDENT[^\n]*NO\s+[X✓]', full_text, re.IGNORECASE):
        data["patient_info"]["condition_related_to_auto_accident"] = "NO"
    if re.search(r'OTHER\s+ACCIDENT[^\n]*NO\s+[X✓]', full_text, re.IGNORECASE):
        data["patient_info"]["condition_related_to_other_accident"] = "NO"
    
    if not data["patient_info"].get("sex"):
        data["patient_info"]["sex"] = ""
    if not data["patient_info"].get("relationship_to_insured"):
        data["patient_info"]["relationship_to_insured"] = ""
    if not data["patient_info"].get("condition_related_to_employment"):
        data["patient_info"]["condition_related_to_employment"] = ""
    if not data["patient_info"].get("condition_related_to_auto_accident"):
        data["patient_info"]["condition_related_to_auto_accident"] = ""
    if not data["patient_info"].get("condition_related_to_other_accident"):
        data["patient_info"]["condition_related_to_other_accident"] = ""
    
    if not data["billing_info"].get("tax_id_type"):
        data["billing_info"]["tax_id_type"] = ""
    if not data["billing_info"].get("accept_assignment"):
        data["billing_info"]["accept_assignment"] = ""
    if not data["billing_info"].get("amount_paid"):
        data["billing_info"]["amount_paid"] = ""
    if not data["billing_info"].get("outside_lab"):
        data["billing_info"]["outside_lab"] = ""
    if not data["billing_info"].get("outside_lab_charges"):
        data["billing_info"]["outside_lab_charges"] = ""
    
    return data

def main():
    pdf_file_path = "example.pdf"
    output_json_path = "extracted_claim_data.json"
    
    try:
        data = extract_structured_data(pdf_file_path, print_raw=False)
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
