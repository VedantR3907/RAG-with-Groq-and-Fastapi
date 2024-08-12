import json
import requests
from typing import List, Tuple, IO
from constants.constants import FASTAPI_URL

def response_from_model(user_prompt: str):

    API = f"{FASTAPI_URL}/groq_api_generator_response_llamaindex"
    response = requests.post(
        API,
        json={"input": user_prompt},
    )

    return response

def loading_files(files: List[Tuple[str, Tuple[str, IO, str]]]):
    """
    Uploads files to the specified API endpoint.

    :param files: A list of tuples where each tuple contains (filename, file object, MIME type).
    :param api_url: The URL of the API endpoint to which the files should be uploaded.
    :return: The response object from the API request.
    """

    API = f"{FASTAPI_URL}/loader/uploadfiles-without-filepath/"
    try:
        # Send the POST request with files
        response = requests.post(API, files=files)
        
        # Return the response object
        return response
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def insert_documents_to_database():
    """
    Inserts the uploaded documents into the database by calling the specified API endpoint.
    """
    API = f"{FASTAPI_URL}/crud/insert-documents"
    
    try:
        # Send the POST request with files
        response = requests.post(API)
        return response
    except requests.RequestException as e:
        return (f"An error occurred: {e}")
    


def delete_documents_from_database(file_names: List[str], keep_special_chars: bool = False, delete_all: bool = False):
    """
    Sends a request to delete documents from the database.

    :param file_names: List of filenames to be deleted.
    :param keep_special_chars: Boolean flag to keep special characters in filenames if True.
    :param delete_all: Boolean flag to delete all records in the namespace if True.
    :return: The response object from the API request.
    """
    API = f"{FASTAPI_URL}/crud/delete-documents"
    
    try:
        response = requests.post(
            API,
            data=json.dumps(file_names),
            params={"id": keep_special_chars, "deleteall": delete_all}
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None