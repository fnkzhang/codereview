import ReviewWindow from './components/ReviewWindow.js';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UserHomePage from './components/UserHomePage.js';

function App() {
  return (
    <Router>
      <Routes>
        <Route exact path="/" element={<ReviewWindow/>} />
        <Route path="/HomePage" element={<UserHomePage/>} />
      </Routes>
    </Router>
  );
}

export default App;
