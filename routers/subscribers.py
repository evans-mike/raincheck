from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from models import Subscriber
from database.subscribers import (
    create_db_subscriber,
    get_db_subscriber_by_id,
    get_db_subscriber_by_phone,
    update_db_subscriber_by_id,
    get_all_db_subscribers,
)

router = APIRouter(
    prefix="/subscriber",
    tags=["Subscribers"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_description="Add new subscriber",
    response_model=Subscriber,
)
def create_subscriber(request: Request, subscriber: Subscriber = Body(...)):
    subscriber = jsonable_encoder(subscriber)
    created_subscriber = create_db_subscriber(subscriber)
    return created_subscriber


@router.get(
    "/{subscription_id}",
    response_description="Get subscriber by ID",
    response_model=Subscriber,
)
def get_subscriber(subscription_id: str):
    subscriber = get_db_subscriber_by_id(subscription_id)
    return subscriber


@router.get(
    "/phone/{phone}",
    response_description="Get subscriber by phone",
    response_model=Subscriber,
)
def get_subscriber_by_phone(phone: str):
    subscriber = get_db_subscriber_by_phone(phone)
    return subscriber


@router.put(
    "/{subscriber_id}",
    response_description="Update subscriber by ID",
    response_model=Subscriber,
)
def update_subscriber(subscriber_id: str, subscriber: Subscriber = Body(...)):
    subscriber = jsonable_encoder(subscriber)
    updated_subscriber = update_db_subscriber_by_id(subscriber_id, subscriber)
    return updated_subscriber


@router.get(  # FAILED database.core.NotFoundError: Subscription all not found
    "/all",
    response_description="Get all subscribers",
    response_model=List[Subscriber],
)
def get_all_subscribers():
    subscribers = get_all_db_subscribers()
    return subscribers
