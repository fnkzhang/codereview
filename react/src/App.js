import ReviewWindow from './components/ReviewWindow.js';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UserHomePage from './components/UserHomePage.js';
import SnapshotSelector from './components/SnapshotSelector.js';


function App() {
  return (
    <Router>
      <Routes>
        <Route exact path="/" element={<ReviewWindow/>} />
        <Route path="/HomePage" element={<UserHomePage/>} />
        <Route path="/Document/:document_id/:snapshot_id" element={<SnapshotSelector/>}/>
      </Routes>
    </Router>
  );
}

export default App;
