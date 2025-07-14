"""
Integration between WebSocket streaming and the main workflow
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


class StreamingWorkflowIntegration:
    """Integration class for streaming workflow updates"""
    
    def __init__(self):
        self.active_requests = {}  # request_id -> {room_id, client_id, status}
        
    def register_request(self, request_id: str, room_id: str, client_id: str):
        """Register a new research request for streaming"""
        self.active_requests[request_id] = {
            "room_id": room_id,
            "client_id": client_id,
            "status": "started",
            "start_time": datetime.now()
        }
        
    def unregister_request(self, request_id: str):
        """Unregister a completed request"""
        if request_id in self.active_requests:
            del self.active_requests[request_id]
    
    async def stream_progress(self, request_id: str, stage: str, progress: int, message: str = ""):
        """Stream progress update to clients"""
        if request_id not in self.active_requests:
            return
            
        request_info = self.active_requests[request_id]
        
        progress_message = {
            "type": "progress_update",
            "request_id": request_id,
            "stage": stage,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to specific client
        await websocket_manager.connection_manager.send_personal_message(
            progress_message, request_info["client_id"]
        )
        
        # Also broadcast to room
        await websocket_manager.connection_manager.broadcast_to_room(
            request_info["room_id"], progress_message, exclude_client=request_info["client_id"]
        )
    
    async def stream_partial_result(self, request_id: str, content: str, section: str = "", is_final: bool = False):
        """Stream partial research results"""
        if request_id not in self.active_requests:
            return
            
        request_info = self.active_requests[request_id]
        
        result_message = {
            "type": "research_result",
            "request_id": request_id,
            "content": content,
            "section": section,
            "is_final": is_final,
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to room
        await websocket_manager.connection_manager.broadcast_to_room(
            request_info["room_id"], result_message
        )
        
        if is_final:
            self.unregister_request(request_id)
    
    async def stream_error(self, request_id: str, error_message: str):
        """Stream error message"""
        if request_id not in self.active_requests:
            return
            
        request_info = self.active_requests[request_id]
        
        error_msg = {
            "type": "research_error",
            "request_id": request_id,
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to specific client
        await websocket_manager.connection_manager.send_personal_message(
            error_msg, request_info["client_id"]
        )
        
        self.unregister_request(request_id)
    
    def get_active_requests(self) -> Dict[str, Any]:
        """Get all active requests"""
        return self.active_requests.copy()


# Global instance
streaming_integration = StreamingWorkflowIntegration()


# Callback functions for workflow integration
class StreamingCallbacks:
    """Callbacks to integrate with the main workflow"""
    
    @staticmethod
    async def on_research_start(request_id: str, query: str, room_id: str, client_id: str):
        """Called when research starts"""
        streaming_integration.register_request(request_id, room_id, client_id)
        await streaming_integration.stream_progress(
            request_id, "initialization", 0, f"Starting research for: {query}"
        )
    
    @staticmethod
    async def on_search_start(request_id: str, search_query: str):
        """Called when search phase starts"""
        await streaming_integration.stream_progress(
            request_id, "searching", 20, f"Searching for: {search_query}"
        )
    
    @staticmethod
    async def on_search_result(request_id: str, url: str, title: str):
        """Called when a search result is found"""
        await streaming_integration.stream_progress(
            request_id, "searching", 30, f"Found: {title}"
        )
    
    @staticmethod
    async def on_scrape_start(request_id: str, url: str):
        """Called when scraping starts"""
        await streaming_integration.stream_progress(
            request_id, "scraping", 40, f"Scraping: {url}"
        )
    
    @staticmethod
    async def on_scrape_complete(request_id: str, url: str, success: bool):
        """Called when scraping completes"""
        if success:
            await streaming_integration.stream_progress(
                request_id, "scraping", 60, f"Successfully scraped: {url}"
            )
        else:
            await streaming_integration.stream_progress(
                request_id, "scraping", 60, f"Failed to scrape: {url}"
            )
    
    @staticmethod
    async def on_analysis_start(request_id: str):
        """Called when analysis phase starts"""
        await streaming_integration.stream_progress(
            request_id, "analyzing", 70, "Analyzing collected data..."
        )
    
    @staticmethod
    async def on_generation_start(request_id: str):
        """Called when report generation starts"""
        await streaming_integration.stream_progress(
            request_id, "generating", 80, "Generating report..."
        )
    
    @staticmethod
    async def on_section_complete(request_id: str, section_name: str, content: str):
        """Called when a report section is completed"""
        await streaming_integration.stream_partial_result(
            request_id, content, section_name, is_final=False
        )
        await streaming_integration.stream_progress(
            request_id, "generating", 90, f"Completed section: {section_name}"
        )
    
    @staticmethod
    async def on_research_complete(request_id: str, final_report: str):
        """Called when research is complete"""
        await streaming_integration.stream_partial_result(
            request_id, final_report, "final_report", is_final=True
        )
        await streaming_integration.stream_progress(
            request_id, "completed", 100, "Research completed successfully"
        )
    
    @staticmethod
    async def on_research_error(request_id: str, error: str):
        """Called when research encounters an error"""
        await streaming_integration.stream_error(request_id, error)


# Integration with message handlers
async def handle_research_request_integration(message: Dict[str, Any], connection_manager):
    """Enhanced research request handler with workflow integration"""
    client_id = message.get("client_id")
    room_id = message.get("room_id", "default")
    query = message.get("query", "")
    request_id = message.get("request_id", f"req_{datetime.now().timestamp()}")
    
    # Send acknowledgment
    await connection_manager.send_personal_message({
        "type": "research_started",
        "query": query,
        "request_id": request_id
    }, client_id)
    
    # Start streaming integration
    await StreamingCallbacks.on_research_start(request_id, query, room_id, client_id)
    
    # TODO: Trigger actual workflow here
    # For now, simulate workflow with async task
    asyncio.create_task(simulate_research_workflow(request_id, query))


async def simulate_research_workflow(request_id: str, query: str):
    """Simulate the research workflow for testing"""
    try:
        # Simulate search
        await StreamingCallbacks.on_search_start(request_id, query)
        await asyncio.sleep(1)
        
        # Simulate finding results
        for i in range(3):
            await StreamingCallbacks.on_search_result(
                request_id, f"https://example{i}.com", f"Example Result {i+1}"
            )
            await asyncio.sleep(0.5)
        
        # Simulate scraping
        for i in range(3):
            await StreamingCallbacks.on_scrape_start(request_id, f"https://example{i}.com")
            await asyncio.sleep(1)
            await StreamingCallbacks.on_scrape_complete(request_id, f"https://example{i}.com", True)
        
        # Simulate analysis
        await StreamingCallbacks.on_analysis_start(request_id)
        await asyncio.sleep(2)
        
        # Simulate report generation
        await StreamingCallbacks.on_generation_start(request_id)
        await asyncio.sleep(1)
        
        # Simulate sections
        sections = ["Introduction", "Analysis", "Findings", "Conclusion"]
        for section in sections:
            content = f"This is the {section.lower()} section about {query}..."
            await StreamingCallbacks.on_section_complete(request_id, section, content)
            await asyncio.sleep(1)
        
        # Final report
        final_report = f"Complete research report about {query}"
        await StreamingCallbacks.on_research_complete(request_id, final_report)
        
    except Exception as e:
        await StreamingCallbacks.on_research_error(request_id, str(e))


# Update the message handler
MESSAGE_HANDLERS = {
    "research_request": handle_research_request_integration,
}

# Export integration components
__all__ = [
    'StreamingWorkflowIntegration', 
    'streaming_integration', 
    'StreamingCallbacks',
    'MESSAGE_HANDLERS'
]
