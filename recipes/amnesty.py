from typing import Any, Dict, List

from .base import ConversionRecipe


class AmnestyRecipe(ConversionRecipe):
    """Recipe optimized for Amnesty International documents."""
    
    def _should_skip_header(self, header_text: str, seen_headers: set) -> bool:
        """Determine if a header should be skipped based on repetition."""
        if header_text in seen_headers:
            return True
        seen_headers.add(header_text)
        return False
    
    def simplify_document(self, doc) -> Dict[str, List[Dict[str, Any]]]:
        sections = []
        current_section = None
        seen_headers = set()
        
        # Create default section
        default_section = {
            "type": "section",
            "title": "",
            "content": [],
            "level": 1
        }
        current_section = default_section
        sections.append(default_section)
        
        # Modified processing logic that skips repeated headers
        for text in doc.texts:
            item_type = type(text).__name__
            
            if item_type == 'SectionHeaderItem':
                if not self._should_skip_header(text.text, seen_headers):
                    current_section = {
                        "type": "section",
                        "title": text.text,
                        "content": []
                    }
                    sections.append(current_section)
            
            # Rest of the processing logic similar to default recipe
            # but with any Amnesty-specific modifications...
            
        return {"document": sections} 