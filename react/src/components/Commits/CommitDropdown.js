import React from "react";
import { Dropdown } from "flowbite-react";
import { truncateString, getColor } from "../../utils/utils";

export default function CommitDropdown( props ) {

  if(props.commits.length !== 0) {
    return (
      <Dropdown 
        className= "bg-background m-1" label={
          <div className="flex max-w-sm text-lg">
            <div className="flex-1 flex-grow w-full flex-col text-textcolor whitespace-nowrap">
              {`${truncateString(props.commit.name)}`}
            </div>
          </div>
        }>
        {props.commits.map((commit, index) => { 
          return (
            <Dropdown.Item 
              className="w-full bg-background hover:bg-alternative"
              key={index}
              onClick={() => {
                props.setCommit(commit)
                if (props.setCommitLoading)
                  props.setCommitLoading(true)
              }}
            >
              <div className="flex text-lg">
                <div className="flex-1 flex-grow flex-col text-textcolor whitespace-nowrap mr-2">
                  {`${truncateString(commit.name)}`}
                </div>
                <div className={"flex-1 " + getColor(commit.state)}>
                  {`*${commit.state.toString().toUpperCase()}`}
                </div>
              </div>
            </Dropdown.Item>
          )
        })}
      </Dropdown>
    )
  }

  return
}