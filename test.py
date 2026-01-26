#!/usr/bin/env python3
"""
Test script for extracting CMS-1500 form data from PDFs using Ollama Vision Models
Saves raw output to .txt file (no JSON parsing)
"""

import json
import pymupdf
import ollama
from datetime import datetime
from pathlib import Path

# Load schema and sample for prompt reference
SCHEMA_PATH = "claim_data_schema.json"
SAMPLE_PATH = "sample2.json"  # Use sample2.json which has multiple service lines

def load_schema_and_sample():
    """Load schema and sample JSON for prompt context"""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    with open(SAMPLE_PATH, 'r', encoding='utf-8') as f:
        sample = json.load(f)
    
    return schema, sample

def pdf_page_to_image(pdf_path, page_num=0, dpi=300):
    """Convert PDF page to image bytes"""
    doc = pymupdf.open(pdf_path)
    page = doc[page_num]
    
    # Convert page to image
    pix = page.get_pixmap(matrix=pymupdf.Matrix(dpi/72, dpi/72))
    img_bytes = pix.tobytes("png")
    
    doc.close()
    return img_bytes

def create_extraction_prompt(schema, sample):
    """Create a detailed prompt for extracting CMS-1500 form data"""
    
    # Extract key structure from sample
    sample_str = json.dumps(sample, indent=2)
    
    prompt = f"""You are a JSON extraction tool. Extract all data from this CMS-1500 Health Insurance Claim Form.

IMPORTANT: Your response must be ONLY valid JSON. No markdown formatting, no explanations, no bullet points, no text before or after the JSON.

Required JSON structure (copy this exact format):

{sample_str}

EXTRACTION RULES:
1. Extract ALL fields visible on the form
2. Dates: Use format MM/DD/YYYY (e.g., "01/20/2026")
3. Diagnosis codes: Extract letter pointer (A-L) and code value
4. Service lines: Extract ALL service lines (there may be multiple)
5. Charges: Extract as numbers (e.g., 435.00 not "$435.00")
6. Empty fields: Use "" for strings, [] for arrays
7. Patient ID: Extract Member ID from field 1a
8. Names: Split into last_name, first_name, middle_initial, full_name
9. Dates: Include formatted, month, day, year components
10. Diagnosis: Array with pointer (A-L) and code value
11. Service lines: Array with all service line items

CRITICAL OUTPUT REQUIREMENT:
- Output ONLY the JSON object
- Start with {{ and end with }}
- No markdown (no **, no *, no ```)
- No explanations or descriptions
- Just the raw JSON matching the structure above

Begin your response with {{ and end with }}. Nothing else."""
    
    return prompt

def extract_with_ollama(pdf_path, model_name="llama3.2-vision:11b"):
    """
    Extract structured data from PDF using Ollama vision model
    Saves raw output to .txt file (no JSON parsing)
    
    Args:
        pdf_path: Path to PDF file
        model_name: Ollama model name (default: llama3.2-vision:11b)
    
    Returns:
        Dictionary with output file path and response length
    """
    print(f"[INFO] Processing PDF: {pdf_path}")
    print(f"[INFO] Using model: {model_name}")
    
    # Load schema and sample for prompt
    schema, sample = load_schema_and_sample()
    
    # Convert first page to image
    print("[INFO] Converting PDF page to image...")
    img_bytes = pdf_page_to_image(pdf_path, page_num=0, dpi=300)
    
    # Create extraction prompt
    prompt = create_extraction_prompt(schema, sample)
    
    print("[INFO] Sending to Ollama for extraction...")
    print("[INFO] This may take a while (30-60 seconds)...")
    
    try:
        # Call Ollama with image
        # Use system message to enforce JSON output
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a JSON extraction tool. Always respond with ONLY valid JSON. No markdown, no explanations, no formatting. Just pure JSON."
                },
                {
                    "role": "user",
                    "content": prompt,
                    "images": [img_bytes]
                }
            ],
            options={
                "temperature": 0.1,  # Low temperature for more consistent extraction
                "num_predict": 50000,  # Very long response limit for complete JSON (allows up to 50k tokens)
            }
        )
        
        # Extract raw response from Ollama
        response_text = response['message']['content']
        
        # Save raw response to text file (no JSON parsing)
        output_txt_path = Path(pdf_path).stem + "_extracted.txt"
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RAW EXTRACTION OUTPUT FROM OLLAMA\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"PDF File: {pdf_path}\n")
            f.write(f"Model: {model_name}\n")
            f.write(f"Extraction Date: {datetime.now().isoformat()}\n")
            f.write(f"Response Length: {len(response_text)} characters\n")
            f.write("=" * 80 + "\n\n")
            f.write("RAW JSON OUTPUT:\n")
            f.write("-" * 80 + "\n")
            f.write(response_text)
            f.write("\n" + "-" * 80 + "\n")
        
        print(f"[SUCCESS] Raw extraction output saved to: {output_txt_path}")
        print(f"[INFO] Response length: {len(response_text)} characters")
        print(f"[INFO] Response lines: {len(response_text.splitlines())} lines")
        
        # Show preview
        preview_lines = response_text.split('\n')[:30]
        print("\n[INFO] Response preview (first 30 lines):")
        print("-" * 60)
        for i, line in enumerate(preview_lines, 1):
            print(f"{i:3d} | {line}")
        if len(response_text.split('\n')) > 30:
            print(f"... ({len(response_text.split('\n')) - 30} more lines)")
        print("-" * 60)
        
        return {
            "raw_output_file": str(output_txt_path),
            "response_length": len(response_text),
            "response_lines": len(response_text.splitlines())
        }
        
    except Exception as e:
        print(f"[ERROR] Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        raise

def main():
    """Main function to test PDF extraction"""
    import sys
    
    # Get PDF path from command line or use default
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Try common test files
        test_files = ["example.pdf", "ex2.pdf", "ex3.pdf"]
        pdf_path = None
        for test_file in test_files:
            if Path(test_file).exists():
                pdf_path = test_file
                break
        
        if not pdf_path:
            print("[ERROR] No PDF file specified and no test files found")
            print("Usage: python test.py <pdf_path>")
            print("Or place example.pdf, ex2.pdf, or ex3.pdf in current directory")
            return
    
    if not Path(pdf_path).exists():
        print(f"[ERROR] PDF file not found: {pdf_path}")
        return
    
    # Model name (can be changed)
    model_name = "llama3.2-vision:11b"  # or "llava:latest", "llava:7b", "bakllava:latest"
    
    if len(sys.argv) > 2:
        model_name = sys.argv[2]
    
    print("=" * 60)
    print("CMS-1500 Form Extraction using Ollama Vision")
    print("=" * 60)
    print(f"PDF: {pdf_path}")
    print(f"Model: {model_name}")
    print("=" * 60)
    print()
    
    try:
        # Extract data (saves to .txt file)
        result = extract_with_ollama(pdf_path, model_name)
        
        print("\n" + "=" * 60)
        print("EXTRACTION COMPLETE")
        print("=" * 60)
        print(f"Output saved to: {result['raw_output_file']}")
        print(f"Response length: {result['response_length']} characters")
        print(f"Response lines: {result['response_lines']} lines")
        print("\n[INFO] Raw output saved to .txt file")
        print("[INFO] You can now review and manually parse the JSON if needed")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Extraction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
