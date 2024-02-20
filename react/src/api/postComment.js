export async function postComment(OAuthToken, diffID, authorID, replyToID, message) {
  let headers = {
    method: "POST",
    mode: "cors",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "credentials": OAuthToken,
      "diff_id": diffID,
      "author_id": authorID,
      "reply_to_id": replyToID,
      "content": message
    })
  };

  return await fetch(`/api/comment`, headers)
    .then(response => response.json())
    .then(data => {
      if (!data.success) {
        console.error("Error: ", data.reason);
      }
    })
}
