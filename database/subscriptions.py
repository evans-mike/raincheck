from typing import Optional
from pydantic import BaseModel
from .core import DB, NotFoundError
from models import Event, Subscriber, Subscription, Time, Place

db = DB()


def create_db_subscription(subscription: Subscription):
    db.database.subscriptions.insert_one(subscription)
    return subscription


def get_db_subscription(subscription_id: str):
    subscription = db.database.subscriptions.find_one({"_id": subscription_id})
    if subscription is None:
        raise NotFoundError(f"Subscription {subscription_id} not found")
    return subscription


def update_db_subscription(subscription_id: str, subscription: Subscription):
    result = db.database.subscriptions.replace_one(
        {"_id": subscription_id}, subscription
    )
    if result.modified_count == 0:
        raise NotFoundError(f"Subscription {subscription_id} not found")
    return subscription


def get_all_db_subscriptions():
    subscriptions = db.database.subscriptions.find()
    return subscriptions


def delete_db_subscription(subscription_id: str):
    result = db.database.subscriptions.delete_one({"_id": subscription_id})
    if result.deleted_count == 0:
        raise NotFoundError(f"Subscription {subscription_id} not found")
    return result.deleted_count
