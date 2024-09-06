import pandas as pd
import numpy as np
from pypdf import PdfReader
import glob, re
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

def extractAmountFrom(string):
    pattern = r'\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?'
    matches = re.findall(pattern, string)
    return float(matches[0][1:]) if matches else 0.00

def readAndGet(pdfFile):
    reader = PdfReader(pdfFile)
    page = reader.pages[0]
    pdfData = page.extract_text().split("\n")
    for eachData in pdfData:
        eachData = eachData.strip().lower()
        if '$' in eachData and ('payment' in eachData or 'amount' in eachData):
            return extractAmountFrom(eachData)
    return 0

def readInsuranceData(allValues):
    data = pd.read_csv('insurance/insuranceData.csv')
    data['Amount Credit'] = data['Amount Credit'].astype(float)
    data['Is Paid'] = np.nan
    data.loc[data['Amount Credit'].isin(allValues), 'Is Paid'] = True
    data.to_csv('insurance/insuranceData_updated.csv', index=False)
    return data

# Process all PDF files
allPDFs = glob.glob("insurance/all/*.pdf")
allInsuranceAmount = []

counter = 0
for eachPDF in allPDFs:
    eachPDF = eachPDF.replace('\\', '/')
    amountPaid = readAndGet(eachPDF)
    if amountPaid != 0.0:
        allInsuranceAmount.append(amountPaid)
    else:
        counter += 1

# Summary
updated_data = readInsuranceData(allInsuranceAmount)

total_amounts = len(allInsuranceAmount)
matched_amounts = len([amount for amount in allInsuranceAmount if amount in updated_data['Amount Credit'].values])
unmatched_amounts = total_amounts - matched_amounts

# Print results with color
print(Fore.GREEN + Style.BRIGHT + "Amounts extracted from PDFs:")
print(Fore.CYAN + str(allInsuranceAmount))

print(Fore.YELLOW + "\nSummary:")
print(Fore.MAGENTA + f"Total amounts extracted: {total_amounts}")
print(Fore.GREEN + f"Amounts matched in the insurance data: {matched_amounts}")
print(Fore.RED + f"Amounts not matched in the insurance data: {unmatched_amounts}")
print(Fore.RED + f"Zer0 values are: {counter}")
