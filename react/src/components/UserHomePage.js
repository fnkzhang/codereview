import ProjectList  from "./Projects/ProjectList";

export default function UserHomePage( props ) {

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