from pypdf import PdfReader 
import glob, re

def extractAmountFrom(string):
    pattern = r'\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?'
    matches = re.findall(pattern, string)
    return matches


def readAndGet(pdfFile):
    reader = PdfReader(pdfFile) 
    page = reader.pages[0] 
    pdfData = page.extract_text().split("\n")
    for eachData in pdfData:
        eachData = eachData.strip().lower()
        if '$' in eachData and ('payment' in eachData or 'amount' in eachData):
            return extractAmountFrom(eachData)
    else:
        return 0

allPDFs = glob.glob("insurance/Aug/*.pdf")
for eachPDF in allPDFs:
    eachPDF = eachPDF.replace('\\', '/')
    print(readAndGet(eachPDF))
    print()
    print()