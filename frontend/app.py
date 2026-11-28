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

if "provenance_list" not in st.session_state:
    st.session_state.provenance_list = []

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

    if len(response["provenance"]) > 0:

        st.divider()

        st.markdown("### Top Sources:")

        hallucination_estimate = response["hallucination_estimate"] * 100
        st.progress(hallucination_estimate, text=f"Source Alignment Estimate: {hallucination_estimate:.2f}%")

        for d in response["provenance"]:
            with st.expander(d["title"]):
                st.subheader(d["source_document"])
                st.markdown(f"Score: {round(d["score"], 2)}")
                st.markdown(f"{d["chunk_content"][:450]}...")

        

    st.session_state.provenance_list.append(response["provenance"])
            


