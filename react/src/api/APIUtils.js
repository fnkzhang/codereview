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

export async function getAllSnapshotsFromDocument(document_id) {
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

    return await fetch((`/api/Document/0/${document_id}/getSnapshotId/`), headers)
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
  .then(response => response.json()
  .then(data => {
    console.log(data)
    if (data.success === false) {
      console.log("FAILED" + data.reason)
      return data.body
    }

    return data.body
}))
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
    console.log(data)
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
    console.log(data)
    if (data.success === false) {
      console.log("FAILED" + data.reason)
      return data.body
    }

    return data.body
  })
}