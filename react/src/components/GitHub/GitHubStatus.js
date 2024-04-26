import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { hasGitHubToken } from "../../api/APIUtils";

export default function GitHubStatus () {
  const [loading, setLoading] = useState(true)
  const [connected, setConnected] = useState(false)
  const GitHub_Client_ID = "5a5dc22f1c77bd1ee081"
  const navigate = useNavigate()

  useEffect( () => {
    async function checkToken() {
      let result = await hasGitHubToken()

      console.log(result)
      if (result.body === true) {
        setConnected(true)
      }
    }

    async function sendData() {
      try {
        await Promise.all([
          checkToken()
        ])
      } catch (error) {
        console.log(error)
      } finally {
        setLoading(false)
      }
    }

    if (loading) {
      sendData()
    }
  })

  if (loading) {
    return(<div>
      Loading...
    </div>)
  }

  if (connected) {
    return(<div>
      Connected to GitHub
    </div>)
  }

  return(<a
    href={`https://github.com/login/oauth/authorize?client_id=${GitHub_Client_ID}&scope=repo`} target="_blank" rel="noopener noreferrer">Connect to GitHub
  </a>)
}