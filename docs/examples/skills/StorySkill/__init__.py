# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Story skill toolkit."""

import random
from lc.toolkit import Toolkit, tool

class StoryTools(Toolkit):
    """Storytelling tools."""
    
    gate_level = 0
    
    @tool
    def idea(self) -> str:
        """
        Provides a random story idea.
        
        Returns:
            An idea.
        """
        return random.choice(IDEAS)
    

IDEAS = [ "A story about antarctic explorers",
          "Memoirs of a rock",
          "Alternate-reality thriller where being overly polite is very hip" ]