# from app.agent.graph import build_graph


# def main():

#     graph = build_graph()

#     queries = [
#         "How does ranking work in Chroma?",
#         "How does hybrid search work?",
#         "How can search results be filtered?",
#         "What is the price of Chroma Enterprise?",
#     ]

#     for query in queries:

#         print("\n")
#         print("=" * 80)
#         print(
#             f"USER: {query}"
#         )
#         print("=" * 80)

#         result = graph.invoke(
#             {
#                 "query": query,
#                 "retry_count": 0,
#             }
#         )

#         print(
#             "\nANSWER:"
#         )

#         print(
#             result.get(
#                 "final_response",
#                 "No response",
#             )
#         )

#         print(
#             "\nGROUNDED:",
#             result.get(
#                 "grounded"
#             ),
#         )


# if __name__ == "__main__":
#     main()

from app.agent.graph import build_graph


def main():

    graph = build_graph()

    queries = [
        "How does ranking work in Chroma?",
        "How does hybrid search work?",
        "How can search results be filtered?",
        "What is Chroma Cloud?",
        "What is the current price of Chroma Enterprise?",
    ]

    for query in queries:

        print("\n")
        print("=" * 80)
        print(f"QUESTION: {query}")
        print("=" * 80)

        result = graph.invoke(
            {
                "query": query,
                "retry_count": 0,
            }
        )

        print("\nANSWER:")
        print(
            result.get(
                "final_response",
                "No response",
            )
        )

        print(
            "\nGrounded:",
            result.get(
                "grounded",
                False,
            ),
        )

        print(
            "Retrieved documents:",
            result.get(
                "retrieval_count",
                0,
            ),
        )


if __name__ == "__main__":
    main()