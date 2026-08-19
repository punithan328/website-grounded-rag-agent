from app.agent.llm import get_llm


def main():

    llm = get_llm()

    response = llm.invoke(
        "Explain RAG in two sentences."
    )

    print("\nLLM RESPONSE")
    print("=" * 60)
    print(response.content)


if __name__ == "__main__":
    main()