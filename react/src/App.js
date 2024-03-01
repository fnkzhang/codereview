import ReviewWindow from './components/ReviewWindow.js';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <Router>
      <Routes>
        <Route exact path="/" element={<ReviewWindow originalID={0} modifiedID={2}/>} />
      </Routes>
    </Router>
  );
}

export default App;
