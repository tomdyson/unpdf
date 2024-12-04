from typing import Dict, Type

from .amnesty import AmnestyRecipe
from .base import ConversionRecipe
from .default import DefaultRecipe
from .frc import FrcRecipe


class RecipeRegistry:
    """Registry for conversion recipes."""
    
    def __init__(self):
        self._recipes: Dict[str, Type[ConversionRecipe]] = {}
        
        # Register built-in recipes
        self.register(DefaultRecipe)
        self.register(AmnestyRecipe)
        self.register(FrcRecipe)
    
    def register(self, recipe_class: Type[ConversionRecipe]):
        """Register a new recipe class."""
        self._recipes[recipe_class.get_name()] = recipe_class
    
    def get_recipe(self, name: str = "default") -> ConversionRecipe:
        """Get a recipe instance by name."""
        recipe_class = self._recipes.get(name)
        if recipe_class is None:
            raise ValueError(f"Unknown recipe: {name}")
        return recipe_class()
    
    def list_recipes(self) -> list[str]:
        """List all available recipe names."""
        return list(self._recipes.keys())

# Global registry instance
registry = RecipeRegistry() 