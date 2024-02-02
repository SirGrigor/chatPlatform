
class WebSocketAuthException(Exception):
    """Custom exception for WebSocket authentication errors."""
    def __init__(self, detail: str):
        self.detail = detail
