from dataclasses import dataclass
from typing import List, Optional, Dict
import json
import os

@dataclass
class ValorantAgent:
    name: str
    role: str
    description: str
    abilities: List[str]
    icon_path: Optional[str] = None

class AgentManager:
    def __init__(self):
        self.agents: Dict[str, ValorantAgent] = {}
        # Pre-seed with known agents to start with, or we could load from a file
        self._initialize_default_agents()

    def _initialize_default_agents(self):
        # This list can be expanded or loaded dynamically
        # For now, we list the known agents to help the vision system
        start_agents = [
            ("Jett", "Duelist"), ("Phoenix", "Duelist"), ("Reyna", "Duelist"), ("Raze", "Duelist"), ("Yoru", "Duelist"), ("Neon", "Duelist"), ("Iso", "Duelist"),
            ("Sage", "Sentinel"), ("Cypher", "Sentinel"), ("Killjoy", "Sentinel"), ("Chamber", "Sentinel"), ("Deadlock", "Sentinel"), ("Vyse", "Sentinel"),
            ("Brimstone", "Controller"), ("Viper", "Controller"), ("Omen", "Controller"), ("Astra", "Controller"), ("Harbor", "Controller"), ("Clove", "Controller"),
            ("Sova", "Initiator"), ("Breach", "Initiator"), ("Skye", "Initiator"), ("KAY/O", "Initiator"), ("Fade", "Initiator"), ("Gekko", "Initiator"), ("Tejo", "Initiator") # Tejo might be new/leaked, but keeping consistent
        ]
        
        for name, role in start_agents:
            self.agents[name.upper()] = ValorantAgent(
                name=name,
                role=role,
                description="",
                abilities=[],
                icon_path=f"blueprints/official/agents/{name.lower()}_icon.png"
            )

    def get_agent(self, name: str) -> Optional[ValorantAgent]:
        return self.agents.get(name.upper())

    def get_all_agents(self) -> List[ValorantAgent]:
        return list(self.agents.values())

    def get_agent_names(self) -> List[str]:
        return [agent.name for agent in self.agents.values()]
