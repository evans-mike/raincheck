from .core import DB, NotFoundError
from models import Event

db = DB()


def update_db_event(event_id: str, event: Event):
    result = db.database.events.update_one
    (
        {"event_id": event_id},
        {"$set": event},
    )
    return event


def add_db_event(subscription_id: str, event: Event):
    subscription = db.database.subscriptions.find_one({"_id": subscription_id})
    if subscription is None:
        raise NotFoundError(f"Subscription {subscription_id} not found")
    db.database.subscriptions.update_one(
        {"_id": subscription_id}, {"$set": {"events": event}}
    )
    return event


def delete_db_event(event_id: str):
    result = db.database.events.delete_one({"event_id": event_id})
    if result.deleted_count == 0:
        raise NotFoundError(f"Event {event_id} not found")
    return result.deleted_count


def get_db_event(event_id: str):
    event = db.database.events.find_one({"event_id": event_id})
    if event is None:
        raise NotFoundError(f"Event {event_id} not found")
    return event


def get_db_events(
    subscription_id: str,
):  # FAILED database.core.NotFoundError: Subscription 65e8d8cc17b2e490c9c912bc not found
    subscription = db.database.subscriptions.find_one({"_id": subscription_id})
    if subscription is None:
        raise NotFoundError(f"Subscription {subscription_id} not found")
    return subscription["events"]


def get_all_db_events():
    events = db.database.events.find(
        {"events": {"$exists": "true"}}, {"events": "true"}
    )
    return events
