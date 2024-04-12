import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UserHomePage from './components/UserHomePage.js';
import MainWindow from './components/MainWindow.js';
import ProjectPage from './components/ProjectPage.js';

import { Navbar, Avatar } from 'flowbite-react';
import ProjectCreation from './components/Projects/ProjectCreation.js';

function App() {
  return (
    <div> 
      {/* MOST LIKELY MOVE THIS INTO PROJECT LATER INSTEAD OF OUTSIDE */}
   <Navbar fluid rounded className='text-3xl text-textcolor p-5 
   list-none justify-between bg-[#373b49] border-b-2 border-slate-500 mb-2'>
      <div className='flex-1'>
        <Navbar.Brand href="#">
            <p>Code Review</p>
          </Navbar.Brand>
      </div>

      <div className='flex flex-1 justify-around align-middle'>
        <Navbar.Link href="/" active>Home</Navbar.Link>
        <Navbar.Link href="#">Account</Navbar.Link>
        <Avatar alt="User settings" 
        img="https://flowbite.com/docs/images/people/profile-picture-5.jpg" 
        className='w-10 h-10 rounded-sm'/>
      </div>

    </Navbar>


      <Router>
        <Routes>
          {/*<Route exact path="/" element={<ReviewWindow/>} /> */}
          <Route path="/" element={<UserHomePage/>} />
          <Route path="/Project/:project_id" element={<ProjectPage/>}/>
          <Route path="/Project/Create" element={<ProjectCreation/>}/>
          {/* todo add new document snapshot selection page for a document */}
          <Route path="/Document/:document_id/" /> 
          <Route path="/Document/:document_id/:left_snapshot_id/:right_snapshot_id" element={<MainWindow/>}/>

        </Routes>
      </Router>
    </div>
  );
}

export default App;
