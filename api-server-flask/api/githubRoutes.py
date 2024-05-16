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

#checks whether authenticated user has github connected
@app.route('/api/Github/userHasGithub/', methods = ["GET"])
def getUserGithubStatus():
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
    return {"success:":True, "reason":"", "body": user["github_token"] != None}

#needs auth because everything does lmao
#put code in the body in "github_code"
@app.route('/api/Github/addToken', methods=["POST"])
def addGithubToken():
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

#format -> repository = "fnkzhang/codereview", branch = "main"
@app.route('/api/Github/PullToNewProject/', methods=["POST"])
def pullToNewProject():
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
    success, rv = getBranches(user["github_token"], body["repository"])
    if (not success):
        return {"success":False,
                "reason": str(rv)}
    if body["branch"] not in rv:
        return {"success":False,
                "reason": "branch does not exist"}
    proj_id = createNewProject(body["project_name"], idInfo["email"])
    g2 = Github(auth = Auth.Token(user["github_token"]))
    repo = g2.get_repo(body["repository"])
    project = getProjectInfo(proj_id)
    pathToFolderID = {}
    pathToFolderID[""] = project["root_folder"]
    contents = repo.get_contents("", body["branch"])
    updated_files = []
    while contents:
        file_content = contents.pop(0)
        index = file_content.path.rfind('/')
        if index < 0:
            path = ""
        else:
            path = file_content.path[:index]
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
            folder_id = createNewFolder(file_content.name, pathToFolderID[path], proj_id)
            pathToFolderID[file_content.path] = folder_id
        else:
            try:
                doc_id = createNewDocument(file_content.name, pathToFolderID[path], proj_id, file_content.decoded_content.decode())
            except:
                pass
    return {"success":True, "reason":"", "body":proj_id}

#needs auth
#put repository path in "repository" and branch in "branch"
#format -> repository = "fnkzhang/codereview", branch = "main"
@app.route('/api/Github/<proj_id>/PullToExistingProject/', methods=["POST"])
def pullToExistingProject(proj_id):
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
    g2 = Github(auth = Auth.Token(user["github_token"]))
    repo = g2.get_repo(body["repository"])
    project = getProjectInfo(proj_id)
    folders = getAllProjectFolders(proj_id)
    pathToFolderID = {}
    pathToFolderID[""] = project["root_folder"]
    contents = repo.get_contents("", body["branch"])
    updated_files = []
    documents = getAllProjectDocuments(proj_id)
    folders = getAllProjectFolders(proj_id)
    docs_to_delete = [document['doc_id'] for document in documents]
    folders_to_delete = [folder['folder_id'] for folder in folders]
    folders_to_delete.remove(project["root_folder"])
    while contents:
        file_content = contents.pop(0)
        index = file_content.path.rfind('/')
        if index < 0:
            path = ""
        else:
            path = file_content.path[:index]
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
            folder = getFolderInfoViaLocation(file_content.name, pathToFolderID[path])
            if folder != None:
                folder_id = folder["folder_id"]
                folders_to_delete.remove(folder_id)
            else:
                folder_id = createNewFolder(file_content.name, pathToFolderID[path], proj_id)
            pathToFolderID[file_content.path] = folder_id
        else:
            document = getDocumentInfoViaLocation(file_content.name, pathToFolderID[path])
            try:
                if document != None:
                    doc_id = document["doc_id"]
                    if file_content.decoded_content != getDocumentLastSnapshotContent(doc_id):
                        createNewSnapshot(proj_id, doc_id, file_content.decoded_content)
                        updated_files.append(doc_id)
                    docs_to_delete.remove(doc_id)
                else:
                    doc_id = createNewDocument(file_content.name, pathToFolderID[path], proj_id, file_content.decoded_content)
                    updated_files.append(doc_id)
            except:
                pass
    for doc_to_delete in docs_to_delete:
        deleteDocumentUtil(doc_to_delete)
    for folder_to_delete in folders_to_delete:
        deleteFolderUtil(folder_to_delete)
    return {"success":True, "reason":"", "body":updated_files}

#needs "branch" in arguments, for example /api/Github/12345/getNonexistent/?owner_name=fnkzhang&repo_name=coderaview&branch=main
@app.route('/api/Github/<proj_id>/getNonexistent/', methods=["GET"])
def getProjectNonexistentGithubDocuments(proj_id):
    headers = request.headers
    repository = request.args.get("repository")
    branch = request.args.get("branch")
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
    user = getUserInfo(idInfo["email"])
    token = user["github_token"]
    documents = getProjectNonexistentGithubDocumentsUtil(repository, branch, token, proj_id)
    return {"success":True, "reason":"", "body":documents}

#put list of snapshots ID's to push in "snapshots"
#put list of paths in deletedDocuments, should just be the samae paths as received in 
#put repository including owner name in "repository", ex: billingtonbill12/testrepo
#put branchname in "branch"
#put branch you're building off of into "oldbranch"
#put commit message in "message", or if we eventually put a generic message that's fine
@app.route('/api/Github/<proj_id>/PushToNewBranch/', methods=["POST"])
def pushToNewBranch(proj_id):
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
    folderIDToPath = getProjectFoldersAsPaths(proj_id)
    body = request.get_json()
    snapshotIDs = body["snapshots"]
    deletedDocumentPaths = body["deletedDocuments"]
    branch_sha = repo.get_branch(body["oldbranch"]).commit.sha
    tree_elements = assembleGithubTreeElements(repo, folderIDToPath, deletedDocumentPaths, snapshotIDs)
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
    ref = repo.create_git_ref(ref='refs/heads/' + body["branch"], sha = branch_sha)
    ref.edit(sha=commit.sha, force=True)
    commit = repo.get_branch(body["branch"]).commit
    allcomments = assembleGithubComments(snapshotIDs)
    for comment in allcomments:
        commit.create_comment(body=comment)
    return {"success":True, "reason":"", "body":updated_files}

#put list of snapshots ID's to push in "snapshots"
#put list of paths in deletedDocuments, should just be the samae paths as received in 
#put repository including owner name in "repository", ex: billingtonbill12/testrepo
#put branchname in "branch"
#put commit message in "message", or if we eventually put a generic message that's fine
@app.route('/api/Github/<proj_id>/PushToExisting/', methods=["POST"])
def pushToExistingBranch(proj_id):
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
    folderIDToPath = getProjectFoldersAsPaths(proj_id)
    body = request.get_json()
    snapshotIDs = body["snapshots"]
    deletedDocumentPaths = body["deletedDocuments"]
    tree_elements = assembleGithubTreeElements(repo, folderIDToPath, deletedDocumentPaths, snapshotIDs)
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
    allcomments = assembleGithubComments(snapshotIDs)
    for comment in allcomments:
        commit.create_comment(body=comment)
    return {"success":True, "reason":"", "body":updated_files}

