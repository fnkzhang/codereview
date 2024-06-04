from google.cloud import storage
import google.auth
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from utils.cacheUtils import cloudStorageCache, publishTopicUpdate
from dotenv import dotenv_values

BUCKET_NAME = dotenv_values('.env')["BUCKET_NAME"]
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "googlecreds.json"
#os.environ["GCLOUD_PROJECT"] = "codereview-413200"
#CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

def uploadBlob(blobName, item):
    """

    **Explanation:**
        Uploads a blob to Google Buckets

    **Args:**
        - blobName (str): name of the blob
        - item (str): blob contents

    **Returns:**
        -True

    """
    storage_client = storage.Client()
    print(BUCKET_NAME)
    bucket = storage_client.bucket(BUCKET_NAME)
    print("Uploading to", blobName)
    blob = bucket.blob(blobName)
    blob.upload_from_string(data = item)

    return True

def getBlob(blobName):
    """

    **Explanation:**
        Gets a blob to Google Buckets

    **Args:**
        - blobName (str): name of the blob

    **Returns:**
        -blobcontents (bytes): Contents of the blob in bytes

    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.get_blob(blobName)
    return blob.download_as_bytes()

def deleteBlob(blobName):
    """

    **Explanation:**
        Deletes a blob in Google Buckets

    **Args:**
        - blobName (str): name of the blob

    **Returns:**
        -True

    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.get_blob(blobName)
        if blob != None:
            blob.delete()
    except:
        pass
    return True

def fetchFromCloudStorage(blobName:str):
    '''
    **Explanation:**

    If cached, returns the blob in cache.
    If uncached, makes a request for the blob in Google Buckets
    and returns the blob.

    **Args:**
        -blobName (str): Name of the blob to retrieve.

    **Returns:**
        -blobContents (bytes): Contents of the blob in bytes
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
    **Explanation:**

    Publishes a message with the blobName as the key to indicate that the
    specified blob has been updated. The key is used to delete the blob
    from cache.

    **Args:**
        -blobName (str): Name of the blob that was updated (created, edited, deleted)
    '''
    publishTopicUpdate("cloud-storage-updates", blobName)
    return


