const socket = new WebSocket("ws://localhost:8000");

socket.onopen = () => {
    console.log("WebSocket connected");
};

socket.onmessage = (event) => {
    console.log("Message from server:", event.data);
};

socket.onerror = (error) => {
    console.error("WebSocket error:", error);
};

socket.onclose = () => {
    console.log("WebSocket closed");
};

// Event listener to send a string message to the server
window.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("sendButton");
    button.addEventListener("click", () => {
        const message = "Hello Server!"; // The string to send
        socket.send(message);
        console.log("Message sent to server:", message);
    });
});
