
from app.retrieval.retriever import WebsiteRetriever


retriever = WebsiteRetriever(top_k=10)

query = input("Query: ")

results = retriever.retrieve(query)

print("\nDistance Distribution")
print("-" * 30)

for r in results:
    print(
        f"{r.distance:.3f} | "
        f"{r.metadata.get('page_title')}"
    )