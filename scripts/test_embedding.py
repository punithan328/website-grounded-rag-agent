from app.embedding.embedder import (
    SentenceTransformerEmbedder,
)


def main():

    embedder = (
        SentenceTransformerEmbedder(
            model_name="all-MiniLM-L6-v2"
        )
    )

    text = """
    ChromaDB is a vector database that can
    store embeddings and perform semantic
    similarity search over documents.
    """

    vector = embedder.embed(
        text
    )

    print(
        f"Embedding dimension: "
        f"{len(vector)}"
    )

    print(
        f"First 10 values:\n"
        f"{vector[:10]}"
    )

    print(
        f"Vector norm: "
        f"{sum(x * x for x in vector) ** 0.5}"
    )


if __name__ == "__main__":
    main()