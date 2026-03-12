# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Filesystem toolkit for lc."""

from pathlib import Path
from typing import Optional

from lc.toolkit import Toolkit, tool


class Filesystem(Toolkit):
    """Toolkit for filesystem operations."""
    
    gate_level = 0
    
    @tool(gate_level=0)
    def read(self, path: str) -> str:
        """
        Read contents of a file.
        
        Args:
            path: Path to the file to read
        
        Returns:
            File contents as string, or error message
        """
        
        try:
            file_path = Path(path).expanduser()
            
            if not file_path.exists():  return f"Error: File not found: {path}"
            if not file_path.is_file(): return f"Error: Not a file: {path}"
            
            # Read as text
            try:
                content = file_path.read_text(encoding='utf-8')
                return content
            
            except UnicodeDecodeError:
                # Try as binary with limited output
                content = file_path.read_bytes()[:2048]
                return f"[Binary file, first 2048 bytes]: {content.hex()}"
                
        except Exception as e:
            return f"Error reading file: {e}"
    
    @tool(gate_level=0, modality="image")
    def read_image(self, path: str) -> str:
        """
        Read an image file and return base64-encoded data.
        
        Args:
            path: Path to the image file
        
        Returns:
            Base64-encoded image data with mime type prefix
        """
        
        import base64
        
        try:
            file_path = Path(path).expanduser()
            
            if not file_path.exists():
                return f"Error: File not found: {path}"
            
            # Detect mime type
            suffix = file_path.suffix.lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
            }

            mime_type = mime_types.get(suffix, 'image/png')
            
            # Read and encode
            image_data = file_path.read_bytes()
            encoded = base64.b64encode(image_data).decode('utf-8')
            
            return f"data:{mime_type};base64,{encoded}"
            
        except Exception as e: return f"Error reading image: {e}"
    
    @tool(gate_level=1)
    def write(self, path: str, content: str) -> str:
        """
        Write content to a file.
        
        Args:
            path: Path to write to
            content: Content to write
        
        Returns:
            Success message or error
        """
        
        try:
            file_path = Path(path).expanduser()
            
            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            
            return f"Successfully wrote {len(content)} characters to {path}"
            
        except Exception as e: return f"Error writing file: {e}"
    
    @tool(gate_level=1)
    def edit(self, path: str, old_string: str, new_string: str) -> str:
        """
        Edit a file by replacing a specific string.
        
        Args:
            path: Path to the file
            old_string: String to find and replace
            new_string: Replacement string
        
        Returns:
            Success message or error
        """
        
        try:
            file_path = Path(path).expanduser()
            if not file_path.exists(): return f"Error: File not found: {path}"
            
            content = file_path.read_text(encoding='utf-8')
            if old_string not in content: return f"Error: String not found in file"
            
            new_content = content.replace(old_string, new_string, 1)
            file_path.write_text(new_content, encoding='utf-8')
            
            return f"Successfully edited {path}"
            
        except Exception as e: return f"Error editing file: {e}"
    
    @tool(gate_level=0)
    def list_dir(self, path: str) -> str:
        """
        List contents of a directory.
        
        Args:
            path: Directory path (use "." for current directory)
        
        Returns:
            Directory listing
        """

        try:
            if not path or path == "": path = "."
            dir_path = Path(path).expanduser()
            
            if not dir_path.exists(): return f"Error: Directory not found: {path}"
            if not dir_path.is_dir(): return f"Error: Not a directory: {path}"
            
            entries = []
            for entry in sorted(dir_path.iterdir()):
                prefix = "📁 " if entry.is_dir() else "📄 "
                entries.append(f"{prefix}{entry.name}")
            
            return "\n".join(entries) if entries else "Empty directory"
            
        except Exception as e: return f"Error listing directory: {e}"
