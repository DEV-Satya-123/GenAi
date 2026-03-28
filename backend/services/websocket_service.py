"""
WebSocket Service
Manages WebSocket connections and real-time message broadcasting
"""

from fastapi import WebSocket
from typing import List


class WebSocketManager:
    """
    Manages WebSocket connections for real-time updates to frontend clients
    
    Handles connection lifecycle, message broadcasting, and approval workflows
    """
    
    def __init__(self):
        """Initialize WebSocket manager with empty connection list"""
        self.active_connections: List[WebSocket] = []
        self.active_agent = None

    async def connect(self, websocket: WebSocket):
        """
        Accept and register a new WebSocket connection
        
        Args:
            websocket: FastAPI WebSocket instance to connect
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection from active connections
        
        Args:
            websocket: FastAPI WebSocket instance to disconnect
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """
        Send a message to all connected WebSocket clients
        
        Args:
            message: Dictionary containing message data to broadcast
            
        Note:
            Silently handles disconnected clients without raising errors
        """
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Client disconnected, skip silently
                pass
    
    def set_active_agent(self, agent):
        """
        Store reference to currently running agent for approval handling
        
        Args:
            agent: GitAutomationAgent instance currently executing
        """
        self.active_agent = agent
    
    def handle_approval(self, approval_data: dict):
        """
        Forward approval decision to active agent
        
        Args:
            approval_data: Dictionary containing approval action and details
        """
        if self.active_agent:
            self.active_agent.handle_approval_response(approval_data)