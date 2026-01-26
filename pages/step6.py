#!/usr/bin/env python3
"""
Step 6: Handle Attachments page - just click Next
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def waitForAttachmentsFormToLoad(driver):
    """Wait for the Attachments form to be fully loaded"""
    try:
        wait = WebDriverWait(driver, 20)
        
        # Wait for the form to be present
        print("[INFO] Waiting for Attachments form to load...")
        wait.until(
            EC.presence_of_element_located((By.ID, "webProfClaimsModel"))
        )
        
        # Wait for "Attachments" section header
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Attachments')]"))
        )
        
        # Wait a bit more for JavaScript to finish rendering
        time.sleep(2)
        print("[INFO] Attachments form is ready")
        return True
    except Exception as e:
        print(f"[ERROR] Form did not load: {e}")
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

def isOnAttachmentsPage(driver):
    """Check if we're still on the Attachments page"""
    try:
        wait = WebDriverWait(driver, 3)
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Attachments')]"))
        )
        return True
    except:
        return False

def executeStep6(driver):
    """Execute step 6: Handle Attachments page - just click Next"""
    try:
        maxRetries = 3
        retryCount = 0
        
        while retryCount < maxRetries:
            retryCount += 1
            print(f"\n[INFO] Step 6 attempt {retryCount}/{maxRetries}")
            
            # Wait for form to load
            if not waitForAttachmentsFormToLoad(driver):
                if retryCount < maxRetries:
                    print("[WARNING] Form did not load, retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Attachments form did not load properly after retries")
            
            # Click Next button (no attachments needed)
            if not clickNextButton(driver):
                if retryCount < maxRetries:
                    print("[WARNING] Failed to click Next button, retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Failed to click Next button after retries")
            
            # Refetch page data after navigation
            time.sleep(2)
            
            # Check if we successfully moved to next page
            if not isOnAttachmentsPage(driver):
                # We're no longer on Attachments page, success!
                print("[INFO] Successfully moved to next page")
                break
            else:
                # Still on Attachments page, need to retry
                if retryCount < maxRetries:
                    print("[WARNING] Still on Attachments page, retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Still on Attachments page after all retries")
        
        print("[INFO] Step 6 completed: Attachments page handled successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Step 6 failed: {e}")
        raise
