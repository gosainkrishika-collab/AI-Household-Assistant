
# import the libraries
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

#creatign the shared memory
from typing import TypedDict, Literal, Optional, List
#creating house states(shared memeory)
class HouseState(TypedDict):
   user_query: str
   intent: List[Literal['food_query', 'appliance_query', 'energy_query']]
   food_item: str
   expiry_status: Literal['expired','fresh','unknown']
   expiry_date: Optional[str] # Made optional(field has a str value or nothing)
   safety_status: Literal['safe', 'unsafe', 'unknown']
   
   #recipe generator
   recipe_name: str
   ingredients: List[str]
   instructions: List[str]
   cook_time: str
   
   #--------------------------
   #appliance diagnosis agent:
   device: str
   problem: str
   symptoms: List[str]
   #problem analysis
   possible_causes: List[str]
   #risk assessment
   risk_level: Literal["Low","Medium","High","Critical","Unknown"]
   risk_reason: str
   #energy saving agent:
   energy_issue: str
   suspected_causes: List[str]
   #electricity analysis
   consumption: Literal["Low", "Moderate", "High", "Unknown"]
   estimated_reason: str
   saving_suggestions: List[str]
   #--------------------
   recommendations:List[str]
   final_response: str

#creating intake node
def intake_node(state:HouseState)-> HouseState:
    return{
       "user_query": state["user_query"],
       "intent": [],
       "food_item": "", #implies no specific food item has been identified
       "expiry_status": "unknown", #implies that the state is currently undetermined
       "expiry_date": "",
       "safety_status": "unknown",
        
        #recipe generator
        "recipe_name": "",
        "ingredients": [],
        "instructions": [],
        "cook_time": "",
       
       #-------------------
       #appliance diagnosis
       "device": "",
       "problem": "",
       "symptoms": [],
       #problem analysis
       "possible_causes": [],
       #risk assessment
       "risk_level": "Unknown",
       "risk_reason": "",
       #energy saving
       "energy_issue": "",
       "suspected_causes": [],
       #electricity analysis
       "consumption": "Unknown",
       "estimated_reason": "",
       "saving_suggestions": [],
       #----------------------
       "recommendations": [],
       "final_response": ""
    }


# creatign router node
from langchain_groq import ChatGroq # enable node to chat with groq api
from langchain_core.messages import SystemMessage, HumanMessage #system message:system prompt, Human Message: Human prompt

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=GROQ_API_KEY) #temp high, llm mre creative if temp =1, LLM creativity high

INTENT_SYSTEM_PROMPT = """You are the Task Planning Agent for a Smart Household Assistant.

Your job is to analyze the user's request and decide which specialized AI agents should handle different parts of it.

The available agents are:

1. food_safety
Use this agent whenever the user asks about:
- food freshness
- food spoilage
- expiry dates
- whether food is safe to eat
- food storage
- leftover food
- recipes using available ingredients

Examples:
- "Can I eat this chicken after two days?"
- "My milk expired yesterday."
- "How should I store cooked rice?"
- "Suggest a recipe using eggs and tomatoes."

2. appliance_diagnosis
Use this agent whenever the user reports:
- broken appliances
- unusual appliance behaviour
- noises
- leaks
- overheating
- electrical faults
- maintenance questions

Examples:
- "My fridge isn't cooling."
- "The washing machine is shaking."
- "My microwave sparks."
- "The AC is leaking water."

3. energy_saving
Use this agent whenever the user asks about:
- electricity bills
- saving electricity
- reducing energy consumption
- efficient appliance usage
- energy recommendations

Examples:
- "My electricity bill is too high."
- "How can I reduce power consumption?"
- "Does keeping the AC at 18°C waste electricity?"
- "Which appliances consume the most power?"

Rules:

- A single user message may contain multiple independent tasks.
- Detect ALL valid tasks.
- Never merge unrelated tasks into one.
- Preserve the user's original wording as much as possible.

If no supported task exists, return an empty task list.

Return ONLY valid JSON.

Do NOT:

- Answer the user's question.
- Give recommendations.
- Diagnose appliances.
- Judge food safety.
- Suggest energy-saving tips.

Your ONLY responsibility is planning.

If unsure, make the best possible classification based on the user's request.

Respond with ONLY a valid JSON object. Do not provide any other text, explanations, or punctuation.

Here are some examples:
User: Is the milk in the fridge still good? My fridge is not cooling properly.
Response: {"intent": ["food_query", "appliance_query"]}

User: How much energy does my fridge use? My thermostat is not working.
Response: {"intent": ["energy_query", "appliance_query"]}

User: My electricity bill is too high.
Response: {"intent": ["energy_query"]}

User: Can I eat this apple? And how can I save electricity?
Response: {"intent": ["food_query", "energy_query"]}

User: What is the capital of France?
Response: {"intent": []}
"""


#importing the library
import json

def intent_query_agent(state: HouseState) -> HouseState:
    response = llm.invoke([
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=state["user_query"])
    ])

    try:
        parsed_response = json.loads(response.content)
        state["intent"] = list(set(parsed_response.get("intent", []))) #to ensure it doesn't return duplicate values
    except json.JSONDecodeError:
        print("Error: Could not parse JSON response from LLM.")
        state["intent"] = []

    return state