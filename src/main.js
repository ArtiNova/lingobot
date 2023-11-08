import React, { Component } from 'react';
import { Navigate } from 'react-router-dom';
import './main.css';
import ChatBubble from './ChatBubble';
import axios from "axios";
import userAvatar from './user-avatar.png'; // Import the user avatar image
import aiAvatar from './ai-avatar.png';
import editLogo from './edit.png';
import delete_logo from './delete.png';

class Main extends Component {
    constructor(props) {
        super(props);
        this.state = {
            messages: [],
            userInput: '',
            context: '',
            isLoading: false,
            previous: [],
            selectedConv: '',
            editingIndex: null,
            newTitle: '',
        };
        this.server = 'http://' + window.location.hostname + ':5500';
        this.model =  'http://' + window.location.hostname + ':5501';
    }
    
    componentDidMount() {
        this.getPrevious()
            .then(response => {
                this.setState({ previous: response.data })
            })
    }

    addNewChat = () => {
        axios.post(this.server + "/api/newChat", {
            "username": window.sessionStorage.getItem("username"),
            "title": "New Chat " + this.state.previous.length
        })
            .then(response => {
                if (response.data) {
                    this.setState({ selectedConv: "New Chat " + this.state.previous.length, previous: [...this.state.previous, "New Chat " + this.state.previous.length], messages: [], context: '' })

                }
            })
            .catch(error => {
                console.log(error)
            })
    }

    handleSend = (event) => {
        if (this.state.userInput.trim() !== '') {
            if (this.state.selectedConv === '') {
                this.addNewChat();
            }
            axios.post(this.model + "/api/correctGrammar", {
                "text": this.state.userInput
            })
                .then(response => {
                    if (response.data !== '') {
                        let msgs = this.state.messages
                        if (msgs.length % 2) {
                            msgs[msgs.length - 1] += '\n' + "-".padStart(response.data.length, '-') + '\n You should have said : ' + response.data;
                        } else {
                            msgs[msgs.length - 2] += '\n' + "-".padStart(response.data.length, '-') + '\n You should have said : ' + response.data;
                        }
                        this.setState({ messages: msgs })
                        axios.post(this.server + '/api/updateMessages', {
                            "username": window.sessionStorage.getItem("username"),
                            "messages": this.state.messages,
                            "title": this.state.selectedConv
                        })

                    }
                })
            this.setState({ messages: [...this.state.messages, this.state.userInput], userInput: '', isLoading: true })
            axios.post(this.model + "/api/inference", {
                "input": this.state.userInput,
                "context": this.state.context
            })
                .then(response => {
                    axios.post(this.server + "/api/updateContext", {
                        "username": window.sessionStorage.getItem("username"),
                        "title": this.state.selectedConv,
                        "context": response.data.context
                    })
                    axios.post(this.server + "/api/updateMessages", {
                        "username": window.sessionStorage.getItem("username"),
                        "messages": [...this.state.messages, response.data.result],
                        "title": this.state.selectedConv
                    })
                    this.setState({ messages: [...this.state.messages, response.data.result], isLoading: false, context: response.data.context })
                    if (this.state.selectedConv.startsWith("New Chat")) {
                        axios.post(this.model + "/api/nameTitle", {
                            question: response.data.context
                        }).then(response => {
                            let index = this.state.previous.indexOf(this.state.selectedConv)
                            let prev_temp = this.state.previous
                            const oldTitle = this.state.selectedConv
                            prev_temp[index] = response.data
                            this.setState({ previous: prev_temp })
                            axios.post(this.server + "/api/renameTitle", {
                                "username": window.sessionStorage.getItem("username"),
                                "oldTitle": oldTitle,
                                "newTitle": response.data
                            })
                                .catch(err => {
                                    console.log(err)
                                })
                        })
                    }
                })
                .catch(error => {
                    alert(error)
                })
        }
    }

    loadPrevious = (event) => {
        if (this.state.editingIndex === null) {
            axios.post(this.server + "/api/loadPrevious", {
                "username": window.sessionStorage.getItem("username"),
                "title": event.target.innerHTML
            })
                .then(response => {
                    this.setState({ messages: response.data.messages, newChatCount: response.data.messages.length })
                    this.setState({ context: response.data.context })
                })
                .catch(error => {
                    alert(error)
                })
            this.setState({ selectedConv: event.target.innerHTML })
        }
    }

    getPrevious = () => {
        const username = window.sessionStorage.getItem("username")
        return axios.post(this.server + "/api/getPrevious", {
            "username": username
        })
    }

    handleEnter = (event) => {
        if (event.key === "Enter") {
            this.handleSend(event);
        }
    }

    handleDeleteConversation = (index) => {
        const updatedPrevious = [...this.state.previous];
        const title = updatedPrevious[index]
        updatedPrevious.splice(index, 1);
        this.setState({ previous: updatedPrevious, messages: [], context: '' });
        axios.post(this.server + "/api/deleteConv", {
            username: window.sessionStorage.getItem("username"),
            "title": title
        })
    }

    rename = (oldTitle, newTitle, index) => {
        let updatePrevious = [...this.state.previous];
        updatePrevious[index] = newTitle;
        this.setState({ previous: updatePrevious });
        axios.post(this.server + "/api/renameTitle", {
            "username": window.sessionStorage.getItem("username"),
            "oldTitle": oldTitle,
            "newTitle": newTitle
        })
        this.setState({ editingIndex: null, newTitle: '' })
    }

    render() {
        if (!window.sessionStorage.getItem('Logged In')) {
            return <Navigate to='/' />
        }

        return (
            <div className="container">
                <div className="sidebar">
                    <h1>Welcome {window.sessionStorage.getItem("username")}!</h1>
                    <button className='sidebar-button-logout' onClick={() => {
                        window.sessionStorage.clear();
                        window.location.replace("http://" + window.location.host + "/")
                    }}>Logout</button>
                    <h2>Previous Conversations</h2>
                    <button className='sidebar-button' onClick={this.addNewChat}><h3>+ New Chat</h3></button>
                    <ul>
                        {this.state.previous.map((title, index) => (
                            <div key={index} className="sidebar-button-container">
                                {(index === this.state.editingIndex) ? <input type='text' autoFocus className='editing-input' value={this.state.newTitle} onChange={(event) => { this.setState({ newTitle: event.target.value }) }} onKeyDown={(event) => { if (event.key === 'Enter') { this.rename(title, event.target.value, index) } }}></input> :
                                    <button id={index} className='sidebar-button' onClick={this.loadPrevious}>
                                        {title}
                                    </button>
                                }
                                <button className='delete-button' onClick={() => { this.setState({ editingIndex: index, newTitle: title }) }}><img className='edit-logo' alt={"rename"} src={editLogo}></img></button>
                                <button className='delete-button' onClick={() => this.handleDeleteConversation(index)}>
                                    <img className='edit-logo' alt={"delete"} src={delete_logo}></img>
                                </button>
                            </div>
                        ))}
                    </ul>
                </div>

                <div className="chat-interface">
                    <div className="chat-messages">
                        {this.state.messages.map((message, index) => (
                            <div key={index} className={index % 2 === 0 ? 'user-message' : 'ai-message'}>
                                <ChatBubble message={message} avatar={index % 2 === 0 ? userAvatar : aiAvatar} />
                            </div>
                        ))}
                    </div>
                    <div className="user-input">
                        <input
                            type="text"
                            placeholder="Send your message..."
                            value={this.state.userInput}
                            onChange={(e) => this.setState({ userInput: e.target.value })}
                            onKeyDown={this.handleEnter}
                        />
                        {(this.state.isLoading === false) ?
                            <button onClick={this.handleSend} disabled={this.state.isLoading}>
                                ▶
                            </button> : <div className="dot-falling-container">
                                <div className="stage">
                                    <div className="dot-falling"></div>
                                </div>
                            </div>
                        }
                    </div>
                </div>
            </div>
        );
    }
}

export default Main;
