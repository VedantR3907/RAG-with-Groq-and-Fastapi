import streamlit as st
import requests
from streamlit_extras.bottom_container import bottom
import time

FASTAPI_URL = "http://127.0.0.1:8000/groq_api_generator_response"


def bottom_container():
    with bottom():
            
        user_prompt = st.chat_input("Write a question")


        if user_prompt:
            return user_prompt


def generate_answer(user_prompt, system_prompt):
    response = requests.post(
        FASTAPI_URL,
        json={"system_prompt": system_prompt, "user_prompt": user_prompt},
        stream=True
    )

    if response.status_code == 200:
        # Process streaming response
        answer = response.text
        for i in answer.split(' '):
            yield i + " "

    else:
        st.error(f"Error: {response.status_code}")

def main():

    st.header("GROQ API CHATBOT")

    user_prompt = bottom_container()

    if user_prompt is not None and user_prompt != '':

        answer = generate_answer(user_prompt, "you are an helpful assistant.")

        with st.container(border=True, height=500):
            with st.chat_message("HUMAN", avatar='./assets/user.png'):
                st.markdown(user_prompt)
                
            with st.chat_message("AI", avatar='./assets/meta.png'):
                st.write(answer)

main()