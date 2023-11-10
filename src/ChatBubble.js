import React from 'react';
import './ChatBubble.css'; // Import the CSS file for ChatBubble
import speak_logo from './speaking.png';
import user from './user-avatar.png';

function text_to_speach(message, avatar) {
    var utterance = new SpeechSynthesisUtterance((avatar === user ? message : message.split('\n')[0]));
    utterance.voice = speechSynthesis.getVoices().find(voice => voice.lang === 'hi-IN');
    utterance.lang = 'hi-IN';
    utterance.rate = 1.0;

    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
}

function ChatBubble({ message, avatar }) {
    return (
        <div className="chat-bubble">
            {avatar && <img src={avatar} alt="Avatar" className="avatar" />}
            {message}
            <button onClick={() => { text_to_speach(message, avatar) }} className='speak-button'><img src={speak_logo} alt={'speak'} className='speak-logo'></img></button>
        </div>
    );
}

export default ChatBubble;
