from app import get_app
app = get_app(__name__)

from flask import request, jsonify

from cloudSql import *

from utils.githubUtils import *
from utils.userAndPermissionsUtils import *
from utils.projectUtils import *
from utils.folderUtils import *
from utils.documentUtils import *
from utils.snapshotUtils import *
from utils.commentUtils import *
import models
import threading
#checks whether authenticated user has github connected
@app.route('/api/Github/userHasGithub/', methods = ["GET"])
def getUserGithubStatus():
    """
    ``GET /api/Github/userHasGithub/``

    **Explanation:**
        Checks if user has github connected

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (bool): Indicates whether the user has a GitHub account associated.

    """
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
                "success":False,
                "reason": "Invalid Token Provided"
        }

    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
    user = getUserInfo(idInfo["email"])
    if user == None:
        return {"success":False, "reason":"User does not exist"}
    try:
        g2 = Github(auth = Auth.Token(user["github_token"]))
        g2.get_user().login
        return {"success:":True, "reason":"", "body": user["github_token"] != None}
    except Exception as e:
        print(e)
        return {"success:":True, "reason":"", "body":False}

#needs auth because everything does lmao
#put code in the body in "github_code"
@app.route('/api/Github/addToken', methods=["POST"])
def addGithubToken():
    """
    ``POST /api/Github/addToken``

    **Explanation:**
        This endpoint adds a GitHub token to the user's account.
        It requires authentication via an Authorization token header.

    **Args:**
        - request.body (dict):
            - github_code (str): code

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.

    """
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
                "success":False,
                "reason": "Invalid Token Provided"
        }

    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }

    body = request.get_json()
    code = body["github_code"]
    token = gapp.get_access_token(code)
    with engine.connect() as conn:
        stmt = update(models.User).where(models.User.user_email == idInfo["email"]).values(github_token = token.token)
        conn.execute(stmt)
        conn.commit()
    return {"success":True,
            "reason": "",
        }

#needs auth because everything does lmao
#needs parameter, ex ..../getRepositoryBranches/?repository=fnkzhang/codereview
@app.route('/api/Github/getRepositoryBranches/', methods=["GET"])
def getGithubRepositoryBranches():
    """
    ``GET /api/Github/getRepositoryBranches/``

    **Explanation:**
        Gets a repository's branches if the user has access

    **Args:**
        - request.body (dict):
            - repository (str): name of repository, includes owner name

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (list): A list of strings representing the branches of the repository.

    """
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
                "success":False,
                "reason": "Invalid Token Provided"
        }

    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
    repository = request.args.get("repository")
    token = getUserInfo(idInfo["email"])["github_token"]
    success, rv = getBranches(token, repository)#body["repository"])
    if (not success):
        return {"success":False,
                "reason": str(rv)
                }
    return {"success":True,
            "reason": "",
            "body": rv
        }
import time

#format -> repository = "fnkzhang/codereview", branch = "main"
@app.route('/api/Github/PullToNewProject/', methods=["POST"])
def pullToNewProject():
    start = time.time()

    """
    ``POST /api/Github/PullToNewProject/``

    **Explanation:**
        Pulls a github repo's contents to a new project. Will not pull files that have content that cannot be decoded.
        The project's first commit will be the github repo's contents

    **Args:**
        - request.body:
            - repository (str): repository you're pulling from
            - branch (str): the branch you're pulling from

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (str): Identifier of the newly created project if successful.

    """
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
                "success":False,
                "reason": "Invalid Token Provided"
        }

    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
        #
    body = request.get_json()
    user = getUserInfo(idInfo["email"])
    permstime = time.time()
    success, rv = getBranches(user["github_token"], body["repository"])
    if (not success):
        return {"success":False,
                "reason": str(rv)}
    if body["branch"] not in rv:
        return {"success":False,
                "reason": "branch does not exist"}
    branchtime = time.time()
    proj_id = createNewProject(body["project_name"], idInfo["email"])
    projectcreation = time.time()
    commit_id = createNewCommit(proj_id, idInfo["email"], None)
    commitcreation = time.time()
    g2 = Github(auth = Auth.Token(user["github_token"]))
    repo = g2.get_repo(body["repository"])
    getrepo = time.time()
    commit = getCommitInfo(commit_id)
    pathToFolderID = {}
    pathToFolderID[""] = commit["root_folder"]
    getpaths = time.time()
    contents = repo.get_contents("", body["branch"])
    threads = []
    while contents:
        file_content = contents.pop(0)
        index = file_content.path.rfind('/')
        if index < 0:
            path = ""
        else:
            path = file_content.path[:index]
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
            folder_id = createNewFolder(file_content.name, pathToFolderID[path], proj_id, commit_id)
            pathToFolderID[file_content.path] = folder_id
        else:
            try:
                thread = threading.Thread(target=createNewDocument, kwargs = {'document_name':file_content.name, 'parent_folder':pathToFolderID[path], 'proj_id':proj_id, 'data': file_content.decoded_content, 'commit_id':commit_id, 'user_email':idInfo["email"]})
                thread.start()
                threads.append(thread)
                #doc_id = createNewDocument(file_content.name, pathToFolderID[path], proj_id, file_content.decoded_content, commit_id, idInfo["email"])
            except Exception as e:
                pass
    commitstart = time.time()
    print(commitstart-getpaths)
    commitACommit(commit_id, "Pulled from branch " + body["branch"] + " of " + body["repository"])
    commiting = time.time()
    for thread in threads:
        thread.join()
    createdocs = time.time()
    print("persm", permstime-start, "branch", branchtime-permstime,"projc", projectcreation-permstime, "commitc", commitcreation-projectcreation, "getrepo", getrepo-commitcreation, "getpaths", getpaths-getrepo, "commit", commiting-commitstart, "createdocs", createdocs-getpaths)
    return {"success":True, "reason":"", "body":proj_id}

#needs auth
#put repository path in "repository" and branch in "branch"
#format -> repository = "fnkzhang/codereview", branch = "main"
#put commit name in "name"
@app.route('/api/Github/<proj_id>/PullToExistingProject/', methods=["POST"])
def pullToExistingProject(proj_id):
    """
    TODO: Documentation
    
    ``<POST/GET/UPDATE/DELETE> /api``

    **Explanation:**
        <insert_explanation_here>

    **Args:**
        - route_params (<param_type>): description
        - request.body (dict):
            - body_params (<param_type>): description

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): description
            - reason (str): description
            - body (<body_type>): <body_contents>

    """
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
                "success":False,
                "reason": "Invalid Token Provided"
        }

    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
        #
    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    body = request.get_json()
    user = getUserInfo(idInfo["email"])
    success, rv = getBranches(user["github_token"], body["repository"])
    if (not success):
        return {"success":False,
                "reason": str(rv)}
    if body["branch"] not in rv:
        return {"success":False,
                "reason": "branch does not exist"}
    last_commit = getProjectLastCommittedCommit(proj_id)["commit_id"]
    commit_id = createNewCommit(proj_id, idInfo["email"], last_commit)
    g2 = Github(auth = Auth.Token(user["github_token"]))
    repo = g2.get_repo(body["repository"])
    folders = getAllCommitItemsOfType(last_commit, True)
    documents = getAllCommitItemsOfType(last_commit, False)
    pathToFolderID = {}
    commit = getCommitInfo(commit_id)
    pathToFolderID[""] = commit["root_folder"]
    contents = repo.get_contents("", body["branch"])
    updated_files = []
    docs_to_delete = [document['doc_id'] for document in documents]
    print(docs_to_delete)
    folders_to_delete = [folder['folder_id'] for folder in folders]
    folders_to_delete.remove(commit["root_folder"])
    print("____________________________________________________")
    threads = []
    while contents:
        file_content = contents.pop(0)
        index = file_content.path.rfind('/')
        if index < 0:
            path = ""
        else:
            path = file_content.path[:index]
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
            folder = getFolderInfoViaLocation(file_content.name, pathToFolderID[path], last_commit)
            if folder != None:
                folder_id = folder["folder_id"]
                folders_to_delete.remove(folder_id)
            else:
                folder_id = createNewFolder(file_content.name, pathToFolderID[path], proj_id, commit_id)
                updated_files.append(folder_id)
            pathToFolderID[file_content.path] = folder_id
        else:
            document = getDocumentInfoViaLocation(file_content.name, pathToFolderID[path], last_commit)
            try:
                if document != None:
                    doc_id = document["doc_id"]
                    if file_content.decoded_content != getDocumentLastCommittedSnapshotContent(doc_id):
                        #print(file_content.decoded_content)
                        #print("")
                        #print(getDocumentLastCommittedSnapshotContent(doc_id))
                        #print("____")
                        thread = threading.Thread(target=createNewSnapshot, kwargs = {'proj_id':proj_id, 'doc_id':doc_id, 'data':file_content.decoded_content, 'commit_id':commit_id, 'user_email':idInfo["email"]})
                        thread.start()
                        threads.append(thread)
                        #createNewSnapshot(proj_id, doc_id, file_content.decoded_content, commit_id, idInfo["email"])
                        updated_files.append(doc_id)
                    #print(doc_id)
                    docs_to_delete.remove(doc_id)
                else:
                    thread = threading.Thread(target=createNewDocument, kwargs = {'document_name':file_content.name, 'parent_folder':pathToFolderID[path], 'proj_id':proj_id, 'data': file_content.decoded_content, 'commit_id':commit_id, 'user_email':idInfo["email"]})
                    thread.start()
                    threads.append(thread)
                    #doc_id = createNewDocument(file_content.name, pathToFolderID[path], proj_id, file_content.decoded_content, commit_id, idInfo["email"])
                    #updated_files.append(doc_id)
            except Exception as e:
                print(e)
    for doc_to_delete in docs_to_delete:
        deleteDocumentFromCommit(doc_to_delete, commit_id)
    for folder_to_delete in folders_to_delete:
        deleteFolderFromCommit(folder_to_delete, commit_id)
    print(len(updated_files), len(docs_to_delete), len(folders_to_delete))
    if len(updated_files) > 0 or len(docs_to_delete) > 0 or len(folders_to_delete) > 0:
        print(commit)
        commitACommit(commit_id, body["name"])

    else:
        deleteCommit(commit_id)
    return {"success":True, "reason":"", "body":updated_files}

#put repository including owner name in "repository", ex: billingtonbill12/testrepo
#put branchname in "branch"
#put branch you're building off of into "oldbranch"
#put commit message in "message", or if we eventually put a generic message that's fine
@app.route('/api/Github/<proj_id>/<commit_id>/PushToNewBranch/', methods=["POST"])
def pushToNewBranch(proj_id, commit_id):
    """
    TODO: Documentation
    
    ``<POST/GET/UPDATE/DELETE> /api``

    **Explanation:**
        <insert_explanation_here>

    **Args:**
        - route_params (<param_type>): description
        - request.body (dict):
            - body_params (<param_type>): description

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): description
            - reason (str): description
            - body (<body_type>): <body_contents>

    """
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
                "success":False,
                "reason": "Invalid Token Provided"
        }

    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
        #
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    body = request.get_json()
    user = getUserInfo(idInfo["email"])
    token = user["github_token"]
    g2 = Github(auth = Auth.Token(token))
    success, rv = getBranches(token, body["repository"])
    if (not success):
        return {"success":False,
                "reason": str(rv)}
    if body["oldbranch"] not in rv:
        return {"success":False,
                "reason": "branch getting built off of does not exist"}
    if body["branch"] in rv:
        return {"success":False,
                "reason": "branch already exists"}
    repo = g2.get_repo(body["repository"])
    updated_files = []
    folderIDToPath = getCommitFoldersAsPaths(commit_id)
    body = request.get_json()
    documentSnapshots = getAllCommitDocumentSnapshotRelation(commit_id)
    deletedDocumentPaths = getCommitNonexistentGithubDocumentsUtil(body["repository"], body["oldbranch"], token, commit_id)
    branch_sha = repo.get_branch(body["oldbranch"]).commit.sha
    tree_elements = assembleGithubTreeElements(repo, folderIDToPath, deletedDocumentPaths, documentSnapshots, commit_id)
    if len(tree_elements) == 0:
        {"success":False,
                "reason": "no files to push"}
    try:
        new_tree = repo.create_git_tree(
            tree = tree_elements,
            base_tree = repo.get_git_tree(sha=branch_sha)
            )
    except:
        new_tree = repo.create_git_tree(
            tree = tree_elements,
            )
    commit = repo.create_git_commit(
        message=body["message"],
        tree = repo.get_git_tree(sha=new_tree.sha),
        parents=[repo.get_git_commit(branch_sha)],
        )
    ref = repo.create_git_ref(ref='refs/heads/' + body["branch"], sha = branch_sha)
    ref.edit(sha=commit.sha, force=True)
    commit = repo.get_branch(body["branch"]).commit
    allcomments = assembleGithubComments(documentSnapshots, commit_id)
    for comment in allcomments:
        commit.create_comment(body=comment)
    return {"success":True, "reason":"", "body":updated_files}

#put repository including owner name in "repository", ex: billingtonbill12/testrepo
#put branchname in "branch"
#put commit message in "message", or if we eventually put a generic message that's fine
@app.route('/api/Github/<proj_id>/<commit_id>/PushToExisting/', methods=["POST"])
def pushToExistingBranch(proj_id, commit_id):
    """
    TODO: Documentation
    
    ``<POST/GET/UPDATE/DELETE> /api``

    **Explanation:**
        <insert_explanation_here>

    **Args:**
        - route_params (<param_type>): description
        - request.body (dict):
            - body_params (<param_type>): description

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): description
            - reason (str): description
            - body (<body_type>): <body_contents>

    """
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
                "success":False,
                "reason": "Invalid Token Provided"
        }

    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
        #
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    body = request.get_json()
    user = getUserInfo(idInfo["email"])
    token = user["github_token"]
    g2 = Github(auth = Auth.Token(token))
    success, rv = getBranches(token, body["repository"])
    if (not success):
        return {"success":False,
                "reason": str(rv)}
    if body["branch"] not in rv:
        return {"success":False,
                "reason": "branch does not exist"}
    repo = g2.get_repo(body["repository"])
    updated_files = []
    start = time.time()
    folderIDToPath = getCommitFoldersAsPaths(commit_id)
    getpaths = time.time()
    print("getpaths", getpaths-start)
    body = request.get_json()
    documentSnapshots = getAllCommitDocumentSnapshotRelation(commit_id)
    relation = time.time()
    print("getrelation", relation-getpaths)

    deletedDocumentPaths = getCommitNonexistentGithubDocumentsUtil(body["repository"], body["branch"], token, commit_id)
    deleted = time.time()
    print("deleted", deleted-relation)
    tree_elements = assembleGithubTreeElements(repo, folderIDToPath, deletedDocumentPaths, documentSnapshots, commit_id)
    print("assemble", time.time()-deleted)
    if len(tree_elements) == 0:
        {"success":False,
                "reason": "no files to push"}
    branch_sha = repo.get_branch(body["branch"]).commit.sha
    try:
        new_tree = repo.create_git_tree(
            tree = tree_elements,
            base_tree = repo.get_git_tree(sha=branch_sha)
            )
    except Exception as e:
        new_tree = repo.create_git_tree(
            tree = tree_elements,
            )
    commit = repo.create_git_commit(
        message=body["message"],
        tree = repo.get_git_tree(sha=new_tree.sha),
        parents=[repo.get_git_commit(branch_sha)],
        )
    ref = repo.get_git_ref(ref='heads/' + body["branch"])
    ref.edit(sha=commit.sha, force=True)
    commit = repo.get_branch(body["branch"]).commit
    allcomments = assembleGithubComments(documentSnapshots, commit_id)
    for comment in allcomments:
        commit.create_comment(body=comment)
    return {"success":True, "reason":"", "body":updated_files}


