import pytest
from unittest.mock import patch
import flaskApi

@pytest.fixture()
def app():
    app = flaskApi.app
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

GOOGLE_FAKE_ID_INFO = {
    "aud": "CLIENT_ID",
    "azp": "CLIENT_ID",
    "email": "fake-email@fake-domain.com",
    "email_verified": True,
    "exp": 9999999999,  # Replace with the actual expiration time as a Unix timestamp
    "family_name": "Fakelast",
    "given_name": "Fakefirst",
    "hd": "fake-domain.com",
    "iat": 1716941903,
    "iss": "https://accounts.google.com",
    "jti": "JWT_ID",
    "name": "Fakefirst Fakelast",
    "nbf": 0,  # Replace with the actual not-before time as a Unix timestamp
    "picture": "https://fake-picture-url.com",
    "sub": "subject_identifier"
}

"""
Unit Tests for authRoutes.py
"""

def test_authenticator(client):
    
    response = client.post("/api/user/authenticate")
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("authRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        response = client.post("/api/user/authenticate")
        assert response.status_code == 200
        assert response.json["success"] == True
        assert response.json["body"]["email"] == GOOGLE_FAKE_ID_INFO["email"]

def test_signUp(client):

    response = client.post("/api/user/signup")
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("authRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        with patch("authRoutes.userExists", autospec=True, return_value=True):
            response = client.post("/api/user/signup")
            assert response.status_code == 200
            assert response.json["success"] == True
            assert response.json["body"] == GOOGLE_FAKE_ID_INFO

        with patch("authRoutes.userExists", autospec=True, return_value=False):
            with patch("authRoutes.createNewUser", autospec=True, return_value=True):
                response = client.post("/api/user/signup")
                assert response.status_code == 200
                assert response.json["success"] == True
                assert response.json["body"] == GOOGLE_FAKE_ID_INFO

def test_checkIsValidUser(client):

    response = client.post("/api/user/isValidUser", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.post("/api/user/isValidUser", headers={"Email": "fake-email@fake-domain.com"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("authRoutes.userExists", autospec=True, return_value=False):
        response = client.post("/api/user/isValidUser", headers={"Authorization": "oAuthToken", "Email": "fake-email@fake-domain.com"})
        assert response.status_code == 200
        assert response.json["success"] == False

    with patch("authRoutes.userExists", autospec=True, return_value=True):
        response = client.post("/api/user/isValidUser", headers={"Authorization": "oAuthToken", "Email": "fake-email@fake-domain.com"})
        assert response.status_code == 200
        assert response.json["success"] == True

"""
Unit Tests for commentRoutes.py
"""

def test_createComment(client):

    response = client.post("/api/Snapshot/123/comment/create")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.post("/api/Snapshot/123/comment/create", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("commentRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        #response = client.post("/api/Snapshot/123/comment/create", headers={"Authorization": "oAuthToken"})
        #assert response.status_code == 200
        #assert response.json["success"] == False

        response = client.post("/api/Snapshot/123/comment/create", headers={"Authorization": "oAuthToken"}, json={})
        assert response.status_code == 200
        assert response.json["success"] == False

        response = client.post("/api/Snapshot/123/comment/create", headers={"Authorization": "oAuthToken"}, json={"author_email": "fake-email@fake-domain.com", "reply_to_id": 0, "content": "This is a comment"})
        assert response.status_code == 200
        assert response.json["success"] == False
        assert response.json["reason"] == "Invalid Permissions"

def test_resolveComment(client):

    # Invalid Requests

    # Valid Requests

    pass

def test_editComment(client):

    # Invalid Requests

    # Valid Requests

    pass

def test_deleteComment(client):

    # Invalid Requests

    # Valid Requests

    pass

"""
Unit Tests for commitRoutes.py
"""

def test_createCommit(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_checkIfNewerCommitExists(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getCommitDifferences(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getCommitDiffCareAboutLast(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_bulkAddToCommit(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_bulkDeleteFromCommit(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_commitCommit(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_setReviewedCommit(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_closeCommit(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_approveCommit(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_deleteWorkingCommit(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getCommitFolderTree(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getUserWorkingCommitForProject(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getAllLatestCommitComments(client):
    
    # Invalid Requests

    # Valid Requests

    pass

"""
Unit Tests for documentRoutes.py
"""

def test_getDocument(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_createDocument(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_deleteDocument(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_renameDocument(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_moveDocument(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getAllDocumentCommittedSnapshots(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getAllDocumentCommittedSnapshotsIncludingWorking(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_changeDocumentSnapshot(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getAllCommentsForDocument(client):
    
    # Invalid Requests

    # Valid Requests

    pass

"""
Unit Tests for folderRoutes.py
"""

def test_getFolder(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_createFolder(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_deleteFolder(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_renameFolder(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_moveFolder(client):
    
    # Invalid Requests

    # Valid Requests

    pass

"""
Unit Tests for githubRoutesRoutes.py
"""

def test_getUserGithubStatus(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_addGithubToken(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getGithubRepositoryBranches(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_pullToNewProject(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_pullToExistingProject(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_pushToNewBranch(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_pushToExistingBranch(client):
    
    # Invalid Requests

    # Valid Requests

    pass



"""
Unit Tests for llmRoutes.py
"""

def test_implement_code_changes_from_comment(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_suggest_comment_from_code(client):
    
    # Invalid Requests

    # Valid Requests

    pass


"""
Unit Tests for projectRoutes.py
"""

def test_getProject(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_createProject(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_deleteProject(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_renameProject(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getProjectCommittedCommits(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getProjectLatestCommit(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getProjectDocuments(client):
    
    # Invalid Requests

    # Valid Requests

    pass

"""
Unit Tests for snapshotRoutes.py
"""

def test_getSnapshot(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_createSnapshot(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_deleteSnapshot(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getCommentsOnSnapshot(client):
    
    # Invalid Requests

    # Valid Requests

    pass

"""
Unit Tests for userAndPermissionsRoutes.py
"""

def test_getAllUserProjects(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_addUser(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_transferProjectOwnership(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_importPermissions(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_addUserAdmin(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_removeUser(client):
    
    # Invalid Requests

    # Valid Requests

    pass

def test_getUsersWithAccessToProject(client):
    
    # Invalid Requests

    # Valid Requests

    pass
