import asyncio
import websockets

async def echo_audio(websocket):
    print("Client connected")
    try:
        async for message in websocket:
            if isinstance(message, bytes):
                # Echo binary audio data back to client
                print(f"Received {len(message)} bytes of audio")
                await websocket.send(message)
            else:
                print(f"Received text: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    print("Echo server started on ws://0.0.0.0:8765")
    async with websockets.serve(echo_audio, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
