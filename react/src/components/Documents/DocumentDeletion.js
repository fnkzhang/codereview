import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router";
import LoadingSpinner from "../Loading/LoadingSpinner.js";
import { Button, Label, TextInput } from "flowbite-react";
import { deleteDocument, getDocumentInfo } from "../../api/APIUtils";
import BackButton from "../BackButton.js";

export default function DcoumentDeletion(props) {
    const [documentName, setDocumentName] = useState("");
    const [inputDocumentName, setInputDocumentName] = useState("");
    const [isError, setIsError] = useState(false);
    const [working, setWorking] = useState(false);
    const { project_id, document_id } = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        async function getDocumentData() {
            let result = await getDocumentInfo(document_id)
            setDocumentName(result.name)
        }

        getDocumentData()
    }, [project_id, document_id])

    const handleDeleteDocumentButtonClick = async (e) => {
        e.preventDefault() // Prevent form submission

        setWorking(true)

        if (inputDocumentName === "") {
            setWorking(false)
            return
        }

        if (inputDocumentName !== documentName) {
            alert("Input Does Not Match Document Name")
            setWorking(false)
            return
        }

        let result = await deleteDocument(document_id)

        if (result.success) {
            navigate("/") // Go Home
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
                <BackButton />
            </div>
            <div className="flex justify-center mt-20">
                <form
                    className="flex max-w-lg flex-1 flex-col gap-4 text-textcolor bg-altBackground p-20 pt-10 rounded"
                    onSubmit={handleDeleteDocumentButtonClick}
                >
                    <div>
                        <div className="mb-3 block">
                            <Label className="text-2xl" value="Are you sure you want to delete this document?" />
                        </div>

                        <div className="mb-3 block">
                            <Label className="text-2xl">
                                Please type <strong className="text-red-500">{projectName}</strong> into the text field.
                            </Label>
                        </div>
                        <TextInput
                            className="text-black shadow-white"
                            placeholder="Name of Project"
                            sizing="lg"
                            onChange={(e) => setInputDocumentName(e.target.value)}
                            shadow
                            required
                        />
                    </div>

                    {isError ? (
                        <p className="text-red-600 text-xl">Error: Could Not Delete Document</p>
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