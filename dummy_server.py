import asyncio
import websockets
import random

# Handle incoming client messages
async def receive_messages(websocket):
    try:
        async for message in websocket:
            print(f"Message received: {message}")
            await websocket.send(f"Echo: {message}")  # Echo back the received message
    except websockets.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

# Periodically send fast messages to the client
async def fast_periodic_messages(websocket):
    try:
        while True:
            await asyncio.sleep(random.randint(5, 10))  # Simulate periodic updates
            fast_message = f"Fast message at {random.randint(1, 100)}"
            print(f"Sending fast message: {fast_message}")
            await websocket.send(fast_message)
    except websockets.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

# Periodically send slower messages to the client
async def slow_periodic_messages(websocket):
    try:
        while True:
            await asyncio.sleep(random.randint(2, 10))  # Simulate slower periodic updates
            slow_message = f"Slow message at with two lines to show notification at {random.randint(101, 200)}"
            print(f"Sending slow message: {slow_message}")
            await websocket.send(slow_message)
    except websockets.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

# Handle client connections
async def handle_client(websocket, *args):
    print(f"New client connected. Arguments received: {args}")
    # Run the receive and send tasks concurrently
    await asyncio.gather(
        receive_messages(websocket),
        fast_periodic_messages(websocket),
        slow_periodic_messages(websocket),
    )

# Start the WebSocket server
async def main():
    print("Starting WebSocket server on ws://localhost:8000")
    async with websockets.serve(handle_client, "localhost", 8000):
        print("Server is running...")
        await asyncio.Future()  # Keep the server running

if __name__ == "__main__":
    asyncio.run(main())
