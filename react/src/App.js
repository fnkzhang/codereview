import './App.css';
import Editor, { DiffEditor, useMonaco, loader } from '@monaco-editor/react';
import react, { useState } from 'react';

function App() {
  //Temp Stuff
  const initial_code = "print('Hello, world')"
  const [code, setCode] = useState(initial_code)

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
    
    await fetch(`/api/sendData`, headers)
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
          defaultValue={initial_code}
          onChange={handleChange}
        />;
      </header>
    </div>
  );
}

export default App;
