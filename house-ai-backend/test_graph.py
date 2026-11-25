from graph import graph

test_queries = [
    "How do I make rice pudding?",
    "Is milk that expired yesterday safe to drink?",
    "Why is my refrigerator not cooling?",
    "How can I reduce my household electricity consumption?"
]

for query in test_queries:
    print("\n" + "=" * 60)
    print("USER QUERY:", query)
    print("=" * 60)

    try:
        result = graph.invoke({
            "user_query": query
        })

        print("\nFINAL RESPONSE:")
        print(result.get("final_response", "No response generated."))

        print("\nDETECTED INTENT:")
        print(result.get("intent", []))
        print("\nENERGY AGENT OUTPUT:")
        print("Energy issue:", result.get("energy_issue"))
        print("Consumption:", result.get("consumption"))
        print("Estimated reason:", result.get("estimated_reason"))
        print("Saving suggestions:", result.get("saving_suggestions"))
    except Exception as e:
        print("\nERROR:", e)