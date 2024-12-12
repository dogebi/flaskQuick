// const API_URL = 'http://localhost:5000/ask_gpt'; // Update with your server's URL
const API_URL = 'https://12054-o.azurewebsites.net/ask_gpt'; // Update with your server's URL

// 메시지 목록 가져오기
async function fetchMessages() {
  try {
    const response = await fetch(API_URL);
    
    // Check if the response is ok (status 200)
    if (!response.ok) {
      throw new Error(`Server error: ${response.statusText}`);
    }

    // Try to parse the response as JSON
    const data = await response.json();

    if (data.success) {
      const messagesContainer = document.getElementById('messages');
      messagesContainer.innerHTML = '';  // Clear existing messages

      data.messages.forEach(({ message, time, username }) => {
        const messageElement = document.createElement('p');
        messageElement.textContent = `[${new Date(time).toLocaleString()}] ${username}: ${message}`;
        messagesContainer.appendChild(messageElement);
      });
    } else {
      alert('Failed to load messages');
    }
  } catch (error) {
    console.error('Error fetching messages:', error.message);
    // Log the response body if it's HTML or plain text
    if (error.message.includes('Unexpected token')) {
      const responseText = await response.text();  // Read the response as text if it's not JSON
      console.error('Response content:', responseText);
    }
  }
}

async function sendMessage(message) {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.statusText}`);
    }

    const data = await response.json();
    if (data.success) {
      fetchMessages(); // Reload messages
    } else {
      alert(data.error || 'Failed to send message');
    }
  } catch (error) {
    console.error('Error sending message:', error);
    alert(`Failed to send message: ${error.message}`);
  }
}


// 초기화
document.addEventListener('DOMContentLoaded', () => {
  fetchMessages();  // Load messages on page load

  const messageForm = document.getElementById('message-form');
  messageForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();

    if (message) {
      sendMessage(message);
      messageInput.value = '';  // Clear input field
    }
  });
});
