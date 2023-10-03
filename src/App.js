import React from 'react';
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Login from './Login.js';
import Main from './main.js';

function App() {
  return (
    <BrowserRouter>
        <Routes>
            <Route path='/' element={<Login/>}></Route>
            <Route path='/chat' element = {<Main/>}></Route>
        </Routes>
    </BrowserRouter>
  )
}

export default App;
