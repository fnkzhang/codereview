export async function sendData(bodyType, bodyContents) {

  let bodyData = {
    [bodyType]: bodyContents
  }
  let headers = {
    method: "POST",
    mode: "cors",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(bodyData)
  }

  return await fetch(`/sendData`, headers)
    .then(response => response.json())
}