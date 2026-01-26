#!/usr/bin/env python3
"""
Step 1: Open portal, find person, and click Professional Claim button
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.step0 import isLoginPage, isPasswordPage, executeStep0

def clickCreateClaimButton(driver):
    """Click the Create Claim button"""
    try:
        wait = WebDriverWait(driver, 10)
        createClaimButton = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-orange') and .//i[contains(@class, 'icon-create-claim')]]"))
        )
        createClaimButton.click()
        print("[INFO] Clicked Create Claim button")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to click Create Claim button: {e}")
        return False

def fillMemberSearchForm(driver, memberId, birthdate):
    """Fill the member search form and click Find"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Wait for the form to be visible (not hidden)
        form = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "form[action='/careconnect/eligibility/results']"))
        )
        print("[INFO] Member search form is now visible")
        
        # Fill Member ID or Last Name
        memberInput = wait.until(
            EC.presence_of_element_located((By.NAME, "memberIdOrLastName"))
        )
        memberInput.clear()
        memberInput.send_keys(memberId)
        print(f"[INFO] Entered Member ID: {memberId}")
        
        # Fill Birthdate
        dobInput = wait.until(
            EC.presence_of_element_located((By.NAME, "dob"))
        )
        dobInput.clear()
        dobInput.send_keys(birthdate)
        print(f"[INFO] Entered Birthdate: {birthdate}")
        
        # Wait 1 second before clicking Find button
        time.sleep(1)
        
        # Click Find button
        findButton = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "form[action='/careconnect/eligibility/results'] button[type='submit']"))
        )
        findButton.click()
        print("[INFO] Clicked Find button")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill member search form: {e}")
        return False

def clickProfessionalClaimButton(driver):
    """Click the Professional Claim button on the claim type selection page"""
    try:
        wait = WebDriverWait(driver, 20)
        
        # Wait for page to be ready - wait for "Choose a Claim Type" text to appear
        print("[INFO] Waiting for claim type selection page to load...")
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Choose a Claim Type')]"))
        )
        print("[INFO] Claim type selection page detected")
        
        # Wait a bit more for JavaScript to finish rendering
        time.sleep(2)
        
        # Wait for the main content section to be visible
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.mainContent"))
        )
        
        # Try multiple selector strategies for the Professional Claim button
        professionalClaimButton = None
        shortWait = WebDriverWait(driver, 5)
        
        try:
            professionalClaimButton = shortWait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '_eventId=profClaim')]"))
            )
            print("[INFO] Found Professional Claim button by href")
        except:
            pass
        
        if not professionalClaimButton:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, "a.btn-success")
                for btn in buttons:
                    href = btn.get_attribute("href") or ""
                    text = btn.text or ""
                    if "Professional Claim" in text or "_eventId=profClaim" in href:
                        professionalClaimButton = btn
                        print("[INFO] Found Professional Claim button by iterating buttons")
                        break
            except Exception as e:
                print(f"[DEBUG] Strategy 4 failed: {e}")
                pass
        
        if not professionalClaimButton:
            raise Exception("Could not find Professional Claim button with any selector strategy")
        
        # Scroll into view if needed
        driver.execute_script("arguments[0].scrollIntoView(true);", professionalClaimButton)
        time.sleep(1)
        
        # Click the button
        professionalClaimButton.click()
        print("[INFO] Clicked Professional Claim button")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to click Professional Claim button: {e}")
        # Print current page source snippet for debugging
        try:
            pageSource = driver.page_source
            if "Choose a Claim Type" in pageSource:
                print("[DEBUG] Page contains 'Choose a Claim Type' text")
            if "_eventId=profClaim" in pageSource:
                print("[DEBUG] Page contains '_eventId=profClaim' in source")
            else:
                print("[DEBUG] Page does NOT contain '_eventId=profClaim' in source")
        except:
            pass
        return False

def executeStep1(driver, insuredId, insuredDob):
    """Execute step 1: Open portal, find person, and click Professional Claim"""
    try:
        if not insuredId:
            raise ValueError("insuredId is required")
        if not insuredDob:
            raise ValueError("insuredDob is required")
        
        print(f"[INFO] Using Member ID: {insuredId}")
        print(f"[INFO] Using Birthdate: {insuredDob}")
        
        # Navigate to claims page
        claimsUrl = "https://provider.superiorhealthplan.com/careconnect/claims/viewClaimsHome"
        print(f"[INFO] Opening {claimsUrl}...")
        driver.get(claimsUrl)
        time.sleep(3)
        print(f"[INFO] Current URL: {driver.current_url}")
        
        # Check if we were redirected to login page
        if isLoginPage(driver) or isPasswordPage(driver):
            print("[INFO] Login page detected, handling login...")
            executeStep0(driver)
            # Navigate back to claims page after login
            print(f"[INFO] Navigating back to {claimsUrl}...")
            driver.get(claimsUrl)
            time.sleep(3)
            print(f"[INFO] Current URL after login: {driver.current_url}")
        
        # Click Create Claim button
        if not clickCreateClaimButton(driver):
            # Check again if we're on login page (might have been redirected)
            if isLoginPage(driver) or isPasswordPage(driver):
                print("[INFO] Redirected to login page, handling login...")
                executeStep0(driver)
                # Navigate back to claims page after login
                print(f"[INFO] Navigating back to {claimsUrl}...")
                driver.get(claimsUrl)
                time.sleep(3)
                # Retry clicking Create Claim button
                if not clickCreateClaimButton(driver):
                    raise Exception("Failed to click Create Claim button after login")
            else:
                raise Exception("Failed to click Create Claim button")
        
        # Fill member search form and click Find
        if not fillMemberSearchForm(driver, insuredId, insuredDob):
            raise Exception("Failed to fill member search form")
        
        print("[INFO] Member search form submitted successfully")
        
        # Wait for navigation to complete and page to load
        print("[INFO] Waiting for page navigation...")
        time.sleep(5)
        
        # Wait for page to be ready - check if we're on the right page
        print(f"[INFO] Current URL: {driver.current_url}")
        wait = WebDriverWait(driver, 20)
        try:
            # Wait for the claim type selection page header to appear
            wait.until(
                EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Choose a Claim Type')]"))
            )
            print("[INFO] Claim type selection page is ready")
        except Exception as e:
            print(f"[INFO] Waiting for page elements... ({e})")
            # Give it more time
            time.sleep(3)
        
        # Click Professional Claim button
        if not clickProfessionalClaimButton(driver):
            raise Exception("Failed to click Professional Claim button")
        
        print("[INFO] Step 1 completed: Professional Claim page opened")
        return True
        
    except Exception as e:
        print(f"[ERROR] Step 1 failed: {e}")
        raise
