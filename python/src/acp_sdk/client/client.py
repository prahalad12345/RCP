import asyncio
import ssl
import typing
from types import TracebackType
from typing import Self
import websockets
from websockets.legacy.client import WebSocketClientProtocol
from pydantic import BaseModel
import json
from acp_sdk.models import Message
from acp_sdk.client.utils import input_to_messages

class Client:
    def __init__(
        self,
        uri: str,
        *,
        timeout: float = 10.0,
        ssl_context: ssl.SSLContext | None = None,
        client: WebSocketClientProtocol | None = None,
        manage_client: bool = True,
    ) -> None:
        self.uri = uri
        self.timeout = timeout
        self.ssl_context = ssl_context
        self._client: WebSocketClientProtocol | None = client
        self._manage_client = manage_client

    @property
    def client(self) -> WebSocketClientProtocol | None:
        return self._client

    async def connect(self) -> Self:
        if not self._client:
            self._client = await websockets.connect(self.uri, ssl=self.ssl_context)
        return self

    async def __aenter__(self) -> Self:
        if self._manage_client and not self._client:
            await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        if self._manage_client:
            await self.close()

    #Approving message recieved
    async def send(self, messages: Message | list[Message]):
        if self._client is None:
            raise RuntimeError("WebSocket client is not connected")

        # Handle single or list of messages
        if isinstance(messages, list):
            data = "[" + ",".join([m.model_dump_json() for m in messages]) + "]"
        else:
            data = messages.model_dump_json()

        await self._client.send(data)
        print(f"Sent: {data}")

    async def receive(self) -> str:
        if self.client is None:
            raise RuntimeError("Cllient is not connected")
        
        response = await self.client.recv()
        print(f"Received: {response}")
        #asyncio.sleep(self.timeout)
        return response

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None
            print("Closed WebSocket connection")


# -----------------------
# Example usage
# -----------------------
async def main():
    async with Client("ws://127.0.0.1:8000/ws") as ws:
        # send a single message
        count = 2
        str = ['Hello', 'World']
        while count>0:
            msg = input_to_messages(str[count-1])  # could return list[Message] or Message
            await ws.send(msg)

            # receive a message
            reply = await ws.receive()
            print(f"Got structured reply: {reply}")
            count-=1

if __name__ == "__main__":
    asyncio.run(main())
