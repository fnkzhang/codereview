import pytest
import sys
sys.path.append("../")
import flaskApiLesserCredentials
import oauth2client.client
import google.oauth2.credentials
from google.oauth2 import id_token
from google.auth.transport import requests
import google.oauth2.id_token
import google.auth.transport.requests
import os
from google.auth import compute_engine
import uuid

proj_name = str(uuid.uuid4())
doc_name = str(uuid.uuid4())
doc_body = str(uuid.uuid4())
email1 = 'billingtonbill12@gmail.com'
email2 = 'mborgthegreat@gmail.com'
@pytest.fixture()
def app():
    app = flaskApiLesserCredentials.app
    app.config.update({
        "TESTING": True,
        })
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def getProjID(client, email):
    response = client.get('/api/User/' + email1 + '/Project/', headers = {'Authorization': email1})
    #print(response.json)
    proj_id = -1
    for project in response.json["body"]:
        if project["name"] == proj_name:
            proj_id = project["proj_id"]
            break
    return proj_id

def getDocID(client, proj_id, email):
    response = client.get('/api/Document/' + str(proj_id) + '/', headers = {'Authorization': email})
    doc_id = -1
    for document in response.json["body"]:
        if document["name"] == doc_name:
            doc_id = document["doc_id"]
            break
    return doc_id

def test_request_example(client):
    response = client.get("/")
    assert b"test" in response.data

'''def test_create_tables(client):
    assert b"Created Table" in client.get("/createTable").data
'''

def test_create_project(client):
    response = client.post('/api/Project/' + proj_name + '/', headers = {'Authorization': email1})
    assert response.json["success"] == True
    
    proj_id = response.json["body"]
    response = client.get('/api/Project/' + str(proj_id) +'/', headers = {'Authorization': email1})
    assert response.json["success"] == True
    assert response.json["body"]["proj_id"] == proj_id
    assert response.json["body"]["name"] == proj_name
    assert response.json["body"]["author_email"] == email1

def test_create_document(client):
    proj_id = getProjID(client, email1)
    assert proj_id != -1
    response = client.post('/api/Document/' + str(proj_id) + '/', headers = {'Authorization': email1}, json = {'data': doc_body, "doc_name": doc_name})
    assert response.json["success"] == True
    
    doc_id = response.json["body"]
    response = client.get('/api/Document/' + str(proj_id) +'/' + str(doc_id) + '/', headers = {'Authorization': email1})
    assert response.json["success"] == True
    assert response.json["body"]["doc_id"] == doc_id
    assert response.json["body"]["name"] == doc_name

    response = client.get('/api/Document/' + str(proj_id) +'/' + str(doc_id) + '/getSnapshotId/', headers = {'Authorization': email1})
    assert response.json["success"] == True
    assert len(response.json["body"]) == 1
    assert response.json["body"][0]["associated_document_id"] == doc_id
    snap_id = response.json["body"][0]["snapshot_id"]
    response = client.get('/api/Snapshot/' + str(proj_id) +'/' + str(doc_id) + '/' + str(snap_id) + '/', headers = {'Authorization': email1})
    assert response.json["success"] == True
    assert response.json["body"] == doc_body

def test_permissions(client):
    proj_id = getProjID(client, email1)
    assert proj_id != -1
    doc_id = getDocID(client, proj_id, email1)
    assert proj_id != -1
    response = client.get('/api/Document/' + str(proj_id) +'/' + str(doc_id) + '/getSnapshotId/', headers = {'Authorization': email1})
    assert response.json["success"] == True

    response = client.get('/api/Document/' + str(proj_id) +'/' + str(doc_id) + '/getSnapshotId/', headers = {'Authorization': email2})
    assert response.json["success"] == False


