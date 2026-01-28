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
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
from extract import extractClaimData
from pages.step0 import executeStep0
from pages.step1 import executeStep1
from pages.step2 import executeStep2
from pages.step3 import executeStep3
from pages.step4 import executeStep4
from pages.step5 import executeStep5
from pages.step6 import executeStep6

load_dotenv()

chromeDriverPath = os.getenv('CHROME_DRIVER_PATH')  # Optional: only if you want to use a specific ChromeDriver path
chromeAppPath = os.getenv('CHROME_APP_PATH')
scrapingPort = os.getenv('BASE_CHROME_PORT', '9222')
baseChromeDir = os.getenv('BASE_CHROME_DIR', os.path.join(os.getcwd(), 'chromeData'))

def checkPortInUse(port):
    """Check if a port is already in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', int(port)))
    sock.close()
    return result == 0

def closeExistingChromeSession(port):
    """Close existing Chrome session on the given port"""
    try:
        import psutil
        port = int(port)
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    connections = proc.info.get('connections')
                    if connections:
                        for conn in connections:
                            if conn.status == psutil.CONN_LISTEN and conn.laddr.port == port:
                                print(f"[INFO] Closing existing Chrome process (PID: {proc.info['pid']}) on port {port}")
                                proc.terminate()
                                time.sleep(2)
                                if proc.is_running():
                                    proc.kill()
                                return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except ImportError:
        # psutil not available, try alternative method
        try:
            # Try to connect and close gracefully
            import requests
            try:
                response = requests.get(f'http://localhost:{port}/json', timeout=1)
                if response.status_code == 200:
                    print(f"[INFO] Found existing Chrome session on port {port}")
                    print(f"[WARNING] Please close existing Chrome browser manually to start with new headless setting")
            except:
                pass
        except ImportError:
            pass
    return False

def startChromeProcess(profileName='default_profile', headless=True):
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
    
    chromeArgs = [
        chromeAppPath,
        f'--remote-debugging-port={scrapingPort}',
        f'--user-data-dir={userDataDir}',
        '--disable-blink-features=AutomationControlled',
        '--disable-notifications',
        '--no-sandbox',
        '--disable-dev-shm-usage'
    ]
    
    # Add headless options
    if headless:
        chromeArgs.extend([
            '--headless=new',  # Use new headless mode (Chrome 109+)
            '--disable-gpu',
            '--window-size=1920,1080'
        ])
        print(f"[INFO] Starting Chrome in HEADLESS mode")
    else:
        print(f"[INFO] Starting Chrome in VISIBLE mode")
    
    chromeProcess = subprocess.Popen(chromeArgs)
    
    time.sleep(3)
    return chromeProcess

def createChromeDriver(options, headless=True):
    """Create Chrome WebDriver instance"""
    try:
        # Add headless options to WebDriver options
        if headless:
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            print(f"[INFO] WebDriver configured for HEADLESS mode")
        
        # Try to use webdriver_manager first (automatic ChromeDriver management)
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            print("[INFO] Using webdriver_manager to get ChromeDriver automatically")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("[INFO] ChromeDriver obtained from webdriver_manager")
        except ImportError:
            # If webdriver_manager is not installed, try custom path or fallback
            if chromeDriverPath:
                print(f"[INFO] Using custom ChromeDriver path: {chromeDriverPath}")
                service = Service(executable_path=chromeDriverPath)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                print("[INFO] Attempting to use ChromeDriver from system PATH")
                driver = webdriver.Chrome(options=options)
        
        return driver
    except Exception as e:
        print(f"[ERROR] Failed to create Chrome driver: {e}")
        raise

def createChromeSession(profileName='default_profile', headless=True):
    """Create or reuse Chrome session with a profile"""
    port = int(scrapingPort)
    
    # Check if port is in use and close existing session to ensure correct headless mode
    if checkPortInUse(port):
        print(f"[INFO] Existing Chrome session detected on port {port}")
        print(f"[INFO] Closing existing session to start with correct headless mode...")
        closeExistingChromeSession(port)
        time.sleep(2)  # Wait for port to be released
    
    # Start fresh session to match the current headless setting
    print(f"[INFO] Starting new Chrome session on port {port}")
    if headless:
        print(f"[INFO] Mode: HEADLESS (browser runs in background)")
    else:
        print(f"[INFO] Mode: VISIBLE (browser window will be shown)")
    
    startChromeProcess(profileName, headless=headless)
    
    chromeOptions = Options()
    chromeOptions.add_experimental_option("debuggerAddress", f"localhost:{port}")
    chromeOptions.add_argument("--disable-notifications")
    
    driver = createChromeDriver(chromeOptions, headless=headless)
    print(f"[INFO] Chrome session created successfully")
    return driver

def maximizeWindow(driver):
    """Maximize the browser window"""
    try:
        driver.maximize_window()
        time.sleep(1)
    except:
        pass

def convertExtractedDataToStepFormat(extractedData):
    """Convert extracted JSON format to step data format"""
    try:
        # Step 1: insuredId and insuredDob
        step1Data = {
            'insuredId': extractedData.get('id', ''),
            'insuredDob': extractedData.get('dob', '')
        }
        
        # Step 2: patientAccountNumber, providerSignatureDate, cliaNumber
        signatureDate = extractedData.get('signatureDate', '')
        providerSignatureDate = signatureDate if signatureDate else ''
        
        step2Data = {
            'patientAccountNumber': extractedData.get('account', ''),
            'providerSignatureDate': providerSignatureDate,
            'cliaNumber': os.getenv('DEFAULT_CLIA_NUMBER', '')
        }
        
        # Step 3: diagnosis codes
        diagnosisCodesList = extractedData.get('diagnosis_codes', [])
        step3Data = {
            'diagnosisCodes': diagnosisCodesList
        }
        
        # Step 4: service lines
        step4DataList = []
        procedures = extractedData.get('procedures', [])
        signatureDate = extractedData.get('signatureDate', '')
        
        for proc in procedures:
            formattedDate = signatureDate if signatureDate else ''
            
            diagnosisPointer = proc.get('diagnosisPointer', '')
            diagnosisCodesForServiceLine = []
            if diagnosisPointer:
                diagnosisCodes = extractedData.get('diagnosis_codes', [])
                pointerMap = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9, 'K': 10, 'L': 11}
                for char in diagnosisPointer:
                    idx = pointerMap.get(char)
                    if idx is not None and idx < len(diagnosisCodes):
                        diagnosisCodesForServiceLine.append(diagnosisCodes[idx])
            
            charges = proc.get('charges', 0)
            chargesFormatted = f"{charges:.2f}" if charges else "0.00"
            
            # Get additionalInfo and remove spaces for NDC field
            additionalInfo = proc.get('additionalInfo', '')
            ndcValue = additionalInfo.replace(' ', '') if additionalInfo else ''
            
            serviceLineData = {
                'serviceDate': formattedDate,
                'procedureCode': proc.get('code', ''),
                'charges': chargesFormatted,
                'units': '1',
                'modifier': proc.get('modifier', ''),
                'diagnosisCodes': diagnosisCodesForServiceLine,
                'ndc': ndcValue
            }
            
            step4DataList.append(serviceLineData)
        
        step4Data = {
            'serviceLines': step4DataList
        }
        
        # Validate data
        if not step1Data['insuredId']:
            raise ValueError("id not found in extracted data")
        if not step1Data['insuredDob']:
            raise ValueError("dob not found in extracted data")
        if not step2Data['patientAccountNumber']:
            raise ValueError("account not found in extracted data")
        if not step3Data['diagnosisCodes'] or len(step3Data['diagnosisCodes']) == 0:
            raise ValueError("diagnosis_codes not found or empty in extracted data")
        if not step4Data['serviceLines'] or len(step4Data['serviceLines']) == 0:
            raise ValueError("procedures not found or empty in extracted data")
        
        return step1Data, step2Data, step3Data, step4Data
    except Exception as e:
        print(f"[ERROR] Failed to convert extracted data: {e}")
        raise

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
                # Remove trailing X characters (e.g., "T16.2XXX" -> "T16.2")
                codeValue = codeValue.rstrip('X')
                if codeValue:  # Only add if code is not empty after stripping
                    diagnosisCodesList.append(codeValue)
        
        step3Data = {
            'diagnosisCodes': diagnosisCodesList
        }
        
        # Extract data for Step 4 - service lines (all service lines)
        if not serviceLines or len(serviceLines) == 0:
            raise ValueError("service_lines not found or empty")
        
        # Process all service lines
        step4DataList = []
        for serviceLine in serviceLines:
            datesOfService = serviceLine.get('dates_of_service', {})
            fromDate = datesOfService.get('from', {})
            procedureCodeObj = serviceLine.get('procedure_code', {})
            chargesObj = serviceLine.get('charges', {})
            daysUnitsObj = serviceLine.get('days_units', {})
            diagnosisPointerObj = serviceLine.get('diagnosis_pointer', {})
            
            # Extract modifier if it exists
            modifier = ''
            if isinstance(procedureCodeObj, dict):
                modifier = procedureCodeObj.get('modifier', '')
            elif isinstance(procedureCodeObj, str):
                modifier = ''
            
            # Extract diagnosis pointers (e.g., ["A", "B", "C", "D"])
            diagnosisPointers = []
            if isinstance(diagnosisPointerObj, dict):
                diagnosisPointers = diagnosisPointerObj.get('pointers', [])
            elif isinstance(diagnosisPointerObj, list):
                diagnosisPointers = diagnosisPointerObj
            
            # Get the diagnosis codes that match the pointers
            diagnosisCodesForServiceLine = []
            if diagnosisPointers:
                for codeObj in diagnosisCodes:
                    pointer = codeObj.get('pointer', '')
                    if pointer in diagnosisPointers:
                        codeValue = codeObj.get('code', '')
                        if codeValue:
                            # Remove trailing X characters
                            codeValue = codeValue.rstrip('X')
                            if codeValue:
                                diagnosisCodesForServiceLine.append(codeValue)
            
            serviceLineData = {
                'serviceDate': fromDate.get('formatted', '') if isinstance(fromDate, dict) else fromDate,
                'procedureCode': procedureCodeObj.get('code', '') if isinstance(procedureCodeObj, dict) else procedureCodeObj,
                'charges': chargesObj.get('formatted', '') if isinstance(chargesObj, dict) else chargesObj,
                'units': daysUnitsObj.get('value', '1') if isinstance(daysUnitsObj, dict) else daysUnitsObj,
                'modifier': modifier,
                'diagnosisCodes': diagnosisCodesForServiceLine  # Only codes for this service line
            }
            
            # Validate service line data
            if not serviceLineData['serviceDate']:
                raise ValueError(f"dates_of_service.from.formatted not found in service_lines[{len(step4DataList)}]")
            if not serviceLineData['procedureCode']:
                raise ValueError(f"procedure_code.code not found in service_lines[{len(step4DataList)}]")
            if not serviceLineData['charges']:
                raise ValueError(f"charges.formatted not found in service_lines[{len(step4DataList)}]")
            
            step4DataList.append(serviceLineData)
        
        step4Data = {
            'serviceLines': step4DataList
        }
        
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


def processSingleFile(driver, filename):
    """Process a single claim file through all steps"""
    try:
        # Extract data from text file
        print(f"\n{'='*60}")
        print(f"[INFO] Processing file: {filename}")
        print(f"{'='*60}")
        jsonOutput = extractClaimData(filename)
        if not jsonOutput:
            raise ValueError(f"Failed to extract data from {filename}")
        
        extractedData = json.loads(jsonOutput)
        print(f"[INFO] Successfully extracted data from {filename}")
        
        # Print the extracted JSON in a formatted way
        print(f"\n{'='*60}")
        print(f"[INFO] Extracted JSON Data:")
        print(f"{'='*60}")
        formattedJson = json.dumps(extractedData, indent=2, ensure_ascii=False)
        print(formattedJson)
        print(f"{'='*60}\n")
        
        print(f"[INFO] Signature Date: {extractedData.get('signatureDate', 'N/A')}")
        print(f"[INFO] Procedures: {len(extractedData.get('procedures', []))}")
        
        # Convert extracted data to step format
        step1Data, step2Data, step3Data, step4Data = convertExtractedDataToStepFormat(extractedData)
        
        print(f"[INFO] Step 2 - Provider Signature Date: {step2Data['providerSignatureDate']}")
        if step4Data.get('serviceLines'):
            print(f"[INFO] Step 4 - First Service Line Date: {step4Data['serviceLines'][0]['serviceDate']}")
        
        # Execute Step 1: Navigate to portal and find person (will handle login if needed)
        print(f"[INFO] Executing Step 1 for {filename}")
        executeStep1(driver, step1Data['insuredId'], step1Data['insuredDob'])
        
        # Execute Step 2: Fill General Info form
        print(f"[INFO] Executing Step 2 for {filename}")
        executeStep2(driver, step2Data['patientAccountNumber'], step2Data['providerSignatureDate'], step2Data['cliaNumber'])
        
        # Execute Step 3: Add Diagnosis Codes
        print(f"[INFO] Executing Step 3 for {filename}")
        executeStep3(driver, step3Data['diagnosisCodes'])
        
        # Execute Step 4: Fill Service Lines (all service lines)
        print(f"[INFO] Executing Step 4 for {filename}")
        executeStep4(driver, step4Data['serviceLines'])
        
        # Execute Step 5: Fill Provider Details
        print(f"[INFO] Executing Step 5 for {filename}")
        executeStep5(driver)
        
        # Execute Step 6: Handle Attachments (just click Next)
        print(f"[INFO] Executing Step 6 for {filename}")
        executeStep6(driver)
        
        print(f"[INFO] Successfully completed processing for {filename}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error processing {filename}: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Extract and process claim data from text file(s)')
    parser.add_argument('filenames', nargs='+', help='Path(s) to the claim text file(s) to process')
    args = parser.parse_args()
    
    driver = None
    try:
        # Create Chrome session (once for all files)
        profileName = 'iandmydoc'
        headlessMode = True  # Set to False to see browser window
        print(f"[INFO] Creating Chrome session...")
        print(f"[INFO] Headless mode: {headlessMode}")
        driver = createChromeSession(profileName, headless=headlessMode)
        if not headlessMode:
            maximizeWindow(driver)
        
        # Process each file sequentially
        totalFiles = len(args.filenames)
        successful = 0
        failed = 0
        
        for idx, filename in enumerate(args.filenames, 1):
            print(f"\n[INFO] Processing file {idx} of {totalFiles}: {filename}")
            if processSingleFile(driver, filename):
                successful += 1
            else:
                failed += 1
                print(f"[WARNING] Failed to process {filename}, continuing with next file...")
        
        print(f"\n{'='*60}")
        print(f"[INFO] Processing complete!")
        print(f"[INFO] Successful: {successful}/{totalFiles}")
        print(f"[INFO] Failed: {failed}/{totalFiles}")
        print(f"{'='*60}")
        
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
