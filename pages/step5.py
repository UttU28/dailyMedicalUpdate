#!/usr/bin/env python3
"""
Step 5: Fill Provider Details form
"""

import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

def waitForProviderDetailsFormToLoad(driver):
    """Wait for the Provider Details form to be fully loaded"""
    try:
        wait = WebDriverWait(driver, 20)
        
        # Wait for the form to be present
        print("[INFO] Waiting for Provider Details form to load...")
        wait.until(
            EC.presence_of_element_located((By.ID, "webProfClaimsModel"))
        )
        
        # Wait for "Providers" section header
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Providers')]"))
        )
        
        # Wait a bit more for JavaScript to finish rendering
        time.sleep(0.5)
        print("[INFO] Provider Details form is ready")
        return True
    except Exception as e:
        print(f"[ERROR] Form did not load: {e}")
        return False

def fillReferringProviderNPI(driver, npi):
    """Fill Referring Provider NPI"""
    try:
        wait = WebDriverWait(driver, 10)
        npiInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.referringProvider.npi"))
        )
        npiInput.clear()
        time.sleep(0.2)
        npiInput.send_keys(npi)
        time.sleep(0.2)
        print(f"[INFO] Entered Referring Provider NPI: {npi}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Referring Provider NPI: {e}")
        return False

def fillReferringProviderQualifier(driver, qualifier="DN"):
    """Select Referring Provider Qualifier"""
    try:
        wait = WebDriverWait(driver, 10)
        qualifierSelect = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.referringProvider.qualifier"))
        )
        select = Select(qualifierSelect)
        select.select_by_value(qualifier)
        time.sleep(0.2)
        print(f"[INFO] Selected Referring Provider Qualifier: {qualifier}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to select Referring Provider Qualifier: {e}")
        return False

def fillReferringProviderName(driver, lastName, firstName):
    """Fill Referring Provider Last Name and First Name"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Fill Last Name
        lastNameInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.referringProvider.last"))
        )
        lastNameInput.clear()
        time.sleep(0.2)
        lastNameInput.send_keys(lastName)
        time.sleep(0.2)
        print(f"[INFO] Entered Referring Provider Last Name: {lastName}")
        
        # Fill First Name
        firstNameInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.referringProvider.first"))
        )
        firstNameInput.clear()
        time.sleep(0.2)
        firstNameInput.send_keys(firstName)
        time.sleep(0.2)
        print(f"[INFO] Entered Referring Provider First Name: {firstName}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Referring Provider Name: {e}")
        return False

def fillRenderingProviderNPI(driver, npi):
    """Fill Rendering Provider NPI"""
    try:
        wait = WebDriverWait(driver, 10)
        npiInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.renderingProvider.npi"))
        )
        npiInput.clear()
        time.sleep(0.2)
        npiInput.send_keys(npi)
        time.sleep(0.2)
        print(f"[INFO] Entered Rendering Provider NPI: {npi}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Rendering Provider NPI: {e}")
        return False

def fillRenderingProviderTaxonomy(driver, taxonomy):
    """Fill Rendering Provider Taxonomy"""
    try:
        wait = WebDriverWait(driver, 10)
        taxonomyInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.renderingProvider.taxonomy"))
        )
        taxonomyInput.clear()
        time.sleep(0.2)
        taxonomyInput.send_keys(taxonomy)
        time.sleep(0.2)
        print(f"[INFO] Entered Rendering Provider Taxonomy: {taxonomy}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Rendering Provider Taxonomy: {e}")
        return False

def fillRenderingProviderName(driver, lastName, firstName):
    """Fill Rendering Provider Last Name and First Name"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Fill Last Name
        lastNameInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.renderingProvider.last"))
        )
        lastNameInput.clear()
        time.sleep(0.2)
        lastNameInput.send_keys(lastName)
        time.sleep(0.2)
        print(f"[INFO] Entered Rendering Provider Last Name: {lastName}")
        
        # Fill First Name
        firstNameInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.renderingProvider.first"))
        )
        firstNameInput.clear()
        time.sleep(0.2)
        firstNameInput.send_keys(firstName)
        time.sleep(0.2)
        print(f"[INFO] Entered Rendering Provider First Name: {firstName}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Rendering Provider Name: {e}")
        return False

def fillBillingProviderName(driver, name):
    """Fill Billing Provider Name"""
    try:
        wait = WebDriverWait(driver, 10)
        nameInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.last"))
        )
        nameInput.clear()
        time.sleep(0.2)
        nameInput.send_keys(name)
        time.sleep(0.2)
        print(f"[INFO] Entered Billing Provider Name: {name}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Billing Provider Name: {e}")
        return False

def fillBillingProviderNPI(driver, npi):
    """Fill Billing Provider NPI"""
    try:
        wait = WebDriverWait(driver, 10)
        npiInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.npi"))
        )
        npiInput.clear()
        time.sleep(0.2)
        npiInput.send_keys(npi)
        time.sleep(0.2)
        print(f"[INFO] Entered Billing Provider NPI: {npi}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Billing Provider NPI: {e}")
        return False

def fillBillingProviderTaxonomy(driver, taxonomy):
    """Fill Billing Provider Taxonomy"""
    try:
        wait = WebDriverWait(driver, 10)
        taxonomyInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.taxonomy"))
        )
        taxonomyInput.clear()
        time.sleep(0.2)
        taxonomyInput.send_keys(taxonomy)
        time.sleep(0.2)
        print(f"[INFO] Entered Billing Provider Taxonomy: {taxonomy}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Billing Provider Taxonomy: {e}")
        return False

def fillBillingProviderAddress(driver, address, city, state, zipCode):
    """Fill Billing Provider Address"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Fill Address
        addressInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.address.addressLine1"))
        )
        addressInput.clear()
        time.sleep(0.2)
        addressInput.send_keys(address)
        time.sleep(0.2)
        print(f"[INFO] Entered Billing Provider Address: {address}")
        
        # Fill City
        cityInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.address.city"))
        )
        cityInput.clear()
        time.sleep(0.2)
        cityInput.send_keys(city)
        time.sleep(0.2)
        print(f"[INFO] Entered Billing Provider City: {city}")
        
        # Select State
        stateSelect = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.address.state"))
        )
        select = Select(stateSelect)
        select.select_by_value(state)
        time.sleep(0.2)
        print(f"[INFO] Selected Billing Provider State: {state}")
        
        # Fill Zip
        zipInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.address.zip"))
        )
        zipInput.clear()
        time.sleep(0.2)
        zipInput.send_keys(zipCode)
        time.sleep(0.2)
        print(f"[INFO] Entered Billing Provider Zip: {zipCode}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Billing Provider Address: {e}")
        return False

def fillServiceFacilityLocation(driver, name, npi, address, city, state, zipCode):
    """Fill Service Facility Location fields"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Fill Name
        nameInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.facilityProvider.last"))
        )
        nameInput.clear()
        time.sleep(0.2)
        nameInput.send_keys(name)
        time.sleep(0.2)
        print(f"[INFO] Entered Service Facility Location Name: {name}")
        
        # Fill NPI
        npiInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.facilityProvider.npi"))
        )
        npiInput.clear()
        time.sleep(0.2)
        npiInput.send_keys(npi)
        time.sleep(0.2)
        print(f"[INFO] Entered Service Facility Location NPI: {npi}")
        
        # Fill Address
        addressInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.facilityProvider.address.addressLine1"))
        )
        addressInput.clear()
        time.sleep(0.2)
        addressInput.send_keys(address)
        time.sleep(0.2)
        print(f"[INFO] Entered Service Facility Location Address: {address}")
        
        # Fill City
        cityInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.facilityProvider.address.city"))
        )
        cityInput.clear()
        time.sleep(0.2)
        cityInput.send_keys(city)
        time.sleep(0.2)
        print(f"[INFO] Entered Service Facility Location City: {city}")
        
        # Select State
        stateSelect = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.facilityProvider.address.state"))
        )
        select = Select(stateSelect)
        select.select_by_value(state)
        time.sleep(0.2)
        print(f"[INFO] Selected Service Facility Location State: {state}")
        
        # Fill Zip
        zipInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.facilityProvider.address.zip"))
        )
        zipInput.clear()
        time.sleep(0.2)
        zipInput.send_keys(zipCode)
        time.sleep(0.2)
        print(f"[INFO] Entered Service Facility Location Zip: {zipCode}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fill Service Facility Location: {e}")
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
        time.sleep(0.5)
        
        nextButton.click()
        print("[INFO] Clicked Next button")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to click Next button: {e}")
        return False

def isOnProviderDetailsPage(driver):
    """Check if we're still on the Provider Details page"""
    try:
        wait = WebDriverWait(driver, 3)
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Providers')]"))
        )
        return True
    except:
        return False

def validateProviderDetails(driver, referringNPI, referringQualifier, referringLastName, referringFirstName,
                           renderingNPI, renderingTaxonomy, renderingLastName, renderingFirstName,
                           billingName, billingNPI, billingTaxonomy, billingAddress, billingCity,
                           billingState, billingZip, facilityName, facilityNPI, facilityAddress,
                           facilityCity, facilityState, facilityZip):
    """Validate all Provider Details form fields are filled correctly"""
    errors = []
    try:
        wait = WebDriverWait(driver, 5)
        
        # Validate Referring Provider NPI
        referringNPIInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.referringProvider.npi"))
        )
        actualReferringNPI = referringNPIInput.get_attribute("value") or ""
        if actualReferringNPI.strip() != referringNPI.strip():
            errors.append(f"Referring Provider NPI mismatch: expected '{referringNPI}', got '{actualReferringNPI}'")
        
        # Validate Referring Provider Qualifier
        referringQualifierSelect = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.referringProvider.qualifier"))
        )
        select = Select(referringQualifierSelect)
        selectedQualifier = select.first_selected_option.get_attribute("value")
        if selectedQualifier != referringQualifier:
            errors.append(f"Referring Provider Qualifier mismatch: expected '{referringQualifier}', got '{selectedQualifier}'")
        
        # Validate Referring Provider Last Name
        referringLastNameInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.referringProvider.last"))
        )
        actualReferringLastName = referringLastNameInput.get_attribute("value") or ""
        if actualReferringLastName.strip() != referringLastName.strip():
            errors.append(f"Referring Provider Last Name mismatch: expected '{referringLastName}', got '{actualReferringLastName}'")
        
        # Validate Referring Provider First Name
        referringFirstNameInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.referringProvider.first"))
        )
        actualReferringFirstName = referringFirstNameInput.get_attribute("value") or ""
        if actualReferringFirstName.strip() != referringFirstName.strip():
            errors.append(f"Referring Provider First Name mismatch: expected '{referringFirstName}', got '{actualReferringFirstName}'")
        
        # Validate Rendering Provider NPI
        renderingNPIInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.renderingProvider.npi"))
        )
        actualRenderingNPI = renderingNPIInput.get_attribute("value") or ""
        if actualRenderingNPI.strip() != renderingNPI.strip():
            errors.append(f"Rendering Provider NPI mismatch: expected '{renderingNPI}', got '{actualRenderingNPI}'")
        
        # Validate Rendering Provider Taxonomy
        renderingTaxonomyInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.renderingProvider.taxonomy"))
        )
        actualRenderingTaxonomy = renderingTaxonomyInput.get_attribute("value") or ""
        if actualRenderingTaxonomy.strip() != renderingTaxonomy.strip():
            errors.append(f"Rendering Provider Taxonomy mismatch: expected '{renderingTaxonomy}', got '{actualRenderingTaxonomy}'")
        
        # Validate Rendering Provider Last Name
        renderingLastNameInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.renderingProvider.last"))
        )
        actualRenderingLastName = renderingLastNameInput.get_attribute("value") or ""
        if actualRenderingLastName.strip() != renderingLastName.strip():
            errors.append(f"Rendering Provider Last Name mismatch: expected '{renderingLastName}', got '{actualRenderingLastName}'")
        
        # Validate Rendering Provider First Name
        renderingFirstNameInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.renderingProvider.first"))
        )
        actualRenderingFirstName = renderingFirstNameInput.get_attribute("value") or ""
        if actualRenderingFirstName.strip() != renderingFirstName.strip():
            errors.append(f"Rendering Provider First Name mismatch: expected '{renderingFirstName}', got '{actualRenderingFirstName}'")
        
        # Validate Billing Provider Name
        billingNameInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.last"))
        )
        actualBillingName = billingNameInput.get_attribute("value") or ""
        if actualBillingName.strip() != billingName.strip():
            errors.append(f"Billing Provider Name mismatch: expected '{billingName}', got '{actualBillingName}'")
        
        # Validate Billing Provider NPI
        billingNPIInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.npi"))
        )
        actualBillingNPI = billingNPIInput.get_attribute("value") or ""
        if actualBillingNPI.strip() != billingNPI.strip():
            errors.append(f"Billing Provider NPI mismatch: expected '{billingNPI}', got '{actualBillingNPI}'")
        
        # Validate Billing Provider Taxonomy
        billingTaxonomyInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.taxonomy"))
        )
        actualBillingTaxonomy = billingTaxonomyInput.get_attribute("value") or ""
        if actualBillingTaxonomy.strip() != billingTaxonomy.strip():
            errors.append(f"Billing Provider Taxonomy mismatch: expected '{billingTaxonomy}', got '{actualBillingTaxonomy}'")
        
        # Validate Billing Provider Address
        billingAddressInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.address.addressLine1"))
        )
        actualBillingAddress = billingAddressInput.get_attribute("value") or ""
        if actualBillingAddress.strip() != billingAddress.strip():
            errors.append(f"Billing Provider Address mismatch: expected '{billingAddress}', got '{actualBillingAddress}'")
        
        # Validate Billing Provider City
        billingCityInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.address.city"))
        )
        actualBillingCity = billingCityInput.get_attribute("value") or ""
        if actualBillingCity.strip() != billingCity.strip():
            errors.append(f"Billing Provider City mismatch: expected '{billingCity}', got '{actualBillingCity}'")
        
        # Validate Billing Provider State
        billingStateSelect = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.address.state"))
        )
        selectState = Select(billingStateSelect)
        selectedBillingState = selectState.first_selected_option.get_attribute("value")
        if selectedBillingState != billingState:
            errors.append(f"Billing Provider State mismatch: expected '{billingState}', got '{selectedBillingState}'")
        
        # Validate Billing Provider Zip
        billingZipInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.billingProvider.address.zip"))
        )
        actualBillingZip = billingZipInput.get_attribute("value") or ""
        if actualBillingZip.strip() != billingZip.strip():
            errors.append(f"Billing Provider Zip mismatch: expected '{billingZip}', got '{actualBillingZip}'")
        
        # Validate Service Facility Location Name
        facilityNameInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.facilityProvider.last"))
        )
        actualFacilityName = facilityNameInput.get_attribute("value") or ""
        if actualFacilityName.strip() != facilityName.strip():
            errors.append(f"Service Facility Location Name mismatch: expected '{facilityName}', got '{actualFacilityName}'")
        
        # Validate Service Facility Location NPI
        facilityNPIInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.facilityProvider.npi"))
        )
        actualFacilityNPI = facilityNPIInput.get_attribute("value") or ""
        if actualFacilityNPI.strip() != facilityNPI.strip():
            errors.append(f"Service Facility Location NPI mismatch: expected '{facilityNPI}', got '{actualFacilityNPI}'")
        
        # Validate Service Facility Location Address
        facilityAddressInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.facilityProvider.address.addressLine1"))
        )
        actualFacilityAddress = facilityAddressInput.get_attribute("value") or ""
        if actualFacilityAddress.strip() != facilityAddress.strip():
            errors.append(f"Service Facility Location Address mismatch: expected '{facilityAddress}', got '{actualFacilityAddress}'")
        
        # Validate Service Facility Location City
        facilityCityInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.facilityProvider.address.city"))
        )
        actualFacilityCity = facilityCityInput.get_attribute("value") or ""
        if actualFacilityCity.strip() != facilityCity.strip():
            errors.append(f"Service Facility Location City mismatch: expected '{facilityCity}', got '{actualFacilityCity}'")
        
        # Validate Service Facility Location State
        facilityStateSelect = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.facilityProvider.address.state"))
        )
        selectFacilityState = Select(facilityStateSelect)
        selectedFacilityState = selectFacilityState.first_selected_option.get_attribute("value")
        if selectedFacilityState != facilityState:
            errors.append(f"Service Facility Location State mismatch: expected '{facilityState}', got '{selectedFacilityState}'")
        
        # Validate Service Facility Location Zip
        facilityZipInput = wait.until(
            EC.presence_of_element_located((By.ID, "professionalClaim.facilityProvider.address.zip"))
        )
        actualFacilityZip = facilityZipInput.get_attribute("value") or ""
        if actualFacilityZip.strip() != facilityZip.strip():
            errors.append(f"Service Facility Location Zip mismatch: expected '{facilityZip}', got '{actualFacilityZip}'")
        
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
            print("[VALIDATION] All provider details fields validated successfully")
            return True, []
    except Exception as e:
        errors.append(f"Validation exception: {e}")
        return False, errors

def fillAllProviderDetails(driver, referringNPI, referringQualifier, referringLastName, referringFirstName,
                          renderingNPI, renderingTaxonomy, renderingLastName, renderingFirstName, 
                          billingName, billingNPI, billingTaxonomy, billingAddress, billingCity, 
                          billingState, billingZip, facilityName, facilityNPI, facilityAddress, 
                          facilityCity, facilityState, facilityZip):
    """Fill all Provider Details form fields"""
    # Fill Referring Provider NPI
    if not fillReferringProviderNPI(driver, referringNPI):
        return False
    
    # Select Referring Provider Qualifier
    if not fillReferringProviderQualifier(driver, referringQualifier):
        return False
    
    # Fill Referring Provider Name
    if not fillReferringProviderName(driver, referringLastName, referringFirstName):
        return False
    
    # Fill Rendering Provider NPI
    if not fillRenderingProviderNPI(driver, renderingNPI):
        return False
    
    # Fill Rendering Provider Taxonomy
    if not fillRenderingProviderTaxonomy(driver, renderingTaxonomy):
        return False
    
    # Fill Rendering Provider Name
    if not fillRenderingProviderName(driver, renderingLastName, renderingFirstName):
        return False
    
    # Fill Billing Provider Name
    if not fillBillingProviderName(driver, billingName):
        return False
    
    # Fill Billing Provider NPI
    if not fillBillingProviderNPI(driver, billingNPI):
        return False
    
    # Fill Billing Provider Taxonomy
    if not fillBillingProviderTaxonomy(driver, billingTaxonomy):
        return False
    
    # Fill Billing Provider Address
    if not fillBillingProviderAddress(driver, billingAddress, billingCity, billingState, billingZip):
        return False
    
    # Fill Service Facility Location
    if not fillServiceFacilityLocation(driver, facilityName, facilityNPI, facilityAddress, 
                                      facilityCity, facilityState, facilityZip):
        return False
    
    return True

def executeStep5(driver):
    """Execute step 5: Fill Provider Details form with values from env"""
    try:
        # Shared values from environment variables
        defaultNPI = os.getenv('DEFAULT_PROVIDER_NPI', '')
        defaultLastName = os.getenv('DEFAULT_PROVIDER_LAST_NAME', '')
        defaultFirstName = os.getenv('DEFAULT_PROVIDER_FIRST_NAME', '')
        defaultTaxonomy = os.getenv('DEFAULT_PROVIDER_TAXONOMY', '')
        defaultAddress = os.getenv('DEFAULT_PROVIDER_ADDRESS', '')
        defaultCity = os.getenv('DEFAULT_PROVIDER_CITY', '')
        defaultState = os.getenv('DEFAULT_PROVIDER_STATE', '')
        defaultZip = os.getenv('DEFAULT_PROVIDER_ZIP', '')
        
        # Referring Provider (uses shared values, qualifier is unique)
        referringNPI = os.getenv('DEFAULT_REFERRING_PROVIDER_NPI', defaultNPI)
        referringQualifier = os.getenv('DEFAULT_REFERRING_PROVIDER_QUALIFIER', '')
        referringLastName = os.getenv('DEFAULT_REFERRING_PROVIDER_LAST_NAME', defaultLastName)
        referringFirstName = os.getenv('DEFAULT_REFERRING_PROVIDER_FIRST_NAME', defaultFirstName)
        
        # Rendering Provider (uses shared values)
        renderingNPI = os.getenv('DEFAULT_RENDERING_PROVIDER_NPI', defaultNPI)
        renderingTaxonomy = os.getenv('DEFAULT_RENDERING_PROVIDER_TAXONOMY', defaultTaxonomy)
        renderingLastName = os.getenv('DEFAULT_RENDERING_PROVIDER_LAST_NAME', defaultLastName)
        renderingFirstName = os.getenv('DEFAULT_RENDERING_PROVIDER_FIRST_NAME', defaultFirstName)
        
        # Billing Provider (uses shared values)
        billingName = os.getenv('DEFAULT_BILLING_PROVIDER_NAME', defaultLastName)
        billingNPI = os.getenv('DEFAULT_BILLING_PROVIDER_NPI', defaultNPI)
        billingTaxonomy = os.getenv('DEFAULT_BILLING_PROVIDER_TAXONOMY', defaultTaxonomy)
        billingAddress = os.getenv('DEFAULT_BILLING_PROVIDER_ADDRESS', defaultAddress)
        billingCity = os.getenv('DEFAULT_BILLING_PROVIDER_CITY', defaultCity)
        billingState = os.getenv('DEFAULT_BILLING_PROVIDER_STATE', defaultState)
        billingZip = os.getenv('DEFAULT_BILLING_PROVIDER_ZIP', defaultZip)
        
        # Service Facility Location (uses shared values, defaults to billing if not set)
        facilityName = os.getenv('DEFAULT_FACILITY_NAME', billingName)
        facilityNPI = os.getenv('DEFAULT_FACILITY_NPI', billingNPI)
        facilityAddress = os.getenv('DEFAULT_FACILITY_ADDRESS', billingAddress)
        facilityCity = os.getenv('DEFAULT_FACILITY_CITY', billingCity)
        facilityState = os.getenv('DEFAULT_FACILITY_STATE', billingState)
        facilityZip = os.getenv('DEFAULT_FACILITY_ZIP', billingZip)
        
        print(f"[INFO] Using Referring Provider NPI: {referringNPI}")
        print(f"[INFO] Using Referring Provider Qualifier: {referringQualifier}")
        print(f"[INFO] Using Referring Provider Name: {referringLastName}, {referringFirstName}")
        print(f"[INFO] Using Rendering Provider NPI: {renderingNPI}")
        print(f"[INFO] Using Rendering Provider Taxonomy: {renderingTaxonomy}")
        print(f"[INFO] Using Rendering Provider Name: {renderingLastName}, {renderingFirstName}")
        print(f"[INFO] Using Billing Provider Name: {billingName}")
        print(f"[INFO] Using Billing Provider NPI: {billingNPI}")
        print(f"[INFO] Using Billing Provider Taxonomy: {billingTaxonomy}")
        print(f"[INFO] Using Billing Provider Address: {billingAddress}, {billingCity}, {billingState} {billingZip}")
        print(f"[INFO] Using Service Facility Location Name: {facilityName}")
        print(f"[INFO] Using Service Facility Location NPI: {facilityNPI}")
        print(f"[INFO] Using Service Facility Location Address: {facilityAddress}, {facilityCity}, {facilityState} {facilityZip}")
        
        maxRetries = 3
        retryCount = 0
        
        while retryCount < maxRetries:
            retryCount += 1
            print(f"\n[INFO] Step 5 attempt {retryCount}/{maxRetries}")
            
            # Wait for form to load
            if not waitForProviderDetailsFormToLoad(driver):
                if retryCount < maxRetries:
                    print("[WARNING] Form did not load, retrying...")
                    time.sleep(0.5)
                    continue
                else:
                    raise Exception("Provider Details form did not load properly after retries")
            
            # Fill all form fields
            if not fillAllProviderDetails(driver, referringNPI, referringQualifier, referringLastName, 
                                         referringFirstName, renderingNPI, renderingTaxonomy, 
                                         renderingLastName, renderingFirstName, billingName, 
                                         billingNPI, billingTaxonomy, billingAddress, 
                                         billingCity, billingState, billingZip, facilityName, 
                                         facilityNPI, facilityAddress, facilityCity, facilityState, facilityZip):
                if retryCount < maxRetries:
                    print("[WARNING] Failed to fill form, retrying...")
                    time.sleep(0.5)
                    continue
                else:
                    raise Exception("Failed to fill form after retries")
            
            # Wait for fields to be processed
            # Validate all fields are filled correctly
            isValid, validationErrors = validateProviderDetails(driver, referringNPI, referringQualifier, 
                                                               referringLastName, referringFirstName,
                                                               renderingNPI, renderingTaxonomy, 
                                                               renderingLastName, renderingFirstName,
                                                               billingName, billingNPI, billingTaxonomy, 
                                                               billingAddress, billingCity, billingState, 
                                                               billingZip, facilityName, facilityNPI, 
                                                               facilityAddress, facilityCity, facilityState, 
                                                               facilityZip)
            if not isValid:
                if retryCount < maxRetries:
                    print(f"[WARNING] Validation failed with {len(validationErrors)} error(s), retrying...")
                    time.sleep(0.5)
                    continue
                else:
                    raise Exception(f"Validation failed after retries: {validationErrors}")
            
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
            if not isOnProviderDetailsPage(driver):
                # We're no longer on Provider Details page, success!
                print("[INFO] Successfully moved to next page")
                break
            else:
                # Still on Provider Details page, need to retry
                if retryCount < maxRetries:
                    print("[WARNING] Still on Provider Details page, form may not have submitted. Retrying...")
                    time.sleep(0.5)
                    continue
                else:
                    raise Exception("Still on Provider Details page after all retries")
        
        print("[INFO] Step 5 completed: Provider Details form submitted successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Step 5 failed: {e}")
        raise
