from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# Configuration
# ============================================================

DATA_DIR = Path("data")
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "mock_knowledge"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Number of chunks to retrieve
TOP_K = 3


# ============================================================
# Load embedding model
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(EMBEDDING_MODEL)

print("Embedding model loaded.")


# ============================================================
# Initialize ChromaDB
# ============================================================

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

# Delete old collection so every run starts clean
try:
    client.delete_collection(COLLECTION_NAME)
except Exception:
    pass

collection = client.create_collection(
    name=COLLECTION_NAME,
    metadata={
        "description": "Mock RAG knowledge base"
    }
)


# ============================================================
# Read text files
# ============================================================

documents = []
metadatas = []
ids = []

file_paths = list(DATA_DIR.glob("*.txt"))

print(f"\nFound {len(file_paths)} text files.")


for file_path in file_paths:

    text = file_path.read_text(
        encoding="utf-8"
    ).strip()

    if not text:
        continue

    documents.append(text)

    metadatas.append({
        "source": file_path.name,
        "file_path": str(file_path)
    })

    ids.append(file_path.stem)


# ============================================================
# Generate embeddings
# ============================================================

print("\nGenerating embeddings...")

embeddings = model.encode(
    documents,
    normalize_embeddings=True
).tolist()

print(
    f"Generated {len(embeddings)} embeddings."
)

print(
    f"Embedding dimension: {len(embeddings[0])}"
)


# ============================================================
# Store in ChromaDB
# ============================================================

collection.add(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas
)

print(
    f"\nStored {collection.count()} documents in ChromaDB."
)


# ============================================================
# Retrieval function
# ============================================================

def retrieve(query: str, top_k: int = TOP_K):

    # Convert user query into embedding
    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    return results


# ============================================================
# Test retrieval
# ============================================================

if __name__ == "__main__":

    query = input(
        "\nEnter your question: "
    ).strip()

    results = retrieve(query)

    print("\n" + "=" * 70)
    print("RETRIEVAL RESULTS")
    print("=" * 70)

    result_documents = results["documents"][0]
    result_metadatas = results["metadatas"][0]
    result_distances = results["distances"][0]

    for i, (
        document,
        metadata,
        distance
    ) in enumerate(
        zip(
            result_documents,
            result_metadatas,
            result_distances
        ),
        start=1
    ):

        print(f"\nResult #{i}")
        print("-" * 70)

        print(
            f"Source   : {metadata['source']}"
        )

        print(
            f"Distance : {distance:.4f}"
        )

        print(
            f"\nContent:\n{document}"
        )