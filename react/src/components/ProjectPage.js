import React, { useState, useEffect} from "react"
import { useNavigate, useParams } from "react-router"
import { Card, Dropdown } from "flowbite-react"
import { getAllSnapshotsFromDocument, getAllUsersWithPermissionForProject, getProjectInfo, getFolderTree,
  getCommits, createCommit, approveCommit, setCommitReviewed, 
  getLatestCommitForProject,
  setCommitClosed} from "../api/APIUtils"
import { IsUserAllowedToShare } from "../utils/permissionChecker"
import CommitDropdown from "./Commits/CommitDropdown"
import BackButton from "./BackButton"

// Display Documents For Project
export default function ProjectPage( props ) {

  const [loading, setLoading] = useState(true)
  const [commitLoading, setCommitLoading] = useState(true)
  const [creatingCommit, setCreatingCommit] = useState(false)
  const [projectOwnerEmail, setProjectOwnerEmail] = useState(null)
  const [projectName, setProjectName] = useState(null)
  const [folderStack, setFolderStack] = useState(null)
  const [commits, setCommits] = useState(null)
  const [commit, setCommit] = useState(null)
  const [latestCommitApproveCount, setLatestCommitApproveCount] = useState(0)
  const [latestCommitId, setLatestCommitId] = useState(null)

  const { project_id, commit_id } = useParams()
  const navigate = useNavigate()

  const [userPermissionLevel, setUserPermissionLevel] = useState(0);

  // Grab Documents if logged in and userdata
  useEffect(() => {

    async function grabProjectData() {
      const result = await getProjectInfo(project_id)
    
      setProjectOwnerEmail(result.author_email)
      setProjectName(result.name)
    }

    async function grabCommits() {
      const commitResult = await getCommits(project_id);
      const commitArray = commitResult.body.reverse();
      setCommits(commitArray);
    }

    async function fetchData() {
      try {
        await Promise.all([
          grabProjectData(),
          grabCommits(),
        ])
      } catch (error) {
        console.log(error)
      } finally {
        setLoading(false)
      }
    }

    if (creatingCommit) {
      setLoading(true)
      setCommitLoading(true)
      setFolderStack(null)
    }

    if (loading && props.isLoggedIn && !creatingCommit) {
      setCommits(null)
      setCommit(null)
      fetchData()
    } else
      return

  }, [project_id, loading, props.isLoggedIn, creatingCommit])

  useEffect(() => {

    function findCommit (x) {
      let foundCommit = null
      for (let i = 0; i < commits.length; i++) {
        if (Number(commits[i].commit_id) === x) {
          foundCommit = commits[i];
          break;
        }
      }
      return foundCommit
    }

    async function getTree() {

      let folderTreeResult = null
      let commit_val = null
      if (commit == null) {
        if (Number(commit_id) === 0) {
          commit_val = commits[0].commit_id
          folderTreeResult = await getFolderTree(commit_val);
        } else {
          commit_val = findCommit(Number(commit_id)).commit_id
          if (commit_val) {
            folderTreeResult = await getFolderTree(commit_val)
          } else {
            console.log("This is an unknown commit_id")
            return
          }
        }
        setCommit(findCommit(commit_val))
      } else {
        commit_val = commit.commit_id
        folderTreeResult = await getFolderTree(commit.commit_id)
      }

      folderTreeResult.body.commit_id = commit_val
      console.log(folderTreeResult.body)
      setFolderStack([folderTreeResult.body])
      navigate(`/Project/${project_id}/Commit/${commit_val}`)
    }

    if (props.isLoggedIn === false)
      return

    if ((commit !== null) && (commit.commit_id === Number(commit_id)))
      return

    if (commitLoading && (loading === false) && (commits !== null)) {
      getTree()
    }

  }, [commit, setCommit, commits, setCommits, commit_id, commitLoading, loading, props.isLoggedIn, navigate, project_id])

  useEffect(() => {
    if (commitLoading && (folderStack !== null) && (folderStack[0].commit_id === commit.commit_id))
      setCommitLoading(false)
  }, [folderStack, commitLoading, setCommitLoading, commit])
  
  // Get Latest Commit Prob optimize later
  useEffect(() => {
    async function getLatestCommitState(project_id){
      const latestCommit = await getLatestCommitForProject(project_id)
      console.log(latestCommit);
      if (latestCommit === null)
        console.log("Failed To get latest commit")
      else {
        if(latestCommit.approved_count !== null)
          setLatestCommitApproveCount(latestCommit.approved_count)
      }

      if (latestCommit !== null)
        setLatestCommitId(latestCommit.commit_id)
    }

    getLatestCommitState(project_id)
  }, [project_id])

  // Get the user permission level for use on the page
  useEffect(() => {
    if (props.userData === null)
      return;
    async function getUserPermissionLevel() {

      let searchResult = await getAllUsersWithPermissionForProject(project_id);

      for (let i = 0; i < searchResult.length; i++) {
        let userData = searchResult.at(i)
        if (userData.user_email === props.userData.email) {
          setUserPermissionLevel(userData.userPermissionLevel);      
          break;
        }
      }
    }

    if (props.isLoggedIn === true)
      getUserPermissionLevel();

  }, [props.userData, project_id, props.isLoggedIn])

  function FolderDisplayBox({id, name, folder}) {

    function handleFolderClick () {
      setFolderStack([...folderStack, folder])
    }

    function DisplayFolderOptions() {
      if (commit.date_committed !== null) {
        return(        
          <Dropdown className="bg-background" inline label="">
            <Dropdown.Item
              className="hover:bg-alternative"            
              onClick={() => handleFolderClick()}
            >
              <div className="text-textcolor m-1">
                View
              </div>
            </Dropdown.Item>
          </Dropdown>
        )
      }

      return(
        <Dropdown className="bg-background" inline label="">
          <Dropdown.Item
            className="hover:bg-alternative"            
            onClick={() => handleFolderClick()}
          >
            <div className="text-textcolor m-1">
              View
            </div>
          </Dropdown.Item>
          <Dropdown.Item
            className="hover:bg-alternative"              
            onClick={() => navigate(`/Project/${project_id}/Commit/${commit_id}/Folder/Delete/${id}`)}
          >
            <div className="text-textcolor m-1">
              Delete
            </div>
          </Dropdown.Item>
        </Dropdown>
      )
    }

    return (
      <Card 
        className="bg-background w-1/4 p-3 m-3"
      >
        <div className="w-full flex justify-between">
          <h4 className="flex flex-col text-textcolor overflow-hidden whitespace-nowrap p-1">
              <span className="font-bold text-xl">{name} </span>
          </h4>
          <div className="text-textcolor flex justify-end px-4 pt-4">
            <DisplayFolderOptions/>
          </div>
        </div>
        <h4 className="text-textcolor p-1">
          <span className="font-bold block">ID: </span>
          <span className="block">{id}</span>
        </h4>
      </Card>
    )
  }

  function DocumentDisplayBox({id, name, date, seenComments, seenSnapshot}) {
    let str1 = ""
    let str2 = ""
    if (seenSnapshot === false)
      str1 += "* New Snapshots"

    if (seenComments === false)
      str2 += "* New Comments"

    async function handleDocumentClick () {
      const result = await getAllSnapshotsFromDocument(project_id, id)

      const latestSnapshot = result.body[0].snapshot.snapshot_id;

      if (result.success)
        navigate(`/Project/${project_id}/Commit/${commit.commit_id}/Document/${id}/${latestSnapshot}/${latestSnapshot}`,
          {state: {documentName: name, addSnapshots: commit.date_committed}})
    }

    function DisplayDocumentOptions() {
      if (commit.date_committed !== null) {
        return(        
          <Dropdown className="bg-background" inline label="">
            <Dropdown.Item
              className="hover:bg-alternative"            
              onClick={() => handleDocumentClick()}
            >
              <div className="text-textcolor m-1">
                View
              </div>
            </Dropdown.Item>
          </Dropdown>
        )
      }
      


      return(
        <Dropdown className="bg-background" inline label="">
          <Dropdown.Item
            className="hover:bg-alternative"            
            onClick={() => handleDocumentClick()}
          >
            <div className="text-textcolor m-1">
              View
            </div>
          </Dropdown.Item>
          <Dropdown.Item
            className="hover:bg-alternative"              
            onClick={() => navigate(`/Project/${project_id}/Commit/${commit_id}/Document/Delete/${id}`)}
          >
            <div className="text-textcolor m-1">
              Delete
            </div>
          </Dropdown.Item>
        </Dropdown>
      )
    }

    // Function for document checkbox
    // async function setDocumentViewed() {

    // }
    
    return (
      <Card 
        className="bg-background w-1/4 p-3 m-3"
      >
        <div className="w-full flex justify-between">
          <h4 className="flex flex-col text-textcolor overflow-hidden whitespace-nowrap p-1">
              <span className="font-bold text-xl">{name} </span>
          </h4>
          <div className="text-textcolor flex align-middle justify-end px-4 pt-4">
            {/* Todo Adding CHeckbox for the document that have been changed for users to manually check */}
            {/* <p>Check If Finished Reviewing</p>
            <input type="checkbox" className="p-2 rounded-sm accent-[#47FF5D]" onChange={setDocumentViewed}/> */}
            <DisplayDocumentOptions/>
          </div>
        </div>
        <div className="flex">
          <div className="flex-1">
            <h4 className="text-textcolor p-1">
              <span className="font-bold block">ID: </span>
              <span className="block">{id}</span>
            </h4>
          </div>
          <div className="flex-1 text-textcolor content-center justify-end">
            <p>{str1}</p>
            <p>{str2}</p>
          </div>
        </div>
        <h4 className="text-textcolor p-1">
        <span className="font-bold block">Date Modified: </span>
          <span className="block">{date}</span>
        </h4>
      </Card>
    )
  }

  function sortByName(a, b) {
    // Convert both names to lowercase to ensure case-insensitive comparison
    const nameA = a.name.toLowerCase();
    const nameB = b.name.toLowerCase();

    if (nameA < nameB) {
      return -1; // nameA should come before nameB in the sorted order
    }
    if (nameA > nameB) {
      return 1; // nameA should come after nameB in the sorted order
    }
    return 0; // names are equal
  }

  function DisplayFolderBox() {
    let currentFolder = folderStack[folderStack.length - 1]
    if(currentFolder.content.folders.length !== 0) {
      return (
        <div>
          <h4 className="text-textcolor text-2xl m-2">Folders: </h4>
          <div className="flex flex-wrap">
            {
              currentFolder.content.folders.sort(sortByName)
              .map((folder, index) => {
                return (<FolderDisplayBox
                  key={index}
                  id={folder.folder_id}
                  name={folder.name}
                  folder={folder}
                />)
              })
            }
          </div>
        </div>
      )
    }
  }

  function DisplayDocumentBox() {
    let currentFolder = folderStack[folderStack.length - 1]
    if(currentFolder.content.documents.length !== 0) {
      return (
        <div>
          <h4 className="text-textcolor text-2xl m-2">Documents: </h4>
          <div className="flex flex-wrap">
            {
              currentFolder.content.documents.sort(sortByName)
              .map((document, index) => {
                return (<DocumentDisplayBox 
                  key={index} 
                  id={document.doc_id} 
                  name={document.name}
                  date={new Date(document.date_modified)
                    .toLocaleDateString("en-US", { 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric', 
                      weekday: 'long',  
                      hour: 'numeric',
                      minute: 'numeric',
                      second: 'numeric',
                      timeZoneName: 'short',
                    })}
                  seenComments={document.seenComments}
                  seenSnapshot={document.seenSnapshot}
                />)
              })
            }
          </div>
        </div>
      )
    }
    if(currentFolder.content.folders.length === 0)
      return (<div className="m-20 text-center text-textcolor text-2xl">
        There is nothing in this Folder.
      </div>)
  }

  function DisplayExportButton() {
    let buttonBackgroundColor = 'bg-alternative'


    if(latestCommitApproveCount > 0)
      buttonBackgroundColor = 'bg-[#23822e]'
    return (
      <div className="text-textcolor text-xl">
        <button className={"p-3 rounded-lg border-2 transition-all duration-300 hover:hover:bg-alternative m-1 " + buttonBackgroundColor }
        onClick={() => navigate(`/Project/Export/${project_id}/`)}>Export Project</button>
      </div>
    )
  }

  function DisplayDeleteButton() {
    if (props.userData === null)
      return

    if (props.userData.email !== projectOwnerEmail)
      return

    return (
      <div className="text-textcolor text-xl">
        <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:bg-red-800/75 m-1"
        onClick={() => navigate(`/Project/Delete/${project_id}`)}>Delete Project</button>
      </div>
    )
  }

  function DisplayShareButton() {
    if (props.userData === null)
      return
    // Make Sure user has permision to share before allowing them to share
    if (!IsUserAllowedToShare(userPermissionLevel))
      return

    return (
      <div className="text-textcolor text-xl">
        <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:bg-alternative m-1"
        onClick={() => navigate(`/Project/${project_id}/Share/`)}>
          Share
        </button>        
      </div>
    )
  }

  function DisplayCreateCommitButton() {
    // If Not Owner Of Project
    if (props.userData.email !== projectOwnerEmail)
      return

    if (commits.some(item => item.date_committed === null))
      return

    return (
      <div className="text-textcolor text-xl">
        <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:hover:bg-alternative m-1"
          onClick={async () => {
            setCreatingCommit(true)
            await createCommit(project_id, commit.commit_id)
            setCreatingCommit(false)
            navigate(`/Project/${project_id}/Commit/0`)
          }}>
          Create Commit
        </button>
      </div>
    )

  }

  function DisplayDeleteWorkingCommitButton() {
    if (props.userData.email !== projectOwnerEmail)
      return

    if (commit.date_committed !== null)
      return

    return(
      <div className="text-textcolor text-xl">
        <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:hover:bg-alternative m-1"
          onClick={() => navigate(`/Project/${project_id}/Commit/Delete/${commit.commit_id}`)}>
          Delete Commit
        </button>
      </div>
    )
  }

  function DisplayCommitWorkingCommitButton() {
    if (commit.date_committed !== null)
      return

    return(
      <div className="text-textcolor text-xl">
        <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:hover:bg-alternative m-1"
          onClick={() => navigate(`/Project/${project_id}/Commit/Submit/${commit.commit_id}`)}>
          Commit Changes
        </button>
      </div>
    )
  }

  function DisplayUploadDocumentButton() {
    if (commit.date_committed !== null)
      return
  
    return (
      <div className="text-textcolor text-xl">
        <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:hover:bg-alternative m-1"
          onClick={() => 
            navigate(`/Project/${project_id}/Commit/${commit.commit_id}/${folderStack[folderStack.length - 1].folder_id}/Document/Create`)
          }
        >
          Upload Document
        </button>
      </div>
    )
  }

  function DisplayCreateFolderButton() {
    if (commit.date_committed !== null)
      return

    return (
      <div className="text-textcolor text-xl">
        <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:hover:bg-alternative m-1"
          onClick={() => 
            navigate(`/Project/${project_id}/Commit/${commit.commit_id}/${folderStack[folderStack.length - 1].folder_id}/Folder/Create`)
          }
        >
          Create Folder
        </button>
      </div>
    )
  }

  function DisplayCloseCommitButton() {
    if(latestCommitApproveCount <= 0 )
      return
    if(props.userData.email !== projectOwnerEmail)
      return
    const closeCommit = async () => {
      const couldCloseCommit = await setCommitClosed(latestCommitId)
      console.log(couldCloseCommit)

      if(couldCloseCommit){
        // Make Export Button Live
      }
        

    }
    return  (
      <div className="flex justify-center text-textcolor text-xl">
        <button className=" p-3 rounded-lg border-2 transition-all duration-300 hover:hover:bg-alternative m-1"
        onClick={closeCommit}>
          Close Review
        </button>
      </div>
    )
  }

  function DisplayNavigateParentFolderButton() {
    if (folderStack.length === 1) {
      return
    }

    return (
      <div className="text-textcolor text-xl">
        <button className="rounded-lg border-2 transition-all duration-300 hover:hover:bg-alternative m-2 pl-1 pr-1"
        onClick={() => {
          setFolderStack(folderStack.slice(0, folderStack.length - 1))
          }
        }>^</button>
      </div>
    )  
  }

  function DisplayApproveChangesDecisionButton() {
    const ApproveCommitedChanges = async () => {
      let isSuccess = await approveCommit(commit_id)
      let isChangedState = await setCommitReviewed(commit_id);

      console.log(isSuccess, isChangedState);
      if(isSuccess)
        navigate('/')

      
    } 
    const DeclineCommitedChanged = async () => {
      let isChangedState = await setCommitReviewed(commit_id);
        // Todo for later handle in API
      if(isChangedState)
        navigate('/')
    }

    // Only Reviewer can decide on changes
    if(props.userData.email === projectOwnerEmail)
      return;

    return (
      <div className="text-textcolor text-xl">
        <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:bg-alternative m-1"
        onClick={ApproveCommitedChanges}>Approve</button>

        <button className="p-3 rounded-lg border-2 transition-all duration-300 hover:bg-alternative m-1"
        onClick={DeclineCommitedChanged}>Needs Changes</button>
      </div>
    ) 
  }

  if( props.isLoggedIn === false ) {
    return (
    <div>
      <div className="m-20 text-center text-textcolor text-2xl">
        You must Log in to view this page.
      </div>
    </div>
    )
  }

  if (creatingCommit) {
    return (
      <div>
        <div className="text-textcolor text-center m-20 text-xl">
          Creating Working Commit...
        </div>
      </div>
    )
  }

  if (loading || (commitLoading && (commit === null))) {
    return (
      <div>
        <div className="text-textcolor text-center m-20 text-xl">
          Loading...
        </div>
      </div>
    )
  }

  if (commitLoading) {
    return(
      <div>
        <h3 className="whitespace-nowrap font-bold text-textcolor text-2xl m-2">{`${projectOwnerEmail}/${projectName}`}</h3>
        <div className="flex m-1">
          <div className="flex flex-1 m-1">
            <BackButton location={`/`}/>
            <DisplayExportButton/>
            <DisplayDeleteButton/>
            <DisplayShareButton/>
          </div>
          <div className="flex-2 m-1">
            <DisplayApproveChangesDecisionButton/>
          </div>
        </div>
        <div className="flex">
          <h3 className="whitespace-nowrap text-textcolor text-2xl m-2">Commit: </h3>
          <CommitDropdown
            commits={commits}
            commit={commit}
            setCommit={setCommit}
            setCommitLoading={setCommitLoading}
          />
        </div>
        <div>
          <div className="text-textcolor text-center m-20 text-xl">
            Loading...
          </div>
        </div>
      </div>
    )
  }

  let path = `root/`
  for (let i = 1; i < folderStack.length; i++) {
    path += `${folderStack[i].name}/`
  }

  return (
    <div>
      <h3 className="whitespace-nowrap font-bold text-textcolor text-2xl m-2">{`${projectOwnerEmail}/${projectName}`}</h3>
      <div className="flex m-1">
        <div className="flex flex-1 m-1">
            <BackButton location={`/`}/>
            <DisplayExportButton/>
            <DisplayDeleteButton/>
            <DisplayShareButton/>
          </div>
          <div className="flex-2 m-1">
            <DisplayApproveChangesDecisionButton/>
            <DisplayCloseCommitButton/>
          </div>
        </div>
      <div className="flex">
        <h3 className="whitespace-nowrap text-textcolor text-2xl m-2">Commit: </h3>
        <CommitDropdown
          commits={commits}
          commit={commit}
          setCommit={setCommit}
          setCommitLoading={setCommitLoading}
        />
      </div>
      <div className="flex m-1">
        <DisplayDeleteWorkingCommitButton/>
        <DisplayCommitWorkingCommitButton/>
        <DisplayCreateCommitButton/>
        <DisplayUploadDocumentButton/>
        <DisplayCreateFolderButton/>
      </div>
      <div className="flex">
        <div className="overflow-x-auto">
          <h3 className="whitespace-nowrap text-textcolor text-2xl m-2">{`${path}`}</h3>
        </div>
        <DisplayNavigateParentFolderButton/>
      </div>
      <DisplayFolderBox/>
      <DisplayDocumentBox/>
    </div>
    
  )
}