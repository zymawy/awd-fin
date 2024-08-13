const roomName = JSON.parse(document.getElementById('room-name').textContent);
const username = JSON.parse(document.getElementById('username').textContent);
const auth_group = JSON.parse(document.getElementById('auth_group').textContent);
const user_id = JSON.parse(document.getElementById('user_id').textContent);

console.log(user_id)
const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/' + roomName + '/');

chatSocket.onopen = function(e) {
    chatSocket.send(JSON.stringify({
        'message': 'Joined room',
        'sender': username,
        'auth_group': auth_group,
        'user_id': user_id,
        'type': 'info'  // Mark as informative message
    }));
};

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const chatLog = document.querySelector('#chat-log');
    const messageElement = document.createElement('div');
    const timestamp = data.timestamp ? data.timestamp : new Date().toLocaleTimeString();

    if (data.message_type === 'info') {
        // Handle informative messages like "Joined room" or "Left room"
        messageElement.className = 'text-center text-gray-500 text-xs my-2';
        messageElement.innerHTML = `
            <hr class="border-gray-300 my-2">
            <span>${data.sender} ${data.message}</span>
            <hr class="border-gray-300 my-2">
        `;
    } else if (data.auth_group === 'instructor') {
        // Styling for instructor messages
        messageElement.className = 'p-2 mb-1 text-white bg-sky-600 rounded-lg';
        messageElement.innerHTML = `<strong>${data.sender} (Instructor)</strong> <span class="text-xs text-gray-200 ml-2">[${timestamp}]</span>: ${data.message}`;
    } else {
        // Styling for student/regular user messages
        messageElement.className = 'p-2 mb-1 bg-gray-200 rounded-lg';
        messageElement.innerHTML = `<strong>${data.sender}</strong> <span class="text-xs text-gray-600 ml-2">[${timestamp}]</span>: ${data.message}`;
    }

    chatLog.appendChild(messageElement);
    chatLog.scrollTop = chatLog.scrollHeight;
};


window.onbeforeunload = function() {
    chatSocket.send(JSON.stringify({
        'message': 'Left room',
        'sender': username,
        'auth_group': auth_group,
		"user_id": user_id,
		'type': 'info'
    }));
    chatSocket.close();
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

chatSocket.onerror = function(e) {
    console.error('WebSocket error:', e);
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    const message = e.target.value;
    const sendButton = document.querySelector('#chat-message-submit');

    if (message.trim() === '') {
        sendButton.disabled = true;
    } else {
        sendButton.disabled = false;
    }

    if (e.keyCode === 13 && !sendButton.disabled) {
        sendButton.click();
    }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value.trim();

    if (message) {
        chatSocket.send(JSON.stringify({
            'message': message,
            'sender': username,
            'auth_group': auth_group,
			"user_id": user_id
        }));
        messageInputDom.value = '';
        document.querySelector('#chat-message-submit').disabled = true;
    }
};
