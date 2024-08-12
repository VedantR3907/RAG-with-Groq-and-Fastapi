import os
import fitz
from fastapi import UploadFile
from typing import List
import io

# Define the paths for the two different folders
base_path = os.path.dirname(os.path.dirname(__file__))
extracted_output_path = os.path.join(base_path, 'extracted_output')
documents_folder = os.path.join(base_path, 'documents')

# Create the folders if they do not exist
os.makedirs(extracted_output_path, exist_ok=True)
os.makedirs(documents_folder, exist_ok=True)

async def process_and_save_files(files: List[UploadFile]):
    saved_text_files = []
    
    for file in files:
        # Save the uploaded file to the documents folder
        document_file_path = os.path.join(documents_folder, file.filename)
        with open(document_file_path, 'wb') as f:
            file_content = await file.read()
            f.write(file_content)
        
        # Process only PDF files for text extraction
        if file.filename.lower().endswith('.pdf'):
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
            
            # Create a text file with the same name as the PDF, saved to extracted_output_path
            txt_filename = os.path.join(extracted_output_path, file.filename.rsplit('.', 1)[0] + '.txt')
            with open(txt_filename, 'w', encoding='utf-8') as txt_file:
                txt_file.write(full_text)
            
            # Track the path of the saved text file
            saved_text_files.append(txt_filename)
            
            # Close the document
            doc.close()
    
    return saved_text_files