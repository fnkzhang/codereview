import React, { useState } from "react";
import { useNavigate, useParams } from "react-router";
import LoadingSpinner from "../Loading/LoadingSpinner.js";
import { Button, Label, TextInput } from "flowbite-react";
import { deleteCommit } from "../../api/APIUtils";
import BackButton from "../BackButton.js";

export default function CommitDeletion(props) {
    const commitName = "User Working Commit" // Actual Commit Name to compare
    const [inputCommitName, setInputCommitName] = useState(""); // Handle Input for commit name
    const [isError, setIsError] = useState(false);
    const [working, setWorking] = useState(false);
    const { project_id, commit_id } = useParams();
    const navigate = useNavigate();

    const handleDeleteCommitButtonClick = async (e) => {
        e.preventDefault() // Prevent form submission

        setWorking(true)

        if (inputCommitName === "") {
            setWorking(false)
            return
        }

        if (inputCommitName !== commitName) {
            alert("Input Does Not Match Commit Name")
            setWorking(false)
            return
        }

        let result = await deleteCommit(project_id)

        if (result.success) {
            navigate(`/Project/${project_id}/Commit/0`) // Go back to project view
        } else {
            setWorking(false)
            setIsError(true)
        }
    };

    if (props.isLoggedIn === false) {
        return (
            <div>
                <div className="m-20 text-center text-textcolor text-2xl">
                    You must Log in to view this page.
                </div>
            </div>
        );
    }

    return (
        <div>
            <div>
                <BackButton
                    location={`/Project/${project_id}/Commit/${commit_id}`}
                />
            </div>
            <div className="flex justify-center mt-20">
                <form
                    className="flex max-w-lg flex-1 flex-col gap-4 text-textcolor bg-altBackground p-20 pt-10 rounded"
                    onSubmit={handleDeleteCommitButtonClick}
                >
                    <div>
                        <div className="mb-3 block">
                            <Label className="text-2xl" value="Are you sure you want to delete your working commit?" />
                        </div>

                        <div className="mb-3 block">
                            <Label className="text-2xl">
                                Please type <strong className="text-red-500">{commitName}</strong> into the text field.
                            </Label>
                        </div>
                        <TextInput
                            className="text-black shadow-white"
                            placeholder="Name of Commit"
                            sizing="lg"
                            onChange={(e) => setInputCommitName(e.target.value)}
                            shadow
                            required
                        />
                    </div>

                    {isError ? (
                        <p className="text-red-600 text-xl">Error: Could Not Delete Commit</p>
                    ) : null}
                    <Button type="submit" className="bg-alternative transition-colors duration-200 hover:bg-red-800/75">
                        Delete
                    </Button>

                    <div className="flex justify-center">
                        <LoadingSpinner active={working} />
                    </div>
                </form>
            </div>
        </div>
    )
}