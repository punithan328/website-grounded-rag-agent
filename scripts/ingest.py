from app.ingestion.pipeline import (
    IngestionPipeline,
)


def main():

    pipeline = (
        IngestionPipeline()
    )

    result = pipeline.run()

    pipeline.print_summary(
        result
    )


if __name__ == "__main__":
    main()