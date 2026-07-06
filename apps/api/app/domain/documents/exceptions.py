class DocumentPipelineError(RuntimeError):
    """Raised when document ingestion cannot complete safely."""


class UnsupportedDocumentError(DocumentPipelineError):
    """Raised when the uploaded file is not a supported document type."""

