import './App.css';
import Editor, { DiffEditor, useMonaco, loader } from '@monaco-editor/react';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <p>
          This is the monaco editor.
        </p>
        <Editor 
          height="90vh"
          defaultLanguage="python"
          defaultValue="print('Hello, world')" 
        />;
      </header>
    </div>
  );
}

export default App;
