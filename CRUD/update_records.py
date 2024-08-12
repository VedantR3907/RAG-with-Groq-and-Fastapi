import os
import sys
import asyncio
from insert_records import upsert_data
from delete_records import delete_records
sys.path.append('../')
from constants.constants import PINECONE_NAMESPACE, PINECONE_CLIENT, PINECONE_INDEX_NAME, DIRECTORY_PATH
from text_and_embeddings.main import Generate_TextAndEmbeddings

index_name = PINECONE_INDEX_NAME
pc = PINECONE_CLIENT,
pc = pc[0]
name_space = PINECONE_NAMESPACE

json_path = os.path.join(DIRECTORY_PATH, 'extracted_output', 'metadata.json')

async def update_records(file_names: list, id: bool = False) -> None:
    """
    Updates records in Pinecone by first deleting the old records and then upserting new ones.

    Args:
        file_names (list): List of file names to be updated.
        metadata_path (str): Path to the JSON file containing metadata and embeddings.
        id (bool): If True, keep special characters in filenames; otherwise, remove them.
    """
    # Delete old records
    await delete_records(file_names, id=id)
    
    # Upsert updated data
    await Generate_TextAndEmbeddings(DIRECTORY_PATH, json_path)
    await upsert_data()

# Example usage
if __name__ == "__main__":

    # Define paths and file names
    metadata_json_path = '../extracted_output/metadata.json'
    file_names_to_update = ['abc.txt']
    
    # Run the update_records function asynchronously
    asyncio.run(update_records(file_names_to_update, metadata_json_path, id=False))