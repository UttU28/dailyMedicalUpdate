import re
import os
import json
from docx import Document
from time import sleep

def list_docx_files_in_folder(folder_path):
    docx_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.docx'):
            docx_files.append(filename)
    return docx_files

def read_docx(file_path):
    doc = Document(file_path)
    paragraphs = []
    for para in doc.paragraphs:
        cleaned_text = para.text.strip()
        if cleaned_text:
            paragraphs.append(cleaned_text)
    return paragraphs

def sanitizeFilename(inputString):
    forbiddenChars = r'[<>:"/\\|?*]'
    safeString = re.sub(forbiddenChars, '_', inputString)
    safeString = safeString.strip()
    return safeString

def load_existing_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

def save_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def extractDataFrom(fileName):
    docx_file_path = f'ChartWatch/{fileName}.docx'
    json_file_path = 'stockData.json'
    
    dateKey = fileName.split(" ")[-1]
    monthKey = fileName.split(" ")[0]
    allLines = read_docx(docx_file_path)
    isStockFound = False
    stockData = load_existing_data(json_file_path)
    
    if monthKey not in stockData:
        stockData[monthKey] = {}
    
    for i in range(len(allLines)-1):
        if "Quarterly Chart:" in allLines[i+1]:
            stockName = sanitizeFilename(allLines[i])
            if stockName not in stockData[monthKey]:
                stockData[monthKey][stockName] = {}
            isStockFound = True
        elif isStockFound and any(req in allLines[i].split(" ")[0].strip() for req in ["Quarterly", "Monthly", "8-Day", "Weekly", "3-Day", "Daily", "233", "144"]):
            chartName = allLines[i].split(" ")[0].strip()
            
            if chartName not in stockData[monthKey][stockName]:
                stockData[monthKey][stockName][chartName] = []
            
            # Append the new data to the list
            stockData[monthKey][stockName][chartName].append({dateKey: allLines[i+1]})
            
            if "144" in allLines[i]:
                isStockFound = False

    save_data(json_file_path, stockData)
    # print("Data updated and saved successfully.")
    # sleep(1)

if __name__ == "__main__":
    folder_path = 'ChartWatch'
    allDocFiles = list_docx_files_in_folder(folder_path)
    # allDocFiles = [f"April {i}" for i in range(1, 31)]
    # allDocFiles = ["April 5"]
    print(allDocFiles)
    for fileName in allDocFiles:
        try:
            extractDataFrom(fileName.replace('.docx', ''))
        except: print(f"Not here {fileName}")