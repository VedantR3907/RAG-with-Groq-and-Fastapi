import os
import json
import asyncio
import streamlit as st
from typing import List, Tuple, IO
from streamlit_extras.bottom_container import bottom
from functions.save_data_to_json import save_to_json
from functions.chat_history import display_chat_history, read_chat_history
from streamlit_api_calls.main import response_from_model, loading_files, insert_documents_to_database, delete_documents_from_database, load_files_with_images
from constants.constants import DIRECTORY_PATH

extracted_output_folder = os.path.join(DIRECTORY_PATH, 'extracted_output')
documents_folder = os.path.join(DIRECTORY_PATH, 'documents')

def load_metadata_excluded_files() -> set:
    metadata_path = os.path.join(DIRECTORY_PATH, 'extracted_output', 'metadata.json')
    excluded_files = set()
    
    if os.path.exists(metadata_path):
        try:
            # Try reading with UTF-8 encoding first
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                if isinstance(metadata, list):
                    for entry in metadata:
                        if 'metadata' in entry and 'file_name' in entry['metadata']:
                            # Add the file names to the excluded set
                            excluded_files.add(entry['metadata']['file_name'])
                else:
                    st.warning("Metadata JSON is not a list.")
        except UnicodeDecodeError:
            # Fallback to another encoding if UTF-8 fails
            with open(metadata_path, 'r', encoding='latin-1') as f:
                metadata = json.load(f)
                if isinstance(metadata, list):
                    for entry in metadata:
                        if 'metadata' in entry and 'file_name' in entry['metadata']:
                            # Add the file names to the excluded set
                            excluded_files.add(entry['metadata']['file_name'])
                else:
                    st.sidebar.warning("Metadata JSON is not a list.")
        except json.JSONDecodeError:
            st.sidebar.warning("Error decoding JSON from metadata file.")
    else:
        st.sidebar.warning("Metadata file does not exist.")

    return excluded_files

def delete_local_files(file_names: List[str]):
    """Delete specified files from both 'extracted_output' and 'documents' directories."""

    for file_name in file_names:
        if file_name == 'metadata.json':
            continue

        file_path_extracted = os.path.join(extracted_output_folder, file_name)
        file_path_documents = os.path.join(documents_folder, file_name)
        
        # Remove from extracted_output folder if exists
        if os.path.isfile(file_path_extracted):
            os.remove(file_path_extracted)
        
        # Remove from documents folder if exists
        if os.path.isfile(file_path_documents):
            os.remove(file_path_documents)

def sidebar():
    st.sidebar.subheader("File Uploads")
    
    uploaded_files = st.sidebar.file_uploader("Choose files", accept_multiple_files=True)
    
    if uploaded_files:
        if st.sidebar.button("Load Files"):
            files: List[Tuple[str, Tuple[str, IO, str]]] = [
                ('files', (uploaded_file.name, uploaded_file, 'application/pdf'))
                for uploaded_file in uploaded_files
            ]

            # HITTING LOADING FILES API
            response = load_files_with_images(files)

            if response:
                if response.status_code == 200:
                    st.sidebar.success("Files uploaded successfully")
                    # Store the uploaded files in the session state
                    st.session_state.uploaded_files = files
                else:
                    st.sidebar.error('Error:', response.text)
            else:
                st.sidebar.error('Failed to upload files.')

        # Show Insert Documents to Database button if files are uploaded
        if 'uploaded_files' in st.session_state:
            if st.sidebar.button("Insert Documents to Database"):
                insert_documents_to_database()
                st.sidebar.success("Documents inserted into the database successfully.")

            if os.path.exists(extracted_output_folder):
                # Load metadata to exclude certain files
                excluded_files = load_metadata_excluded_files()
                
                # List only .txt files and remove .txt extension for display
                files_in_folder = [f for f in os.listdir(extracted_output_folder) 
                                if os.path.isfile(os.path.join(extracted_output_folder, f)) 
                                and f.lower().endswith('.txt')]

                # Remove the .txt extension for display and apply exclusion
                files_display_names = [
                    os.path.splitext(f)[0] 
                    for f in files_in_folder 
                    if f not in excluded_files  # Exclude files based on the original filename with extension
                ]
                
                selected_files = st.sidebar.multiselect(
                    "Select files to delete.", 
                    options=files_display_names
                )
                
                if st.sidebar.button("Delete Documents from Database"):
                    # Map the selected display names back to the original filenames
                    selected_files_full = [f"{name}.txt" for name in selected_files]

                    print(selected_files_full)

                    response = delete_documents_from_database(selected_files_full)

                    if response and response.status_code == 200:
                        st.sidebar.success("Documents deleted from the database successfully.")
                    else:
                        st.sidebar.error(f"Error deleting documents: {response.text if response else 'Unknown error'}")

                    delete_local_files(selected_files_full)
                
                # New button to delete all documents from the database
                if st.sidebar.button("Delete All Documents from Database"):
                    response = delete_documents_from_database(file_names= [], delete_all=True)  # Call the API with deleteall=true

                    if response and response.status_code == 200:
                        st.sidebar.success("All documents deleted from the database successfully.")

                        all_files = [f for f in os.listdir(extracted_output_folder) if os.path.isfile(os.path.join(extracted_output_folder, f))]
                        all_files.extend([f for f in os.listdir(documents_folder) if os.path.isfile(os.path.join(documents_folder, f))])
                        
                        # Delete from local filesystem
                        delete_local_files(all_files)
                    else:
                        st.sidebar.error(f"Error deleting all documents: {response.text if response else 'Unknown error'}")
        else:
            st.sidebar.error("The folder 'extracted_output' does not exist.")

def bottom_container():
    with bottom():      
        user_prompt = st.chat_input("Write a question")
        if user_prompt:
            return user_prompt

def generate_answer(user_prompt):
    response = response_from_model(user_prompt)

    if response.status_code == 200:
        # Process streaming response
        answer = response.text  # Remove extra whitespace/newlines
        if answer.startswith('"') and answer.endswith('"'):
            answer = answer[1:-1]  # Remove the leading and trailing quotes

        answer = answer.replace('\\n', '\n')
        final_response = ''
        for i in answer.split(' '):
            text = i + " "
            yield text
            final_response += text
        
        save_to_json(user_prompt, final_response)

    else:
        st.error(f"Error: {response.status_code}")

async def main():
    st.header("GROQ API CHATBOT")
    sidebar()
    user_prompt = bottom_container()
    if user_prompt is not None and user_prompt != '':
        answer = generate_answer(user_prompt)
        with st.container(border=True, height=500):
            chat_history = await read_chat_history()
            display_chat_history(chat_history)
            
            with st.chat_message("HUMAN", avatar='./assets/user.png'):
                st.markdown(user_prompt)
                
            with st.chat_message("AI", avatar='./assets/meta.png'):
                st.write(answer)

asyncio.run(main())
