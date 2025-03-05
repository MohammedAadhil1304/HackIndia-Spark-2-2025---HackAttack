// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Chatbot functionality for reporting
let conversationState = {};

function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    const chatWindow = document.getElementById('chat-window');
    const submitButton = document.getElementById('submit-report-btn');

    if (userInput.trim() !== "") {
        chatWindow.innerHTML += `<div class="message user">${userInput}</div>`;
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userInput, conversation_state: conversationState })
        })
        .then(response => response.json())
        .then(data => {
            chatWindow.innerHTML += `<div class="message bot">${data.message}</div>`;
            conversationState = data.report || {};
            
            if (data.ready_to_submit) {
                submitButton.style.display = 'block';
                chatWindow.innerHTML += `
                    <div class="message bot">
                        Here’s the report I’ve prepared:<br>
                        Crime Type: ${conversationState.crime_type}<br>
                        Description: ${conversationState.description}<br>
                        Date: ${conversationState.date_reported}<br>
                        Ready to submit?
                    </div>`;
            }
            chatWindow.scrollTop = chatWindow.scrollHeight;
        })
        .catch(error => {
            chatWindow.innerHTML += `<div class="message bot">Error: ${error}</div>`;
            chatWindow.scrollTop = chatWindow.scrollHeight;
        });
        document.getElementById('user-input').value = '';
    }
}

function submitReport() {
    const chatWindow = document.getElementById('chat-window');
    const submitButton = document.getElementById('submit-report-btn');

    fetch('/submit_report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(conversationState)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            chatWindow.innerHTML += `<div class="message bot">${data.message}</div>`;
            conversationState = {};
            submitButton.style.display = 'none';
        } else {
            chatWindow.innerHTML += `<div class="message bot">Error: ${data.message}</div>`;
        }
        chatWindow.scrollTop = chatWindow.scrollHeight;
    })
    .catch(error => {
        chatWindow.innerHTML += `<div class="message bot">Error: ${error}</div>`;
        chatWindow.scrollTop = chatWindow.scrollHeight;
    });
}

// AI Awareness bot functionality
function sendAwarenessMessage() {
    const userInput = document.getElementById('awareness-input').value;
    const awarenessWindow = document.getElementById('awareness-window');

    if (userInput.trim() !== "") {
        awarenessWindow.innerHTML += `<div class="message user">${userInput}</div>`;
        fetch('/ai-awareness', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userInput })
        })
        .then(response => response.json())
        .then(data => {
            awarenessWindow.innerHTML += `<div class="message bot">${data.response}</div>`;
            awarenessWindow.scrollTop = awarenessWindow.scrollHeight;
        })
        .catch(error => {
            awarenessWindow.innerHTML += `<div class="message bot">Error: ${error}</div>`;
            awarenessWindow.scrollTop = awarenessWindow.scrollHeight;
        });
        document.getElementById('awareness-input').value = '';
    }
}

// Handle file upload
document.getElementById('file-input')?.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const chatWindow = document.getElementById('chat-window');
        chatWindow.innerHTML += `<div class="message user">Uploaded: ${file.name}</div>`;
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});