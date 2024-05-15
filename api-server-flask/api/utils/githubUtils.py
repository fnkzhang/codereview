from github import Github, InputGitTreeElement
from github import Auth

import json

from utils.projectUtils import *
from utils.documentUtils import *
from utils.snapshotUtils import *
from utils.commentUtils import *


creds = open('credentials/github_oath_credentials.json')
creds = json.load(creds)
github_client_id = creds["client-id"]
github_client_secret = creds["client-secret"]

g = Github()
gapp = g.get_oauth_application(github_client_id, github_client_secret)

#repository = "user/reponame", aka just github style
def getBranches(token, repository):
    try:
        auth = Auth.Token(token)
        g2 = Github(auth=auth)

        repo = g2.get_repo(repository)
        branches = list(repo.get_branches())
        branchnames = []
        for branch in branches:
            branchnames.append(branch.name)
        return True, branchnames
    except Exception as e:
        return False, e

def getGithubProjectDocumentsAsPaths(repo, branch, token):
    g2 = Github(auth = Auth.Token(token))
    repo = g2.get_repo(repo)
    try:
        contents = repo.get_contents("", branch)
    except:
        return []
    githubfiles = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            print(file_content.path)
            githubfiles.append(file_content.path)
    return githubfiles

def getProjectNonexistentGithubDocumentsUtil(repo, branch, token, proj_id):
    allGithubFiles = set(getGithubProjectDocumentsAsPaths(repo, branch, token))
    projectDocuments = getAllProjectDocuments(proj_id)
    projectDocumentPaths = set([getFolderPath(document['parent_folder']) + document['name'] for document in projectDocuments])
    nonexistant = list(allGithubFiles - projectDocumentPaths)
    return nonexistant

def assembleGithubTreeElements(repo, folderIDToPath, deletedDocumentPaths, snapshotIDs):
    tree_elements = []
    for deletedDocumentPath in deletedDocumentPaths:
        tree_elements.append(InputGitTreeElement(path = deletedDocumentPath,
                mode = "100644",
                type = "blob",
                sha = None
            ))
    for snapshotID in snapshotIDs:
        snapshot = getSnapshotInfo(snapshotID)
        document = getDocumentInfo(snapshot["associated_document_id"])
        blob = repo.create_git_blob(
                content = getSnapshotContentUtil(snapshotID),
                encoding = 'utf-8',
                )
        tree_elements.append(InputGitTreeElement(path = folderIDToPath[document["parent_folder"]] + document["name"],
                mode = "100644",
                type = "blob",
                sha = blob.sha
            ))
    return tree_elements

def assembleGithubComments(snapshotIDs):
    githubComments = []
    for snapshotID in snapshotIDs:
        doc_id = getSnapshotInfo(snapshotID)["associated_document_id"]
        documentPath = getFolderPath(document['parent_folder']) + document['name']
        commentList = filterCommentsByPredicate(models.Comment.snapshot_id == snapshotID )
        for comment in commentList:
            if comment["is_resolved"] == False:
                githubComments.append("Comment From CodeReview\nComment Author:" + comment["author_email"] + "\nDocument:"+documentPath + '\nLine ' + str(comment["highlight_start_y"]) + ' to Line ' + str(comment["highlight_end_y"])+ '\n'+ str(comment["content"]))
    return githubComments

