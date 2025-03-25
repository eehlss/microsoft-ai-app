import PyPDF2
import pdf2image
import pytesseract
from PIL import Image
import io
import re

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_image(image_file):
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text

def extract_parameters(text):
    # Initialize results dictionary
    results = {
        'RBC': None,
        'HGB': None,
        'MCV': None,
        'MCH': None,
        'MCHC': None,
        'RDW': None,
        'F_concentration': None,
        'A2_concentration': None,
        'Ao_peak': None,
        'S_peak': None
    }
    
    # Regular expressions for parameter extraction
    patterns = {
        'RBC': r'RBC[:\s]+(\d+\.?\d*)',
        'HGB': r'HGB[:\s]+(\d+\.?\d*)',
        'MCV': r'MCV[:\s]+(\d+\.?\d*)',
        'MCH': r'MCH[:\s]+(\d+\.?\d*)',
        'MCHC': r'MCHC[:\s]+(\d+\.?\d*)',
        'RDW': r'RDW[:\s]+(\d+\.?\d*)',
        'F_concentration': r'F[:\s]+(\d+\.?\d*)',
        'A2_concentration': r'A2[:\s]+(\d+\.?\d*)',
        'Ao_peak': r'Ao[\s\w]*Calibrated Area[:\s]+(\d+\.?\d*)',
        'S_peak': r'S[\s\w]*Calibrated Area[:\s]+(\d+\.?\d*)'
    }
    
    # Extract values using regex patterns
    for param, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            results[param] = float(match.group(1))
    
    return results

def process_pdf_file(pdf_file):
    text = extract_text_from_pdf(pdf_file)
    return extract_parameters(text)

def process_image_file(image_file):
    text = extract_text_from_image(image_file)
    return extract_parameters(text)
