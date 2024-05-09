import getCookie from "../utils/utils"

export async function sendData(bodyContents) {

  let credentialToken = getCookie("cr_id_token")
  let bodyData = {
    "credential": credentialToken,
    data: bodyContents
  }
  console.log(bodyData)
  let headers = {
    method: "POST",
    mode: "cors",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(bodyData)
  }

  return await fetch(`/api/sendData`, headers)
    .then(response => response.json())
}

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
    }
  }
  return await fetch((`/api/Project/${projectName}/`), headers)
    .then(response => response.json())

}
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

export async function createDocument(documentName, proj_id, documentData, parent_folder_id) {

  let oAuthToken = getCookie("cr_id_token")
  let bodyData = {
    document_name: documentName,
    data: documentData,
    project_id: proj_id,
    parent_folder_id: parent_folder_id
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
  return await fetch((`/api/Document/${proj_id}/`), headers)
    .then(response => response.json())
}

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
export async function createSnapshotForDocument(proj_id, doc_id, snapshot_data) {
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

  // Fail = Null
  // Success = SnapshotID
  return await fetch((`/api/Snapshot/${proj_id}/${doc_id}/`), headers)
    .then(response => response.json())
    .then(data => {
      if (data.success)
        return data.body
      return null
    })
    .catch(error => console.log(error))
}

// snapshot_id: int
// author_email: string
// reply_to_id: int
// content: string
// creates a comment and (temporarily) generates an id between 0 and 2^31 - 1
export async function createComment(snapshot_id, author_email, reply_to_id, content, 
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
      "snapshot_id": snapshot_id,
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

  return await fetch(`/api/Snapshot/${snapshot_id}/comment/create`, headers)
    .then(response => response.json())

}

//
//
//
//
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

// snapshot_id: int
// returns all comments (temporarily including subcomments) that match the snapshot_id
export async function getCommentsOnSnapshot(snapshot_id) {
  
  let oAuthToken = getCookie("cr_id_token")
  let headers = {
    method: "GET",
    mode: "cors",
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  };

  return await fetch(`/api/Snapshot/${snapshot_id}/comments/get`, headers)
    .then(response => response.json())
    .then(data => data.body)
    .catch(error => {
      console.log(error)
    })

}

export async function getAllCommentsForDocument(document_id) {
  let oAuthToken = getCookie("cr_id_token")
  let headers = {
    method: "GET",
    mode: "cors",
    headers: {
      "Authorization": oAuthToken,
      "Content-Type": "application/json"
    }
  };

  return await fetch(`/api/Document/${document_id}/comments/`, headers)
    .then(response => response.json())
    .then(data => data.body)
    .catch(error => {
      console.log(error)
    })
}

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

export async function getAllSnapshotsFromDocument(project_id, document_id) {
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

    return await fetch((`/api/Document/${project_id}/${document_id}/getSnapshotId/`), headers)
      .then(response => response.json())
}

export async function getUserProjects(userEmail) {
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

  return await fetch((`/api/User/${userEmail}/Project/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
      return data.body
    }

    return data.body
  })
}

export async function getProjectInfo(project_id) {
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

  return await fetch((`/api/Project/${project_id}/`), headers)
  .then(response => response.json()
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
      return data.body
    }
    return data.body
  }))

}


export async function getProjectDocuments(proj_id) {
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

  return await fetch((`/api/Document/${proj_id}/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
      return data.body
    }

    return data.body
  })
}

export async function getProjectTree(proj_id) {
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

  return await fetch((`/api/Project/${proj_id}/getFolderTree/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
      return data.body
    }

    return data.body
  })
}

export async function createFolder(folder_name, proj_id, parent_folder_id) {

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

  return await fetch((`/api/Folder/${proj_id}/`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
      return data.body
    }

    return data
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

/**
 * @param {string} code The entire code in the document/snapshot
 * @param {string} language The coding language used
 * @param {number} startLine Starting line # of highlighted code
 * @param {number} endLine Ending line # of highlighted code
 * @param {string} comment A suggestion on what to do with the highlighted code
 * @returns {string} The entire code with the comment suggestion implemented
*/
export async function getCodeImplementation2(code, language, startLine, endLine, comment) {
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
      "language": language,
      "startLine": startLine,
      "endLine": endLine,
      "comment": comment
    })
  };

  return await fetch((`/api/llm/code-implementation`), headers)
  .then(response => response.json())
  .then(data => {
    console.log(data)
    if (data.success === false) {
      console.log("FAILED" + data.reason)
      return code
    }

    return data.body
  });

}

/**
 * @param {string} code The entire code in the document/snapshot
 * @param {string} language The coding language used
 * @returns {object[]} A list of JSON objects that have keys startLine, endLine, and suggestion.
 * startLine: number - line # to begin highlight
 * endLine: number - line # to stop highlight
 * suggestion: string - Suggestion on how to improve the highlighted section of code
*/
export async function getCommentSuggestion(code, language) {
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
      "language": language
    })
  };

  return await fetch((`/api/llm/comment-suggestion`), headers)
  .then(response => response.json())
  .then(data => {
    console.log(data)
    if (data.success === false) {
      console.log("FAILED" + data.reason)
      return []
    }

    return data.body
  })
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
      return data.body
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
      return data.body
    }
    return data
  })
}

export async function pullFromGitHub(proj_id, repo_name, branch_name) {
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
    })
  };

  return await fetch((`/api/Github/Pull/${proj_id}`), headers)
  .then(response => response.json())
  .then(data => {
    if (data.success === false) {
      console.log("FAILED" + data.reason)
      return data.body
    }
    return data
  })
}