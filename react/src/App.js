import './App.css';
import Editor, { DiffEditor, useMonaco, loader } from '@monaco-editor/react';
import react, { useState } from 'react';

function App() {
  //Temp Stuff
  const API_URL = "http://127.0.0.1:5000"
  
  const [code, setCode] = useState('')

  const handleClick = (e) => {
    console.log(code)

  }


  async function handleChange(newValue) {
    setCode(newValue)

    let headers = {
      method: "GET",
      mode: "cors",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify()
    }
    
    await fetch(`${API_URL}/sendCode`, headers)
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
