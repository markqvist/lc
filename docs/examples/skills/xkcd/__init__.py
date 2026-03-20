"""XKCD explorer skill toolkit."""

import json
from lc.toolkit import Toolkit, tool


class XKCDTools(Toolkit):
    """XKCD comic exploration tools."""

    gate_level = 0

    @tool(gate_level=0, modality="text")
    def get_random_comic(self) -> str:
        """
        Get a random XKCD comic with title, image URL, and alt text.

        Returns:
            JSON string with comic details: title, number, image URL, alt text
        """
        import random

        # XKCD has over 3000 comics as of 2026
        # We'll fetch a random number and try to get valid data
        max_comic = 3000
        comic_num = random.randint(1, max_comic)

        try:
            # Fetch comic metadata from XKCD API
            info_url = f"https://xkcd.com/{comic_num}/info.0.json"
            # Use a timeout to avoid hanging
            import urllib.request
            import ssl

            # Disable SSL verification for simplicity (XKCD uses Let's Encrypt)
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(info_url, timeout=10, context=context) as response:
                data = json.loads(response.read().decode('utf-8'))

            result = {
                "title": data.get("title", "Untitled"),
                "number": data.get("num", comic_num),
                "image_url": data.get("img", ""),
                "alt_text": data.get("alt", "No alt text available"),
                "safe_title": data.get("safe_title", ""),
                "year": data.get("year", ""),
                "month": data.get("month", ""),
                "day": data.get("day", ""),
                "transcript": data.get("transcript", "")
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            # If the comic doesn't exist or there's an error, try again
            return f"Error fetching random comic: {e}. Please try again."

    @tool(gate_level=0, modality="image")
    def view_comic(self, comic_number: int = None) -> str:
        """
        Display a specific XKCD comic image.

        Args:
            comic_number: The XKCD comic number (defaults to latest if None)

        Returns:
            Base64-encoded image data with mime type prefix
        """
        import base64
        import urllib.request
        import ssl
        from pathlib import Path

        # If no number provided, get the latest comic number
        if comic_number is None:
            try:
                info_url = "https://xkcd.com/info.0.json"
                context = ssl._create_unverified_context()
                with urllib.request.urlopen(info_url, timeout=10, context=context) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    comic_number = data.get("num", 3000)
            except Exception:
                comic_number = 3000

        # Fetch comic info to get the actual image URL
        try:
            info_url = f"https://xkcd.com/{comic_number}/info.0.json"
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(info_url, timeout=10, context=context) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            image_url = data.get("img", f"https://imgs.xkcd.com/comics/{comic_number}.png")
            
            # Fetch the image
            with urllib.request.urlopen(image_url, timeout=10, context=context) as response:
                image_data = response.read()

            # Detect and encode based on content type
            content_type = response.headers.get('Content-Type', 'image/png')
            encoded = base64.b64encode(image_data).decode('utf-8')

            return f"data:{content_type};base64,{encoded}"

        except Exception as e:
            return f"Error viewing comic {comic_number}: {e}"

    @tool(gate_level=0, modality="text")
    def explain_humor(self, comic_number: int = None, comic_title: str = None) -> str:
        """
        Explain why an XKCD comic is funny using its alt text and context.

        Args:
            comic_number: The XKCD comic number (can be omitted if you already have the comic)
            comic_title: Optional title to provide context

        Returns:
            Explanation of the comic's humor
        """
        # If we have a comic number, fetch the full comic info
        if comic_number is not None:
            try:
                info_url = f"https://xkcd.com/{comic_number}/info.0.json"
                import urllib.request
                import ssl
                import json

                context = ssl._create_unverified_context()
                with urllib.request.urlopen(info_url, timeout=10, context=context) as response:
                    data = json.loads(response.read().decode('utf-8'))

                alt_text = data.get("alt", "")
                transcript = data.get("transcript", "")
                safe_title = data.get("safe_title", "")

                explanation = f"# XKCD #{comic_number}: {safe_title or data.get('title', 'Untitled')}\n\n"
                explanation += f"## Why This Comic Is Funny\n\n"
                explanation += f"**Alt Text:** {alt_text}\n\n"
                explanation += f"**Transcript:**\n{transcript[:500]}...\n\n" if len(transcript) > 500 else f"**Transcript:**\n{transcript}\n\n"

                return explanation

            except Exception as e:
                return f"Error explaining humor for comic {comic_number}: {e}"
        else:
            return "Please provide a comic number to explain, or get a random comic first using `get_random_comic`."