import sys
sys.path.append('.')
from models.valorant_agent import AgentManager

manager = AgentManager()
print(f"Loaded {len(manager.get_all_agents())} agents.")
for agent in manager.get_all_agents()[:5]:
    print(f"- {agent.name} ({agent.role})")
