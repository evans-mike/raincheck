from bson.objectid import ObjectId
from .core import DB, NotFoundError
from models import Subscriber

db = DB()


def create_db_subscriber(subscriber: Subscriber):
    """
    Create a new subscription with only a subscriber.
    """
    subscription = {}
    subscription["_id"] = str(ObjectId())
    subscription["subscriber"] = subscriber
    db.database.subscriptions.insert_one(subscription)
    return subscription["subscriber"]


def get_db_subscriber_by_id(subscription_id: str):
    subscription = db.database.subscriptions.find_one({"_id": subscription_id})
    if subscription is None:
        raise NotFoundError(f"Subscription {subscription_id} not found")
    return subscription["subscriber"]


def get_db_subscriber_by_phone(phone: str):
    subscription = db.database.subscriptions.find_one({"subscriber.phone": phone})
    if subscription is None:
        raise NotFoundError(f"Subscription with phone {phone} not found")
    return subscription["subscriber"]


def update_db_subscriber_by_id(subscription_id: str, subscriber: Subscriber):
    subscription = db.database.subscriptions.find_one({"_id": subscription_id})
    if subscription is None:
        raise NotFoundError(f"Subscription {subscription_id} not found")
    subscription["subscriber"] = subscriber
    db.database.subscriptions.update_one(
        {"_id": subscription_id}, {"$set": subscription}
    )
    return subscriber


def get_all_db_subscribers():  # FAILED database.core.NotFoundError: Subscription all not found
    subscriptions = db.database.subscriptions.find(
        {"subscriber": {"$exists": "true"}}, {"subscriber": "true"}
    )

    return subscriptions
