import re
import os
import json
from docx import Document

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

if __name__ == "__main__":
    fileDate = 'April 1'
    docx_file_path = f'ChartWatch/{fileDate}.docx'
    json_file_path = 'stock_data.json'
    
    dateKey = fileDate.split(" ")[-1]
    monthKey = fileDate.split(" ")[0]
    allLines = read_docx(docx_file_path)
    isStockFound = False
    stockData = load_existing_data(json_file_path)
    
    if monthKey not in stockData:
        stockData[monthKey] = {}
    for i in range(len(allLines)-1):
        if allLines[i+1] == "Quarterly Chart:":
            stockName = sanitizeFilename(allLines[i])
            if stockName not in stockData:
                stockData[monthKey][stockName] = {}
            isStockFound = True
        elif isStockFound and any(req in allLines[i] for req in ["Quarterly Chart:", "Monthly Chart:", "8-Day Chart:", "Weekly Chart:", "3-Day Chart:", "Daily Chart:", "233 Chart:", "144 Chart:"]):
            chartName = allLines[i][:-7]
            
            if chartName not in stockData[monthKey][stockName]:
                stockData[monthKey][stockName][chartName] = {}
            
            # Check if the date key already exists and if so, update it
            if dateKey in stockData[monthKey][stockName][chartName]:
                print(f"Data for {stockName} - {chartName} on {dateKey} already exists and will be updated.")
            
            stockData[monthKey][stockName][chartName][dateKey] = allLines[i+1]
            if "144" in allLines[i]:
                isStockFound = False

    save_data(json_file_path, stockData)
    print("Data updated and saved successfully.")
