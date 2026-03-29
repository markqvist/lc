# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md
#
# Provides tools for web search, webpage extraction, and YouTube transcript retrieval.
#
# Web toolkit for lc - Example implementation. For this to actually work beyond web
# search, and have page fetching, markdown formatting and youtube transcripts, you'll
# need the lc web and youtube-loader backend. If you don't have this, you can have lc
# create your own implementation and simply point the API endpoint URLs to that.
#
# Point lc to this source code, and it will know what to do. Or contact me if you want
# to save the hassle with a pre-made solution that works.
# 
# Web search uses SearXNG compatible API, and you can point it directly to your local
# SearXNG instance for instant web search functionality.

import os
import json
import urllib.request
import urllib.parse
from typing import List

from lc.toolkit import Toolkit, tool

# Toggle between raw JSON and formatted markdown output
SEARCH_RETURN_RAW = True
FETCH_RETURN_RAW  = False

class Web(Toolkit):
    """Toolkit for web operations - search, fetch, and transcript retrieval."""
    
    gate_level = 0
    
    # API endpoint configuration
    EXTRACT_URL = os.environ.get("LC_WEB_FETCH_API",  "http://192.168.1.2:8543/extract")
    SEARCH_URL  = os.environ.get("LC_WEB_SEARCH_API", "http://192.168.1.2:8544/search")
    YOUTUBE_URL = os.environ.get("LC_YOUTUBE_API",    "http://192.168.1.2:8545/transcript")
    
    @tool(gate_level=0)
    def fetch_webpage(self, url: str) -> str:
        """
        Get the contents of a webpage.
        
        Args:
            url: URL of the webpage to fetch
        
        Returns:
            Page content with metadata, or error message
        """
        try:
            data = json.dumps({"urls": [url]}).encode("utf-8")
            headers = {"Content-Type": "application/json", "Content-Length": len(data)}
            req = urllib.request.Request(self.EXTRACT_URL, data=data, headers=headers, method="POST")
            
            with urllib.request.urlopen(req, timeout=30) as response: result = json.loads(response.read().decode("utf-8"))
            if not result or not isinstance(result, list) or len(result) == 0: return "Error: No content extracted"
            
            page_data = result[0]
            content = page_data.get("content", "")
            title = page_data.get("title", "Untitled")
            truncated = page_data.get("truncated", False)
            
            if FETCH_RETURN_RAW: return json.dumps(page_data, indent=2)
            
            truncated_note = ""
            if truncated: truncated_note = "\n\n[...] WARNING: Content truncated due to length limit."
            
            return f"# {title}\nRetrieved from {url}\n\n{content}{truncated_note}"
            
        except urllib.error.HTTPError as e: return f"HTTP Error: {e.code} {e.reason}"
        except urllib.error.URLError as e:  return f"Connection Error: {e.reason}"
        except Exception as e:              return f"Error: {e}"
    
    @tool(gate_level=0)
    def search_web(self, queries: List[str], max_results: int = 6) -> str:
        """
        Search the web for information.
        
        Args:
            queries: List of search queries to execute
            max_results: Maximum results to return per query (default: 6)
        
        Returns:
            Search results with titles, snippets, URLs and relevance scores
        """
        if isinstance(queries, str): queries = [queries]
        
        all_results = []
        for query in queries:
            try:
                encoded_query = urllib.parse.quote(query)
                url = f"{self.SEARCH_URL}?format=json&q={encoded_query}"
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=30) as response:
                    data = json.loads(response.read().decode("utf-8"))
                
                if not data or "results" not in data: continue
                
                query_results = []
                for r in data["results"]:
                    result = { "title": r.get("title", ""), "snippet": r.get("content", ""),
                               "url": r.get("url", ""), "query": query, "score": r.get("score", 0.0) }
                    
                    query_results.append(result)
                
                # Sort by score and limit
                query_results.sort(key=lambda x: x["score"], reverse=True)
                all_results.extend(query_results[:max_results])
                
            except urllib.error.HTTPError as e: continue
            except urllib.error.URLError as e:  continue
            except Exception as e:              continue
        
        # Sort all results by score
        all_results.sort(key=lambda x: x["score"], reverse=True)
        
        if SEARCH_RETURN_RAW: return json.dumps(all_results, indent=2)
        if not all_results: return "No results found."
        
        formatted = "## Search Results\n\n"
        for r in all_results:
            snippet = r["snippet"]
            snippet_str = f"\n{snippet}\n" if snippet else "\n"
            formatted += f"### {r['title']}\n{r['url']}\nQuery: {r['query']} (score={round(r['score'], 1)}){snippet_str}"
        
        return formatted
    
    @tool(gate_level=0)
    def get_youtube_transcript(self, url: str) -> str:
        """
        Get the transcript of a YouTube video.
        
        Args:
            url: URL of the YouTube video
        
        Returns:
            Video transcript and metadata, or error message
        """
        try:
            data = json.dumps({"url": url}).encode("utf-8")
            headers = {"Content-Type": "application/json", "Content-Length": len(data) }
            
            req = urllib.request.Request(self.YOUTUBE_URL, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=45) as response:
                if not response: return "Error: Could not connect to Youtube extraction API"
                result = json.loads(response.read().decode("utf-8"))
            
            if result.get("status") != "success": return f"Error: {result.get('message', 'Unknown error')}"
            
            transcript = result.get("transcript", "")
            return transcript
            
        except urllib.error.HTTPError as e: return f"HTTP Error: {e.code} {e.reason}"
        except urllib.error.URLError as e:  return f"Connection Error: {e.reason}"
        except Exception as e:              return f"Error: {e}"
