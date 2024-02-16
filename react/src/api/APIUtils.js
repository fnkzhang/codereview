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