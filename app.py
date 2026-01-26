#!/usr/bin/env python3
"""
Simple Selenium script to create Chrome profile and open python.org
All functions are self-contained in this file
"""

import os
import json
import subprocess
import time
import socket
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
from pages.step0 import executeStep0
from pages.step1 import executeStep1
from pages.step2 import executeStep2
from pages.step3 import executeStep3
from pages.step4 import executeStep4
from pages.step5 import executeStep5
from pages.step6 import executeStep6

load_dotenv()

chromeDriverPath = os.getenv('CHROME_DRIVER_PATH')
chromeAppPath = os.getenv('CHROME_APP_PATH')
scrapingPort = os.getenv('BASE_CHROME_PORT', '9222')
baseChromeDir = os.getenv('BASE_CHROME_DIR', os.path.join(os.getcwd(), 'chromeData'))

def checkPortInUse(port):
    """Check if a port is already in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', int(port)))
    sock.close()
    return result == 0

def startChromeProcess(profileName='default_profile'):
    """Start Chrome as a separate process with remote debugging"""
    if not chromeAppPath:
        raise ValueError("CHROME_APP_PATH environment variable is not set")
    
    if not baseChromeDir:
        raise ValueError("BASE_CHROME_DIR environment variable is not set")

    if not os.path.exists(baseChromeDir):
        os.makedirs(baseChromeDir, exist_ok=True)
        print(f"[INFO] Created directory: {baseChromeDir}")

    userDataDir = os.path.join(baseChromeDir, profileName)
    if not os.path.exists(userDataDir):
        os.makedirs(userDataDir, exist_ok=True)
        print(f"[INFO] Created profile directory: {userDataDir}")
    else:
        print(f"[INFO] Using existing profile: {userDataDir}")

    userDataDir = os.path.abspath(userDataDir)
    
    chromeProcess = subprocess.Popen([
        chromeAppPath,
        f'--remote-debugging-port={scrapingPort}',
        f'--user-data-dir={userDataDir}',
        '--disable-blink-features=AutomationControlled',
        '--disable-notifications',
        '--no-sandbox',
        '--disable-dev-shm-usage'
    ])
    
    time.sleep(3)
    return chromeProcess

def createChromeDriver(options):
    """Create Chrome WebDriver instance"""
    try:
        if chromeDriverPath:
            service = Service(executable_path=chromeDriverPath)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            except ImportError:
                driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"[ERROR] Failed to create Chrome driver: {e}")
        raise

def createChromeSession(profileName='default_profile'):
    """Create or reuse Chrome session with a profile"""
    port = int(scrapingPort)
    
    if checkPortInUse(port):
        print(f"[INFO] Reusing existing Chrome session on port {port}")
        chromeOptions = Options()
        chromeOptions.add_experimental_option("debuggerAddress", f"localhost:{port}")
        chromeOptions.add_argument("--disable-notifications")
    else:
        print(f"[INFO] Starting new Chrome session on port {port}")
        startChromeProcess(profileName)
        
        chromeOptions = Options()
        chromeOptions.add_experimental_option("debuggerAddress", f"localhost:{port}")
        chromeOptions.add_argument("--disable-notifications")
    
    driver = createChromeDriver(chromeOptions)
    print(f"[INFO] Chrome session created successfully")
    return driver

def maximizeWindow(driver):
    """Maximize the browser window"""
    try:
        driver.maximize_window()
        time.sleep(1)
    except:
        pass

def loadAndExtractClaimData(jsonFilePath='sample.json'):
    """Load claim data from JSON and extract only needed fields"""
    try:
        with open(jsonFilePath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[INFO] Successfully loaded data from {jsonFilePath}")
        
        # Extract data for Step 1 - from patient_info (using id_number and date_of_birth)
        patientInfo = data.get('patient_info', {})
        idNumberObj = patientInfo.get('id_number', {})
        step1Data = {
            'insuredId': idNumberObj.get('value', '') if isinstance(idNumberObj, dict) else idNumberObj,
            'insuredDob': patientInfo.get('date_of_birth', {}).get('formatted', '') if isinstance(patientInfo.get('date_of_birth'), dict) else patientInfo.get('date_of_birth', '')
        }
        
        # Extract data for Step 2
        # Use service line date as provider signature date if signatures not available
        serviceLines = data.get('service_lines', [])
        providerSignatureDate = ''
        if serviceLines and len(serviceLines) > 0:
            firstServiceLine = serviceLines[0]
            datesOfService = firstServiceLine.get('dates_of_service', {})
            providerSignatureDate = datesOfService.get('from', {}).get('formatted', '')
        
        billingInfo = data.get('billing_info', {})
        patientAccountNumberObj = billingInfo.get('patient_account_number', {})
        step2Data = {
            'patientAccountNumber': patientAccountNumberObj.get('value', '') if isinstance(patientAccountNumberObj, dict) else patientAccountNumberObj,
            'providerSignatureDate': providerSignatureDate,
            'cliaNumber': os.getenv('DEFAULT_CLIA_NUMBER', '')  # CLIA number from env
        }
        
        # Extract data for Step 3 - diagnosis codes (the actual code values like "Z00.01")
        diagnosisCodesList = []
        diagnosisCodes = data.get('diagnosis', {}).get('codes', [])
        for codeObj in diagnosisCodes:
            # In sample.json, the code is in the "code" field (e.g., "Z00.01")
            codeValue = codeObj.get('code', '')
            if codeValue:
                diagnosisCodesList.append(codeValue)
        
        step3Data = {
            'diagnosisCodes': diagnosisCodesList
        }
        
        # Extract data for Step 4 - service lines
        if not serviceLines or len(serviceLines) == 0:
            raise ValueError("service_lines not found or empty")
        
        # Get first service line (assuming one service line for now)
        firstServiceLine = serviceLines[0]
        datesOfService = firstServiceLine.get('dates_of_service', {})
        fromDate = datesOfService.get('from', {})
        procedureCodeObj = firstServiceLine.get('procedure_code', {})
        chargesObj = firstServiceLine.get('charges', {})
        daysUnitsObj = firstServiceLine.get('days_units', {})
        
        step4Data = {
            'serviceDate': fromDate.get('formatted', '') if isinstance(fromDate, dict) else fromDate,
            'procedureCode': procedureCodeObj.get('code', '') if isinstance(procedureCodeObj, dict) else procedureCodeObj,
            'charges': chargesObj.get('formatted', '') if isinstance(chargesObj, dict) else chargesObj,
            'units': daysUnitsObj.get('value', '1') if isinstance(daysUnitsObj, dict) else daysUnitsObj
        }
        
        # Validate Step 4 data
        if not step4Data['serviceDate']:
            raise ValueError("dates_of_service.from.formatted not found in service_lines")
        if not step4Data['procedureCode']:
            raise ValueError("procedure_code.code not found in service_lines")
        if not step4Data['charges']:
            raise ValueError("charges.formatted not found in service_lines")
        
        # Validate Step 1 data
        if not step1Data['insuredId']:
            raise ValueError("patient_info.id_number.value not found")
        if not step1Data['insuredDob']:
            raise ValueError("patient_info.date_of_birth.formatted not found")
        
        # Validate Step 2 data
        if not step2Data['patientAccountNumber']:
            raise ValueError("billing_info.patient_account_number.value not found")
        if not step2Data['providerSignatureDate']:
            raise ValueError("provider_signature_date not found (using service line date)")
        
        # Validate Step 3 data
        if not step3Data['diagnosisCodes'] or len(step3Data['diagnosisCodes']) == 0:
            raise ValueError("diagnosis codes not found in diagnosis.codes")
        
        return step1Data, step2Data, step3Data, step4Data
    except Exception as e:
        print(f"[ERROR] Failed to load or extract claim data: {e}")
        raise


def main():
    """Main function"""
    driver = None
    try:
        # Create Chrome session
        profileName = 'uttu'
        driver = createChromeSession(profileName)
        
        maximizeWindow(driver)
        
        # Load and extract claim data
        step1Data, step2Data, step3Data, step4Data = loadAndExtractClaimData('sample.json')
        
        # Execute Step 1: Navigate to portal and find person (will handle login if needed)
        executeStep1(driver, step1Data['insuredId'], step1Data['insuredDob'])
        
        # Execute Step 2: Fill General Info form
        executeStep2(driver, step2Data['patientAccountNumber'], step2Data['providerSignatureDate'], step2Data['cliaNumber'])
        
        # Execute Step 3: Add Diagnosis Codes
        executeStep3(driver, step3Data['diagnosisCodes'])
        
        # Execute Step 4: Fill Service Lines
        executeStep4(driver, step4Data['serviceDate'], step4Data['procedureCode'], 
                    step4Data['charges'], step4Data['units'])
        
        # Execute Step 5: Fill Provider Details
        executeStep5(driver)
        
        # Execute Step 6: Handle Attachments (just click Next)
        executeStep6(driver)
        
        print("\n[INFO] Browser will stay open. Press Ctrl+C to exit script (browser stays open)...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[INFO] Exiting script (Chrome process continues running)...")
    
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    finally:
        print("[INFO] Script ended. Chrome browser remains open.")

if __name__ == "__main__":
    main()
