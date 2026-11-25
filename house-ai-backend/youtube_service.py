
from urllib.parse import quote_plus

def get_youtube_link(recipe_name):

    query = f"{recipe_name} recipe step by step"
    
    encoded_query = quote_plus(query)

    youtube_link = (
        f"https://www.youtube.com/results?search_query={encoded_query}"
    )

    return youtube_link
