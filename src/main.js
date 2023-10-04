import React, { Component } from 'react';
import { Navigate } from 'react-router-dom';
import './main.css';
import ChatBubble from './ChatBubble';
import axios from "axios";
import userAvatar from './user-avatar.png'; // Import the user avatar image
import aiAvatar from './ai-avatar.png';
import dotLoading from './load.gif'

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
        };
    }

    componentDidMount() {
        this.getPrevious()
            .then(response => {
                this.setState({ previous: response.data })
            })
    }

    addNewChat = () => {
        axios.post("http://localhost:5500/api/newChat", {
            "username": window.sessionStorage.getItem("username"),
            "title": "New Chat " + this.state.messages.length + 1
        })
            .then(response => {
                if (response.data) {
                    this.setState({ previous: [...this.state.previous, "New Chat " + this.state.messages.length + 1], selectedConv: "New Chat " + this.state.messages.length + 1, messages: [] })

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
            this.setState({ messages: [...this.state.messages, this.state.userInput], userInput: '', isLoading: true })
            axios.post("http://localhost:5501/api/inference", {
                "input": this.state.userInput,
                "context": this.state.context
            })
                .then(response => {
                    axios.post("http://localhost:5500/api/updateContext", {
                        "username": window.sessionStorage.getItem("username"),
                        "title": this.state.selectedConv,
                        "context": response.data.context
                    })
                    axios.post("http://localhost:5500/api/updateMessages", {
                        "username": window.sessionStorage.getItem("username"),
                        "messages": [...this.state.messages, response.data.result],
                        "title": this.state.selectedConv
                    })
                    this.setState({ messages: [...this.state.messages, response.data.result], isLoading: false, context: response.data.context })
                    if (this.state.messages.length === 2) {
                        axios.post("http://localhost:5501/api/nameTitle", {
                            question: response.data.context
                        }).then(response => {
                            let index = this.state.messages.indexOf(this.state.selectedConv)
                            let mess_temp = this.state.messages
                            const oldTitle = mess_temp[index]
                            mess_temp[index] = response.data
                            this.setState({ messages: mess_temp })
                            axios.post("http://localhost:5500/api/renameTitle", {
                                "username": window.sessionStorage.getItem("username"),
                                "title": oldTitle,
                                "newTitle": response.data
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
        axios.post("http://localhost:5500/api/loadPrevious", {
            "username": window.sessionStorage.getItem("username"),
            "title": event.target.innerHTML
        })
            .then(response => {
                this.setState({ messages: response.data.messages, newChatCount: response.data.messages.length })
                this.setState({ context: response.data.context })
                console.log(this.state.context)
                console.log(this.state)
            })
            .catch(error => {
                alert(error)
            })
        this.setState({ selectedConv: event.target.innerHTML })
    }

    getPrevious = () => {
        const username = window.sessionStorage.getItem("username")
        return axios.post("http://localhost:5500/api/getPrevious", {
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
        this.setState({ previous: updatedPrevious, messages: [] });
        axios.post("http://localhost:5500/api/deleteConv", {
            username: window.sessionStorage.getItem("username"),
            "title": title
        })
    }

    render() {
        if (!window.sessionStorage.getItem('Logged In')) {
            return <Navigate to='/' />
        }

        return (
            <div className="container">
                <div className="sidebar">
                    <h1>Welcome {window.sessionStorage.getItem("username")}!</h1>
                    <h2>Previous Conversations</h2>
                    <button className='sidebar-button' onClick={this.addNewChat}><h3>+ New Chat</h3></button>
                    <ul>
                        {this.state.previous.map((title, index) => (
                            <div key={index} className="sidebar-button-container">
                                <button className='sidebar-button' onClick={this.loadPrevious}>
                                    {title}
                                </button>
                                <button className='delete-button' onClick={() => this.handleDeleteConversation(index)}>
                                    🗑
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
                        <button onClick={this.handleSend} disabled={this.state.isLoading}>
                            {(this.state.isLoading === false) ? "▶" : <img className='dotLoading' src={dotLoading} alt={"gif"}></img>

                            }
                        </button>
                    </div>
                </div>
            </div>
        );
    }
}

export default Main;
