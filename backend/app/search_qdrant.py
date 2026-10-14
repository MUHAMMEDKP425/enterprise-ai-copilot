from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient


# 1. Load the same embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# 2. Connect to our local Qdrant database
client = QdrantClient(path="qdrant_data")


# 3. Our user's question
question = "How many days before planned leave should employees submit their request?"

# 4. Convert the question into an embedding
question_embedding = model.encode(question)


# 5. Search Qdrant
results = client.query_points(
    collection_name="company_documents",
    query=question_embedding.tolist(),
    limit=2,
).points


# 6. Display the results
for result in results:
    print("\n--- Result ---")
    print("Score:", result.score)
    print("Text:", result.payload["text"])