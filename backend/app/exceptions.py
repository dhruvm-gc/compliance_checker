class AppError(Exception):
    """Base app error"""

class FileParseError(AppError):
    """Raised when PDF/DOCX parsing fails"""

class VectorDBError(AppError):
    """Raised when ChromaDB operations fail"""

class ComplianceError(AppError):
    """Raised when compliance check fails"""
