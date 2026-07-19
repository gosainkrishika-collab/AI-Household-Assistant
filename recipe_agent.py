import json

from langchain_core.messages import SystemMessage, HumanMessage #system message:system prompt, Human Message: Human prompt
from intent_ai_agent import HouseState, llm

RECIPE_AGENT_PROMPT = """You are a culinary expert and recipe generator for a smart household assistant. Your role is to create delicious and practical recipes based on the user's request and any specified food items. The output should be a structured JSON object containing all the details of the recipe. You should prioritize using the `food_item` provided in the context, if available, to ensure relevant recipes. If no specific food item is mentioned, generate a general recipe based on the user's query. Ensure the recipe is suitable for cooking at home. Handle cases where the food item might be generic or if the user is just asking for recipe ideas.

Instructions:
- **recipe_name**: A concise and appealing name for the recipe.
- **ingredients**: A list of strings, where each string represents one ingredient and its quantity (e.g., "2 large eggs", "1 cup all-purpose flour").
- **instructions**: A list of strings, where each string is a single step in the cooking process. Provide clear and easy-to-follow steps.
- **cook_time**: The estimated cooking time (e.g., "20 minutes", "45 minutes").

Return ONLY a valid JSON object. Do not include any other text, explanations, or punctuation outside the JSON.

Examples:
User: Give me a recipe for chicken.
{
  "recipe_name": "Classic Roasted Chicken",
  "ingredients": [
    "1 whole chicken (3-4 lbs)",
    "2 tbsp olive oil",
    "1 tsp salt",
    "1/2 tsp black pepper",
    "1 tsp dried rosemary",
    "4 cloves garlic, minced",
    "1 lemon, quartered"
  ],
  "instructions": [
    "Preheat oven to 400°F (200°C).",
    "Pat chicken dry with paper towels.",
    "In a small bowl, mix olive oil, salt, pepper, rosemary, and garlic.",
    "Rub the mixture all over the chicken, including under the skin.",
    "Place lemon quarters in the chicken cavity.",
    "Roast for 60-90 minutes, or until internal temperature reaches 165°F (74°C).",
    "Let rest for 10 minutes before carving."
  ],
  "cook_time": "75 minutes"
}

User: I have tomatoes and eggs. What can I make?
{
  "recipe_name": "Scrambled Eggs with Tomatoes",
  "ingredients": [
    "3 large eggs",
    "1 medium tomato, diced",
    "1 tbsp butter",
    "Salt and pepper to taste",
    "Fresh parsley, chopped (optional)"
  ],
  "instructions": [
    "Whisk eggs in a bowl with salt and pepper.",
    "Melt butter in a non-stick pan over medium heat.",
    "Add diced tomatoes and cook for 2-3 minutes until slightly softened.",
    "Pour in the whisked eggs.",
    "Scramble gently until cooked to your desired consistency.",
    "Garnish with fresh parsley, if using."
  ],
  "cook_time": "8 minutes"
}

User: Suggest a quick dessert.
{
  "recipe_name": "No-Bake Chocolate Mousse",
  "ingredients": [
    "1 cup heavy cream",
    "1/2 cup powdered sugar",
    "1/4 cup unsweetened cocoa powder",
    "1 tsp vanilla extract",
    "Pinch of salt"
  ],
  "instructions": [
    "Chill a large mixing bowl and whisk attachments for 15 minutes.",
    "In the chilled bowl, combine heavy cream, powdered sugar, cocoa powder, vanilla extract, and salt.",
    "Whip on high speed until stiff peaks form.",
    "Spoon into serving dishes and refrigerate for at least 30 minutes before serving."
  ],
  "cook_time": "0 minutes"
}
"""

def recipe_agent(state: HouseState) -> HouseState:
    print("=== Recipe Agent ===")

    # Combine user query and any identified food item for better context
    query_for_llm = state['user_query']
    if state['food_item'] and state['food_item'] != 'unknown':
        query_for_llm = f"Recipe using {state['food_item']} and the original request: {state['user_query']}"
#check if state of food item is not empty("") and unknown
    response = llm.invoke([
        SystemMessage(content=RECIPE_AGENT_PROMPT),
        HumanMessage(content=query_for_llm)
    ])

    try:
        parsed_response = json.loads(response.content)
        state['recipe_name'] = parsed_response.get('recipe_name', '')
        state['ingredients'] = parsed_response.get('ingredients', [])
        state['instructions'] = parsed_response.get('instructions', [])
        state['cook_time'] = parsed_response.get('cook_time', '')

    except json.JSONDecodeError:
        print("Error: Could not parse JSON response from LLM for recipe.")

    return state