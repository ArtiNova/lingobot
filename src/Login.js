import React, { Component } from 'react';
import './Login.css';
import axios from "axios";
import { Navigate } from "react-router-dom";



class Login extends Component {
  constructor(props) {
    super(props);
    this.state = {
      username: '',
      password: '',
      error: ''
    };
    this.url = 'https://' + window.location.hostname + ':5500';
  }
  handleChange = (event) => {
    const { name, value } = event.target;
    this.setState({ [name]: value });
  }

  login = (username, password) => {
    return axios.post(this.url + "/api/login", {
      "username": username,
      "password": password
    })
  }

  signup = (username, password) => {
    return axios.post(this.url + "/api/signup", {
      "username": username,
      "password": password
    })
  }

  handleSubmit = (event) => {
    event.preventDefault();
    if (this.state.username !== '') {
      this.setState({ username: this.state.username.trim(), password: this.state.password.trim() })
      const { username, password } = this.state;
      this.login(username, password)
        .then(response => {
          if (response.data['status'] === false) {
            this.setState({ error: 'Invalid Credentials. Please try again' })
          } else {
            window.sessionStorage.setItem('Logged In', true);
            window.sessionStorage.setItem('username', username)
            window.sessionStorage.setItem('token', response.data['token'])
            this.setState({ error: '' })

          }
        })
        .catch(error => {
          this.setState({ error: 'Server Issues!' })
        })
    } else {
      this.setState({error : 'Enter a valid username!'})
    }
  }

  createUser = () => {
    const { username, password } = this.state;
    if (username !== '' || password !== '') {
      this.signup(username, password)
        .then(response => {
          if (response.data['status'] === false) {
            this.setState({ error: 'Credentials already exist' })
          } else {
            this.setState({ error: '' })
            window.sessionStorage.setItem('Logged In', true);
            window.sessionStorage.setItem('username', username)
            window.sessionStorage.setItem('token', response.data['token'])
          }
        })
    } else {
      this.setState({ error: 'Blank Fields not allowed!!' })
    }
  }

  render() {
    if (window.sessionStorage.getItem('Logged In')) {
      return <Navigate to='/chat' />
    }
    return (
      <div className="login-page">
        <div className="login-title">
          <h1>Chat2Fluency</h1>
        </div>
        <div className="login-container">
          <form onSubmit={this.handleSubmit} method="POST" className="login-form">
            <input
              className="input-field"
              type="text"
              name="username"
              placeholder="Username"
              value={this.state.username}
              onChange={this.handleChange}
            />
            <input
              className="input-field"
              type="password"
              name="password"
              placeholder="Password"
              value={this.state.password}
              onChange={this.handleChange}
            />
            <button className="login-button" type="submit">
              Login
            </button>
          </form>
          <button className="signup-button" type="submit" onClick={this.createUser}>
            Sign Up
          </button>
          <div className="error-message-container">
            <p className='error-message'>{this.state.error}</p>
          </div>
        </div>
      </div>
    );
  }
}

export default Login;
