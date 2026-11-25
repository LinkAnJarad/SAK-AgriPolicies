from agent.agent import Agent

_sessions: dict[str, Agent] = {}

def get_agent_from_session(session_id: str) -> Agent:
    if session_id not in _sessions:
        _sessions[session_id] = Agent()
        return _sessions[session_id]
    
    return _sessions[session_id]