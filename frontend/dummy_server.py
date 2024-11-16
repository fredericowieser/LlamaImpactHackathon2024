import asyncio
import websockets

# Adapt the handler to accept *args and handle missing arguments
async def handle_client(websocket, *args):
    print(f"New client connected. Arguments received: {args}")
    try:
        async for message in websocket:
            print(f"Message received: {message}")
            await websocket.send(f"Echo: {message}")
    except websockets.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    print("Starting WebSocket server on ws://localhost:8000")
    async with websockets.serve(handle_client, "localhost", 8000):
        print("Server is running...")
        await asyncio.Future()  # Keep the server running

if __name__ == "__main__":
    asyncio.run(main())


