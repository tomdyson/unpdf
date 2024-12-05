import re
from typing import Any, Dict, List

from .default import DefaultRecipe


class AmnestyRecipe(DefaultRecipe):
    """Recipe optimized for Amnesty International documents."""
    
    def is_page_number(self, content_item: Dict[str, Any]) -> bool:
        """Check if a content item appears to be a standalone page number."""
        if content_item.get("type") == "paragraph":
            text = content_item.get("text", "")
            # Check if text is just a number (allowing for whitespace)
            return text.strip().isdigit()
        return False

    def is_url_only(self, content_item: Dict[str, Any]) -> bool:
        """Check if a content item contains only a URL."""
        if content_item.get("type") == "paragraph":
            text = content_item.get("text", "").strip()
            # Match common URL patterns, particularly amnesty.org.uk
            url_pattern = r'^(?:https?:\/\/)?(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^\s]*)?$'
            return bool(re.match(url_pattern, text))
        return False

    def is_page_footer(self, content_item: Dict[str, Any]) -> bool:
        """Check if a content item appears to be a page footer."""
        if content_item.get("type") == "paragraph":
            text = content_item.get("text", "").strip()
            # Check if text starts with "Amnesty International UK"
            # and is relatively short (less than 100 chars)
            # and is the last item in its section
            return (
                   text.startswith("Amnesty International UK") and 
                   len(text) < 100)
        return False

    def is_address_footer(self, content_item: Dict[str, Any]) -> bool:
        """Check if a content item appears to be an address footer."""
        if content_item.get("type") == "paragraph":
            text = content_item.get("text", "").strip()
            # Check if text starts with "Amnesty International"
            # and ends with the postcode "EC2A 3EA"
            # and is the last item in its section
            return (text.startswith("Amnesty International") and 
                    text.endswith("EC2A 3EA"))
        return False

    def is_short_header(self, content_item: Dict[str, Any]) -> bool:
        """Check if a content item appears to be a short Amnesty header."""
        if content_item.get("type") == "paragraph":
            text = content_item.get("text", "").strip()
            # Check if text starts with "Amnesty International UK"
            # and has at most 10 more characters after that
            prefix = "Amnesty International UK"
            return (text.startswith(prefix) and 
                    len(text) <= len(prefix) + 10)
        return False

    def simplify_document(self, doc) -> Dict[str, List[Dict[str, Any]]]:
        """Override to remove page numbers, URLs, footers and apply other Amnesty-specific processing."""
        result = super().simplify_document(doc)
        
        # Clean up unwanted content from all sections
        for section in result["document"]:
            if "content" in section:
                content = section["content"]
                # Filter out page numbers and URLs first
                filtered_content = [
                    item for item in content 
                    if not (self.is_page_number(item) or self.is_url_only(item))
                ]
                
                # Then filter out footers and headers
                section["content"] = [
                    item for i, item in enumerate(filtered_content)
                    if not (self.is_page_footer(item) or 
                           self.is_address_footer(item) or
                           self.is_short_header(item))
                ]
            
            # Also clean subsections
            if "subsections" in section:
                for subsection in section["subsections"]:
                    if "content" in subsection:
                        content = subsection["content"]
                        # Same filtering process for subsections
                        filtered_content = [
                            item for item in content
                            if not (self.is_page_number(item) or self.is_url_only(item))
                        ]
                        subsection["content"] = [
                            item for i, item in enumerate(filtered_content)
                            if not (self.is_page_footer(item) or
                                   self.is_address_footer(item) or
                                   self.is_short_header(item))
                        ]
        
        return result 