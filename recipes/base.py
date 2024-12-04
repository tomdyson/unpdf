from abc import ABC, abstractmethod
from typing import Any, Dict

from docling.datamodel.document import DsDocument


class ConversionRecipe(ABC):
    """Base class for document conversion recipes."""
    
    @abstractmethod
    def simplify_document(self, doc: DsDocument) -> Dict[str, Any]:
        """Convert a Docling document to simplified format using recipe-specific logic."""
        pass

    @classmethod
    def get_name(cls) -> str:
        """Get the recipe name. Defaults to lowercase class name without 'Recipe' suffix."""
        name = cls.__name__.lower()
        return name[:-6] if name.endswith('recipe') else name 