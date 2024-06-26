import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import { Navbar } from 'flowbite-react';
import Oauth from './components/Oauth.js';
import UserHomePage from './components/UserHomePage.js';
import MainWindow from './components/MainWindow.js';
import ProjectPage from './components/ProjectPage.js';
import ProjectCreation from './components/Projects/ProjectCreation.js';
import ProjectDeletion from './components/Projects/ProjectDeletion.js';
import ProjectExport from './components/Projects/ProjectExport.js';
import CommitDeletion from './components/Commits/CommitDeletion.js';
import CommitSubmission from './components/Commits/CommitSubmission.js';
import DocumentCreation from './components/Documents/DocumentCreation.js';
import DocumentDeletion from './components/Documents/DocumentDeletion.js'
import FolderCreation from './components/Folders/FolderCreation.js';
import FolderDeletion from './components/Folders/FolderDeletion.js';
import PermissionPage from './components/Permissions/PermissionPage.js';

/**
 * Main App component that sets up routing and authentication for the application.
 * 
 * This component consists of a header, and the router which allows the user to access each of the application pages.
 *
 * @component
 * @example
 * // Example usage:
 * <App />
 */
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
          <Route path="/" element={<UserHomePage
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/Create" element={<ProjectCreation
            isLoggedIn={isLoggedIn} userData={userData}
            connected={connected} setConnected={setConnected}/>}/>
          <Route path="/Project/Delete/:project_id" element={<ProjectDeletion
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/:project_id/Share" element={<PermissionPage
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/:project_id/Commit/:commit_id" element={<ProjectPage
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/:project_id/Commit/Delete/:commit_id" element={<CommitDeletion
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/:project_id/Commit/Submit/:commit_id" element={<CommitSubmission
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/Export/:project_id" element={<ProjectExport
            isLoggedIn={isLoggedIn} userData={userData}
            connected={connected} setConnected={setConnected}/>}/>
          <Route path="/Project/:project_id/Commit/:commit_id/:parent_folder_id/Document/Create" element={<DocumentCreation
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/:project_id/Commit/:commit_id/Document/Delete/:document_id" element={<DocumentDeletion
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/:project_id/Commit/:commit_id/:parent_folder_id/Folder/Create" element={<FolderCreation
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/:project_id/Commit/:commit_id/Folder/Delete/:folder_id" element={<FolderDeletion
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/:project_id/Commit/:commit_id/Document/:document_id/:left_snapshot_id/:right_snapshot_id" element={<MainWindow
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
        </Routes>
      </Router>
    </div>
  );
}

export default App;
