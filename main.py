from agent.agent import Agent

agent = Agent()

prompt = """Hello! Are there any PH policies for modernizing fisheries through research?"""
messages = agent.call_agent(prompt)

print(messages)

for i in messages:
    print("--------------")
    print(i.content)