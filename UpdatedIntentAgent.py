#import the api
import os
from getpass import getpass
os.environ["GROQ_API_KEY"] = getpass("Enter your Groq API key: ")

#shared memory (intent agent)
from typing import TypedDict

class HouseState(TypedDict):
    user_query: str
    tasks: list
    results: dict
    final_response: str

#function to input user query and modify state
def input_node(state:HouseState)-> HouseState:
    print("=== House Intake Form ===")
    user_query = input("Describe your household issue: ")
    return{
        "user_query" : user_query,
        "tasks" : [],
        "resuslts" : {},
        "final_response" : ""
    }

from langchain_groq import ChatGroq #enable node to chat with groq api
from langchain_core.messages import SystemMessage, HumanMessage #system prompt and human prompt

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0) #a high temp means llm is creative, temp=1 means llm creativity is high

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

Output format:

{
  "tasks": [
    {
      "agent": "<food_safety | appliance_diagnosis | energy_saving>",
      "query": "<relevant part of the user's request>"
    }
  ]
}

Examples

User:
"My fridge isn't cooling."

Output:
{
  "tasks":[
    {
      "agent":"appliance_diagnosis",
      "query":"My fridge isn't cooling."
    }
  ]
}

User:
"My fridge isn't cooling and my milk expired yesterday."

Output:
{
  "tasks":[
    {
      "agent":"appliance_diagnosis",
      "query":"My fridge isn't cooling."
    },
    {
      "agent":"food_safety",
      "query":"My milk expired yesterday."
    }
  ]
}

User:
"My AC leaks water and my electricity bill has doubled."

Output:
{
  "tasks":[
    {
      "agent":"appliance_diagnosis",
      "query":"My AC leaks water."
    },
    {
      "agent":"energy_saving",
      "query":"My electricity bill has doubled."
    }
  ]
}
"""