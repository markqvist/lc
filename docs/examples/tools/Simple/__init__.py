# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Minimal toolkit for demonstration purposes."""

from lc.toolkit import Toolkit, tool


class TestTools(Toolkit):
    """A test standalone tool."""
    
    gate_level = 0
    
    @tool
    def greet(self, name: str = "world") -> str:
        """
        Return a greeting message.
        
        Args:
            name: Name to greet (default: world)
        
        Returns:
            Greeting message
        """
        return f"Hello, {name}! This is a tool response."
    
    @tool
    def multiply(self, x: float, y: float) -> str:
        """
        Multiply two numbers.
        
        Args:
            x: First number
            y: Second number
        
        Returns:
            Product as string
        """
        return str(x * y)

    @tool(gate_level=0, modality="image")
    def read_image(self, path: str) -> str:
        """
        Example of reading an image file and returning base64-
        encoded data in image modality for vision-capable models.
        
        Args:
            path: Path to the image file
        
        Returns:
            Base64-encoded image data with mime type prefix
        """
        
        import base64
        
        try:
            file_path = Path(path).expanduser()
            if not file_path.exists(): return f"Error: File not found: {path}"
            
            # Detect mime type
            suffix = file_path.suffix.lower()
            mime_types = { '.png': 'image/png',
                           '.jpg': 'image/jpeg',
                           '.jpeg': 'image/jpeg',
                           '.gif': 'image/gif',
                           '.webp': 'image/webp' }

            mime_type = mime_types.get(suffix, 'image/png')
            
            # Read and encode
            image_data = file_path.read_bytes()
            encoded = base64.b64encode(image_data).decode('utf-8')
            
            return f"data:{mime_type};base64,{encoded}"
            
        except Exception as e: return f"Error reading image: {e}"
