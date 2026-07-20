from IPython.display import Image, display
#temp test block
if __name__ == "__main__":
    png_data = graph.get_graph().draw_mermaid_png()

    with open("house_ai_graph.png", "wb") as f:
        f.write(png_data)

    print("Graph saved as house_ai_graph.png")

    final_state = graph.invoke({
        "user_query": "My milk expired yesterday."
    })
print("\n===== FINAL RESPONSE =====")
print(final_state["final_response"])