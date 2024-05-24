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

def getCommitNonexistentGithubDocumentsUtil(repo, branch, token, commit_id):
    allGithubFiles = set(getGithubProjectDocumentsAsPaths(repo, branch, token))
    commitDocuments = getAllCommitItemsOfType(commit_id, False)
    projectDocumentPaths = set([getFolderPath(document['parent_folder'], commit_id) + document['name'] for document in commitDocuments])
    nonexistant = list(allGithubFiles - projectDocumentPaths)
    return nonexistant

def assembleGithubTreeElements(repo, folderIDToPath, deletedDocumentPaths, documentSnapshots, commit_id):
    tree_elements = []
    for deletedDocumentPath in deletedDocumentPaths:
        tree_elements.append(InputGitTreeElement(path = deletedDocumentPath,
                mode = "100644",
                type = "blob",
                sha = None
            ))
    print(documentSnapshots)
    for doc_id in documentSnapshots.keys():
        document = getDocumentInfo(doc_id, commit_id)
        blob = repo.create_git_blob(
                content = getSnapshotContentUtil(documentSnapshots[doc_id]),
                encoding = 'utf-8',
                )
        tree_elements.append(InputGitTreeElement(path = folderIDToPath[document["parent_folder"]] + document["name"],
                mode = "100644",
                type = "blob",
                sha = blob.sha
            ))
    return tree_elements

def assembleGithubComments(documentSnapshots, commit_id):
    githubComments = []
    for doc_id in documentSnapshots.keys():
        document = getDocumentInfo(doc_id, commit_id)
        documentPath = getFolderPath(document['parent_folder'], commit_id) + document['name']
        commentList = filterCommentsByPredicate(models.Comment.snapshot_id == documentSnapshots[doc_id] )
        for comment in commentList:
            if comment["is_resolved"] == False:
                githubComments.append("Comment From CodeReview\nComment Author:" + comment["author_email"] + "\nDocument:"+documentPath + '\nLine ' + str(comment["highlight_start_y"]) + ' to Line ' + str(comment["highlight_end_y"])+ '\n'+ str(comment["content"]))
    return githubComments

