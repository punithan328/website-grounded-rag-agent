from typing import Optional

from app.ingestion.extractor import (
    ContentExtractor,
)

from app.ingestion.validator import (
    ContentValidator,
)

from app.models.page import (
    ExtractedPage,
)


class DocumentProcessor:
    """
    Converts raw HTML into a validated
    structured document.
    """

    def __init__(
        self,
        extractor: Optional[
            ContentExtractor
        ] = None,
        validator: Optional[
            ContentValidator
        ] = None,
    ):

        self.extractor = (
            extractor
            or ContentExtractor()
        )

        self.validator = (
            validator
            or ContentValidator()
        )

    def process(
        self,
        html: str,
        url: str,
    ) -> Optional[ExtractedPage]:

        page = self.extractor.extract(
            html=html,
            url=url,
        )

        if page is None:
            return None

        page = self.validator.validate(
            page
        )

        return page