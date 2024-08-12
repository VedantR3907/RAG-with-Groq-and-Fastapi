import sys
import asyncio
sys.path.append('../')
from typing import List
from constants.constants import PINECONE_NAMESPACE, PINECONE_CLIENT, PINECONE_INDEX_NAME
from text_and_embeddings.textsplitter import filter_filename


index_name = PINECONE_INDEX_NAME
pc = PINECONE_CLIENT,
pc = pc[0]
namespace = PINECONE_NAMESPACE

async def delete_records(file_names: List[str], id: bool = False, deleteall: bool = False) -> None:
    """
    Asynchronously deletes all records associated with the given list of file names from Pinecone.

    Args:
        file_names (List[str]): List of file names whose chunks should be deleted.
        id (bool): If True, keep special characters in filenames; otherwise, remove them.
        deleteall (bool): If True, delete all records in the namespace.
    """
    # Initialize Pinecone index
    index = pc.Index(index_name)

    if deleteall:
        # Delete all records from the namespace
        index.delete(namespace=namespace, delete_all=True)
        print('All records deleted successfully')
        return
    
    # Extract existing IDs from Pinecone
    existing_ids = list(index.list(namespace=namespace))[0]

    ids_to_delete = set()
    
    for file_name in file_names:
        formatted_file_name = filter_filename(file_name, id)
        ids_to_delete.update({existing_id for existing_id in existing_ids if formatted_file_name in existing_id})
    
    if not ids_to_delete:
        print("No records found for the specified files.")
        return
    
    # Delete records from Pinecone
    index.delete(ids=list(ids_to_delete), namespace=namespace)
    print(f"Records associated with the specified files have been deleted from Pinecone index '{index_name}'.")

# Example usage
if __name__ == "__main__":
    async def main():
        # Define paths and keys
        file_names_to_delete = ['Vedant Rajpurohit Resume new.txt']
        
        # Delete records for the specified files
        await delete_records(file_names_to_delete, id=False, deleteall=False)
    
    # Run the async main function
    asyncio.run(main())