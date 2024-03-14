import ReviewWindow from './components/ReviewWindow.js';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UserHomePage from './components/UserHomePage.js';
import SnapshotSelector from './components/SnapshotSelector.js';
import MainWindow from './components/MainWindow.js';
import SelectDocumentsPage from './components/SelectDocumentsPage.js';

function App() {
  return (
    <Router>
      <Routes>
        <Route exact path="/" element={<ReviewWindow/>} />
        <Route path="/Home" element={<UserHomePage/>} />
        <Route path="/Project/:project_id" element={<SelectDocumentsPage/>}/>
        <Route path="/Document/:document_id/:left_snapshot_id/:right_snapshot_id" 
              element={<MainWindow/>}/>
      </Routes>
    </Router>
  );
}

export default App;
