import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def csv_to_pdf(csv_file, pdf_file):
    # Load CSV data
    df = pd.read_csv(csv_file)
    
    # Create a PDF canvas
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter  # Page dimensions
    
    # Set up positions
    x_offset = 0.5 * inch
    y_offset = height - 1 * inch
    line_height = 0.2 * inch
    
    # Draw table header
    for col_num, column in enumerate(df.columns):
        c.drawString(x_offset + col_num * 1.5 * inch, y_offset, column)
    
    y_offset -= line_height
    
    # Draw table rows
    for index, row in df.iterrows():
        for col_num, value in enumerate(row):
            c.drawString(x_offset + col_num * 1.5 * inch, y_offset, str(value))
        y_offset -= line_height
    
    # Save the PDF
    c.save()

# Convert each CSV file to PDF
csv_to_pdf('allSeniorPatients_2023_2024.csv', 'allSeniorPatients_2023_2024.pdf')
csv_to_pdf('allSeniorPatients_2022.csv', 'allSeniorPatients_2022.pdf')
csv_to_pdf('allSeniorPatients_2021.csv', 'allSeniorPatients_2021.pdf')
csv_to_pdf('allSeniorPatients_before_2021.csv', 'allSeniorPatients_before_2021.pdf')
csv_to_pdf('allSeniorPatients_nan.csv', 'allSeniorPatients_nan.pdf')
