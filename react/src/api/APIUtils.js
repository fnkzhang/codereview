export async function sendData(bodyContents) {

  let bodyData = {
    data: bodyContents
  }
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

export async function createDoc(bodyContents, proj_id, doc_id) {

  let bodyData = {
    data: bodyContents
  }
  let headers = {
    method: "POST",
    mode: "cors",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(bodyData)
  }
  return await fetch((`/api/Document/`).concat(proj_id).concat('/').concat(doc_id).concat('/create'), headers)
    .then(response => response.json())
}

export async function getDoc(proj_id, doc_id) {

  let headers = {
    method: "GET",
    mode: "cors",
    headers: {
      "Content-Type": "application/json"
    }
  }

  return await fetch((`/api/Document/`).concat(proj_id).concat('/').concat(doc_id).concat('/get'), headers)
    .then(response => response.json())
}

export async function createDiff(proj_id, doc_id, diff_id, originalCode, updatedCode) {

  let bodyData = {
    original: originalCode,
    updated: updatedCode
  }
  let headers = {
    method: "POST",
    mode: "cors",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(bodyData)
  }

  return await fetch((`/api/Document/`).concat(proj_id).concat('/').concat(doc_id).concat('/')
    .concat(diff_id).concat('/create'), headers)
    .then(response => response.json())
}

export async function getDiff(proj_id, doc_id, diff_id) {

  let headers = {
    method: "GET",
    mode: "cors",
    headers: {
      "Content-Type": "application/json"
    }
  }

  return await fetch((`/api/Document/`).concat(proj_id).concat('/').concat(doc_id).concat('/')
    .concat(diff_id).concat('/get'), headers)
    .then(response => response.json())
}

export async function createComment(diff_id, author_id, reply_to_id, content) {
  let oAuthToken = "fake oauth token"
  let headers = {
    method: "POST",
    mode: "cors",
    headers: {
      "Authorization": `Bearer ${oAuthToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "diff_id": diff_id,
      "author_id": author_id,
      "reply_to_id": reply_to_id,
      "content": content
    })
  };

  return await fetch(`/api/diffs/${diff_id}/comment/create`, headers)
    .then(response => response.json())
}

export async function getCommentsOnDiff(diff_id) {
  let oAuthToken = "fake oauth token"
  let headers = {
    method: "GET",
    mode: "cors",
    headers: {
      "Authorization": `Bearer ${oAuthToken}`,
      "Content-Type": "application/json"
    }
  };

  return await fetch(`/api/diffs/${diff_id}/comments/get`, headers)
    .then(response => response.json())
}

export async function getSubcommentsOnComment(comment_id) {
  let oAuthToken = "fake oauth token"
  let headers = {
    method: "GET",
    mode: "cors",
    headers: {
      "Authorization": `Bearer ${oAuthToken}`,
      "Content-Type": "application/json"
    }
  };

  return await fetch(`/api/comments/${comment_id}/subcomments/get`, headers)
    .then(response => response.json())
}

export async function editComment(comment_id) {
  let oAuthToken = "fake oauth token"
  let headers = {
    method: "PUT",
    mode: "cors",
    headers: {
      "Authorization": `Bearer ${oAuthToken}`,
      "Content-Type": "application/json"
    }
  };

  return await fetch(`/api/comments/${comment_id}/edit`, headers)
    .then(response => response.json())
}

export async function deleteComment(comment_id) {
  let oAuthToken = "fake oauth token"
  let headers = {
    method: "DELETE",
    mode: "cors",
    headers: {
      "Authorization": `Bearer ${oAuthToken}`,
      "Content-Type": "application/json"
    }
  };

  return await fetch(`/api/comments/${comment_id}/delete`, headers)
    .then(response => response.json())
}
