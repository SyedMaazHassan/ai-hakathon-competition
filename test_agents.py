from apps.depts.agents.router_agent.agent import ROUTER_AGENT
import json
from dotenv import load_dotenv
import json
load_dotenv()
# from apps.depts.agents.department_agent.agent import create_department_agent

user_request = {
    "text" :"I need help with rescue team, my neighbour's house is in fire",
    "city" : "Karachi"
}
output = ROUTER_AGENT.run(input=json.dumps(user_request))
print(output)

output = {
    "department": "fire_brigade",
    "confidence": 0.9,
    "urgency_indicators": ["emergency", "help"],
    "reason": "The request indicates a fire emergency at a neighbor's house, which is a critical situation requiring immediate response from the fire brigade. The presence of the word 'fire' and the request for a rescue team strongly indicate the need for fire services.",
    "keywords_detected": ["fire", "help", "rescue team"],
    "degraded_mode_used": None,
    "classification_source": "llm"
}



# DEPARTMENT_AGENT = create_department_agent("police")
# updated_dict = user_request.update(output)
# print(user_request)
# output = DEPARTMENT_AGENT.run(input=json.dumps(updated_dict))

# print(output.content)