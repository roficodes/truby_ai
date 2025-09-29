# import os
# from typing import Any
# from openai import OpenAI
# from dotenv import load_dotenv
# from mcp.server.fastmcp import FastMCP
# from pinecone.db_data import Index
# from pinecone.db_data.index_asyncio import IndexAsyncio
# from core.config import TOP_K_CONTEXTS, PINECONE_NAMESPACE
# from core.clients import init_openai_client, init_pinecone_client

# load_dotenv()
# PINECONE_HOST_URL = os.getenv("PINECONE_HOST_URL")
# mcp = FastMCP("trubyai")

# openai_client = init_openai_client()
# pinecone_client = init_pinecone_client()
# pinecone_index = pinecone_client.IndexAsyncio(name="trubyai", host=PINECONE_HOST_URL)

# def create_embeddings(
#         user_query: str, 
#         client: OpenAI = openai_client,
#         model: str = "text-embedding-3-small"
#     ) -> list[float]:
#     """Create an embedding vector for the user query using the AI client.
#     Args:
#         user_query (str): The user's search or question.
#         client (OpenAI): Configured OpenAI client instance.
#         model (str): Embedding model to use.
#     Returns:
#         list[float]: The embedding vector.
#     """
#     embedding = client.embeddings.create(
#         input=user_query,
#         model=model
#     )
#     return embedding.data[0].embedding

# def fetch_contexts(
#     vector: list[float], 
#     top_k: int, 
#     index: Index | IndexAsyncio = pinecone_index,
#     namespace: str=PINECONE_NAMESPACE,
# ) -> dict[str, Any]:
#     """
#     Fetch relevant contexts from the vector database.
#     Args:
#         vector (list[float]): The embedding vector for the user query.
#         top_k (int): Number of top results to return.
#         index (Index | IndexAsyncio): Pinecone index instance.
#         namespace (str): Namespace in the vector database to query.

#     Returns:
#         dict[str, Any]: A dictionary containing the query results.
#     """
#     results = index.query(
#         vector=vector,
#         top_k=top_k,
#         namespace=namespace,
#         include_metadata=True
#     )
#     return results["matches"]

# def clean_contexts(
#     contexts: list[dict]
# ) -> list[str]:
#     """
#     Clean and format the fetched contexts for use in prompts.
#     Args:
#         contexts (list[dict]): List of context dictionaries fetched from the vector database.
    
#     Returns:
#         list[str]: A list of cleaned context strings.
#     """
#     HEADER = "<START SCENE>"
#     FOOTER = "<END SCENE>"
#     cleaned_contexts = []
#     for result in contexts:
#         cleaned_context = HEADER + result["metadata"]["embedding_text"] + FOOTER
#         cleaned_contexts.append(cleaned_context)
#     return cleaned_contexts

# @mcp.tool(
#     name="get_contexts",
#     description="Fetch relevant contexts for a user's query from the vector database."
# )
# async def get_contexts(
#     user_query: str,
#     top_k: int = TOP_K_CONTEXTS,
# ) -> list[Any]:
#     """Fetch relevant contexts for a user query.

#     This is a placeholder implementation. Replace with calls to your
#     vector database (e.g. Pinecone) to compute or fetch similarity
#     scores and return the top-k results.

#     Args:
#         user_query (str): The user's search or question.
#         client (OpenAI): Configured OpenAI client instance.
#         index (Index | IndexAsyncio): Pinecone index instance.
#         top_k (int): Number of top results to return.
#         model (str): Embedding model to use.

#     Returns:
#         list[Any]: A list of context dictionaries (one per result).
#     """
#     embedding_vector = create_embeddings(user_query=user_query, client=openai_client)
#     contexts = fetch_contexts(
#         vector=embedding_vector,
#         top_k=top_k,
#         index=pinecone_index,
#         namespace=PINECONE_NAMESPACE
#     )
#     return contexts if contexts else [{"message": "No contexts found."}]

# mcp.add_tool(get_contexts)

# if __name__ == "__main__":
#     mcp.run(transport="stdio")