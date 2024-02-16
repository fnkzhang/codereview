import getCookie from "../utils/utils"

export async function sendData(bodyType, bodyContents) {

  let credentialToken = getCookie("cr_id_token")
  let bodyData = {
    "credential": credentialToken,
    [bodyType]: bodyContents
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