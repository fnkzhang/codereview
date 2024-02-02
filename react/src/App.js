import './App.css';
import Editor, { DiffEditor, useMonaco, loader } from '@monaco-editor/react';
import react, { useState } from 'react';

function App() {
  //Temp Stuff
  const API_URL = "http://127.0.0.1:5000"
  
  const [code, setCode] = useState('')

  async function handleClick(e) {
    console.log(code)

    let bodyData = {
      "code": code
    }
    let headers = {
      method: "POST",
      mode: "cors",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(bodyData)
    }
    
    await fetch(`${API_URL}/sendData`, headers)
      .then(response => response.json())
      .then(data => console.log(data))
      .catch((e) => {
        console.log(e)
      })
  }


  function handleChange(newValue) {
    setCode(newValue)

  }

  return (
    <div className="App">
      <header className="App-header">
        <p>
          This is the monaco editor.
        </p>
        <button onClick={handleClick}>SubmitStuff</button>
        <Editor 
          height="90vh"
          defaultLanguage="python"
          defaultValue="print('Hello, world')"
          onChange={handleChange}
        />;
      </header>
    </div>
  );
}

export default App;
