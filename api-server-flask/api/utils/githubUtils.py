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
    """
    **Explanation:**
        Gets a repository's branches if the token has access

    **Args:**
        - token (int): A user's github token from the Oauth app
        - repository (str): name of repository, includes owner name

    **Returns:**
        branches (list): list of branch names of the repository as strings
    """
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

def getGithubProjectDocumentsAsPaths(repository, branch, token):
    """
    **Explanation:**
        Gets all of the repository's documents as paths from a specific branch

    **Args:**
        - repository (str): name of repository, includes owner name
        - branch (str): name of the branch
        - token (int): A user's github token from the Oauth app

    **Returns:**
        githubFiles (list): list of document paths as strings
    """
    g2 = Github(auth = Auth.Token(token))
    repo = g2.get_repo(repository)
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

def getCommitNonexistentGithubDocumentsUtil(repository, branch, token, commit_id):
    """
    **Explanation:**
        Gets all of the repository's documents from a specific branch that do not exist in the given commit as paths

    **Args:**
        - repository (str): name of repository, includes owner name
        - branch (str): name of the branch
        - token (int): A user's github token from the Oauth app
        - commit_id (int): id of the commit you're comparing to

    **Returns:**
        nonexistant (list): list of documents paths that do not exist in the commit as strings
    """
    allGithubFiles = set(getGithubProjectDocumentsAsPaths(repository, branch, token))
    commitDocuments = getAllCommitItemsOfType(commit_id, False)
    projectDocumentPaths = set([getFolderPath(document['parent_folder'], commit_id) + document['name'] for document in commitDocuments])
    nonexistant = list(allGithubFiles - projectDocumentPaths)
    return nonexistant

import base64
def addTreeElement(tree_elements, doc_id, commit_id, repo, documentSnapshots, folderIDToPath):
    """
    **Explanation:**
        Creates a git blob for the given repo and adds it to the tree_elements list
    **Args:**
        - tree_elements (list): List you're adding an element to
        - doc_id (int): id of the document you're adding
        - commit_id (int): id of the commit this is taking place in
        - repo (Repository): Repository object https://pygithub.readthedocs.io/en/stable/github_objects/Repository.html
        - documentSnapshots (dict): Keys of document ids that map to their respective snapshot ids in the commit
        - folderIDToPath (dict): dict of folder ids mapping to their paths
    """
    document = getDocumentInfo(doc_id, commit_id)
    snapcontent = getSnapshotContentUtil(documentSnapshots[doc_id])
    blob = repo.create_git_blob(
        content = base64.b64encode(snapcontent).decode(),
        encoding = 'base64',
        )
    tree_elements.append(InputGitTreeElement(path = folderIDToPath[document["parent_folder"]] + document["name"],
            mode = "100644",
            type = "blob",
            sha = blob.sha
        ))
    
def assembleGithubTreeElements(repo, folderIDToPath, deletedDocumentPaths, documentSnapshots, commit_id):
    """
    **Explanation:**
        Creates a list of tree elements for the given repo, includes deletions and existing files
    **Args:**
        - repo (Repository): Repository object https://pygithub.readthedocs.io/en/stable/github_objects/Repository.html
        - deletedDocumentPaths (list): List of document paths that should be deleted from the github
        - documentSnapshots (dict): Keys of document ids that map to their respective snapshot ids in the commit
        - folderIDToPath (dict): dict of folder ids mapping to their paths
        - commit_id (int): id of the commit you're grabbing from

    **Returns:**
        tree_elements (list): list of InputGitTreeElements https://pygithub.readthedocs.io/en/stable/utilities.html
    """
    tree_elements = []
    for deletedDocumentPath in deletedDocumentPaths:
        tree_elements.append(InputGitTreeElement(path = deletedDocumentPath,
                mode = "100644",
                type = "blob",
                sha = None
            ))
    threads = []
    for doc_id in documentSnapshots.keys():
        thread = threading.Thread(target=addTreeElement, kwargs={"tree_elements":tree_elements, "doc_id": doc_id, "commit_id":commit_id, "repo":repo, "documentSnapshots":documentSnapshots, "folderIDToPath":folderIDToPath})
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    return tree_elements

def assembleGithubComments(documentSnapshots, commit_id):
    """
    **Explanation:**
        Creates a list of comments to Comment for a commit, includes all comments on all snapshots on a commit
    **Args:**
        - documentSnapshots (dict): Keys of document ids that map to their respective snapshot ids in the commit
        - commit_id (int): id of the commit you're grabbing from

    **Returns:**
        githubComments (list): list of comments to make on Github
    """
    githubComments = []
    for doc_id in documentSnapshots.keys():
        document = getDocumentInfo(doc_id, commit_id)
        documentPath = getFolderPath(document['parent_folder'], commit_id) + document['name']
        commentList = filterCommentsByPredicate(models.Comment.snapshot_id == documentSnapshots[doc_id] )
        for comment in commentList:
            if comment["is_resolved"] == False:
                githubComments.append("Comment From CodeReview\nComment Author: " + comment["author_email"] + "\nDocument: "+documentPath + '\nLine ' + str(comment["highlight_start_y"]) + ' to Line ' + str(comment["highlight_end_y"])+ '\n'+ str(comment["content"]))
    return githubComments

