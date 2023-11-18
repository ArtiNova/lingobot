import React, { Component } from 'react';
import './ChatBubble.css'; // Import the CSS file for ChatBubble
import speak_logo from './speaking.png';
import user from './user-avatar.png';
import axios from 'axios';
import stop_speak from './stop.png';

// function text_to_speach(message, avatar) {
//     var to_speak = (avatar === user ? message : message.split('\n')[0])
//     // var utterance = new SpeechSynthesisUtterance((avatar === user ? message : message.split('\n')[0]));
//     // utterance.voice = speechSynthesis.getVoices().find(voice => voice.lang === 'hi-IN');
//     // utterance.lang = 'hi-IN';
//     // utterance.rate = 1.0;

//     // speechSynthesis.cancel();
//     // speechSynthesis.speak(utterance);
//     axios.post('http://' + window.location.hostname + ':5500/api/audio', {
//         "message": to_speak
//     })
//         .then(response => {
//             if (response.data === true) {
//                 var audio = new Audio('http://' + window.location.hostname + ':5500/api/playSound');
//                 audio.playbackRate = 1.2;
//                 audio.play().then(() => {
//                     axios.post('http://' + window.location.hostname + ':5500/api/deleteAudio')
//                 })
//             } else {
//                 alert("Server Issues. Please Try again in sometime");
//             }
//         })
// }

// function ChatBubble({ message, avatar }) {
//     return (
//         <div className="chat-bubble">
//             {avatar && <img src={avatar} alt="Avatar" className="avatar" />}
//             {message}
//             <button onClick={() => { text_to_speach(message, avatar) }} className='speak-button'><img src={speak_logo} alt={'speak'} className='speak-logo'></img></button>
//         </div>
//     );
// }

class ChatBubble extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isPlaying: false
        }
        this.audio = new Audio();
    }

    text_to_speach = () => {
        var to_speak = (this.props.avatar === user ? this.props.message : this.props.message.split('\n')[0])
        // var utterance = new SpeechSynthesisUtterance((avatar === user ? message : message.split('\n')[0]));
        // utterance.voice = speechSynthesis.getVoices().find(voice => voice.lang === 'hi-IN');
        // utterance.lang = 'hi-IN';
        // utterance.rate = 1.0;

        // speechSynthesis.cancel();
        // speechSynthesis.speak(utterance);
        axios.post('http://' + window.location.hostname + ':5500/api/audio', {
            "message": to_speak
        })
            .then(response => {
                if (response.data === true) {
                    this.audio.src = 'http://' + window.location.hostname + ':5500/api/playSound'
                    this.audio.playbackRate = 1.2;
                    this.audio.onplay = (event) => {
                        this.setState({isPlaying : true});
                    }
                    this.audio.play().then(() => {
                        axios.post('http://' + window.location.hostname + ':5500/api/deleteAudio')
                    })
                    this.audio.onended = (event) => {
                        this.setState({isPlaying : false});
                    }
                } else {
                    alert("Server Issues. Please Try again in sometime");
                }
            })
    }

    stopSpeach = () => {
        this.audio.pause()
        this.audio.currentTime = 0;
        this.setState({isPlaying : false});
    }

    render() {
        return (
            <div className="chat-bubble">
                {this.props.avatar && <img src={this.props.avatar} alt="Avatar" className="avatar" />}
                {this.props.message}
                {(this.state.isPlaying === false) ? <button onClick={this.text_to_speach} className='speak-button'><img src={speak_logo} alt={'speak'} className='speak-logo'></img></button> : 
                <button onClick={this.stopSpeach} className='speak-button'><img src={stop_speak} alt={'speak'} className='speak-logo'></img></button>
                }
            </div>
        );
    }
}

export default ChatBubble;
