from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Sample documents
texts = [
    "Amazon Bedrock is a fully managed service for foundation models.",
    "Amazon S3 is an object storage service.",
    "LangGraph is used to build stateful AI agent workflows."
]

# Generate embeddings
embeddings = model.encode(
    texts,
    normalize_embeddings=True
)

print("Number of texts:", len(texts))
print("Embedding shape:", embeddings.shape)

for i, embedding in enumerate(embeddings):
    print(f"\nText {i + 1}: {texts[i]}")
    print("Embedding dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])