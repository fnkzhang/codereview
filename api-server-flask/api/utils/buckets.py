from google.cloud import storage
import google.auth
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from utils.cacheUtils import cloudStorageCache, publishTopicUpdate

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "googlecreds.json"
os.environ["GCLOUD_PROJECT"] = "codereview-413200"
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

def uploadBlob(blobName, item):
    storage_client = storage.Client()
    bucket = storage_client.bucket('cr_storage')
    print("Uploading to", blobName)
    blob = bucket.blob(blobName)
    blob.upload_from_string(data = item, content_type='application/json')

    return True

def getBlob(blobName):
    storage_client = storage.Client()
    bucket = storage_client.bucket('cr_storage')
    blob = bucket.get_blob(blobName)
    return blob.download_as_bytes()

def deleteBlob(blobName):
    storage_client = storage.Client()
    bucket = storage_client.bucket('cr_storage')
    blob = bucket.get_blob(blobName)
    if blob != None:
        blob.delete()
    return True

#location = basically the folder the files are located in
def deleteBlobsInDirectory(location):
    storage_client = storage.Client()
    bucket = storage_client.bucket('cr_storage')
    blobs = bucket.list_blobs(prefix = location)
    for blob in blobs:
        blob.delete()
    return True

def fetchFromCloudStorage(blobName:str):
    '''
    If cached, returns the blob in cache.
    If uncached, makes a request for the blob in Google Buckets
    and returns the blob.

    Args
      blobName:
        Name of the blob to retrieve.
    '''
    try:
        from utils.cacheUtils import getCloudStorageCache
        blobContents = getCloudStorageCache().get(blobName)
        if blobContents is None:
            blobContents = getBlob(blobName)
            print('uncached\n\n\n')
        else:
            print('cached\n\n\n')

        if blobContents is not None:
            getCloudStorageCache().set(blobName, blobContents)

        return blobContents
    except Exception as e:
        print(e)
        return None

def publishCloudStorageUpdate(blobName: str):
    '''
    Publishes a message with the blobName as the key to indicate that the
    specified blob has been updated. The key is used to delete the blob
    from cache.

    Args
      blobName:
        Name of the blob that was updated (created, edited, deleted)
    '''
    publishTopicUpdate("cloud-storage-updates", blobName)
    return


