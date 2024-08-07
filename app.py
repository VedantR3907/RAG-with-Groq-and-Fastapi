import asyncio
import streamlit as st
import requests
from streamlit_extras.bottom_container import bottom
from functions.save_data_to_json import save_to_json
from functions.chat_history import display_chat_history, read_chat_history

FASTAPI_URL = "http://127.0.0.1:8000/groq_api_generator_response_llamaindex"


def sidebar():

    st.sidebar.subheader("File Uploads")
    uploaded_files = st.sidebar.file_uploader("Choose files", accept_multiple_files=True)
    if st.sidebar.button("Load Files"):
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # Display file name
                st.sidebar.write(f"File name: {uploaded_file.name}")
                # Process file here (e.g., save to disk, read content, etc.)
                file_content = uploaded_file.read().decode('utf-8')
                st.sidebar.write(file_content[:1000])  # Show first 1000 characters
        else:
            st.sidebar.write("No files uploaded.")

def bottom_container():
    with bottom():      
        user_prompt = st.chat_input("Write a question")
        if user_prompt:
            return user_prompt


def generate_answer(user_prompt):
    response = requests.post(
        FASTAPI_URL,
        json={"input": user_prompt},
    )

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