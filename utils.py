import ollama
from qdrant_client import QdrantClient
from openai import OpenAI
from icecream import ic
import concurrent.futures

ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required, but unused
)

qdrant_client = QdrantClient(url="http://localhost:6333")


def get_embedding(text, model="mxbai-embed-large"):
    return ollama.embeddings(
        model=model,
        prompt=text,
    )["embedding"]


def similarity_search(query, limit=10):
    query_vector = get_embedding(query)
    search_result = qdrant_client.search(
        collection_name="movies", query_vector=query_vector, limit=limit
    )
    return search_result


def parse_similar_context(similar_context):
    payload = similar_context.payload
    formatted_string = f"""\
        Title: {payload['title']}
        Overview: {payload['overview']}
        Release Date: {payload['release_date']}
        Revenue: {payload['revenue']}
        Runtime: {payload['runtime']}
        Budget: {payload['budget']}
        Genre: {payload['genre']}
        Production Companies: {payload['production_companies']}
        Vote Average: {payload['vote_average']}
        Vote Count: {payload['vote_count']}
        Score: {similar_context.score}
    """
    return formatted_string


def run_conversation(query):
    similar_context = similarity_search(query)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        similar_context = list(executor.map(parse_similar_context, similar_context))

    context = "\n".join(similar_context)

    response = ollama_client.chat.completions.create(
        model="qwen:7b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. That are a expert in movie recommendations.",
            },
            {
                "role": "user",
                "content": f"""\
                Below are some movies that are similar to "{query}":
                {context}
             """,
            },
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content
