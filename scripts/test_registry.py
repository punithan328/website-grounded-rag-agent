from app.config import (
    REGISTRY_DB,
    SEED_URL,
    ALLOWED_DOMAIN
)

from app.ingestion.registry import IngestionRegistry


registry = IngestionRegistry(
    REGISTRY_DB
)

website_id = registry.get_or_create_website(
    domain=ALLOWED_DOMAIN,
    seed_url=SEED_URL
)

print("Website ID:", website_id)

print("\nRegistry statistics:")

stats = registry.get_statistics()

for key, value in stats.items():
    print(f"{key}: {value}")
    
