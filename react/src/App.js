import EditWindow from './components/EditWindow.js';
import CommentDetail from './components/Comments/CommentDetail.js'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <Router>
      <Routes>
        <Route exact path="/" element={<EditWindow/>} />
        <Route path="/comment/:commentId" element={<CommentDetail/>} />
      </Routes>
    </Router>
  );
}

export default App;
