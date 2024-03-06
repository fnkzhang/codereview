from flask_caching import Cache
from google.cloud import pubsub_v1

"""
-------------------------------------------------------------------------------
Caching Configs for Per-Instance Cache (currently empty)
    "CACHE_TYPE": "SimpleCache"
-------------------------------------------------------------------------------
"""

"""
-------------------------------------------------------------------------------
Caching Configs for Shared Cache
    "CACHE_TYPE": "FileSystemCache"
-------------------------------------------------------------------------------
"""

cacheRoot = "./../cr_cache"
project_id = "codereview-413200"
subscriber = pubsub_v1.SubscriberClient()
publisher = pubsub_v1.PublisherClient()

documentCacheConfig = {
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DIR": f"{cacheRoot}/documents",
    "CACHE_THRESHOLD": 200
}
documentCache = Cache(config=documentCacheConfig)

diffCacheConfig = {
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DIR": f"{cacheRoot}/diffs",
    "CACHE_THRESHOLD": 200
}
diffCache = Cache(config=diffCacheConfig)

commentsCacheConfig = {
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DIR": f"{cacheRoot}/comments",
    "CACHE_THRESHOLD": 200
}
commentsCache = Cache(config=commentsCacheConfig)

"""
-------------------------------------------------------------------------------
Initializing Caches
-------------------------------------------------------------------------------
"""

def initCaches(app):
    # initialize per-instance cache (currently empty)

    # initialize shared cache
    documentCache.init_app(app)
    diffCache.init_app(app)
    commentsCache.init_app(app)
    subscribeToTopicUpdates()
    return

"""
-------------------------------------------------------------------------------
Pub/Sub Helper Functions
-------------------------------------------------------------------------------
"""

def subscribeToTopicUpdates():
    subscribeToTopicUpdate("document-updates", documentCache)
    subscribeToTopicUpdate("diff-updates", diffCache)
    subscribeToTopicUpdate("comment-updates", commentsCache)

def subscribeToTopicUpdate(topic_id, cacheToUpdate):
    '''
    Subscriber receives the key as a message by the Topic's Publisher and
    deletes the key from cache. Caching prevents repetitive requests to Google
    Buckets and Cloud SQL when a resource has not been updated. Deleting the
    key from cache will force a request for the updated resource.

    Parameters
    ----------
    topic_id: str
        Topic ID Column in https://console.cloud.google.com/cloudpubsub/topic.
        Make sure there is a Subscription with the same name suffixed with
        a "-sub" in https://console.cloud.google.com/cloudpubsub/subscription.
    cacheToUpdate: Cache
        Cache Object of type FileSystemCache.
    '''
    def handleTopicUpdate(message):
        key = message.data.decode()
        cacheToUpdate.delete(key)

        message.ack()
        return

    subscriptionPath = subscriber \
        .subscription_path(project_id, f"{topic_id}-sub")
    
    subscriber.subscribe(subscriptionPath, handleTopicUpdate)
    return

"""
-------------------------------------------------------------------------------
Pub/Sub Functions
-------------------------------------------------------------------------------
"""

def publishTopicUpdate(topic_id, key):
    '''
    Publisher sends the key to the Topic to indicate that the resource was
    updated. Any Subscribers that are subscribed to the Topic will receive the
    key.
    
    Parameters
    ----------
    topic_id: str
        Topic ID Column in https://console.cloud.google.com/cloudpubsub/topic.
        Make sure there is a Subscription with the same name suffixed with
        a "-sub" in https://console.cloud.google.com/cloudpubsub/subscription.
    key: str
        Unique identifier of the updated resource
    '''
    topicPath = publisher \
        .topic_path(project_id, topic_id)

    message = key.encode()
    publisher.publish(topicPath, message)
    return
