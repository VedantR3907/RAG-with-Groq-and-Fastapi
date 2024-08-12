import os
import sys
import asyncio
sys.path.append('../')
from text_and_embeddings.textsplitter import process_metadata
from text_and_embeddings.embeddings import generate_embeddings

async def Generate_TextAndEmbeddings(directory_path: str, json_path: str) -> None:
    # Process metadata
    await process_metadata(directory_path)

    # Define the path to the metadata JSON file
    metadata_json_path = json_path

    # Generate embeddings and update the metadata
    await generate_embeddings(metadata_json_path)

    print(f"Metadata with embeddings has been updated in {metadata_json_path}.")

if __name__ == "__main__":
    # Define directory and JSON paths
    directory_path = '../extracted_output'
    json_path = os.path.join(directory_path, 'metadata.json')

    # Run the async function
    asyncio.run(Generate_TextAndEmbeddings(directory_path, json_path))
