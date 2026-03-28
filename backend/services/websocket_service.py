"""WebSocket Service - Manages real-time connections"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        """Initialize WebSocket manager"""
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


# Global WebSocket manager instance
ws_manager = WebSocketManager()


async def handle_websocket(websocket: WebSocket, manager: WebSocketManager):
    """Handle WebSocket connection lifecycle"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)