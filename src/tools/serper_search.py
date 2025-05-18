import os
import requests
from typing import Dict, List, Optional
from langchain.tools.base import BaseTool
from pydantic import Field
from dotenv import load_dotenv
load_dotenv()

SERPER_API_URL = "https://google.serper.dev/search"
SERPER_IMAGE_API_URL = "https://google.serper.dev/images"
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

class SerperSearchTool(BaseTool):
    name: str = "serper_search"
    description: str = (
        "Searches the web using Serper.dev (Google Search API). Requires SERPER_API_KEY in environment."
    )
    max_results: int = Field(default=5, description="Maximum number of results to return.")

    def _run(self, query: str) -> List[Dict]:
        headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
        payload = {"q": query, "num": self.max_results}
        response = requests.post(SERPER_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Extract relevant results (organic results)
        results = data.get("organic", [])[: self.max_results]
        # Normalize to Tavily format
        normalized = []
        for result in results:
            normalized.append({
                "type": "page",
                "title": result.get("title", ""),
                "url": result.get("link", ""),
                "content": result.get("snippet", ""),
            })
        return normalized

    async def _arun(self, query: str) -> List[Dict]:
        # Async version not implemented
        raise NotImplementedError("Async not implemented for SerperSearchTool.")

class SerperImageSearchTool(BaseTool):
    name: str = "serper_image_search"
    description: str = (
        "Searches for images using Serper.dev (Google Image Search API). Requires SERPER_API_KEY in environment."
    )
    max_results: int = Field(default=5, description="Maximum number of image results to return.")

    def _run(self, query: str) -> List[Dict]:
        headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
        payload = {"q": query, "num": self.max_results}
        response = requests.post(SERPER_IMAGE_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        images = data.get("images", [])[: self.max_results]
        normalized = []
        for img in images:
            normalized.append({
                "type": "image",
                "image_url": img.get("imageUrl", ""),
                "image_description": img.get("title", ""),
            })
        return normalized

    async def _arun(self, query: str) -> List[Dict]:
        # Async version not implemented
        raise NotImplementedError("Async not implemented for SerperImageSearchTool.")


if __name__ == "__main__":
    import json
    results = SerperSearchTool(name="web_search", max_results=3).invoke("cute panda")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    image_results = SerperImageSearchTool(name="image_search", max_results=3).invoke("cute panda")
    print(json.dumps(image_results, indent=2, ensure_ascii=False))