import React from "react";
import { Dropdown } from "flowbite-react";

export default function CommitDropdown( props ) {
  if(props.commits.length !== 0) {
    return (
      <Dropdown 
        className= "bg-background m-1" label={`${props.commit.name}`}>
        {props.commits.map((commit, index) => { 
          return (
            <Dropdown.Item 
              className="hover:bg-alternative"
              key={index}
              onClick={() => {
                props.setCommit(commit)
                if (props.setCommitLoading)
                  props.setCommitLoading(true)
              }}
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