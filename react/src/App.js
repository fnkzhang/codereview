import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import Oauth from './components/Oauth.js';
import UserHomePage from './components/UserHomePage.js';
import MainWindow from './components/MainWindow.js';
import ProjectPage from './components/ProjectPage.js';
import ProjectCreation from './components/Projects/ProjectCreation.js';
import ProjectDeletion from './components/Projects/ProjectDeletion.js';
import DocumentCreation from './components/Documents/DocumentCreation.js';
import FolderCreation from './components/Folders/FolderCreation.js';
import { Navbar } from 'flowbite-react';

function App() {

  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [connected, setConnected] = useState(false)
  const [userData, setUserData] = useState(null)

  return (
    <div> 
      <Router>
              {/* MOST LIKELY MOVE THIS INTO PROJECT LATER INSTEAD OF OUTSIDE */}
        <Navbar fluid rounded className='text-3xl text-textcolor p-5 
        list-none justify-between bg-[#373b49] border-b-2 border-slate-500 mb-2'>
          <div className='flex-1'>
            <Navbar.Brand>
                <p>Code Review</p>
              </Navbar.Brand>
          </div>

          <div className='flex flex-1 justify-around align-middle'>
            <Navbar.Brand href="/" active>Home</Navbar.Brand>
            <Navbar.Brand>
              <Oauth
                isLoggedIn={isLoggedIn}
                setIsLoggedIn={setIsLoggedIn}
                userData={userData}
                setUserData={setUserData}
                connected={connected}
                setConnected={setConnected}
              />
            </Navbar.Brand>
          </div>
        </Navbar>
        <Routes>
          {/*<Route exact path="/" element={<ReviewWindow/>} /> */}
          <Route path="/" element={<UserHomePage
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/:project_id" element={<ProjectPage
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/Create" element={<ProjectCreation
            isLoggedIn={isLoggedIn} userData={userData}
            connected={connected} setConnected={setConnected}/>}/>
          <Route path="/Project/Delete/:project_id/" element={<ProjectDeletion
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/:project_id/:parent_folder_id/Document/Create" element={<DocumentCreation/>}/>
          <Route path="/Project/:project_id/:parent_folder_id/Folder/Create" element={<FolderCreation/>}/>
          <Route path="/Document/:document_id/" /> 
          <Route path="Project/:project_id/Document/:document_id/:left_snapshot_id/:right_snapshot_id" element={<MainWindow
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
        </Routes>
      </Router>
    </div>
  );
}

export default App;
