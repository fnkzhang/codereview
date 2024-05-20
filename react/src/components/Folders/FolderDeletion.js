import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router";
import LoadingSpinner from "../Loading/LoadingSpinner.js";
import { Button, Label, TextInput } from "flowbite-react";
import { deleteFolder, getFolderInfo } from "../../api/APIUtils";
import BackButton from "../BackButton.js";

export default function FolderDeletion(props) {
    const [FolderName, setFolderName] = useState("");
    const [inputFolderName, setInputFolderName] = useState("");
    const [isError, setIsError] = useState(false);
    const [working, setWorking] = useState(false);
    const { project_id, commit_id, folder_id } = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        async function getFolderData() {
            let result = await getFolderInfo(project_id, commit_id, folder_id)
            setFolderName(result.name)
        }

        if (props.isLoggedIn)
            getFolderData()
    }, [project_id, commit_id, folder_id, props.isLoggedIn])

    const handleDeleteFolderButtonClick = async (e) => {
        e.preventDefault() // Prevent form submission

        if (working)
            return

        if (inputFolderName === "") {
            return
        }

        if (inputFolderName !== FolderName) {
            alert("Input Does Not Match Folder Name")
            return
        }

        setWorking(true)

        let result = await deleteFolder(folder_id, commit_id)

        if (result.success) {
            navigate(`/Project/${project_id}/Commit/${commit_id}`)
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
                    onSubmit={handleDeleteFolderButtonClick}
                >
                    <div>
                        <div className="mb-3 block">
                            <Label className="text-2xl" value="Are you sure you want to delete this Folder?" />
                        </div>

                        <div className="mb-3 block">
                            <Label className="text-2xl">
                                Please type <strong className="text-red-500">{FolderName}</strong> into the text field.
                            </Label>
                        </div>
                        <TextInput
                            className="text-black shadow-white"
                            placeholder="Name of Folder"
                            sizing="lg"
                            onChange={(e) => setInputFolderName(e.target.value)}
                            shadow
                            required
                        />
                    </div>

                    {isError ? (
                        <p className="text-red-600 text-xl">Error: Could Not Delete Folder</p>
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