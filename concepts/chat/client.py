from .websocket import WSConnection
import base64

# from typing import 
# fmt: off
__all__ = (
    'Client',
)
# fmt: on

class Client:
    
    def __init__(self, prefix: str):
        self._prefix = prefix