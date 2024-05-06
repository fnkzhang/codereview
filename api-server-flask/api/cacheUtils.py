from app import get_app
from flask_caching import Cache
from google.cloud import pubsub_v1

from flask import Flask

#------------------------------------------------------------------------------
# Pub/Sub
#-------------------------------------------------------------------------------

subscriber = pubsub_v1.SubscriberClient()
def subscribeToTopicUpdate(topic_id: str,
                           cacheToUpdate: Cache):
    '''
    Subscriber receives the key as a message by the Topic's Publisher and
    deletes the key from cache. Caching prevents repetitive requests to Google
    Buckets and Cloud SQL when a resource has not been updated. Deleting the
    key from cache will force a request for the updated resource.

    Args
      topic_id:
        Topic ID Column in https://console.cloud.google.com/cloudpubsub/topic.
        Make sure there is a Subscription with the same name suffixed with
        a "-sub" in https://console.cloud.google.com/cloudpubsub/subscription.
      cacheToUpdate:
        The cache from which the key will be removed.
    '''
    def handleTopicUpdate(message):
        key = message.data.decode()
        message.ack()

        if cacheToUpdate.has(key):
            cacheToUpdate.delete(key)

        return

    subscriptionPath = subscriber \
        .subscription_path(PROJECT_ID, f"{topic_id}-sub")
    
    subscriber.subscribe(subscriptionPath, handleTopicUpdate)
    return

publisher = pubsub_v1.PublisherClient()
def publishTopicUpdate(topic_id: str,
                       key: str):
    '''
    Publisher sends the key to the Topic to indicate that the resource was
    updated. Any Subscribers that are subscribed to the Topic will receive the
    key.
    
    Args
      topic_id:
        Topic ID Column in https://console.cloud.google.com/cloudpubsub/topic.
        Make sure there is a Subscription with the same name suffixed with
        a "-sub" in https://console.cloud.google.com/cloudpubsub/subscription.
      key:
        Unique identifier of the updated resource. Must be the same as the
        key used to cache the resource.
    '''
    topicPath = publisher \
        .topic_path(PROJECT_ID, topic_id)

    message = key.encode()
    publisher.publish(topicPath, message)
    return


#------------------------------------------------------------------------------
# Caching Configs for Per-Instance Cache (currently empty)
#-------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Caching Configs for Shared Cache
#-------------------------------------------------------------------------------

CACHE_ROOT = "./../cr_cache"
PROJECT_ID = "codereview-413200"

GCLOUD_STORAGE_CACHE_CONFIG = {
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DEFAULT_TIMEOUT": 60,
    "CACHE_THRESHOLD": 500,
    "CACHE_DIR": f"{CACHE_ROOT}/GCloud_Storage"
}

#------------------------------------------------------------------------------
# Initializing Caches
#-------------------------------------------------------------------------------

def initSharedCache(topic_id: str,
                    cacheConfig: dict):
    '''
    Publisher sends the key to the Topic to indicate that the resource was
    updated. Any Subscribers that are subscribed to the Topic will receive the
    key.
    
    Args
      topic_id:
        Topic ID Column in https://console.cloud.google.com/cloudpubsub/topic.
        Make sure there is a Subscription with the same name suffixed with
        a "-sub" in https://console.cloud.google.com/cloudpubsub/subscription.
      key:
        Unique identifier of the updated resource. Must be the same as the
        key used to cache the resource.
    '''
    cache = Cache(get_app(__name__), config=cacheConfig)
    subscribeToTopicUpdate(topic_id, cache)
    
    return cache

cloudStorageCache = None
def getCloudStorageCache():
    global cloudStorageCache
    if cloudStorageCache is None:
        cloudStorageCache = initSharedCache("cloud-storage-updates",
                                            GCLOUD_STORAGE_CACHE_CONFIG)
    return cloudStorageCache