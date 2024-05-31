import React, { useState } from "react";
import { useNavigate, useParams } from "react-router";
import LoadingSpinner from "../Loading/LoadingSpinner.js";
import { Button, Label, TextInput } from "flowbite-react";
import { submitCommit } from "../../api/APIUtils";
import BackButton from "../Buttons/BackButton.js";

export default function CommitSubmission(props) {
    const [commitName, setCommitName] = useState(""); // Handle Input for commit name
    const [isError, setIsError] = useState(false);
    const [working, setWorking] = useState(false);
    const { project_id, commit_id } = useParams();
    const navigate = useNavigate();

    const handleSubmitCommitButtonClick = async (e) => {
        e.preventDefault() // Prevent form submission

        setWorking(true)

        if (commitName === "") {
            setWorking(false)
            return
        }

        let result = await submitCommit(commit_id, commitName)

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
                    onSubmit={handleSubmitCommitButtonClick}
                >
                    <div>
                        <div className="mb-3 block">
                            <Label className="text-2xl" value="Commit Your Working Changes" />
                        </div>

                        <div className="mb-3 block">
                            <Label className="text-2xl">
                                Please provide a name for your commit.
                            </Label>
                        </div>
                        <TextInput
                            className="text-black shadow-white"
                            placeholder="Name of Commit"
                            sizing="lg"
                            onChange={(e) => setCommitName(e.target.value)}
                            shadow
                            required
                        />
                    </div>

                    {isError ? (
                        <p className="text-red-600 text-xl">Error: Could Not Submit Commit</p>
                    ) : null}
                    <Button type="submit" className="bg-alternative transition-colors duration-200 hover:bg-slate-500">
                        Commit
                    </Button>

                    <div className="flex justify-center">
                        <LoadingSpinner active={working} />
                    </div>
                </form>
            </div>
        </div>
    )
}