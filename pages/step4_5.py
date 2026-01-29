#!/usr/bin/env python3
"""
Step 4.5: Fill a single Service Line form
"""

import os
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from config import load_env_file

load_env_file()

def waitForServiceLinesFormToLoad(driver):
    """Wait for the Service Lines form to be fully loaded"""
    try:
        wait = WebDriverWait(driver, 20)
        
        # Wait for the form to be present
        print("[INFO] Waiting for Service Lines form to load...")
        wait.until(
            EC.presence_of_element_located((By.ID, "slform"))
        )
        
        # Wait for "Service Lines" section header
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Service Lines')]"))
        )
        
        # Wait for the dates of service input field to be present
        wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.fromDate"))
        )
        
        # Wait a bit more for JavaScript to finish rendering
        time.sleep(0.5)
        print("[INFO] Service Lines form is ready")
        return True
    except Exception as e:
        print(f"[ERROR] Form did not load: {e}")
        return False

def fillDatesOfService(driver, serviceDate):
    """Fill Dates of Service (From and To)"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Fill From Date
        fromDateInput = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.fromDate"))
        )
        fromDateInput.clear()
        time.sleep(0.2)
        fromDateInput.send_keys(serviceDate)
        time.sleep(0.2)
        print(f"[INFO] Entered From Date: {serviceDate}")
        
        # Fill To Date
        toDateInput = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.toDate"))
        )
        toDateInput.clear()
        time.sleep(0.2)
        toDateInput.send_keys(serviceDate)
        time.sleep(0.2)
        print(f"[INFO] Entered To Date: {serviceDate}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Dates of Service: {e}")
        return False

def selectPlaceOfService(driver, placeOfService):
    """Select Place of Service"""
    try:
        wait = WebDriverWait(driver, 10)
        
        placeOfServiceSelect = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.placeOfService"))
        )
        select = Select(placeOfServiceSelect)
        select.select_by_value(placeOfService)
        time.sleep(0.5)
        print(f"[INFO] Selected Place of Service: {placeOfService}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to select Place of Service: {e}")
        return False

def fillProcedureCode(driver, procedureCode):
    """Fill Procedure Code"""
    try:
        wait = WebDriverWait(driver, 10)
        
        procedureCodeInput = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.procedureCode"))
        )
        procedureCodeInput.clear()
        time.sleep(0.2)
        procedureCodeInput.send_keys(procedureCode)
        time.sleep(0.2)
        print(f"[INFO] Entered Procedure Code: {procedureCode}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Procedure Code: {e}")
        return False

def checkModifierExists(driver, modifier):
    """Check if modifier is already added in the table"""
    try:
        # Check if modifier table exists
        modifierTable = driver.find_elements(By.CSS_SELECTOR, "table.table-condensed tbody tr")
        if not modifierTable:
            return False
        
        # Get all existing modifiers from the table
        existingModifiers = []
        for row in modifierTable:
            try:
                # Get the modifier value from the first <td> in each row
                modifierCell = row.find_element(By.CSS_SELECTOR, "td:first-child")
                existingModifier = modifierCell.text.strip()
                if existingModifier:
                    existingModifiers.append(existingModifier)
            except:
                continue
        
        # Check if our modifier is already in the list
        modifierValue = modifier.strip()
        if modifierValue in existingModifiers:
            print(f"[INFO] Modifier '{modifierValue}' already exists in the table (found {existingModifiers.count(modifierValue)} time(s))")
            return True
        
        return False
    except Exception as e:
        # If we can't check, assume it doesn't exist and let the add proceed
        print(f"[WARNING] Could not check for existing modifiers: {e}")
        return False

def addModifier(driver, modifier):
    """Add modifier if provided and not already added"""
    try:
        if not modifier or modifier.strip() == '':
            print("[INFO] No modifier provided, skipping modifier addition")
            return True
        
        wait = WebDriverWait(driver, 10)
        
        # Check if modifier is already added
        if checkModifierExists(driver, modifier):
            print(f"[INFO] Modifier '{modifier}' already exists, skipping addition")
            return True
        
        # Wait for modifier input field
        modifierInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalServiceLineModifier.modifier"))
        )
        
        # Clear and fill modifier
        modifierInput.clear()
        time.sleep(0.2)
        modifierInput.send_keys(modifier.strip())
        time.sleep(0.2)
        print(f"[INFO] Entered Modifier: {modifier}")
        
        # Find and click Add button
        addButton = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='_eventId_addWebProfServiceLineModifier']"))
        )
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", addButton)
        time.sleep(0.5)
        
        # Click Add button
        addButton.click()
        print(f"[INFO] Clicked Add button for modifier: {modifier}")
        
        # Wait for page to reload (soft reload with JS)
        time.sleep(0.5)
        
        # Wait for form to reload - check if modifier was added (table appears)
        try:
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-condensed tbody tr"))
            )
            print(f"[INFO] Modifier '{modifier}' added successfully, page reloaded")
        except:
            # Alternative: just wait for form to be present
            try:
                wait.until(
                    EC.presence_of_element_located((By.ID, "slform"))
                )
                print(f"[INFO] Page reloaded after adding modifier: {modifier}")
            except:
                time.sleep(0.5)
                print(f"[INFO] Waiting for page reload after adding modifier: {modifier}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to add modifier {modifier}: {e}")
        return False

def selectDiagnosisCodes(driver, diagnosisCodes):
    """Select only the specified diagnosis code checkboxes"""
    try:
        if not diagnosisCodes or len(diagnosisCodes) == 0:
            print("[WARNING] No diagnosis codes provided for selection")
            return False
        
        wait = WebDriverWait(driver, 10)
        
        # Find all diagnosis code checkboxes
        diagnosisCheckboxes = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[name='potentialServiceLineDiagCodes'][type='checkbox']"))
        )
        
        # Normalize diagnosis codes for matching (remove dots and convert to uppercase)
        # The checkbox values are like "I10", "E782", "R5383", "T162" (no dots, no trailing X)
        normalizedCodes = []
        for code in diagnosisCodes:
            # Remove dots and trailing X, convert to uppercase
            normalized = code.replace('.', '').rstrip('X').upper()
            normalizedCodes.append(normalized)
        
        selectedCount = 0
        for checkbox in diagnosisCheckboxes:
            checkboxValue = checkbox.get_attribute('value') or ''
            # Normalize checkbox value for comparison
            normalizedCheckboxValue = checkboxValue.replace('.', '').rstrip('X').upper()
            
            # Check if this checkbox matches any of our diagnosis codes
            if normalizedCheckboxValue in normalizedCodes:
                if not checkbox.is_selected():
                    # Scroll into view
                    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                    time.sleep(0.2)
                    checkbox.click()
                    selectedCount += 1
                    print(f"[INFO] Selected diagnosis code: {checkboxValue}")
            else:
                # Unselect if it was previously selected but shouldn't be
                if checkbox.is_selected():
                    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                    time.sleep(0.2)
                    checkbox.click()
                    print(f"[INFO] Unselected diagnosis code: {checkboxValue}")
        
        time.sleep(0.2)
        print(f"[INFO] Selected {selectedCount} diagnosis code(s) out of {len(normalizedCodes)} specified")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to select diagnosis codes: {e}")
        return False

def fillCharges(driver, charges):
    """Fill Charges (remove $ sign if present)"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Remove $ sign and any spaces
        chargesValue = re.sub(r'[\$\s]', '', charges)
        
        chargesInput = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.amount"))
        )
        chargesInput.clear()
        time.sleep(0.2)
        chargesInput.send_keys(chargesValue)
        time.sleep(0.2)
        print(f"[INFO] Entered Charges: {chargesValue}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Charges: {e}")
        return False

def fillUnits(driver, units, unitType="UN"):
    """Fill Units and select Type"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Fill Units
        unitsInput = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.daysUnits"))
        )
        unitsInput.clear()
        time.sleep(0.2)
        unitsInput.send_keys(str(units))
        time.sleep(0.2)
        print(f"[INFO] Entered Units: {units}")
        
        # Select Type
        unitTypeSelect = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.serviceUnitQualifier"))
        )
        select = Select(unitTypeSelect)
        select.select_by_value(unitType)
        time.sleep(0.5)
        print(f"[INFO] Selected Unit Type: {unitType}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Units: {e}")
        return False

def fillNDC(driver, ndc):
    """Fill NDC field (without spaces)"""
    try:
        if not ndc or ndc.strip() == '':
            print("[INFO] No NDC value provided, skipping NDC field")
            return True
        
        wait = WebDriverWait(driver, 10)
        
        # Remove all spaces from NDC value
        ndcValue = ndc.replace(' ', '')
        
        ndcInput = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.ndc"))
        )
        ndcInput.clear()
        time.sleep(0.2)
        ndcInput.send_keys(ndcValue)
        time.sleep(0.2)
        print(f"[INFO] Entered NDC: {ndcValue}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill NDC: {e}")
        return False

def clickSaveUpdateButton(driver):
    """Click the Save / Update button"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Find the Save/Update button
        saveButton = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='_eventId_saveActiveServiceLine']"))
        )
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", saveButton)
        time.sleep(0.5)
        
        saveButton.click()
        print("[INFO] Clicked Save / Update button")
        
        # Wait for page to reload (soft reload with JS)
        time.sleep(0.5)
        
        # Wait for form to reload
        try:
            wait.until(
                EC.presence_of_element_located((By.ID, "slform"))
            )
            print("[INFO] Page reloaded after Save / Update")
        except:
            time.sleep(0.5)
            print("[INFO] Waiting for page reload...")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to click Save / Update button: {e}")
        return False

def checkForValidationErrors(driver):
    """Check for validation errors on the form before Save/Update"""
    try:
        errors = []
        
        # Check for visible error messages
        errorMessages = driver.find_elements(By.CSS_SELECTOR, ".help-inline, .error, [class*='error'], span[class*='error']")
        for error in errorMessages:
            errorText = error.text.strip()
            if errorText and errorText.lower() not in ['', 'required field']:
                # Check if error is visible
                if error.is_displayed():
                    errors.append(f"Error message: {errorText}")
        
        # Check date input fields for invalid values
        dateInputs = driver.find_elements(By.CSS_SELECTOR, "input.mask-date, input[id*='Date']")
        for dateInput in dateInputs:
            try:
                value = dateInput.get_attribute("value") or ""
                if value and len(value) > 0:
                    # Check if date format looks wrong (e.g., "20/20/2511" instead of "11/20/2025")
                    if "/" in value:
                        parts = value.split("/")
                        if len(parts) == 3:
                            month, day, year = parts
                            # Check if month > 12 or day > 31 (basic validation)
                            try:
                                monthInt = int(month)
                                dayInt = int(day)
                                if monthInt > 12 or dayInt > 31 or monthInt < 1 or dayInt < 1:
                                    fieldId = dateInput.get_attribute("id") or "unknown"
                                    errors.append(f"Invalid date value in {fieldId}: {value} (month: {monthInt}, day: {dayInt})")
                            except ValueError:
                                fieldId = dateInput.get_attribute("id") or "unknown"
                                errors.append(f"Invalid date format in {fieldId}: {value}")
                    
                    # Check for red border or error styling
                    classes = dateInput.get_attribute("class") or ""
                    style = dateInput.get_attribute("style") or ""
                    parent = dateInput.find_element(By.XPATH, "./..")
                    parentClasses = parent.get_attribute("class") or ""
                    
                    # Check if there's an error indicator
                    if ("error" in classes.lower() or "error" in parentClasses.lower() or 
                        "red" in style.lower() or "border" in style.lower()):
                        # Check for error message near this field
                        try:
                            errorSpan = dateInput.find_element(By.XPATH, "./following-sibling::span[contains(@class, 'help-inline')] | ./../span[contains(@class, 'help-inline')]")
                            if errorSpan and errorSpan.is_displayed():
                                errorText = errorSpan.text.strip()
                                if errorText:
                                    fieldId = dateInput.get_attribute("id") or "unknown"
                                    errors.append(f"Validation error in {fieldId}: {errorText}")
                        except:
                            pass
            except Exception as e:
                # Skip this input if there's an issue
                pass
        
        if errors:
            print(f"[WARNING] Found validation errors: {errors}")
            return True, errors
        return False, []
    except Exception as e:
        print(f"[WARNING] Error checking validation: {e}")
        return False, []

def validateServiceLineFields(driver, serviceDate, placeOfService, procedureCode, diagnosisCodes, charges, units):
    """Validate all Service Line form fields are filled correctly"""
    errors = []
    try:
        wait = WebDriverWait(driver, 5)
        
        # Validate From Date
        fromDateInput = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.fromDate"))
        )
        actualFromDate = fromDateInput.get_attribute("value") or ""
        if actualFromDate.strip() != serviceDate.strip():
            errors.append(f"From Date mismatch: expected '{serviceDate}', got '{actualFromDate}'")
        
        # Validate To Date
        toDateInput = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.toDate"))
        )
        actualToDate = toDateInput.get_attribute("value") or ""
        if actualToDate.strip() != serviceDate.strip():
            errors.append(f"To Date mismatch: expected '{serviceDate}', got '{actualToDate}'")
        
        # Validate Place of Service
        placeOfServiceSelect = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.placeOfService"))
        )
        select = Select(placeOfServiceSelect)
        selectedValue = select.first_selected_option.get_attribute("value")
        if selectedValue != placeOfService:
            errors.append(f"Place of Service mismatch: expected '{placeOfService}', got '{selectedValue}'")
        
        # Validate Procedure Code
        procedureCodeInput = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.procedureCode"))
        )
        actualProcedureCode = procedureCodeInput.get_attribute("value") or ""
        if actualProcedureCode.strip() != procedureCode.strip():
            errors.append(f"Procedure Code mismatch: expected '{procedureCode}', got '{actualProcedureCode}'")
        
        # Validate Charges (remove $ and spaces for comparison)
        chargesInput = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.amount"))
        )
        actualCharges = chargesInput.get_attribute("value") or ""
        expectedCharges = re.sub(r'[\$\s]', '', charges)
        actualChargesClean = re.sub(r'[\$\s]', '', actualCharges)
        if actualChargesClean.strip() != expectedCharges.strip():
            errors.append(f"Charges mismatch: expected '{expectedCharges}', got '{actualChargesClean}'")
        
        # Validate Units
        unitsInput = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.daysUnits"))
        )
        actualUnits = unitsInput.get_attribute("value") or ""
        # Handle float values (e.g., "1.0" vs "1")
        try:
            actualUnitsFloat = float(actualUnits)
            expectedUnitsFloat = float(units)
            if actualUnitsFloat != expectedUnitsFloat:
                errors.append(f"Units mismatch: expected '{units}', got '{actualUnits}'")
        except:
            if str(actualUnits).strip() != str(units).strip():
                errors.append(f"Units mismatch: expected '{units}', got '{actualUnits}'")
        
        # Validate Unit Type
        unitTypeSelect = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.serviceUnitQualifier"))
        )
        selectUnitType = Select(unitTypeSelect)
        selectedUnitType = selectUnitType.first_selected_option.get_attribute("value")
        if selectedUnitType != "UN":
            errors.append(f"Unit Type mismatch: expected 'UN', got '{selectedUnitType}'")
        
        # Validate Diagnosis Codes are selected (only the specified ones)
        if diagnosisCodes and len(diagnosisCodes) > 0:
            # Normalize diagnosis codes for matching
            normalizedCodes = []
            for code in diagnosisCodes:
                normalized = code.replace('.', '').rstrip('X').upper()
                normalizedCodes.append(normalized)
            
            diagnosisCheckboxes = driver.find_elements(By.CSS_SELECTOR, "input[name='potentialServiceLineDiagCodes'][type='checkbox']")
            selectedCodes = []
            for checkbox in diagnosisCheckboxes:
                checkboxValue = checkbox.get_attribute('value') or ''
                normalizedCheckboxValue = checkboxValue.replace('.', '').rstrip('X').upper()
                if checkbox.is_selected():
                    selectedCodes.append(normalizedCheckboxValue)
            
            # Check if all required codes are selected
            missingCodes = [code for code in normalizedCodes if code not in selectedCodes]
            if missingCodes:
                errors.append(f"Missing diagnosis codes: {missingCodes}")
            
            # Check if any extra codes are selected
            extraCodes = [code for code in selectedCodes if code not in normalizedCodes]
            if extraCodes:
                errors.append(f"Extra diagnosis codes selected: {extraCodes}")
        
        # Check for validation errors
        hasErrors, errorMessages = checkForValidationErrors(driver)
        if hasErrors:
            errors.extend([f"Form validation error: {msg}" for msg in errorMessages])
        
        if errors:
            print(f"[VALIDATION] Found {len(errors)} validation error(s):")
            for error in errors:
                print(f"  - {error}")
            return False, errors
        else:
            print("[VALIDATION] All service line fields validated successfully")
            return True, []
    except Exception as e:
        errors.append(f"Validation exception: {e}")
        return False, errors

def fillSingleServiceLine(driver, serviceDate, placeOfService, procedureCode, modifier, diagnosisCodes, charges, units, ndc=None):
    """Fill a single Service Line form with all fields"""
    # Fill Dates of Service
    if not fillDatesOfService(driver, serviceDate):
        return False
    
    # Select Place of Service
    if not selectPlaceOfService(driver, placeOfService):
        return False
    
    # Fill Procedure Code
    if not fillProcedureCode(driver, procedureCode):
        return False
    
    # Add Modifier if provided (this will reload the page)
    if not addModifier(driver, modifier):
        return False
    
    # Refetch page data after modifier addition (JS changes the page)
    time.sleep(0.5)
    if not waitForServiceLinesFormToLoad(driver):
        print("[WARNING] Form reload check failed after modifier addition, continuing anyway...")
    
    # Select specified Diagnosis Codes (not all)
    if not selectDiagnosisCodes(driver, diagnosisCodes):
        return False
    
    # Fill Charges
    if not fillCharges(driver, charges):
        return False
    
    # Fill Units
    if not fillUnits(driver, units, "UN"):
        return False
    
    # Fill NDC if provided
    if ndc:
        if not fillNDC(driver, ndc):
            return False
    
    return True
