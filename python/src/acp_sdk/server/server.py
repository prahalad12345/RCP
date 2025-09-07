# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket

#from acp_sdk.server.logging import configure_logger as configure_logger_func
from acp_sdk.server.logger import logger,configure_logger
#from acp_sdk.server.utils import async_request_with_retry


class WebSocketHandler:
    """Handles WebSocket connections and communication."""

    def __init__(self):
        configure_logger()
        logger.info("Server initialized.")
        self.counter = 0

    async def handle(self, websocket: WebSocket) -> None:
        """Main WebSocket handler loop."""
        await websocket.accept()
        logger.info("Client connected.")
        try:
            while True:
                # Increment and send data to client
                self.counter += 1
                await websocket.send_text(f"Value from server: {self.counter}")
                logger.debug(f"Sent: {self.counter}")

                # Wait for client's response
                response = await websocket.receive_text()
                logger.debug(f"Client says: {response}")

                # Sleep if needed
                # await asyncio.sleep(1)

        except Exception as e:
            logger.warning(f"Connection closed: {e}")


class WebSocketServer:
    """Encapsulates FastAPI app and WebSocket routing."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
        self.host = host
        self.port = port
        self.reload = reload
        self.app = FastAPI()
        self.handler = WebSocketHandler()

        self._configure_routes()

    def _configure_routes(self) -> None:
        @self.app.websocket("/ws")
        async def websocket_route(websocket: WebSocket):
            await self.handler.handle(websocket)

    def run(self) -> None:
        """Start the WebSocket server."""
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            reload=False,  # important
        )



if __name__ == "__main__":
    #configure_logger_func()
    server = WebSocketServer()
    server.run()
