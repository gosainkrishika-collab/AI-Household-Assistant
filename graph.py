#imports
from langgraph.graph import StateGraph, END

from intent_ai_agent import HouseState, intake_node, intent_query_agent
from food_safety_agent import food_safety_agent
from recipe_agent import recipe_agent
from appliance_ai_agent import appliance_agent_node
from energy_ai_agent import energy_agent_node
from recommendation_agent import recommendation_agent
from response_formatter import response_formatter_node

#create the graph
builder = StateGraph(HouseState)

#create all the nodes
builder.add_node("intake",intake_node)
builder.add_node("intent",intent_query_agent)
builder.add_node("food",food_safety_agent)
builder.add_node("recipe",recipe_agent)
builder.add_node("appliance",appliance_agent_node)
builder.add_node("energy",energy_agent_node)
builder.add_node("recommendation_generator", recommendation_agent)
builder.add_node("response_formatter",response_formatter_node)

#set entry point
builder.set_entry_point("intake")

#connect all nodes
builder.add_edge("intake", "intent")
builder.add_edge("intent", "food")
builder.add_edge("food", "recipe")
builder.add_edge("recipe", "appliance")
builder.add_edge("appliance", "energy")
builder.add_edge("energy", "recommendation_generator")
builder.add_edge("recommendation_generator", "response_formatter")
builder.add_edge("response_formatter", END)

#compile the graph
graph = builder.compile()

#temp test block
if __name__ == "__main__":
    final_state = graph.invoke({})

    print("\n===== FINAL RESPONSE =====")
    print(final_state["final_response"])