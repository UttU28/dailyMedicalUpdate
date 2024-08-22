import json
import os
from docx import Document
from docx.shared import Pt

with open('stockData.json', 'r') as file:
    stockData = json.load(file)

def createDoc(ofWhat, withWhat, month, rootDir):
    doc = Document()
    doc.add_heading(ofWhat, level=1)

    for item in withWhat:
        for key, value in item.items():
            p = doc.add_paragraph()
            run = p.add_run(f'{month} {key}: ')
            run.bold = True
            run.font.name = 'Arial'
            run.font.size = Pt(12)
            p.add_run(value).font.name = 'Arial'
            # p.add_run(value).font.size = Pt(12)
    doc.save(f'{rootDir}/{ofWhat}.docx')



def createDirIfNotExists(directoryPath):
    if not os.path.exists(directoryPath):
        os.makedirs(directoryPath)

def sortDictsByKeys(data):
    baseDir = 'tradingData'
    createDirIfNotExists(baseDir)
    for month, categories in data.items():
        createDirIfNotExists(baseDir+'/'+month)
        for symbol, schedules in categories.items():
            docxDir = baseDir+'/'+month+'/'+symbol
            createDirIfNotExists(docxDir)
            for scheduleType, entries in schedules.items():
                sortedEntries = sorted(entries, key=lambda x: int(next(iter(x))))
                schedules[scheduleType] = sortedEntries
                createDoc(scheduleType, sortedEntries, month, docxDir)
sortDictsByKeys(stockData)


# with open('ilteredStocks.json', 'w') as file:
#     json.dump(stockData, file, indent=4)
