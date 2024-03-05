from flask_caching import Cache
from google.cloud import pubsub_v1

subscriber = pubsub_v1.SubscriberClient()
publisher = pubsub_v1.PublisherClient()

cacheConfig = {
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DIR": "./../cr_cache",
    "CACHE_THRESHOLD": 500
}

"""
Caching
"""
def initCache(app):
    global cache
    cache = Cache(app, config=cacheConfig)

    subscribeToTopics()
    return

def getValueFromCache(key):
    return cache.get(key)

def addToCacheWithTimeout(key, value, timeout):
    cache.set(key, value, timeout)
    return

def deleteValueFromCache(key):
    cache.delete(key)
    return

"""
Pub/Sub
"""
def subscribeToTopics():
    subscribeToDocumentUpdate()
    return

"""
Pub/Sub for Document Updates
"""
def subscribeToDocumentUpdate():
    def handleDocumentUpdate(message):
        doc_id = message.data.decode()
        cache.delete(doc_id)

        message.ack()
        return

    subscriptionPath = subscriber \
        .subscription_path("codereview-413200", "document-updates-sub")
    
    subscriber.subscribe(subscriptionPath, handleDocumentUpdate)
    return

def publishDocumentUpdate(doc_id):
    topicPath = publisher \
        .topic_path("codereview-413200", "document-updates")

    message = doc_id.encode()
    publisher.publish(topicPath, message)
    return
