import os
import asyncio
import aiofiles
import sys
sys.path.append('../')
from loaders.llamaparse_loader import llamaparser
from loaders.pdf_loader import pdfLoader
from loaders.image_loader import generate_descriptions_for_images
from typing import List
from fastapi import UploadFile
from constants.constants import FILES_INPUT_DIR, FILES_OUTPUT_DIR

input_dir = FILES_INPUT_DIR
output_dir = FILES_OUTPUT_DIR

async def save_files_to_directory(files: List[UploadFile]):
    """
    Save uploaded files to the specified directory.

    Args:
        files (List[UploadFile]): List of files to save.
        input_dir (str): Directory path where files will be saved.

    Raises:
        Exception: If there is an error during file saving.
    """
    # Ensure the directory exists
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)

    # Save each file to the input directory
    for file in files:
        file_path = os.path.join(input_dir, file.filename)
        try:
            async with aiofiles.open(file_path, 'wb') as buffer:
                while chunk := await file.read(1024):  # Read file in chunks
                    await buffer.write(chunk)
        except Exception as e:
            raise Exception(f"Error saving file {file.filename}: {e}")

async def process_files():
    """
    Process files in the input directory based on their extensions and
    save the output to the specified directory.

    Args:
        input_dir (str): The directory containing files to process.
        output_dir (str): The directory to save the output files.
    """
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # List all files in the input directory
        files = os.listdir(input_dir)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        text_files = [f for f in files if f.lower().endswith('.txt') or f.lower().endswith('.doc')]
        image_files = [f for f in files if f.lower().endswith('.png') or f.lower().endswith('.jpeg')]

        # Create a list of tasks for processing
        tasks = []

        # Process PDF files
        if image_files:
            print("Processing image files...")
            tasks.append(generate_descriptions_for_images(input_dir, output_dir))
            
        if pdf_files:
            print("Processing PDF files...")
            tasks.append(pdfLoader(input_dir=input_dir, output_dir=output_dir))

        # Process .txt and .doc files
        if text_files:
            print("Processing text and doc files...")
            tasks.append(llamaparser(input_dir=input_dir, output_dir=output_dir))
        
        # Await all tasks
        await asyncio.gather(*tasks)

        print(f"Processing complete. Output files are located in '{output_dir}'.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(process_files())
