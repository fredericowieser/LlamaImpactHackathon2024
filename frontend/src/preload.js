window.addEventListener("DOMContentLoaded", () => {
    const backButton = document.getElementById("backButton");
    const mainScreen = document.getElementById("mainScreen");
    const messageInput = document.getElementById("messageInput");

    // Divs for displaying fast and slow messages
    const fastMessagesDiv = document.getElementById("fastMessages");
    const slowMessagesDiv = document.getElementById("slowMessages");

    // WebSocket setup
    const socket = new WebSocket("ws://localhost:8000");

    socket.onopen = () => {
        console.log("WebSocket connected");
    };

    // Display incoming server messages in their respective divs
    socket.onmessage = (event) => {
        const serverMessage = event.data; // Incoming message from the server
        console.log("Message from server:", serverMessage);

        // Append the message to the appropriate div
        if (serverMessage.startsWith("Fast")) {
            const fastMessageElement = document.createElement("p");
            fastMessageElement.textContent = serverMessage;
            fastMessagesDiv.appendChild(fastMessageElement);
        } else if (serverMessage.startsWith("Slow")) {
            const slowMessageElement = document.createElement("p");
            slowMessageElement.textContent = serverMessage;
            slowMessagesDiv.appendChild(slowMessageElement);
        }
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
    };

    socket.onclose = () => {
        console.log("WebSocket closed");
    };

    // Back button functionality
    backButton.addEventListener("click", () => {
        console.log("Back button clicked");
        // Clear the input field and messages
        messageInput.value = ""; // Clear the input field
        fastMessagesDiv.innerHTML = ""; // Clear fast messages
        slowMessagesDiv.innerHTML = ""; // Clear slow messages

        // Send [RESTART] message to the server
        if (socket.readyState === WebSocket.OPEN) {
            socket.send("[RESTART]");
            console.log("Sent [RESTART] to server");
        } else {
            console.warn("WebSocket is not open. Could not send [RESTART].");
        }
    });

    // Handle message sending via text input when Enter is pressed
    messageInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault(); // Prevent the default behavior (form submission)
            const message = messageInput.value.trim(); // Get input value and trim whitespace
            if (message) {
                socket.send(message); // Send the message to the server
                console.log("Message sent to server:", message);
                messageInput.value = ""; // Clear the input field
            }
        }
    });
});
