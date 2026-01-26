#!/usr/bin/env python3
"""
Step 2: Fill General Info form on Professional Claim page
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

def waitForFormToLoad(driver):
    """Wait for the General Info form to be fully loaded"""
    try:
        wait = WebDriverWait(driver, 20)
        
        # Wait for the form to be present
        print("[INFO] Waiting for General Info form to load...")
        wait.until(
            EC.presence_of_element_located((By.ID, "webProfClaimsModel"))
        )
        
        # Wait for "General Info" section header
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'General Info')]"))
        )
        
        # Wait a bit more for JavaScript to finish rendering
        time.sleep(2)
        print("[INFO] General Info form is ready")
        return True
    except Exception as e:
        print(f"[ERROR] Form did not load: {e}")
        return False

def fillPatientAccountNumber(driver, accountNumber):
    """Fill Patient's Account Number"""
    try:
        wait = WebDriverWait(driver, 10)
        accountInput = wait.until(
            EC.presence_of_element_located((By.ID, "profClaim.patCtrlNbr"))
        )
        accountInput.clear()
        time.sleep(0.2)
        accountInput.send_keys(accountNumber)
        time.sleep(0.2)
        print(f"[INFO] Entered Patient's Account Number: {accountNumber}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Patient's Account Number: {e}")
        return False

def fillStatementDates(driver, startDate, endDate):
    """Fill Statement Start Date and End Date"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Fill Start Date
        startDateInput = wait.until(
            EC.presence_of_element_located((By.ID, "profClaim.statementStartDate"))
        )
        startDateInput.clear()
        time.sleep(0.2)
        startDateInput.send_keys(startDate)
        time.sleep(1)  # Extra sleep for date field
        print(f"[INFO] Entered Statement Start Date: {startDate}")
        
        # Wait before filling next field
        time.sleep(0.2)
        
        # Fill End Date
        endDateInput = wait.until(
            EC.presence_of_element_located((By.ID, "profClaim.statementEndDate"))
        )
        endDateInput.clear()
        time.sleep(0.2)
        endDateInput.send_keys(endDate)
        time.sleep(1)  # Extra sleep for date field
        print(f"[INFO] Entered Statement End Date: {endDate}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Statement Dates: {e}")
        return False

def fillCurrentIllness(driver, illnessDate):
    """Select Current Illness or Injury and fill the date"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Select "Current Illness or Injury" from dropdown
        illnessDropdown = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.professionalClaimDate.illnessLmpQual"))
        )
        select = Select(illnessDropdown)
        select.select_by_value("431")  # Current Illness or Injury
        time.sleep(1)  # Wait for dropdown selection to process
        print("[INFO] Selected 'Current Illness or Injury' from dropdown")
        
        # Wait before filling date field
        time.sleep(0.2)
        
        # Fill the illness date
        illnessDateInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.professionalClaimDate.illnessImpDate"))
        )
        illnessDateInput.clear()
        time.sleep(0.2)
        illnessDateInput.send_keys(illnessDate)
        time.sleep(1)  # Extra sleep for date field
        print(f"[INFO] Entered Current Illness Date: {illnessDate}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Current Illness: {e}")
        return False

def fillCLIANumber(driver, cliaNumber):
    """Fill CLIA Number"""
    try:
        wait = WebDriverWait(driver, 10)
        cliaInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.cliaNbr"))
        )
        cliaInput.clear()
        time.sleep(0.2)
        cliaInput.send_keys(cliaNumber)
        time.sleep(0.2)
        print(f"[INFO] Entered CLIA Number: {cliaNumber}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill CLIA Number: {e}")
        return False

def clickNextButton(driver):
    """Click the Next button to proceed to next step"""
    try:
        wait = WebDriverWait(driver, 10)
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

def isOnGeneralInfoPage(driver):
    """Check if we're still on the General Info page"""
    try:
        wait = WebDriverWait(driver, 3)
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'General Info')]"))
        )
        return True
    except:
        return False

def isOnDiagnosisCodesPage(driver):
    """Check if we're on the Diagnosis Codes page"""
    try:
        wait = WebDriverWait(driver, 3)
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Diagnosis Codes')]"))
        )
        return True
    except:
        return False

def validateGeneralInfoForm(driver, patientAccountNumber, providerSignatureDate, cliaNumber):
    """Validate all General Info form fields are filled correctly"""
    errors = []
    try:
        wait = WebDriverWait(driver, 5)
        
        # Validate Patient Account Number
        accountInput = wait.until(
            EC.presence_of_element_located((By.ID, "profClaim.patCtrlNbr"))
        )
        actualValue = accountInput.get_attribute("value") or ""
        if actualValue.strip() != patientAccountNumber.strip():
            errors.append(f"Patient Account Number mismatch: expected '{patientAccountNumber}', got '{actualValue}'")
        
        # Validate Statement Start Date
        startDateInput = wait.until(
            EC.presence_of_element_located((By.ID, "profClaim.statementStartDate"))
        )
        actualStartDate = startDateInput.get_attribute("value") or ""
        if actualStartDate.strip() != providerSignatureDate.strip():
            errors.append(f"Statement Start Date mismatch: expected '{providerSignatureDate}', got '{actualStartDate}'")
        
        # Validate Statement End Date
        endDateInput = wait.until(
            EC.presence_of_element_located((By.ID, "profClaim.statementEndDate"))
        )
        actualEndDate = endDateInput.get_attribute("value") or ""
        if actualEndDate.strip() != providerSignatureDate.strip():
            errors.append(f"Statement End Date mismatch: expected '{providerSignatureDate}', got '{actualEndDate}'")
        
        # Validate Current Illness dropdown
        illnessDropdown = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.professionalClaimDate.illnessLmpQual"))
        )
        select = Select(illnessDropdown)
        selectedValue = select.first_selected_option.get_attribute("value")
        if selectedValue != "431":
            errors.append(f"Current Illness dropdown mismatch: expected '431', got '{selectedValue}'")
        
        # Validate Current Illness Date
        illnessDateInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.professionalClaimDate.illnessImpDate"))
        )
        actualIllnessDate = illnessDateInput.get_attribute("value") or ""
        if actualIllnessDate.strip() != providerSignatureDate.strip():
            errors.append(f"Current Illness Date mismatch: expected '{providerSignatureDate}', got '{actualIllnessDate}'")
        
        # Validate CLIA Number
        cliaInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.cliaNbr"))
        )
        actualClia = cliaInput.get_attribute("value") or ""
        if actualClia.strip() != cliaNumber.strip():
            errors.append(f"CLIA Number mismatch: expected '{cliaNumber}', got '{actualClia}'")
        
        # Check for validation errors on page
        errorMessages = driver.find_elements(By.CSS_SELECTOR, ".help-inline, .error, [class*='error']")
        for error in errorMessages:
            errorText = error.text.strip()
            if errorText and errorText.lower() not in ['', 'required field'] and error.is_displayed():
                errors.append(f"Form validation error: {errorText}")
        
        if errors:
            print(f"[VALIDATION] Found {len(errors)} validation error(s):")
            for error in errors:
                print(f"  - {error}")
            return False, errors
        else:
            print("[VALIDATION] All fields validated successfully")
            return True, []
    except Exception as e:
        errors.append(f"Validation exception: {e}")
        return False, errors

def fillGeneralInfoForm(driver, patientAccountNumber, providerSignatureDate, cliaNumber):
    """Fill all General Info form fields"""
    # Fill Patient's Account Number
    if not fillPatientAccountNumber(driver, patientAccountNumber):
        return False
    
    # Wait between fields
    time.sleep(0.3)
    
    # Fill Statement Dates (start and end with same date)
    if not fillStatementDates(driver, providerSignatureDate, providerSignatureDate):
        return False
    
    # Wait between fields
    time.sleep(0.3)
    
    # Fill Current Illness
    if not fillCurrentIllness(driver, providerSignatureDate):
        return False
    
    # Wait between fields
    time.sleep(0.3)
    
    # Fill CLIA Number
    if not fillCLIANumber(driver, cliaNumber):
        return False
    
    return True

def executeStep2(driver, patientAccountNumber, providerSignatureDate, cliaNumber):
    """Execute step 2: Fill General Info form with retry logic"""
    try:
        if not patientAccountNumber:
            raise ValueError("patientAccountNumber is required")
        if not providerSignatureDate:
            raise ValueError("providerSignatureDate is required")
        if not cliaNumber:
            raise ValueError("cliaNumber is required")
        
        print(f"[INFO] Using Patient Account Number: {patientAccountNumber}")
        print(f"[INFO] Using Statement Date: {providerSignatureDate}")
        print(f"[INFO] Using CLIA Number: {cliaNumber}")
        
        maxRetries = 3
        retryCount = 0
        
        while retryCount < maxRetries:
            retryCount += 1
            print(f"\n[INFO] Step 2 attempt {retryCount}/{maxRetries}")
            
            # Wait for form to load
            if not waitForFormToLoad(driver):
                if retryCount < maxRetries:
                    print("[WARNING] Form did not load, retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Form did not load properly after retries")
            
            # Fill all form fields
            if not fillGeneralInfoForm(driver, patientAccountNumber, providerSignatureDate, cliaNumber):
                if retryCount < maxRetries:
                    print("[WARNING] Failed to fill form, retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Failed to fill form after retries")
            
            # Wait for fields to be processed
            time.sleep(2)
            
            # Validate all fields are filled correctly
            isValid, validationErrors = validateGeneralInfoForm(driver, patientAccountNumber, providerSignatureDate, cliaNumber)
            if not isValid:
                if retryCount < maxRetries:
                    print(f"[WARNING] Validation failed with {len(validationErrors)} error(s), retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception(f"Validation failed after retries: {validationErrors}")
            
            # Wait a moment before clicking Next
            time.sleep(2)
            
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
            if not isOnGeneralInfoPage(driver):
                # We're no longer on General Info page, success!
                print("[INFO] Successfully moved to next page")
                break
            else:
                # Still on General Info page, need to retry
                if retryCount < maxRetries:
                    print("[WARNING] Still on General Info page, form may not have submitted. Retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Still on General Info page after all retries")
        
        print("[INFO] Step 2 completed: General Info form submitted successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Step 2 failed: {e}")
        raise
