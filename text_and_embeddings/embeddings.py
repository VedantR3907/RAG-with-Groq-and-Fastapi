import os
import sys
import json
import aiofiles
import asyncio
sys.path.append('../')
from constants.constants import EMBEDDING_MODEL

# Adding the directory to the system path

embeddings = EMBEDDING_MODEL

async def generate_embeddings(metadata_path: str) -> None:
    """
    Generate embeddings for text chunks and update the metadata JSON file with these embeddings.

    Args:
        metadata_path (str): The path to the JSON file containing the metadata and where embeddings will be added.
    """
    
    # Load the metadata
    async with aiofiles.open(metadata_path, 'r', encoding='utf-8') as file:
        metadata = json.loads(await file.read())
    
    # Prepare the texts for embedding
    texts = [entry['metadata']['text'] for entry in metadata]
    
    # Generate embeddings for the texts
    document_embeddings = await asyncio.to_thread(embeddings.embed_documents, texts)
    
    # Update the metadata with embeddings
    for entry, embedding in zip(metadata, document_embeddings):
        entry['values'] = embedding  # Assign the embedding to the values key
    
    # Save the updated metadata with embeddings back to the same JSON file
    async with aiofiles.open(metadata_path, 'w', encoding='utf-8') as file:
        await file.write(json.dumps(metadata, ensure_ascii=False, indent=4))

# Example usage
async def main():
    # Get the directory path of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the path to the metadata JSON file relative to the current file's directory
    metadata_json_path = os.path.join(current_dir, '../extracted_output/metadata.json')
    
    # Generate embeddings and update the metadata
    await generate_embeddings(metadata_json_path)
    
    print(f"Metadata with embeddings has been updated in {metadata_json_path}.")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())