import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useNavigate } from 'react-router';
import { useState } from 'react';
import Oauth from './components/Oauth.js';
import UserHomePage from './components/UserHomePage.js';
import MainWindow from './components/MainWindow.js';
import ProjectPage from './components/ProjectPage.js';
import ProjectCreation from './components/Projects/ProjectCreation.js';
import ProjectDeletion from './components/Projects/ProjectDeletion.js';
import DocumentCreation from './components/Documents/DocumentCreation.js';
import { Navbar, Avatar } from 'flowbite-react';

function App() {

  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userData, setUserData] = useState(null)

  function displayProfileImage(isLoggedIn) {
    if (isLoggedIn) {
      return (<Avatar alt="User settings" 
      img="https://flowbite.com/docs/images/people/profile-picture-5.jpg" 
      className='w-10 h-10 rounded-sm'/>)
    }

    return
  }

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
              />
            </Navbar.Brand>
            {displayProfileImage(isLoggedIn)}
          </div>
        </Navbar>
        <Routes>
          {/*<Route exact path="/" element={<ReviewWindow/>} /> */}
          <Route path="/" element={<UserHomePage
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/Create" element={<ProjectCreation/>}/>
          <Route path="/Project/:project_id" element={<ProjectPage
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/Delete/:project_id/" element={<ProjectDeletion
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
          <Route path="/Project/:project_id/:project_root_folder_id/Document/Create" element={<DocumentCreation/>}/>
          {/* todo add new document snapshot selection page for a document */}
          <Route path="/Document/:document_id/" /> 
          <Route path="Project/:project_id/Document/:document_id/:left_snapshot_id/:right_snapshot_id" element={<MainWindow
            isLoggedIn={isLoggedIn} userData={userData}/>}/>
        </Routes>
      </Router>
    </div>
  );
}

export default App;
