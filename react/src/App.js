import ReviewWindow from './components/ReviewWindow.js';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UserHomePage from './components/UserHomePage.js';
import SnapshotSelector from './components/SnapshotSelector.js';
import MainWindow from './components/MainWindow.js';
import ProjectPage from './components/ProjectPage.js';

function App() {
  return (
    <Router>
      <Routes>
        <Route exact path="/" element={<ReviewWindow/>} />
        <Route path="/Home" element={<UserHomePage/>} />
        <Route path="/Project/:project_id" element={<ProjectPage/>}/>
        {/* todo add new document snapshot selection page for a document */}
        <Route path="/Document/:document_id/" /> 
        <Route path="/Document/:document_id/:left_snapshot_id/:right_snapshot_id" 
              element={<MainWindow/>}/>
      </Routes>
    </Router>
  );
}

export default App;
