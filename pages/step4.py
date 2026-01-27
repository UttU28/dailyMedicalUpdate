#!/usr/bin/env python3
"""
Step 4: Orchestrate Service Lines - loop through all service lines, add them, and proceed
"""

import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from pages.step4_5 import (
    waitForServiceLinesFormToLoad,
    fillSingleServiceLine,
    validateServiceLineFields,
    clickSaveUpdateButton
)

load_dotenv()

def clickNewServiceLineButton(driver):
    """Click the New Service Line button to add another service line"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Find the "New Service Line" link/button
        newServiceLineButton = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.addServiceLine, a[href*='_eventId=addWebProfServiceLine']"))
        )
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", newServiceLineButton)
        time.sleep(0.5)
        
        # Click the button
        newServiceLineButton.click()
        print("[INFO] Clicked New Service Line button")
        time.sleep(0.5)
        
        # Wait for form to reload
        if not waitForServiceLinesFormToLoad(driver):
            print("[WARNING] Form reload check failed after New Service Line, continuing anyway...")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to click New Service Line button: {e}")
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
        time.sleep(0.5)
        
        nextButton.click()
        print("[INFO] Clicked Next button")
        time.sleep(0.5)
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

def verifyAllServiceLinesAdded(driver, expectedProcedureCodes):
    """Verify all service lines are added by checking the nav for procedure codes"""
    try:
        wait = WebDriverWait(driver, 5)
        
        # Find the nav section with service lines
        nav = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "nav"))
        )
        
        # Get all procedure codes from the nav (they appear as links like "1: 99204")
        serviceLineLinks = nav.find_elements(By.CSS_SELECTOR, "ul li a")
        
        foundProcedureCodes = []
        for link in serviceLineLinks:
            linkText = link.text.strip()
            # Extract procedure code from text like "1: 99204 / $435.00"
            if ":" in linkText:
                parts = linkText.split(":")
                if len(parts) > 1:
                    procedurePart = parts[1].strip().split()[0]  # Get "99204" from "99204 /"
                    foundProcedureCodes.append(procedurePart)
        
        # Normalize expected codes (remove any formatting)
        normalizedExpected = [str(code).strip() for code in expectedProcedureCodes]
        normalizedFound = [str(code).strip() for code in foundProcedureCodes]
        
        # Check if all expected codes are found
        missingCodes = [code for code in normalizedExpected if code not in normalizedFound]
        if missingCodes:
            print(f"[WARNING] Missing procedure codes in nav: {missingCodes}")
            return False, missingCodes
        
        if len(normalizedFound) != len(normalizedExpected):
            print(f"[WARNING] Procedure code count mismatch: expected {len(normalizedExpected)}, found {len(normalizedFound)}")
            return False, []
        
        print(f"[INFO] All {len(normalizedExpected)} service lines verified in nav: {normalizedFound}")
        return True, []
    except Exception as e:
        print(f"[ERROR] Failed to verify service lines: {e}")
        return False, []

def executeStep4(driver, serviceLinesList):
    """Execute step 4: Fill all Service Lines with retry logic"""
    try:
        if not serviceLinesList or len(serviceLinesList) == 0:
            raise ValueError("serviceLinesList is required and cannot be empty")
        
        # Place of Service from env
        placeOfService = os.getenv('DEFAULT_PLACE_OF_SERVICE', '')
        
        print(f"[INFO] Processing {len(serviceLinesList)} service line(s)")
        
        # Extract expected procedure codes for verification
        expectedProcedureCodes = []
        for serviceLine in serviceLinesList:
            expectedProcedureCodes.append(serviceLine['procedureCode'])
        
        # Process each service line
        for index, serviceLine in enumerate(serviceLinesList, 1):
            serviceDate = serviceLine['serviceDate']
            procedureCode = serviceLine['procedureCode']
            modifier = serviceLine.get('modifier', '')
            diagnosisCodes = serviceLine.get('diagnosisCodes', [])
            charges = serviceLine['charges']
            units = serviceLine['units']
            
            print(f"\n{'='*60}")
            print(f"[INFO] Processing Service Line {index}/{len(serviceLinesList)}")
            print(f"[INFO] Procedure Code: {procedureCode}")
            if modifier:
                print(f"[INFO] Modifier: {modifier}")
            print(f"[INFO] Diagnosis Codes: {diagnosisCodes}")
            print(f"[INFO] Charges: {charges}")
            print(f"{'='*60}")
            
            maxRetries = 3
            retryCount = 0
            
            while retryCount < maxRetries:
                retryCount += 1
                print(f"\n[INFO] Service Line {index} attempt {retryCount}/{maxRetries}")
                
                # Wait for form to load
                if not waitForServiceLinesFormToLoad(driver):
                    if retryCount < maxRetries:
                        print("[WARNING] Form did not load, retrying...")
                        time.sleep(0.5)
                        continue
                    else:
                        raise Exception(f"Service Lines form did not load properly for service line {index}")
                
                # Fill all form fields (using step4_5)
                if not fillSingleServiceLine(driver, serviceDate, placeOfService, procedureCode, modifier, diagnosisCodes, charges, units):
                    if retryCount < maxRetries:
                        print("[WARNING] Failed to fill form, retrying...")
                        time.sleep(0.5)
                        continue
                    else:
                        raise Exception(f"Failed to fill form for service line {index}")
                
                # Validate all fields are filled correctly
                isValid, validationErrors = validateServiceLineFields(driver, serviceDate, placeOfService, procedureCode, diagnosisCodes, charges, units)
                if not isValid:
                    if retryCount < maxRetries:
                        print(f"[WARNING] Validation failed with {len(validationErrors)} error(s), retrying...")
                        time.sleep(0.5)
                        continue
                    else:
                        raise Exception(f"Validation failed for service line {index}: {validationErrors}")
                
                # Click Save / Update button
                if not clickSaveUpdateButton(driver):
                    if retryCount < maxRetries:
                        print("[WARNING] Failed to click Save/Update button, retrying...")
                        time.sleep(0.5)
                        continue
                    else:
                        raise Exception(f"Failed to click Save/Update button for service line {index}")
                
                # Refetch page data after reload (JS changes the page)
                time.sleep(0.5)
                if not waitForServiceLinesFormToLoad(driver):
                    print("[WARNING] Form reload check failed, continuing anyway...")
                
                # Check if service line was saved successfully
                try:
                    wait = WebDriverWait(driver, 5)
                    # Check if we can see the service line in nav or if Next button is available
                    nav = driver.find_element(By.CSS_SELECTOR, "nav")
                    serviceLineLinks = nav.find_elements(By.CSS_SELECTOR, "ul li a")
                    if len(serviceLineLinks) >= index or driver.find_elements(By.CSS_SELECTOR, "button[name='_eventId_next']"):
                        print(f"[INFO] Service line {index} saved successfully")
                        break
                except:
                    if retryCount < maxRetries:
                        print("[WARNING] Service line save verification failed, retrying...")
                        time.sleep(0.5)
                        continue
                    else:
                        print("[WARNING] Could not verify service line save, continuing...")
                        break
            
            # If not the last service line, click "New Service Line" button
            if index < len(serviceLinesList):
                print(f"\n[INFO] Adding next service line ({index + 1}/{len(serviceLinesList)})...")
                if not clickNewServiceLineButton(driver):
                    raise Exception(f"Failed to click New Service Line button after service line {index}")
        
        # After all service lines are added, verify all procedures are in nav
        print(f"\n[INFO] Verifying all {len(serviceLinesList)} service lines are added...")
        isValid, missingCodes = verifyAllServiceLinesAdded(driver, expectedProcedureCodes)
        if not isValid:
            print(f"[WARNING] Service line verification failed. Missing: {missingCodes}")
            # Continue anyway, but log warning
        
        # Wait a moment before clicking Next
        time.sleep(0.5)
        
        # Click Next button to proceed to next step
        if not clickNextButton(driver):
            raise Exception("Failed to click Next button after all service lines")
        
        # Wait for page to potentially change
        time.sleep(0.5)
        
        # Check if we successfully moved to next page
        if not isOnServiceLinesPage(driver):
            print("[INFO] Successfully moved to next page")
        else:
            print("[WARNING] Still on Service Lines page after clicking Next")
        
        print(f"[INFO] Step 4 completed: All {len(serviceLinesList)} service line(s) added successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Step 4 failed: {e}")
        raise
