from typing import Any, Dict, List

from .frc import FrcRecipe


class DefaultRecipe(FrcRecipe):
    """Default conversion recipe that inherits FRC document processing behavior."""
    
    def clean_title(self, title: str) -> str:
        """Clean up section titles by removing LaTeX-style artifacts and extra whitespace."""
        # Add debug print
        print(f"Cleaning title: {title}")
        
        # Remove LaTeX math mode markers and empty superscripts
        title = title.replace("$^{ }$", "")
        
        # Remove any remaining LaTeX math markers
        title = title.replace("$", "")
        
        # Clean up extra whitespace
        title = " ".join(title.split())
        
        # Add debug print
        print(f"Cleaned title: {title}")
        
        return title

    def simplify_document(self, doc) -> Dict[str, List[Dict[str, Any]]]:
        """Override to clean section titles during document processing."""
        result = super().simplify_document(doc)
        
        # Clean titles in all sections
        for section in result["document"]:
            if "title" in section:
                section["title"] = self.clean_title(section["title"])
            
            # Also clean subsection titles
            if "subsections" in section:
                for subsection in section["subsections"]:
                    if "title" in subsection:
                        subsection["title"] = self.clean_title(subsection["title"])
        
        return result