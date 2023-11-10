import React from 'react';
import './ChatBubble.css'; // Import the CSS file for ChatBubble
import speak_logo from './speaking.png';

function text_to_speach(message) {
    var utterance = new SpeechSynthesisUtterance();
    utterance.text = message;
    utterance.lang = 'hi-IN';
    utterance.voice = speechSynthesis.getVoices()[0];

    speechSynthesis.speak(utterance);
}

function ChatBubble({ message, avatar }) {
    return (
        <div className="chat-bubble">
            {avatar && <img src={avatar} alt="Avatar" className="avatar" />}
            {message}
            <button onClick={() => { text_to_speach(message) }} className='speak-button'><img src={speak_logo} alt={'speak'} className='speak-logo'></img></button>
        </div>
    );
}

export default ChatBubble;
