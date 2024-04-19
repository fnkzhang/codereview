import ProjectList  from "./Projects/ProjectList";

export default function UserHomePage( props ) {

  console.log(props.isLoggedIn)
  console.log(props.userData)

  if (props.isLoggedIn) {
    return (
      <div>          
        <div className="m-5">
          <ProjectList
            isLoggedIn={props.isLoggedIn}
            userData={props.userData}
          />
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="m-20 text-center text-textcolor text-2xl">
        You must Log in to view this page.
      </div>
    </div>
  )
}