import React from "react";
import { Dropdown } from "flowbite-react";

export default function CommitDropdown( props ) {
  console.log(props)
  if(props.commits.length !== 0) {
    return (
      <Dropdown 
        className= "bg-background m-1" label={`${props.commit.name}`}>
        {props.commits.map((commit, index) => { 
          return (
            <Dropdown.Item 
              key={index}
              onClick={() => props.setCommit(commit)}
            >
              <div className="text-textcolor m-1">
                {commit.name}
              </div>
            </Dropdown.Item>
          )
        })}
      </Dropdown>
    )
  }

  return
}