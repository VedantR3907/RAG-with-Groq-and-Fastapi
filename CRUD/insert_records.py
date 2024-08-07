import os
import sys
import json
import aiofiles
sys.path.append('../')
from constants.constants import PINECONE_NAMESPACE, PINECONE_CLIENT, PINECONE_INDEX_NAME
from text_and_embeddings.main import Generate_TextAndEmbeddings
from pinecone import ServerlessSpec

index_name = PINECONE_INDEX_NAME
pc = PINECONE_CLIENT
namespace = PINECONE_NAMESPACE

async def upsert_data(json_path: str, index_name: str, namespace: str) -> None:
    """
    Asynchronously upserts data into a Pinecone index and removes these records from the metadata file.

    Args:
        json_path (str): The path to the JSON file containing the embeddings.
        index_name (str): The name of the Pinecone index.
        namespace (str): The namespace for the Pinecone index.
    """

    # Initialize Pinecone client
    if index_name not in await pc.list_indexes():
        await pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        print("INDEX CREATED SUCCESSFULLY")
    else:
        print("INDEX ALREADY EXISTS")
    
    index = pc.Index(index_name)
    
    # Asynchronously load the data from JSON
    async with aiofiles.open(json_path, 'r', encoding='utf-8') as file:
        data = json.loads(await file.read())
    
    # Prepare vectors for upsertion
    vectors = [
        {
            "id": entry["id"],
            "values": entry["values"],
            "metadata": {
                "text": entry["metadata"]["text"],
                "creation_date": entry["metadata"]["creation_date"],
                "file_name": entry["metadata"]["file_name"],
                "file_path": entry["metadata"]["file_path"],
                "file_size": entry["metadata"]["file_size"],
                "last_modified_date": entry["metadata"]["last_modified_date"]
            }
        }
        for entry in data
    ]
    
    # Extract IDs for the records to be upserted
    ids_to_upsert = [entry["id"] for entry in data]
    
    # Asynchronously upsert vectors into Pinecone
    await index.upsert(vectors=vectors, namespace=namespace)
    print(f"Data has been upserted into the Pinecone index '{index_name}'.")
    
    # Remove records from metadata that were upserted
    updated_metadata = [entry for entry in data if entry["id"] not in ids_to_upsert]
    
    # Asynchronously write the updated metadata back to the JSON file
    async with aiofiles.open(json_path, 'w', encoding='utf-8') as file:
        await file.write(json.dumps(updated_metadata, indent=4))
    
    print("Records that were upserted have been removed from the metadata file.")

if __name__ == "__main__":
    # Define paths and credentials
    metadata_json_path = '../extracted_output/metadata.json'
    directory_path = os.path.dirname(metadata_json_path)

    Generate_TextAndEmbeddings(directory_path, metadata_json_path)

    # Upsert data
    upsert_data(metadata_json_path, index_name)
