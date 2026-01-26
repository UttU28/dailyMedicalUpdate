#!/usr/bin/env python3
"""
Step 4: Fill Service Lines form
"""

import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

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
        time.sleep(2)
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
        time.sleep(0.5)
        fromDateInput.send_keys(serviceDate)
        time.sleep(1)
        print(f"[INFO] Entered From Date: {serviceDate}")
        
        # Fill To Date
        toDateInput = wait.until(
            EC.presence_of_element_located((By.ID, "activeProfessionalServiceLine.toDate"))
        )
        toDateInput.clear()
        time.sleep(0.5)
        toDateInput.send_keys(serviceDate)
        time.sleep(1)
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
        time.sleep(1)
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
        time.sleep(0.5)
        procedureCodeInput.send_keys(procedureCode)
        time.sleep(0.5)
        print(f"[INFO] Entered Procedure Code: {procedureCode}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Procedure Code: {e}")
        return False

def selectAllDiagnosisCodes(driver):
    """Select all diagnosis code checkboxes"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Find all diagnosis code checkboxes
        diagnosisCheckboxes = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[name='potentialServiceLineDiagCodes'][type='checkbox']"))
        )
        
        selectedCount = 0
        for checkbox in diagnosisCheckboxes:
            if not checkbox.is_selected():
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                time.sleep(0.2)
                checkbox.click()
                selectedCount += 1
        
        time.sleep(0.5)
        print(f"[INFO] Selected {selectedCount} diagnosis code(s)")
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
        time.sleep(0.5)
        chargesInput.send_keys(chargesValue)
        time.sleep(0.5)
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
        time.sleep(0.5)
        unitsInput.send_keys(str(units))
        time.sleep(0.5)
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
        time.sleep(1)
        
        saveButton.click()
        print("[INFO] Clicked Save / Update button")
        
        # Wait for page to reload (soft reload with JS)
        time.sleep(3)
        
        # Wait for form to reload
        try:
            wait.until(
                EC.presence_of_element_located((By.ID, "slform"))
            )
            print("[INFO] Page reloaded after Save / Update")
        except:
            time.sleep(2)
            print("[INFO] Waiting for page reload...")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to click Save / Update button: {e}")
        return False

def clickNextButton(driver):
    """Click the Next button after service line is saved"""
    try:
        wait = WebDriverWait(driver, 20)
        
        # After saving service line, the page reloads and Next button appears
        print("[INFO] Waiting for Next button to appear after page reload...")
        
        # Wait for Next button to be clickable
        nextButton = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='_eventId_next']"))
        )
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", nextButton)
        time.sleep(1)
        
        nextButton.click()
        print("[INFO] Clicked Next button")
        time.sleep(3)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to click Next button: {e}")
        return False

def isOnServiceLinesPage(driver):
    """Check if we're still on the Service Lines page"""
    try:
        wait = WebDriverWait(driver, 3)
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Service Lines')]"))
        )
        return True
    except:
        return False

def isOnProviderDetailsPage(driver):
    """Check if we're on the Provider Details page"""
    try:
        wait = WebDriverWait(driver, 3)
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Provider Details')]"))
        )
        return True
    except:
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

def validateServiceLineFields(driver, serviceDate, placeOfService, procedureCode, charges, units):
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
        
        # Validate Diagnosis Codes are selected
        diagnosisCheckboxes = driver.find_elements(By.CSS_SELECTOR, "input[name='potentialServiceLineDiagCodes'][type='checkbox']")
        unselectedCount = 0
        for checkbox in diagnosisCheckboxes:
            if not checkbox.is_selected():
                unselectedCount += 1
        if unselectedCount == len(diagnosisCheckboxes):
            errors.append("No diagnosis codes are selected")
        elif unselectedCount > 0:
            errors.append(f"{unselectedCount} diagnosis code(s) are not selected")
        
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

def fillAllServiceLineFields(driver, serviceDate, placeOfService, procedureCode, charges, units):
    """Fill all Service Line form fields"""
    # Fill Dates of Service
    if not fillDatesOfService(driver, serviceDate):
        return False
    
    time.sleep(0.3)
    
    # Select Place of Service (default to "11")
    if not selectPlaceOfService(driver, placeOfService):
        return False
    
    time.sleep(0.3)
    
    # Fill Procedure Code
    if not fillProcedureCode(driver, procedureCode):
        return False
    
    time.sleep(0.3)
    
    # Select all Diagnosis Codes
    if not selectAllDiagnosisCodes(driver):
        return False
    
    time.sleep(0.3)
    
    # Fill Charges
    if not fillCharges(driver, charges):
        return False
    
    time.sleep(0.3)
    
    # Fill Units
    if not fillUnits(driver, units, "UN"):
        return False
    
    return True

def executeStep4(driver, serviceDate, procedureCode, charges, units):
    """Execute step 4: Fill Service Lines form with retry logic and validation checks"""
    try:
        if not serviceDate:
            raise ValueError("serviceDate is required")
        if not procedureCode:
            raise ValueError("procedureCode is required")
        if not charges:
            raise ValueError("charges is required")
        if not units:
            raise ValueError("units is required")
        
        # Default Place of Service to "11"
        placeOfService = "11"
        
        print(f"[INFO] Using Service Date: {serviceDate}")
        print(f"[INFO] Using Place of Service: {placeOfService} (default)")
        print(f"[INFO] Using Procedure Code: {procedureCode}")
        print(f"[INFO] Using Charges: {charges}")
        print(f"[INFO] Using Units: {units}")
        
        maxRetries = 3
        retryCount = 0
        
        while retryCount < maxRetries:
            retryCount += 1
            print(f"\n[INFO] Step 4 attempt {retryCount}/{maxRetries}")
            
            # Wait for form to load initially
            if not waitForServiceLinesFormToLoad(driver):
                if retryCount < maxRetries:
                    print("[WARNING] Form did not load, retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Service Lines form did not load properly after retries")
            
            # Fill all form fields
            if not fillAllServiceLineFields(driver, serviceDate, placeOfService, procedureCode, charges, units):
                if retryCount < maxRetries:
                    print("[WARNING] Failed to fill form, retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Failed to fill form after retries")
            
            # Wait for fields to be processed
            time.sleep(2)
            
            # Validate all fields are filled correctly
            isValid, validationErrors = validateServiceLineFields(driver, serviceDate, placeOfService, procedureCode, charges, units)
            if not isValid:
                if retryCount < maxRetries:
                    print(f"[WARNING] Validation failed with {len(validationErrors)} error(s), retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception(f"Validation failed after retries: {validationErrors}")
            
            time.sleep(1)
            
            # Click Save / Update button
            if not clickSaveUpdateButton(driver):
                if retryCount < maxRetries:
                    print("[WARNING] Failed to click Save/Update button, retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Failed to click Save/Update button after retries")
            
            # Refetch page data after reload (JS changes the page)
            time.sleep(2)
            if not waitForServiceLinesFormToLoad(driver):
                print("[WARNING] Form reload check failed, continuing anyway...")
            
            # Wait a bit more for JS to finish updating the page
            time.sleep(2)
            
            # Check if we successfully moved to next page (service line saved)
            # After save, we should still be on Service Lines page but with Next button enabled
            # So we check if Next button is available
            try:
                wait = WebDriverWait(driver, 5)
                nextButton = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='_eventId_next']"))
                )
                print("[INFO] Next button is available, service line saved successfully")
            except:
                # Next button not available, might still be processing
                if retryCount < maxRetries:
                    print("[WARNING] Next button not yet available, retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Next button not available after Save/Update")
            
            # Click Next button
            if not clickNextButton(driver):
                if retryCount < maxRetries:
                    print("[WARNING] Failed to click Next button, retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Failed to click Next button after retries")
            
            # Wait for page to potentially change
            time.sleep(3)
            
            # Check if we successfully moved to next page
            if not isOnServiceLinesPage(driver):
                # We're no longer on Service Lines page, success!
                print("[INFO] Successfully moved to next page")
                break
            else:
                # Still on Service Lines page, need to retry
                if retryCount < maxRetries:
                    print("[WARNING] Still on Service Lines page, form may not have submitted. Retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Still on Service Lines page after all retries")
        
        print("[INFO] Step 4 completed: Service Line added and Next button clicked")
        return True
        
    except Exception as e:
        print(f"[ERROR] Step 4 failed: {e}")
        raise
