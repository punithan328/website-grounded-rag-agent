from app.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DIR,
)

from app.vectorstore.chroma_store import (
    ChromaStore,
)


def main():

    store = ChromaStore(
        persist_directory=str(
            CHROMA_DIR
        ),
        collection_name=(
            CHROMA_COLLECTION_NAME
        ),
    )

    print(
        "ChromaDB initialized successfully."
    )

    print(
        f"Collection: "
        f"{CHROMA_COLLECTION_NAME}"
    )

    print(
        f"Document count: "
        f"{store.count()}"
    )


if __name__ == "__main__":
    main()