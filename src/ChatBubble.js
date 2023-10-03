import React from 'react';
import './ChatBubble.css'; // Import the CSS file for ChatBubble

function ChatBubble({ message, avatar}) {
    return (
        <div className="chat-bubble">
            {avatar && <img src={avatar} alt="Avatar" className="avatar" />}
            {message}
        </div>
    );
}

export default ChatBubble;
