import getCookie from "../utils/utils"

/**
 * @param {string} projectName The Name of the project being created
 * @returns {string} The server response message
*/
export async function createProject(projectName) {

  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "POST",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "project_name": projectName
    })
  }
  return await fetch((`/api/Project/createProject/`), headers)
    .then(response => response.json())

}

/**
 * @param {number} proj_id The project id number for the project being deleted
 * @returns {string} The server response message
*/
export async function deleteProject(proj_id) {

  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "DELETE",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  }
  return await fetch((`/api/Project/${proj_id}/`), headers)
    .then(response => response.json())

}

/**
* @param {number} proj_id The project id number for the project which a user is being added to
* @param {string} emailToAdd The new users email
* @param {string} foleNameForEmail The role which will be displayed for the user
* @param {number} permissionLevel The permission value assigned to that user
* @returns {string} The server response message
*/
export async function addUserToProject(proj_id, emailToAdd, roleNameForEmail, permissionLevel) {

  let oAuthToken = getCookie("cr_id_token")

  let bodyData = {
    "email": emailToAdd,
    "role": roleNameForEmail,
    "permissions": permissionLevel
  }
  let headers = {
    method: "POST",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(bodyData)
  }

  return await fetch((`/api/Project/${proj_id}/addUser/`), headers)
    .then(response => response.json())

}

/**
* @param {number} proj_id The project id number for the project which a user is being deleted from
* @param {string }emailToRemove The email for the user which is being removed from the project
* @returns {string} The server response message
*/
export async function removeUserFromProject(proj_id, emailToRemove) {

  let oAuthToken = getCookie("cr_id_token")

  let bodyData = {
    "email": emailToRemove,
  }
  let headers = {
    method: "DELETE",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(bodyData)
  }

  return await fetch((`/api/Project/${proj_id}/removeUser/`), headers)
    .then(response => response.json())

}

/**
* @param {number} proj_id The project id for which the users are being requested
* @returns {[users]} The list of users which have permissions on the project
*/
export async function getAllUsersWithPermissionForProject(proj_id) {

  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  }

  return await fetch((`/api/Project/${proj_id}/Users/`), headers)
    .then(response => response.json())
    .then(data => data.body)
    .catch(error => console.log(error))

}

/**
* @param {number} proj_id The project id number for the project which a user is being promoted
* @param {string} currentOwnerEmail The email for the current owner of the project
* @param {string} newOwnerEmail The email for the new owner of the project
* @returns {string} The server response message
*/
export async function promoteEmailToProjectOwner(proj_id, currentOwnerEmail, newOwnerEmail) {

  let oAuthToken = getCookie("cr_id_token")

  const body = {
    "email": newOwnerEmail
  }

  let headers = {
    method: "POST",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  }

  return await fetch((`/api/Project/${proj_id}/transferOwnership/`), headers)
    .then(response => response.json())
    .catch(error => console.log(error))

}

/**
* @param {string} documentName The name for the newly created document
* @param {number} proj_id The project id number for the project which the user will belong
* @param {number} commit_id The commit id number for the working commit which will hold this document
* @param {string} documentData The document's contents
* @param {number} parent_folder_id The folder id number for the folder which will hold this document
* @returns {string} The server response message
*/
export async function createDocument(documentName, proj_id, commit_id, documentData, parent_folder_id) {

  let oAuthToken = getCookie("cr_id_token")

  let bodyData = {
    doc_name: documentName,
    data: documentData,
    project_id: proj_id,
    parent_folder: parent_folder_id
  }
  
  let headers = {
    method: "POST",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(bodyData)
  }
  return await fetch((`/api/Document/${proj_id}/${commit_id}/`), headers)
    .then(response => response.json())

}

/**
* @param {number} doc_id The document id number for the document which is being deleted
* @param {number} commit_id The commit id number which this document is being deleted from
* @returns {string} The server response message
*/
export async function deleteDocument(doc_id, commit_id) {

  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "DELETE",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  }
  return await fetch((`/api/Document/${doc_id}/${commit_id}/`), headers)
    .then(response => response.json())

}

/**
* @param {number} proj_id The project id number for the project which the document is in
* @param {number} commit_id The commit id number for the commit wich the document is a part of
* @param {number} doc_id The document id number for the document
* @returns {document} The document info
*/
export async function  getDocumentInfo(proj_id, commit_id, doc_id) {

  let oAuthToken = getCookie("cr_id_token")
  
  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  }

  return await fetch((`/api/Document/${proj_id}/${doc_id}/${commit_id}/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data.body
  })

}

/**
* @param {number} proj_id The project id number for the project which the document is in
* @param {number} doc_id The document id number for the document
* @param {number} snap_id The snapshot id number for the desired snapshot
* @returns {string} The contents of the snapshot
*/
export async function getDocSnapshot(proj_id, doc_id, snap_id) {

  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    credentials: 'include',
    headers: {
      "Access-Control-Allow-Credentials": true,
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  }

  return await fetch((`/api/Snapshot/${proj_id}/${doc_id}/${snap_id}/`), headers)
    .then(response => response.json())

}

/**
* @param {number} proj_id The project id number for the project which the document is in
* @param {number} commit_id The commit id number for the commit wich the document is a part of
* @param {number} doc_id The document id number for the document
* @param {string} snapshot_data The contents of the newly created snapshot
* @returns {string} The server response message, contains the snapshot_id if successful
*/
export async function createSnapshotForDocument(proj_id, commit_id, doc_id, snapshot_data) {

  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "POST",
    mode: "cors",
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "data": snapshot_data
    })
  }

  return await fetch((`/api/Snapshot/${proj_id}/${doc_id}/${commit_id}/`), headers)
    .then(response => response.json())
    .then(data => {
      if (data.success)
        return data.body
      return null
    })
    .catch(error => console.log(error))
  
}

/**
* @param {number} snap_id The snapshot id number for the snapshot the comment is being created on
* @param {string} author_email The user who is creating the comment
* @param {number} reply_to_id The id of the comment which this comment is responding to
* @param {string} content The message which the user is submitting in the comment
* @param {number} highlight_start_x The column for which the users highlight begins
* @param {number} highlight_start_y The row for which the users highligh begins
* @param {number} highlight_end_x The column for which the users highlight ends
* @param {number} highlight_end_y The row for which the users highlight ends
* @returns {string} The server response message
*/
export async function createComment(snap_id, author_email, reply_to_id, content, 
   highlight_start_x, highlight_start_y, highlight_end_x, highlight_end_y) {
  
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "POST",
    mode: "cors",
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "snapshot_id": snap_id,
      "author_email": author_email,
      "reply_to_id": reply_to_id,
      "content": content,
      "highlight_start_x": highlight_start_x,
      "highlight_start_y": highlight_start_y,
      "highlight_end_x": highlight_end_x,
      "highlight_end_y": highlight_end_y,
      "is_resolved": false,
    })
  };

  return await fetch(`/api/Snapshot/${snap_id}/comment/create`, headers)
    .then(response => response.json())

}

/**
* @param {number} comment_id The comment id number for the comment which is being resolved
* @returns {string} The server response message
*/
export async function resolveComment(comment_id) {

  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "PUT",
    mode: "cors",
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
  };

  return await fetch(`/api/comment/${comment_id}/resolve`, headers)
  .then(response => response.json())

}

/**
* @param {number} snap_id The snpashot id number for the snapshot which the comments are being requested from
* @returns {[comments]} The list of comments on the given snapshot
*/
export async function getCommentsOnSnapshot(snap_id) {
  
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  };

  return await fetch(`/api/Snapshot/${snap_id}/comments/get`, headers)
    .then(response => response.json())
    .then(data => data.body)
    .catch(error => {
      console.log(error)
    })

}

/**
* @param {number} doc_id The document id number for the document which the comments are being requested from
* @returns {[comments]} The list of comments on the given document, accross all snapshots
*/
export async function getAllCommentsForDocument(doc_id) {

  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  };

  return await fetch(`/api/Document/${doc_id}/comments/`, headers)
    .then(response => response.json())
    .then(data => data.body)
    .catch(error => {
      console.log(error)
    })

}

/**
* @param {number} comment_id The comment id number for which the subcomments are being requested
* @returns {[comments]} The list of subcomments on the given comment
*/
export async function getSubcommentsOnComment(comment_id) {
  
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  };

  return await fetch(`/api/comments/${comment_id}/subcomments/get`, headers)
    .then(response => response.json())
}

/**
* @param {number} comment_id The comment id number for which the subcomments are being requested
* @param {string} content The content of the updated comment
* @returns {string} The server response message
*/
export async function editComment(comment_id, content) {
  
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "PUT",
    mode: "cors",
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "content": content
    })
  };

  return await fetch(`/api/comments/${comment_id}/edit`, headers)
    .then(response => response.json())

}

/**
* @param {number} comment_id The comment id number for the comment which is being deleted
* @returns {string} The server response message
*/
export async function deleteComment(comment_id) {
  
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "DELETE",
    mode: "cors",
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  };
  
  return await fetch(`/api/comments/${comment_id}/delete`, headers)
    .then(response => response.json())

}

/**
* @param {number} proj_id The project id number for the project which the document is in
* @param {number} doc_id The document id number for the document
* @returns {[(snapshot, commit)]} A list of (snapshot, commit) pairs
*/
export async function getAllSnapshotsFromDocument(proj_id, doc_id) {

  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },

  };

    return await fetch((`/api/Document/${proj_id}/${doc_id}/getSnapshotIdAndWorking/`), headers)
      .then(response => response.json())
  
}

/**
* @returns {[project]} A list of projects which the user has access to
*/
export async function getUserProjects() {

  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },

  };

  return await fetch((`/api/User/Project/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data.body
  })

}

/**
* @param {number} proj_id The project id number for the info which is being requested
* @returns {project} The project info
*/
export async function getProjectInfo(proj_id) {

  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },

  };

  return await fetch((`/api/Project/${proj_id}/`), headers)
  .then(response => response.json()
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data.body
  }))

}

/**
* @param {number} commit_id The commit_id number for the commit which the folder tree is needed
* @returns {JSON} The folder tree for the desired commit
*/
export async function getFolderTree(commit_id) {

  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
  };

  return await fetch((`/api/Commit/${commit_id}/getFolderTree/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data
  })

}

export async function createFolder(folder_name, proj_id, commit_id, parent_folder_id) {

  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "POST",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "folder_name" : folder_name,
      "parent_folder" : parent_folder_id,
    }),
  };

  return await fetch((`/api/Folder/${proj_id}/${commit_id}/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data
  })
}

export async function deleteFolder(folder_id, commit_id) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "DELETE",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  }
  return await fetch((`/api/Folder/${folder_id}/${commit_id}/`), headers)
    .then(response => response.json())
}

export async function  getFolderInfo(proj_id, commit_id, folder_id) {
  let oAuthToken = getCookie("cr_id_token")
  
  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  }

  return await fetch((`/api/Folder/${proj_id}/${folder_id}/${commit_id}/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data.body
  })
}

/**
 * @param {string} code The entire code in the document/snapshot
 * @param {string} highlightedCode A substring of the code that will be changed
 * @param {number} startLine Starting line # of highlighted code
 * @param {number} endLine Ending line # of highlighted code
 * @param {string} comment A suggestion on what to do with the highlighted code
 * @param {string} language The coding language used
 * @returns {string} The code implementation based on the suggestion
*/
export async function getCodeImplementation(code, highlightedCode, startLine, endLine, comment, language) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "POST",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "code": code,
      "highlightedCode": highlightedCode,
      "startLine": startLine,
      "endLine": endLine,
      "comment": comment,
      "language": language
    })
  };

  return await fetch((`/api/llm/code-implementation`), headers)
  .then(response => response.json())
  .then(data => {
    console.log(data)
    if (data.success === false) {
      console.log("FAILED" + data.reason)
      return highlightedCode
    }

    return data.body
  });

}

export async function addGitHubToken(token) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "POST",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "github_code" : token,
    })
  };

  return await fetch((`/api/Github/addToken`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data
  })
}

export async function hasGitHubToken() {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
  };

  return await fetch((`/api/Github/userHasGithub/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data
  })
}

export async function pullFromGitHub(proj_name, repo_name, branch_name) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "POST",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "repository" : repo_name,
      "branch" : branch_name,
      "project_name" : proj_name,
    })
  };

  return await fetch((`/api/Github/PullToNewProject/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data
  })
}

export async function pushToExistingBranch(proj_id, repo_name, branch_name, commit_id, message) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "POST",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "repository" : repo_name,
      "branch" : branch_name,
      "message" : message,
    })
  };

  return await fetch((`/api/Github/${proj_id}/${commit_id}/PushToExisting/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data
  })
}

export async function getCommits(proj_id) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
  };

  return await fetch((`/api/Project/${proj_id}/GetCommits/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data
  })
}

export async function createCommit(proj_id, commit_id) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "POST",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "last_commit" : commit_id,
    })
  };

  return await fetch((`/api/Commit/${proj_id}/createCommit/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data
  })
}

export async function deleteCommit(proj_id) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "DELETE",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  };

  return await fetch((`/api/Commit/${proj_id}/workingCommit/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data
  })
}

export async function submitCommit(commit_id, commit_name) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "POST",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }, 
    body: JSON.stringify({
      name: commit_name
    })
  };

  return await fetch((`/api/Commit/${commit_id}/commitCommit/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
    }
    return data
  })
}

export async function getLatestCommitForProject(project_id) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  };

  return await fetch((`/api/Project/${project_id}/GetLatestCommit/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
      return null
    }
    return data.body
  })
}

export async function approveCommit(commit_id) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  };

  return await fetch((`/api/Commit/${commit_id}/approve/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false)
      console.log("FAILED" + data.reason)

    return data.success
  })
}

export async function setCommitReviewed(commit_id) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  };

  return await fetch((`/api/Commit/${commit_id}/setReviewed/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false)
      console.log("FAILED" + data.reason)

    return data.success
  })
}
export async function setCommitClosed(commit_id) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  };

  return await fetch((`/api/Commit/${commit_id}/close/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false)
      console.log("FAILED" + data.reason)

    return data.success
  })
}

export async function getAllProjectActiveCommentsForLatestCommit(project_id) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  };


  return await fetch((`/api/Commit/${project_id}/getLatestComments/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
      return null
    }

    return data.body
  })
}

export async function getCommitData(commit_id) {
  let oAuthToken = getCookie("cr_id_token")

  let headers = {
    method: "GET",
    mode: "cors",
    withCredentials: true,
    credentials: 'include',
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  };

  return await fetch((`/api/Commit/${commit_id}/info/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false){
      console.log("FAILED" + data.reason)
      return null
    }

    return data.info
  })
}