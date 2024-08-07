import os
import fitz
from fastapi import UploadFile
from typing import List
import io

output_path = './extracted_output'

async def process_and_save_files(files: List[UploadFile]):
    saved_files = []
    for file in files:
        # Read the file content
        file_content = await file.read()
        
        # Create an in-memory file object
        pdf_file = io.BytesIO(file_content)
        
        # Open the PDF with PyMuPDF
        doc = fitz.open(stream=pdf_file, filetype="pdf")
        
        # Initialize an empty string to accumulate text
        full_text = ""
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            full_text += page.get_text()
        
        # Create a text file with the same name as the PDF, saved to output_path
        txt_filename = os.path.join(output_path, file.filename.rsplit('.', 1)[0] + '.txt')
        with open(txt_filename, 'w', encoding='utf-8') as txt_file:
            txt_file.write(full_text)
        
        # Track the path of the saved file
        saved_files.append(txt_filename)
        
        # Close the document
        doc.close()
    
    return saved_files