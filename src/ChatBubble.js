import React from 'react';
import './ChatBubble.css'; // Import the CSS file for ChatBubble
import speak_logo from './speaking.png';

function text_to_speach(message) {
    console.log("Speak!")
    var utterance = new SpeechSynthesisUtterance(message.replace(/--+/g, ''));
    utterance.voice = speechSynthesis.getVoices().find(voice => voice.lang === 'hi-IN');
    utterance.lang = 'hi-IN';

    speechSynthesis.cancel();
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
