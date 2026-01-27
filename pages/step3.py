#!/usr/bin/env python3
"""
Step 3: Fill Diagnosis Codes form
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def waitForDiagnosisFormToLoad(driver):
    """Wait for the Diagnosis Codes form to be fully loaded"""
    try:
        wait = WebDriverWait(driver, 20)
        
        # Wait for the form to be present
        print("[INFO] Waiting for Diagnosis Codes form to load...")
        wait.until(
            EC.presence_of_element_located((By.ID, "webProfClaimsModel"))
        )
        
        # Wait for "Diagnosis Codes" section header
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Diagnosis Codes')]"))
        )
        
        # Wait for the diagnosis code input field to be present
        wait.until(
            EC.presence_of_element_located((By.ID, "diagnosisCode.code"))
        )
        
        # Wait a bit more for JavaScript to finish rendering
        time.sleep(0.5)
        print("[INFO] Diagnosis Codes form is ready")
        return True
    except Exception as e:
        print(f"[ERROR] Form did not load: {e}")
        return False

def addDiagnosisCode(driver, codeValue):
    """Add a single diagnosis code"""
    try:
        wait = WebDriverWait(driver, 20)
        
        # Wait for the input field to be available and clear
        codeInput = wait.until(
            EC.presence_of_element_located((By.ID, "diagnosisCode.code"))
        )
        codeInput.clear()
        codeInput.send_keys(codeValue)
        print(f"[INFO] Entered diagnosis code: {codeValue}")
        
        # Find and click the Add button
        addButton = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='_eventId_addWebProfIcdCode']"))
        )
        
        # Scroll into view if needed
        driver.execute_script("arguments[0].scrollIntoView(true);", addButton)
        time.sleep(0.5)
        
        # Click the Add button
        addButton.click()
        print(f"[INFO] Clicked Add button for code: {codeValue}")
        
        # Wait for page to reload (soft reload with JS)
        time.sleep(0.5)
        
        # Wait for the form to reload - wait for input field to be present and enabled again
        try:
            # Wait for the input field to be present and empty (indicating page reloaded)
            wait.until(
                lambda d: d.find_element(By.ID, "diagnosisCode.code").is_displayed() and 
                         d.find_element(By.ID, "diagnosisCode.code").get_attribute("value") == ""
            )
            print(f"[INFO] Page reloaded after adding code: {codeValue}")
        except:
            # Alternative: just wait for element to be present
            try:
                wait.until(
                    EC.presence_of_element_located((By.ID, "diagnosisCode.code"))
                )
                print(f"[INFO] Page reloaded after adding code: {codeValue}")
            except:
                # Give it more time and continue
                time.sleep(0.5)
                print(f"[INFO] Waiting for page reload after adding code: {codeValue}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to add diagnosis code {codeValue}: {e}")
        return False

def isOnDiagnosisCodesPage(driver):
    """Check if we're still on the Diagnosis Codes page"""
    try:
        wait = WebDriverWait(driver, 3)
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Diagnosis Codes')]"))
        )
        return True
    except:
        return False

def isOnServiceLinesPage(driver):
    """Check if we're on the Service Lines page"""
    try:
        wait = WebDriverWait(driver, 3)
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Service Lines')]"))
        )
        return True
    except:
        return False

def validateDiagnosisCodes(driver, expectedCodes):
    """Validate all diagnosis codes are added correctly"""
    errors = []
    try:
        wait = WebDriverWait(driver, 5)
        
        # Get page source for basic check
        pageSource = driver.page_source
        
        # Try to find diagnosis codes in various HTML structures
        foundCodes = []
        
        # Method 1: Check page source (most reliable)
        for code in expectedCodes:
            # Check both with and without dots
            normalizedCode = code.replace(".", "")
            if code in pageSource or normalizedCode in pageSource:
                foundCodes.append(code)
            else:
                errors.append(f"Diagnosis code '{code}' not found on page after adding")
        
        # Method 2: Try to find in table rows or list items
        try:
            # Look for table rows containing diagnosis codes
            tableRows = driver.find_elements(By.CSS_SELECTOR, "table tr, tbody tr, .diagnosis-code, [class*='diagnosis']")
            for row in tableRows:
                rowText = row.text
                for code in expectedCodes:
                    if code in rowText and code not in foundCodes:
                        foundCodes.append(code)
        except:
            pass
        
        # Method 3: Try to find in any visible text elements
        try:
            allTextElements = driver.find_elements(By.XPATH, "//*[contains(text(), '.')]")
            for element in allTextElements:
                elementText = element.text
                for code in expectedCodes:
                    if code in elementText and code not in foundCodes:
                        foundCodes.append(code)
        except:
            pass
        
        # Final validation: ensure all codes were found
        missingCodes = [code for code in expectedCodes if code not in foundCodes]
        if missingCodes:
            errors.extend([f"Diagnosis code '{code}' not found on page after adding" for code in missingCodes])
        
        # Check for validation errors
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
            print(f"[VALIDATION] All {len(expectedCodes)} diagnosis codes validated successfully")
            return True, []
    except Exception as e:
        errors.append(f"Validation exception: {e}")
        return False, errors

def addAllDiagnosisCodes(driver, diagnosisCodes):
    """Add all diagnosis codes one by one"""
    for index, codeValue in enumerate(diagnosisCodes, 1):
        print(f"\n[INFO] Adding diagnosis code {index}/{len(diagnosisCodes)}: {codeValue}")
        
        # Refetch page data by waiting for form to be ready
        if index > 1:
            # For subsequent codes, wait for form to reload
            if not waitForDiagnosisFormToLoad(driver):
                print(f"[WARNING] Form reload check failed, continuing anyway...")
                time.sleep(0.5)
        
        # Add the diagnosis code
        if not addDiagnosisCode(driver, codeValue):
            return False
        
        # Wait a bit more for the page to stabilize
        time.sleep(0.5)
    
    return True

def executeStep3(driver, diagnosisCodes):
    """Execute step 3: Add all diagnosis codes one by one with retry logic"""
    try:
        if not diagnosisCodes or len(diagnosisCodes) == 0:
            raise ValueError("diagnosisCodes list is required and cannot be empty")
        
        print(f"[INFO] Adding {len(diagnosisCodes)} diagnosis codes")
        
        maxRetries = 3
        retryCount = 0
        
        while retryCount < maxRetries:
            retryCount += 1
            print(f"\n[INFO] Step 3 attempt {retryCount}/{maxRetries}")
            
            # Wait for form to load initially
            if not waitForDiagnosisFormToLoad(driver):
                if retryCount < maxRetries:
                    print("[WARNING] Form did not load, retrying...")
                    time.sleep(0.5)
                    continue
                else:
                    raise Exception("Diagnosis Codes form did not load properly after retries")
            
            # Add all diagnosis codes
            if not addAllDiagnosisCodes(driver, diagnosisCodes):
                if retryCount < maxRetries:
                    print("[WARNING] Failed to add all diagnosis codes, retrying...")
                    time.sleep(0.5)
                    continue
                else:
                    raise Exception("Failed to add all diagnosis codes after retries")
            
            print(f"\n[INFO] Successfully added all {len(diagnosisCodes)} diagnosis codes")
            
            # Wait for codes to be processed
            time.sleep(2)
            
            # Validate all diagnosis codes are added correctly
            isValid, validationErrors = validateDiagnosisCodes(driver, diagnosisCodes)
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
                    time.sleep(0.5)
                    continue
                else:
                    raise Exception("Failed to click Next button after retries")
            
            # Wait for page to potentially change
            time.sleep(0.5)
            
            # Check if we successfully moved to next page
            if not isOnDiagnosisCodesPage(driver):
                # We're no longer on Diagnosis Codes page, success!
                print("[INFO] Successfully moved to next page")
                break
            else:
                # Still on Diagnosis Codes page, need to retry
                if retryCount < maxRetries:
                    print("[WARNING] Still on Diagnosis Codes page, form may not have submitted. Retrying...")
                    time.sleep(0.5)
                    continue
                else:
                    raise Exception("Still on Diagnosis Codes page after all retries")
        
        print("[INFO] Step 3 completed: All diagnosis codes added and Next button clicked")
        return True
        
    except Exception as e:
        print(f"[ERROR] Step 3 failed: {e}")
        raise

def clickNextButton(driver):
    """Click the Next button to proceed to next step"""
    try:
        wait = WebDriverWait(driver, 10)
        nextButton = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='_eventId_next']"))
        )
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", nextButton)
        time.sleep(0.5)
        
        nextButton.click()
        print("[INFO] Clicked Next button")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to click Next button: {e}")
        return False
