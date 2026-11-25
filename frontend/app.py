import streamlit as st
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage

import requests
from dotenv import load_dotenv
import os
from uuid import uuid4

load_dotenv()
SEND_MESSAGE_ENDPOINT = os.getenv("SEND_MESSAGE_ENDPOINT")


if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())

st.title("SAK-AgriPolicies")
st.markdown("Start chatting! SAK-AgriPolicies has a knowledge base containing 68 detailed documents on Philippine agricultural policies and frameworks.")

for message in st.session_state.messages:

    if isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            if message.content != "":
                st.markdown(message.content)

    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)

if prompt := st.chat_input("Ask anything about PH agricultural policies..."):

    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append(
        HumanMessage(content=prompt)
    )

    payload = {
        "message": prompt,
        "session_id": st.session_state.session_id
    }
    response = requests.post(SEND_MESSAGE_ENDPOINT, json=payload)

    response = response.json()


    with st.chat_message("assistant"):
        st.markdown(response["message"])

    st.session_state.messages.append(
        AIMessage(content=response["message"])
    )

