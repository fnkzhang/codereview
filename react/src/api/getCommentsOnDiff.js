export async function getCommentsOnDiffID(OAuthToken, diffID) {
  let headers = {
    method: "GET",
    mode: "cors",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "credentials": OAuthToken,
      "diff_id": diffID
    })
  };

  return await fetch(`/api/comment`, headers)
    .then(response => response.json())
    .then(data => {
      if (!data.success) {
        console.error("Error: ", data.reason);
      }

      return data.body // array of comments attached to diff
    })
}
