# # from app.config import (
# #     CHROMA_COLLECTION_NAME,
# #     CHROMA_DIR,
# #     EMBEDDING_MODEL,
# # )

# # from app.embedding.embedder import (
# #     SentenceTransformerEmbedder,
# # )

# # from app.vectorstore.chroma_store import (
# #     ChromaStore,
# # )


# # def main():

# #     store = ChromaStore(
# #         persist_directory=str(
# #             CHROMA_DIR
# #         ),
# #         collection_name=(
# #             CHROMA_COLLECTION_NAME
# #         ),
# #     )

# #     embedder = (
# #         SentenceTransformerEmbedder(
# #             model_name=EMBEDDING_MODEL
# #         )
# #     )

# #     query = (
# #         "How does ChromaDB rank search results?"
# #     )

# #     print(
# #         f"\nQuery: {query}"
# #     )

# #     query_embedding = (
# #         embedder.embed(query)
# #     )

# #     results = store.query(
# #         query_embedding=query_embedding,
# #         n_results=5,
# #     )

# #     print("\n" + "=" * 70)
# #     print("RETRIEVAL RESULTS")
# #     print("=" * 70)

# #     documents = results.get(
# #         "documents",
# #         [[]]
# #     )[0]

# #     metadatas = results.get(
# #         "metadatas",
# #         [[]]
# #     )[0]

# #     distances = results.get(
# #         "distances",
# #         [[]]
# #     )[0]

# #     for index, document in enumerate(
# #         documents
# #     ):

# #         print(
# #             f"\nResult #{index + 1}"
# #         )

# #         print(
# #             f"Distance: "
# #             f"{distances[index]}"
# #         )

# #         metadata = (
# #             metadatas[index]
# #         )

# #         print(
# #             f"Section: "
# #             f"{metadata.get('section_path')}"
# #         )

# #         print(
# #             f"Source: "
# #             f"{metadata.get('source_url')}"
# #         )

# #         print(
# #             "\nContent:"
# #         )

# #         print(
# #             document[:1200]
# #         )

# #         print(
# #             "-" * 70
# #         )


# # if __name__ == "__main__":
# #     main()

# from app.retrieval.retriever import (
#     WebsiteRetriever,
# )


# def main():

#     retriever = WebsiteRetriever(
#         top_k=5
#     )

#     queries = [
#         "How does hybrid search work in Chroma?",
#         "How does filtering work in Chroma?",
#         "How does ranking work in Chroma?",
#     ]

#     for query in queries:

#         print("\n")
#         print("=" * 80)
#         print(
#             f"QUERY: {query}"
#         )
#         print("=" * 80)

#         results = retriever.retrieve(
#             query
#         )

#         if not results:

#             print(
#                 "No results found."
#             )

#             continue

#         for index, result in enumerate(
#             results,
#             start=1,
#         ):

#             print(
#                 f"\n[{index}] "
#                 f"distance="
#                 f"{result.distance:.4f}"
#             )

#             print(
#                 f"score="
#                 f"{result.score:.4f}"
#             )

#             print(
#                 f"URL: "
#                 f"{result.metadata.get('url')}"
#             )

#             print(
#                 f"Section: "
#                 f"{result.metadata.get('section')}"
#             )

#             print(
#                 "\nContent:"
#             )

#             print(
#                 result.content[:1000]
#             )


# if __name__ == "__main__":
#     main()


from app.retrieval.retriever import WebsiteRetriever


def print_results(query: str):

    retriever = WebsiteRetriever(top_k=5)

    results = retriever.retrieve(
        query=query,
        max_distance=0.85,
    )

    print("\n" + "=" * 80)
    print(query)
    print("=" * 80)

    if not results:
        print("No relevant content found.")
        return

    for i, result in enumerate(results, start=1):

        print(f"\n[{i}] Score: {result.score:.3f}")
        print(f"Distance: {result.distance:.3f}")
        print(f"Title: {result.metadata.get('page_title')}")
        print(f"Section: {result.metadata.get('section_path')}")
        print(f"URL: {result.metadata.get('source_url')}")

        print("\nContent:")
        print(result.content[:700])
        print("-" * 80)


if __name__ == "__main__":

    queries = [
        "How does hybrid search work in Chroma?",
        "How do ranking expressions work?",
        "How can I filter search results?",
        "What is collection forking?",
    ]

    for query in queries:
        print_results(query)