window.addEventListener("DOMContentLoaded", () => {
    const socket = new WebSocket("ws://localhost:8000/ws");
    let mediaRecorder = null;
    let isRecording = false;

    // Get DOM elements
    const fastMessagesDiv = document.getElementById("fastMessages");
    const slowMessagesDiv = document.getElementById("slowMessages");
    const messageInput = document.getElementById("messageInput");
    const backButton = document.getElementById("backButton");

    // WebSocket event handlers
    socket.onopen = () => {
        console.log("WebSocket connected");
        startAudioStreaming();
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            updateUI(data);
        } catch (error) {
            console.error("Error handling message:", error);
        }
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
    };

    socket.onclose = () => {
        console.log("WebSocket closed");
        stopAudioStreaming();
    };

    // Function to update UI with server responses
    function updateUI(data) {
        switch(data.type) {
            case "transcript_update":
            case "update":
                if (data.transcript) {
                    fastMessagesDiv.innerHTML = data.transcript;
                }
                break;
            case "full_update":
                if (data.transcript) {
                    fastMessagesDiv.innerHTML = data.transcript;
                }
                if (data.summary) {
                    const notification = document.createElement("div");
                    notification.classList.add("notification");
                    notification.textContent = data.summary;
                    slowMessagesDiv.prepend(notification);
                }
                break;
            default:
                console.log("Unknown message type:", data.type);
        }
    }

    // Audio streaming setup
    async function startAudioStreaming() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    echoCancellation: true,
                    noiseSuppression: true
                } 
            });

            console.log('Got audio stream:', stream);
            console.log('Audio tracks:', stream.getAudioTracks());

            mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus',
                audioBitsPerSecond: 16000
            });

            console.log('MediaRecorder created:', mediaRecorder);

            mediaRecorder.ondataavailable = async (event) => {
                if (event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
                    console.log('Data available event:', event);
                    console.log('Data size:', event.data.size);
                    
                    const buffer = await event.data.arrayBuffer();
                    console.log('Sending buffer size:', buffer.byteLength);
                    socket.send(buffer);
                }
            };

            // Add debug event listeners
            mediaRecorder.onstart = (event) => {
                console.log('MediaRecorder started:', event);
                isRecording = true;
            };

            mediaRecorder.onstop = (event) => {
                console.log('MediaRecorder stopped:', event);
                isRecording = false;
            };

            mediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event);
                isRecording = false;
            };

            // Start recording in small chunks
            mediaRecorder.start(1000);
            console.log("Audio streaming started");
            
        } catch (error) {
            console.error("Error starting audio stream:", error);
            // Try fallback if main method fails
            startAudioStreamingFallback();
        }
    }

    // Fallback audio method
    async function startAudioStreamingFallback() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    echoCancellation: true,
                    noiseSuppression: true
                } 
            });
            
            mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm',
                audioBitsPerSecond: 16000
            });

            mediaRecorder.addEventListener("dataavailable", async (event) => {
                if (event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
                    const buffer = await event.data.arrayBuffer();
                    socket.send(buffer);
                    console.log(`Sent audio chunk: ${buffer.byteLength} bytes`);
                }
            });

            mediaRecorder.start(1000);
            isRecording = true;
            console.log("Started audio recording (fallback)");
            
        } catch (error) {
            console.error("Error starting fallback audio stream:", error);
        }
    }

    function stopAudioStreaming() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            console.log("Audio streaming stopped");
        }
    }

    // Handle back button
    backButton?.addEventListener("click", () => {
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ 
                type: "text", 
                text: "[RESTART]" 
            }));
            fastMessagesDiv.innerHTML = "";
            slowMessagesDiv.innerHTML = "";
            messageInput.value = "";
        }
    });

    // Handle text input
    messageInput?.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            const message = messageInput.value.trim();
            if (message && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ 
                    type: "text", 
                    text: message 
                }));
                messageInput.value = "";
            }
        }
    });

    // Clean up on page unload
    window.addEventListener("beforeunload", () => {
        stopAudioStreaming();
        if (socket.readyState === WebSocket.OPEN) {
            socket.close();
        }
    });
});