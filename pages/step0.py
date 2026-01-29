#!/usr/bin/env python3
"""
Step 0: Handle login if required before proceeding to Step 1
"""

import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import load_env_file

load_env_file()

def isLoginPage(driver):
    """Check if we're on a login page"""
    try:
        # Check for login form elements
        wait = WebDriverWait(driver, 3)
        # Check for email/username input field
        wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        # Check for login form
        driver.find_element(By.NAME, "getUsername")
        return True
    except:
        return False

def isPasswordPage(driver):
    """Check if we're on the password page"""
    try:
        wait = WebDriverWait(driver, 3)
        # Check for password input field
        wait.until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        # Check for password form
        driver.find_element(By.NAME, "getPassword")
        return True
    except:
        return False

def fillEmailAndContinue(driver, email):
    """Fill email address and click Continue button"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Wait for email input field
        emailInput = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        
        # Clear and fill email
        emailInput.clear()
        time.sleep(0.2)
        emailInput.send_keys(email)
        time.sleep(0.2)
        print(f"[INFO] Entered email: {email}")
        
        # Wait for Continue button
        continueButton = wait.until(
            EC.element_to_be_clickable((By.ID, "nextButton"))
        )
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", continueButton)
        time.sleep(0.5)
        
        # Click Continue button
        continueButton.click()
        print("[INFO] Clicked Continue button")
        time.sleep(0.5)
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill email and continue: {e}")
        return False

def fillPasswordAndLogin(driver, password):
    """Fill password and click Login button"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Wait for password page to load
        if not isPasswordPage(driver):
            print("[WARNING] Password page not detected, waiting...")
            time.sleep(0.5)
        
        # Wait for password input field
        passwordInput = wait.until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        
        # Clear any existing password value
        passwordInput.clear()
        time.sleep(0.2)
        
        # Double-check: select all and delete to ensure it's completely cleared
        passwordInput.send_keys(Keys.CONTROL + "a")
        time.sleep(0.2)
        passwordInput.send_keys(Keys.DELETE)
        time.sleep(0.2)
        
        # Fill password
        passwordInput.send_keys(password)
        time.sleep(0.2)
        print("[INFO] Entered password")
        
        # Wait for Login button
        loginButton = wait.until(
            EC.element_to_be_clickable((By.ID, "loginButton"))
        )
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", loginButton)
        time.sleep(0.5)
        
        # Click Login button
        loginButton.click()
        print("[INFO] Clicked Login button")
        time.sleep(0.5)  # Wait for login to complete and redirect
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill password and login: {e}")
        return False

def executeStep0(driver):
    """Execute step 0: Handle login if required"""
    try:
        # Get credentials from environment variables
        email = os.getenv('LOGIN_EMAIL', '')
        password = os.getenv('LOGIN_PASSWORD', '')
        
        if not email or not password:
            print("[INFO] Login credentials not provided in env, skipping login")
            return True
        
        print(f"[INFO] Checking if login is required...")
        print(f"[INFO] Current URL: {driver.current_url}")
        
        # Check if we're on a login page
        if not isLoginPage(driver):
            print("[INFO] Not on login page, proceeding without login")
            return True
        
        print("[INFO] Login page detected, proceeding with login...")
        
        # Fill email and click Continue
        if not fillEmailAndContinue(driver, email):
            raise Exception("Failed to fill email and continue")
        
        # Wait for page to potentially change
        time.sleep(2)
        
        # Check if we're now on password page
        if not isPasswordPage(driver):
            print("[WARNING] Password page not detected after Continue, checking current state...")
            time.sleep(2)
            # Re-check
            if not isPasswordPage(driver):
                print("[INFO] May have logged in automatically or redirected, proceeding...")
                return True
        
        # Fill password and click Login
        if not fillPasswordAndLogin(driver, password):
            raise Exception("Failed to fill password and login")
        
        # Wait for redirect after login
        time.sleep(0.5)
        print(f"[INFO] Login completed. Current URL: {driver.current_url}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Step 0 (Login) failed: {e}")
        raise
