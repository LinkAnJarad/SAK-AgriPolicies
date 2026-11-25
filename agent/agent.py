from langchain.agents import create_agent
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

from agent.agent_tools import lexical_retrieve, semantic_retrieve, read_document

class Agent:
    def __init__(self):
        model = ChatOpenAI(
            model = os.getenv("COMPLETIONS_MODEL_NAME"),
            base_url = os.getenv("COMPLETIONS_API_BASE_URL"),
            api_key = os.getenv("COMPLETIONS_API_KEY"),
            temperature = 0.7,
            timeout = 120,
            max_retries = 3
        )

        self.agent = create_agent(
            model = model,
            tools = [lexical_retrieve, semantic_retrieve, read_document],
            system_prompt = "You are an intelligent assistant for assisting with searching information related to Philippine argicultural policies. Use the tools available to you to answer the user's question, which allows you to query a knowledge base. Do not invent tool results or answers if they are not present from the knowledge base. Always cite your answers." # replace with config.py
        )

        self.history: list[BaseMessage] = []

    def call_agent(self, message):

        history = [*self.history, HumanMessage(content=message)]

        result = self.agent.invoke(
            {"messages": history}
        )

        new_history = result["messages"]
        self.history = new_history

        return new_history