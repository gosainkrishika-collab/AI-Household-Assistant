
# import the libraries
import os
from getpass import getpass
os.environ["GROQ_API_KEY"] = getpass("Enter your Groq API key:")

#creatign the shared memory
from typing import TypedDict, Literal, Optional, List
#creating house states(shared memeory)
class HouseState(TypedDict):
   user_query: str
   intent: Literal['food_query', 'appliance_query', 'energy_query', 'unknown']
   food_item: str
   expiry_status: Literal['expired','fresh','unknown']
   expiry_date: Optional[str] # Made optional(field has a str value or nothing)
   safety_status: Literal['safe', 'unsafe', 'unknown']
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
    print("=== House Intake Form ===")
    name = input("Patient name: ")
    user_query = input("Describe your problem: ")
    return{
       "user_query": user_query,
       "intent": "unknown",
       "food_item": "", #implies no specific food item has been identified
       "expiry_status": "unknown", #implies that the state is currently undetermined
       "expiry_date": "",
       "safety_status": "unknown",
        
        #recipe genrator
        "recipe_name": str,
        "ingredients": List[str],
        "instructions": List[str],
        "cook_time": str,
       
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
       "final response": ""
    }


# creatign router node
from langchain_groq import ChatGroq # enable node to chat with groq api
from langchain_core.messages import SystemMessage, HumanMessage #system message:system prompt, Human Message: Human prompt

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0) #temp high, llm mre creative if temp =1, LLM creativity high

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
- Split the user's request into separate queries whenever necessary.
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

Respond with ONLY the name of the intent category, e.g., 'food_query', 'appliance_query', 'energy_query', or 'unknown'. Do not provide any other text, explanations, or punctuation.

Here are some examples:
User: Is the milk in the fridge still good?
Intent: food_query

User: My fridge is not cooling properly.
Intent: appliance_query
User: My thermostat is not working.
Intent: appliance_query

User: How much energy does my fridge use?
Intent: energy_query
User: Best thermostat setting to save electricity.
Intent: energy_query
"""

# Hard safety-net keywords with assigned weights (1-5), overriding the LLM if matched.
# Higher weights indicate higher priority for that keyword.
# You can adjust these weights as needed.

FOOD_QUERY_KEYWORDS = {
    "food": 3, "gluten": 3, "lactose": 3, "egg": 3, "meat": 3, "chicken": 3, "fish": 3, "rice": 5, "bread": 3, "milk": 4, "cheese": 3, "butter": 3, "yogurt": 3, "banana": 3, "apple": 3, "orange": 3, "potato": 3, "tomato": 3, "onion": 3,
    "pasta": 3, "pizza": 3, "burger": 3, "eat": 3, "recipe": 5, "cook": 5, "ingredient": 3, "meal": 5, "breakfast": 3, "lunch": 3, "dinner": 3, "diet": 3, "nutrition": 3, "fridge": 2, "refrigerator": 2, "pantry": 3, "expiration": 5,
    "fresh": 4, "spoiled": 5, "safe to eat": 5, "fruit": 3, "vegetable": 3, "dairy": 3, "seafood": 3, "grain": 3, "beverages": 3, "snack": 3, "rotten": 5, "mold": 5, "food poisoning": 5, "freeze": 3, "leftovers": 3, "reheat": 3
}

APPLIANCE_QUERY_KEYWORDS = {
    "appliance": 3, "refrigerator": 4, "fridge": 4, "air fryer": 3, "oven": 3, "microwave": 3, "dishwasher": 3, "washing machine": 3, "dryer": 3, "stove": 3, "cooktop": 3, "blender": 3, "grinder": 3, "toaster": 3, "chimney": 3, "exhaust fan": 3, "coffee maker": 3, "vacuum": 3, "air conditioner": 3, "AC": 3, "fan": 3, "water purifier": 3, "geyser": 3, "water heater": 3, "induction": 3, "electric kettle": 3, "kettle": 3, "mixer": 3, "thermostat": 4, "smart home device": 3, "broken": 5, "repair": 5, "fix": 5, "malfunction": 5, "problem": 4, "error": 4, "not working": 5, "not cooling": 5, "overheating": 5, "water leakage": 5, "strange noise": 4, "loud noise": 4, "vibration": 4, "smoke": 5, "burning smell": 5, "spark": 5, "power failure": 5, "low performance": 4, "slow": 4, "stopped working": 5, "temperature": 3, "setting": 3, "manual": 3, "troubleshoot": 4
}

ENERGY_QUERY_KEYWORDS = {
    "energy": 3, "consumption": 3, "smart home": 3, "electricity": 4, "power": 4, "bill": 5, "cost": 4, "usage": 3, "monitor": 3, "efficiency": 4, "save energy": 5, "energy saving": 5, "carbon footprint": 3, "green energy": 3, "solar": 3, "wind": 3, "battery": 3, "grid": 3, "utilities": 4, "meter": 3, "peak hours": 3, "off-peak hours": 3, "thermostat setting": 4, "HVAC": 3, "heating": 3, "cooling": 3, "light": 3, "lighting": 3, "water heater energy": 3, "insulation": 3, "drafts": 3, "leakage": 3, "renewable": 3, "non-renewable": 3, "kilowatt": 3, "watt": 3, "joule": 3, "Btu": 3, "gas": 3, "propane": 3, "fuel": 3, "tariff": 3, "provider": 3, "utility company": 3, "energy audit": 3, "conservation": 3, "emission": 3
}

# FunctiON for calculatign score for each dictionary
def score_count(user_query,keyword_dict):
  score =0
  query = user_query.lower()
  for keyword, weight in keyword_dict.items(): # keyword is there in dictionary
    if keyword in query: # keyword is in user query also
      score += weight # weight of the keyeord is assigned to the score
  return score


#aFunction to calculate score for each dictionary
def route_intent(user_query: str):

    print("=== Intent Router ===")

    user_query = user_query.lower()

    food_score = score_count(user_query, FOOD_QUERY_KEYWORDS)
    appliance_score = score_count(user_query, APPLIANCE_QUERY_KEYWORDS)
    energy_score = score_count(user_query, ENERGY_QUERY_KEYWORDS)

    scores = {
        "food_query": food_score,
        "appliance_query": appliance_score,
        "energy_query": energy_score
    }

    print(scores)
    best_intent = max(scores, key=scores.get)
    highest = scores[best_intent]
    sorted_scores = sorted(scores.values(), reverse=True)

    # No keyword matched
    if highest == 0:
        return llm_route(user_query)

    # Ambiguous query
    if sorted_scores[0] - sorted_scores[1] <= 2:
        return llm_route(user_query)

    return best_intent

# Using llm if the score =0 or difference between 2 scores is less than 2
def llm_route(user_query):
   response = llm.invoke([
       SystemMessage(content=INTENT_SYSTEM_PROMPT),
       HumanMessage(content=user_query)
    ])
   return response.content.strip()
#importing the library
import json
def intent_query_agent(state: HouseState) -> HouseState:
    response = llm.invoke([
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=state['user_query'])
    ])
    state["intent"] = response.content.strip()
    return state