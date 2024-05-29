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

FAKE_ID_INFO = {
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

@pytest.fixture()
def client(app):
    with patch('utils.miscUtils.id_token.verify_oauth2_token', autospec=True) as mock_verify_oauth2_token:
        mock_verify_oauth2_token.return_value = FAKE_ID_INFO
        
        yield app.test_client()

"""
Unit Tests for authRoutes.py
"""

def test_authenticator_invalid_request(client):
    
    response = client.post("/api/user/authenticate")
    assert response.json["success"] == False

def test_authenticator_valid_request(client):
    
    response = client.post("/api/user/authenticate", headers={"Authorization": "oAuthToken"})
    print(response.json["reason"])
    assert response.json["success"] == True

def test_signUp_invalid_request(client):
    response = client.post("/api/user/signup")
    assert response.json["success"] == False
    
def test_signUp_valid_request(client):
    with patch('authRoutes.createNewUser', autospec=True) as mock_createNewUser:

        mock_createNewUser.return_value = True
        response = client.post("/api/user/signup", headers={"Authorization": "oAuthToken"})
        assert response.json["success"] == True

        with patch('authRoutes.userExists', autospec=True) as mock_userExists:
            
            mock_userExists.return_value = True
            response = client.post("/api/user/signup", headers={"Authorization": "oAuthToken"})
            assert response.json["success"] == True

            mock_userExists.return_value = False
            response = client.post("/api/user/signup", headers={"Authorization": "oAuthToken"})
            assert response.json["success"] == True

def test_checkIsValidUser_invalid_request(client):
    with patch('authRoutes.userExists', autospec=True) as mock_UserExists:

        mock_UserExists.return_value = False

        response = client.post("/api/user/isValidUser", headers={"Authorization": "oAuthToken"})
        assert response.json["success"] == False

        response = client.post("/api/user/isValidUser", headers={"Email": "fake-email@fake-domain.com"})
        assert response.json["success"] == False

def test_checkIsValidUser_valid_request(client):
    with patch('authRoutes.userExists', autospec=True) as mock_UserExists:

        mock_UserExists.return_value = False
        response = client.post("/api/user/isValidUser", headers={"Authorization": "oAuthToken", "Email": "fake-email@fake-domain.com"})
        assert response.json["success"] == False

        mock_UserExists.return_value = True
        response = client.post("/api/user/isValidUser", headers={"Authorization": "oAuthToken", "Email": "fake-email@fake-domain.com"})
        assert response.json["success"] == True

"""
Unit Tests for commentRoutes.py
"""
