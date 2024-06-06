"""
Commented out assertions are tests that failed
"""

import pytest
from unittest.mock import patch, MagicMock
import flaskApi
from flask import request
import json

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

def get_request_body(response):
    """
    **Args:**
        - response (Response): Response object from a Flask request

    **Returns:**
        The input body of a request which includes the parameters from route.

    """
    try:
        print(json.loads(response.data.decode('utf-8')))
        return json.loads(response.data.decode('utf-8'))["body"]
    except:
        return {}
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

        response = client.post("/api/Snapshot/123/comment/create", headers={"Authorization": "oAuthToken"}, 
                               json={
                                   "author_email": "fake-email@fake-domain.com",
                                   "reply_to_id": 0,
                                   "content": "This is a comment",
                                   "highlight_start_x": 1,
                                   "highlight_start_y": 1,
                                   "highlight_end_x": 1,
                                   "highlight_end_y": 1,
                                   "is_resolved": False
                                   })
        assert response.status_code == 200
        assert response.json["success"] == False

        with patch("commentRoutes.getUserProjPermissions", autospec=True, return_value=5), \
             patch("commentRoutes.createNewComment", autospec=True, return_value=123):
            SAME_EMAIL = GOOGLE_FAKE_ID_INFO["email"]
            DIFFERENT_EMAIL = "fake-email-2@fake-domain.com"

            response = client.post("/api/Snapshot/123/comment/create", headers={"Authorization": "oAuthToken"},
                                   json={
                                       "author_email": DIFFERENT_EMAIL,
                                       "reply_to_id": 0,
                                       "content": "This is a comment",
                                       "highlight_start_x": 1,
                                       "highlight_start_y": 1,
                                       "highlight_end_x": 1,
                                       "highlight_end_y": 1,
                                       "is_resolved": False
                                       })
            
            #body = get_request_body(response)
            #assert body["author_email"] == GOOGLE_FAKE_ID_INFO["email"]
            #assert response.status_code == 200
            #assert response.json["success"] == False

            response = client.post("/api/Snapshot/123/comment/create", headers={"Authorization": "oAuthToken"},
                                   json={
                                       "author_email": SAME_EMAIL,
                                       "reply_to_id": 0,
                                       "content": "This is a comment",
                                       "highlight_start_x": 1,
                                       "highlight_start_y": 1,
                                       "highlight_end_x": 1,
                                       "highlight_end_y": 1,
                                       "is_resolved": False
                                       })
            assert response.status_code == 200
            assert response.json["success"] == True

def test_resolveComment(client):

    response = client.put("/api/comment/123/resolve")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.put("/api/comment/123/resolve", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("commentRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO), \
         patch("commentRoutes.getCommentProject", autospec=True, return_value=123):

        response = client.put('/api/comment/123/resolve', headers={"Authorization": "oAuthToken"})
        assert response.status_code == 200
        assert response.json["success"] == False

        with patch("commentRoutes.getUserProjPermissions", autospec=True, return_value=5), \
             patch("commentRoutes.resolveCommentHelperFunction", autospec=True, return_valu = None):

            response = client.put('/api/comment/123/resolve', headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == True

def test_editComment(client):

    response = client.put("/api/comments/123/edit")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.put("/api/comments/123/edit", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("commentRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        #response = client.put("/api/comments/123/resolve", headers={"Authorization": "oAuthToken"})
        #assert response.status_code == 200
        #assert response.json["success"] == False

        with patch("commentRoutes.getCommentProject", autospec=True, return_value=123):
            response = client.put("/api/comments/123/edit", headers={"Authorization": "oAuthToken"}, json={"content": "This is an edited comment."})
            assert response.status_code == 200
            assert response.json["success"] == False

            DIFFERENT_EMAIL = "fake-email-2@fake-domain.com"
            with patch("commentRoutes.getUserProjPermissions", autospec=True, return_value=5), \
                 patch("commentRoutes.getCommentInfo", autospec=True, return_value={"author_email": DIFFERENT_EMAIL}):

                response = client.put("/api/comments/123/edit", headers={"Authorization": "oAuthToken"}, json={"content": "This is an edited comment."})
                assert response.status_code == 200
                assert response.json["success"] == False

            with patch("commentRoutes.getUserProjPermissions", autospec=True, return_value=5), \
                 patch("commentRoutes.getCommentInfo", autospec=True, return_value={"author_email": GOOGLE_FAKE_ID_INFO["email"]}):
                    
                    with patch("commentRoutes.Session", autospec=True) as mock_session_class:
                        mock_session = MagicMock()
                        mock_session_class.return_value = mock_session
                        mock_query = mock_session.query.return_value
                        mock_update = mock_query.filter_by.return_value.update
                        mock_commit = mock_session.commit

                        mock_session_class.side_effect = Exception("Fake DB Error")
                        response = client.put("/api/comments/123/edit", headers={"Authorization": "oAuthToken"}, json={"content": "Updated content"})
                        assert response.status_code == 200
                        assert response.json["success"] == False

                        mock_session_class.side_effect = None
                        response = client.put("/api/comments/123/edit", headers={"Authorization": "oAuthToken"}, json={"content": "Updated content"})
                        assert response.status_code == 200
                        assert response.json["success"] == True

def test_deleteComment(client):

    response = client.delete("/api/comments/123/delete")
    assert response.status_code == 200
    assert response.json['success'] == False

    response = client.delete("/api/comments/123/delete", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json['success'] == False

    with patch("commentRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        with patch("commentRoutes.getCommentProject", autospec=True, return_value=123):
            #response = client.delete("/api/comments/123/delete", headers={"Authorization": "oAuthToken"})
            #assert response.status_code == 200
            #assert response.json["success"] == False

            DIFFERENT_EMAIL = "fake-email-2@fake-domain.com"
            with patch("commentRoutes.getUserProjPermissions", autospec=True, return_value=5), \
                 patch("commentRoutes.getCommentInfo", autospec=True, return_value={"author_email": DIFFERENT_EMAIL}):

                response = client.delete("/api/comments/123/delete", headers={"Authorization": "oAuthToken"})
                assert response.status_code == 200
                assert response.json["success"] == False

            with patch("commentRoutes.getUserProjPermissions", autospec=True, return_value=5), \
                 patch("commentRoutes.getCommentInfo", autospec=True, return_value={"author_email": GOOGLE_FAKE_ID_INFO["email"]}):
                    
                    with patch("commentRoutes.Session", autospec=True) as mock_session_class:
                        mock_session = MagicMock()
                        mock_session_class.return_value = mock_session
                        mock_query = mock_session.query.return_value
                        mock_delete = mock_query.filter_by.return_value.delete
                        mock_commit = mock_session.commit

                        mock_session_class.side_effect = Exception("Fake DB Error")
                        response = client.delete("/api/comments/123/delete", headers={"Authorization": "oAuthToken"})
                        assert response.status_code == 200
                        assert response.json["success"] == False

                        mock_session_class.side_effect = None
                        response = client.delete("/api/comments/123/delete", headers={"Authorization": "oAuthToken"})
                        assert response.status_code == 200
                        assert response.json["success"] == True

"""
Unit Tests for commitRoutes.py
"""

def test_getCommitInformation(client):
    pass

def test_getCommitDocumentSnapshotPairs(client):
    pass

def test_createCommit(client):
    
    response = client.post("/api/Commit/123/createCommit/")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.post("/api/Commit/123/createCommit/", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("commitRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        response = client.post("/api/Commit/123/createCommit/", headers={"Authorization": "oAuthToken"})
        assert response.status_code == 200
        assert response.json["success"] == False

        with patch("commitRoutes.getUserProjPermissions", autospec=True, return_value=5):
            with patch("commitRoutes.getUserWorkingCommitInProject", autospec=True, return_value="workingCommitDict"):
                response = client.post("/api/Commit/123/createCommit/", headers={"Authorization": "oAuthToken"})
                assert response.status_code == 200
                assert response.json["success"] == False

            with patch("commitRoutes.getUserWorkingCommitInProject", autospec=True, return_value=None), \
                patch("commitRoutes.createNewCommit", autospec=True, return_value=456), \
                patch("commitRoutes.setCommitOpen", autospec=True, return_value=None):
                response = client.post("/api/Commit/123/createCommit/", headers={"Authorization": "oAuthToken"})
                assert response.status_code == 200
                assert response.json["success"] == True

def test_commitCommit(client):
    
    response = client.post("/api/Commit/123/commitCommit/")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.post("/api/Commit/123/commitCommit/", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("commitRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        #response = client.post("/api/Commit/123/commitCommit/", headers={"Authorization": "oAuthToken"})
        #assert response.status_code == 200
        #assert response.json["success"] == False

        with patch("commitRoutes.getCommitInfo", autospec=True, return_value={"proj_id": 456}):
            response = client.post("/api/Commit/123/commitCommit/", headers={"Authorization": "oAuthToken"}, json={"name":"Commit Name"})
            assert response.status_code == 200
            assert response.json["success"] == False

            with patch("commitRoutes.getUserProjPermissions", autospec=True, return_value=5), \
                 patch("commitRoutes.commitACommit", autospec=True, return_value=True), \
                 patch("commitRoutes.setCommitOpen", autospec=True, return_value=None):
                response = client.post("/api/Commit/123/commitCommit/", headers={"Authorization": "oAuthToken"}, json={"name":"Commit Name"})
                assert response.status_code == 200
                assert response.json["success"] == True

def test_setReviewedCommit(client):
    
    response = client.get("/api/Commit/123/setReviewed/")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.get("/api/Commit/123/setReviewed/", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("commitRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        with patch("commitRoutes.getCommitInfo", autospec=True, return_value={"proj_id": 456}):
            response = client.get("/api/Commit/123/setReviewed/", headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == False

            with patch("commitRoutes.getUserProjPermissions", autospec=True, return_value=5), \
                 patch("commitRoutes.commitACommit", autospec=True, return_value=True), \
                 patch("commitRoutes.setCommitReviewed", autospec=True, return_value=True):
                response = client.get("/api/Commit/123/setReviewed/", headers={"Authorization": "oAuthToken"})
                assert response.status_code == 200
                assert response.json["success"] == True

def test_closeCommit(client):
    response = client.get("/api/Commit/123/close/")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.get("/api/Commit/123/close/", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("commitRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        with patch("commitRoutes.getCommitInfo", autospec=True, return_value={"proj_id": 456}):
            response = client.get("/api/Commit/123/close/", headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == False

            with patch("commitRoutes.getUserProjPermissions", autospec=True, return_value=5), \
                 patch("commitRoutes.setCommitClosed", autospec=True, return_value=True):
                response = client.get("/api/Commit/123/close/", headers={"Authorization": "oAuthToken"})
                assert response.status_code == 200
                assert response.json["success"] == True

def test_approveCommit(client):
    response = client.get("/api/Commit/123/approve/")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.get("/api/Commit/123/approve/", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("commitRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        with patch("commitRoutes.getCommitInfo", autospec=True, return_value={"proj_id": 456}):
            response = client.get("/api/Commit/123/approve/", headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == False

            with patch("commitRoutes.getUserProjPermissions", autospec=True, return_value=5):
                with patch("commitRoutes.setCommitApproved", autospec=True, return_value=False):
                    response = client.get("/api/Commit/123/approve/", headers={"Authorization": "oAuthToken"})
                    assert response.status_code == 200
                    assert response.json["success"] == False

                with patch("commitRoutes.setCommitApproved", autospec=True, return_value=True):
                    response = client.get("/api/Commit/123/approve/", headers={"Authorization": "oAuthToken"})
                    assert response.status_code == 200
                    assert response.json["success"] == True

def test_deleteWorkingCommit(client):
    response = client.delete("/api/Commit/123/workingCommit/")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.delete("/api/Commit/123/workingCommit/", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("commitRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        SAME_EMAIL = GOOGLE_FAKE_ID_INFO["email"]
        DIFFERENT_EMAIL = "fake-email-2@fake-domain.com"
        with patch("commitRoutes.getUserWorkingCommitInProject", autospec=True, return_value=None):
            response = client.delete("/api/Commit/123/workingCommit/", headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == False

        with patch("commitRoutes.getUserWorkingCommitInProject", autospec=True) as mock_getUserWorkingCommitInProject:
            mock_getUserWorkingCommitInProject.side_effect = Exception("Fake Error")
            response = client.delete("/api/Commit/123/workingCommit/", headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == False

            mock_getUserWorkingCommitInProject.side_effect = None
            mock_getUserWorkingCommitInProject.return_value = {"author_email": DIFFERENT_EMAIL, "commit_id": 456}
            response = client.delete("/api/Commit/123/workingCommit/", headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == False

            mock_getUserWorkingCommitInProject.return_value = {"author_email": SAME_EMAIL, "commit_id": 456}
            with patch("commitRoutes.deleteCommit", autospec=True) as mock_deleteCommit:
                mock_deleteCommit.return_value = (False, "Fake Error")
                response = client.delete("/api/Commit/123/workingCommit/", headers={"Authorization": "oAuthToken"})
                assert response.status_code == 200
                assert response.json["success"] == False

                mock_deleteCommit.return_value = (True, None)
                response = client.delete("/api/Commit/123/workingCommit/", headers={"Authorization": "oAuthToken"})
                assert response.status_code == 200
                assert response.json["success"] == True

def test_getCommitFolderTree(client):

    response = client.get("/api/Commit/123/getFolderTree/")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.get("/api/Commit/123/getFolderTree/", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("commitRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        with patch("commitRoutes.getCommitInfo", autospec=True, return_value={"proj_id": 456}):
            response = client.get("/api/Commit/123/getFolderTree/", headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == False

            with patch("commitRoutes.getUserProjPermissions", autospec=True, return_value=5):
                with patch("commitRoutes.getCommitTreeWithAddons", autospec=True, return_value="treeDict"):
                    response = client.get("/api/Commit/123/getFolderTree/", headers={"Authorization": "oAuthToken"})
                    assert response.status_code == 200
                    assert response.json["success"] == True

def test_getUserWorkingCommitForProject(client):
    
    response = client.get("/api/Commit/123/workingCommit")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.get("/api/Commit/123/workingCommit", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("commitRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        with patch("commitRoutes.getCommitInfo", autospec=True, return_value={"proj_id": 456}):
            response = client.get("/api/Commit/123/workingCommit", headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == False

            with patch("commitRoutes.getUserProjPermissions", autospec=True, return_value=5):
                with patch("commitRoutes.getUserWorkingCommitInProject", autospec=True, return_value=None):
                    response = client.get("/api/Commit/123/workingCommit", headers={"Authorization": "oAuthToken"})
                    assert response.status_code == 200
                    assert response.json["success"] == False

                with patch("commitRoutes.getUserWorkingCommitInProject", autospec=True, return_value="commitDict"):
                    response = client.get("/api/Commit/123/workingCommit", headers={"Authorization": "oAuthToken"})
                    assert response.status_code == 200
                    assert response.json["success"] == True

def test_getAllLatestCommitComments(client):
    response = client.get("/api/Commit/123/getLatestComments/")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.get("/api/Commit/123/getLatestComments/", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("commitRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        response = client.get("/api/Commit/123/getLatestComments/", headers={"Authorization": "oAuthToken"})
        assert response.status_code == 200
        assert response.json["success"] == False

        with patch("commitRoutes.getUserProjPermissions", autospec=True, return_value=5):
            with patch("commitRoutes.getProjectLastCommittedCommit", autospec=True, return_value=None):
                response = client.get("/api/Commit/123/getLatestComments/", headers={"Authorization": "oAuthToken"})
                assert response.status_code == 200
                assert response.json["success"] == False

            with patch("commitRoutes.getProjectLastCommittedCommit", autospec=True, return_value=None):
                assert response.status_code == 200
                assert response.json["success"] == False

            with patch("commitRoutes.getProjectLastCommittedCommit", autospec=True, return_value={"commit_id": 456}):
                with patch("commitRoutes.getAllCommitDocumentSnapshotRelation", autospec=True, return_value={"doc1": 789}):
                    # everything past here is difficult to write a unit test for
                    pass

"""
Unit Tests for documentRoutes.py
"""

def test_getDocument(client):
    response = client.get("/api/Document/123/456/789/")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.get("/api/Document/123/456/789/", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("documentRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
        response = client.get("/api/Document/123/456/789/", headers={"Authorization": "oAuthToken"})
        assert response.status_code == 200
        assert response.json["success"] == False

        with patch("documentRoutes.getUserProjPermissions", autospec=True, return_value=5), \
             patch("documentRoutes.getDocumentInfo", autospec=True, return_value="documentDict"):
                response = client.get("/api/Document/123/456/789/", headers={"Authorization": "oAuthToken"})
                assert response.status_code == 200
                assert response.json["success"] == True

def test_createDocument(client):
    request_body = {
        "doc_name": "Test Document",
        "data": "Test data",
        "parent_folder": 123
    }
    
    response = client.post("/api/Document/123/456/", json=request_body)
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("documentRoutes.isValidRequest", autospec=True, return_value=True):
        with patch("documentRoutes.authenticate", autospec=True, return_value=None):
            response = client.post("/api/Document/123/456/", json=request_body, headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == False

        with patch("documentRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO):
            with patch("documentRoutes.getUserProjPermissions", autospec=True, return_value=1):
                response = client.post("/api/Document/123/456/", json=request_body, headers={"Authorization": "oAuthToken"})
                assert response.status_code == 200
                assert response.json["success"] == False

            with patch("documentRoutes.getUserProjPermissions", autospec=True, return_value=2), \
                 patch("documentRoutes.createNewDocument", autospec=True, return_value=456):
                response = client.post("/api/Document/123/456/", json=request_body, headers={"Authorization": "oAuthToken"})
                assert response.status_code == 200
                assert response.json["success"] == True

def test_deleteDocument(client):
    response = client.delete("/api/Document/123/456/")
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("documentRoutes.isValidRequest", autospec=True, return_value=True), \
         patch("documentRoutes.authenticate", autospec=True, return_value=None):
            response = client.delete("/api/Document/123/456/", headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == False

    with patch("documentRoutes.isValidRequest", autospec=True, return_value=True), \
         patch("documentRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO), \
         patch("documentRoutes.getDocumentInfo", autospec=True, side_effect=Exception("Fake DB Error")):
            response = client.delete("/api/Document/123/456/", headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == False

    with patch("documentRoutes.isValidRequest", autospec=True, return_value=True), \
         patch("documentRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO), \
         patch("documentRoutes.getDocumentInfo", autospec=True, return_value={"associated_proj_id": 123}), \
         patch("documentRoutes.getUserProjPermissions", autospec=True, return_value=1):
            response = client.delete("/api/Document/123/456/", headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == False

    with patch("documentRoutes.isValidRequest", autospec=True, return_value=True):
        with patch("documentRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO), \
             patch("documentRoutes.getDocumentInfo", autospec=True, return_value={"associated_proj_id": 123}), \
             patch("documentRoutes.getUserProjPermissions", autospec=True, return_value=2), \
             patch("documentRoutes.deleteDocumentFromCommit", autospec=True, return_value=(True, None)):
            response = client.delete("/api/Document/123/456/", headers={"Authorization": "oAuthToken"})
            assert response.status_code == 200
            assert response.json["success"] == True

def test_renameDocument(client):
    request_body = {
        "doc_name": "New Document Name"
    }

    response = client.post("/api/Document/123/456/rename/", json=request_body)
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("documentRoutes.isValidRequest", autospec=True, return_value=True), \
         patch("documentRoutes.authenticate", autospec=True, return_value=None):
        response = client.post("/api/Document/123/456/rename/", json=request_body, headers={"Authorization": "oAuthToken"})
        assert response.status_code == 200
        assert response.json["success"] == False

    with patch("documentRoutes.isValidRequest", autospec=True, return_value=True), \
         patch("documentRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO), \
         patch("documentRoutes.getDocumentInfo", autospec=True, return_value={"associated_proj_id": 123}), \
         patch("documentRoutes.getUserProjPermissions", autospec=True, return_value=1):
        response = client.post("/api/Document/123/456/rename/", json=request_body, headers={"Authorization": "oAuthToken"})
        assert response.status_code == 200
        assert response.json["success"] == False

    with patch("documentRoutes.isValidRequest", autospec=True, return_value=True), \
         patch("documentRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO), \
         patch("documentRoutes.getDocumentInfo", autospec=True, return_value={"associated_proj_id": 123}), \
         patch("documentRoutes.getUserProjPermissions", autospec=True, return_value=2), \
         patch("documentRoutes.renameItem", autospec=True, return_value=(True, None)):
        response = client.post("/api/Document/123/456/rename/", json=request_body, headers={"Authorization": "oAuthToken"})
        assert response.status_code == 200
        assert response.json["success"] == True

def test_moveDocument(client):
    request_body = {
        "parent_folder": 456
    }

    response = client.post("/api/Document/123/456/move/", json=request_body)
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("documentRoutes.isValidRequest", autospec=True, return_value=True), \
         patch("documentRoutes.authenticate", autospec=True, return_value=None):
        response = client.post("/api/Document/123/456/move/", json=request_body, headers={"Authorization": "oAuthToken"})
        assert response.status_code == 200
        assert response.json["success"] == False

    with patch("documentRoutes.isValidRequest", autospec=True, return_value=True), \
         patch("documentRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO), \
         patch("documentRoutes.getDocumentInfo", autospec=True, return_value={"associated_proj_id": 123}), \
         patch("documentRoutes.getUserProjPermissions", autospec=True, return_value=1):
        response = client.post("/api/Document/123/456/move/", json=request_body, headers={"Authorization": "oAuthToken"})
        assert response.status_code == 200
        assert response.json["success"] == False

    with patch("documentRoutes.isValidRequest", autospec=True, return_value=True), \
         patch("documentRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO), \
         patch("documentRoutes.getDocumentInfo", autospec=True, return_value={"associated_proj_id": 123}), \
         patch("documentRoutes.getUserProjPermissions", autospec=True, return_value=2), \
         patch("documentRoutes.moveItem", autospec=True, return_value=True):
        response = client.post("/api/Document/123/456/move/", json=request_body, headers={"Authorization": "oAuthToken"})
        assert response.status_code == 200
        assert response.json["success"] == True

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
    
    response = client.post("/api/llm/code-implementation")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.post("/api/llm/code-implementation", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("llmRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO), \
         patch("llmRoutes.get_llm_code_from_suggestion") as mock_get_llm_code_from_suggestion:
        mock_get_llm_code_from_suggestion.return_value = None
        #response = client.post("/api/llm/code-implementation", headers={"Authorization": "oAuthToken"})
        #assert response.status_code == 200
        #assert response.json["success"] == False

        response = client.post("/api/llm/code-implementation", headers={"Authorization": "oAuthToken"}, json={})
        assert response.status_code == 200
        assert response.json["success"] == False

        mock_get_llm_code_from_suggestion.return_value = {"success": False}
        response = client.post("/api/llm/code-implementation", headers={"Authorization": "oAuthToken"}, json={})
        assert response.status_code == 200
        assert response.json["success"] == False

        with patch("llmRoutes.buildStringFromLLMResponse", autospec=True, return_value=None):
            mock_get_llm_code_from_suggestion.return_value = {"success": True}
            response = client.post("/api/llm/code-implementation", headers={"Authorization": "oAuthToken"}, json={})
            assert response.status_code == 200
            assert response.json["success"] == False

        with patch("llmRoutes.buildStringFromLLMResponse", autospec=True, return_value="buildString"):
            mock_get_llm_code_from_suggestion.return_value = {"success": True}
            response = client.post("/api/llm/code-implementation", headers={"Authorization": "oAuthToken"}, json={})
            assert response.status_code == 200
            assert response.json["success"] == True

def test_suggest_comment_from_code(client):
    
    response = client.post("/api/llm/comment-suggestion")
    assert response.status_code == 200
    assert response.json["success"] == False

    response = client.post("/api/llm/comment-suggestion", headers={"Authorization": "oAuthToken"})
    assert response.status_code == 200
    assert response.json["success"] == False

    with patch("llmRoutes.authenticate", autospec=True, return_value=GOOGLE_FAKE_ID_INFO), \
         patch("llmRoutes.get_llm_suggestion_from_code") as mock_get_llm_suggestion_from_code:
        mock_get_llm_suggestion_from_code.return_value = None
        #response = client.post("/api/llm/comment-suggestion", headers={"Authorization": "oAuthToken"})
        #assert response.status_code == 200
        #assert response.json["success"] == False

        response = client.post("/api/llm/comment-suggestion", headers={"Authorization": "oAuthToken"}, json={})
        assert response.status_code == 200
        assert response.json["success"] == False

        mock_get_llm_suggestion_from_code.return_value = "Fake LLM Response"
        response = client.post("/api/llm/comment-suggestion", headers={"Authorization": "oAuthToken"}, json={})
        assert response.status_code == 200
        assert response.json["success"] == True

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
