from fastapi import APIRouter, Body, Request, Response, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from typing import List, Annotated
from bson.objectid import ObjectId
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from models import Event, Subscriber, Subscription, Time, Place
from database.core import DB, NotFoundError
from database.subscribers import (
    create_db_subscriber,
    get_db_subscriber_by_id,
    get_db_subscriber_by_phone,
    update_db_subscriber_by_id,
    update_db_subscriber_by_phone,
    get_all_db_subscribers,
)

router = APIRouter(
    prefix="/subscribers",
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
    "/{subscriber_id}",
    response_description="Get subscriber by ID",
    response_model=Subscriber,
)
def get_subscriber(subscriber_id: str):
    subscriber = get_db_subscriber_by_id(subscriber_id)
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


@router.put(
    "/phone/{phone}",
    response_description="Update subscriber by phone",
    response_model=Subscriber,
)
def update_subscriber_by_phone(phone: str, subscriber: Subscriber = Body(...)):
    subscriber = jsonable_encoder(subscriber)
    updated_subscriber = update_db_subscriber_by_phone(phone, subscriber)
    return updated_subscriber


# GET all subscribers
@router.get(
    "/",
    response_description="Get all subscribers",
    response_model=List[Subscriber],
)
def get_all_subscribers():
    subscribers = get_all_db_subscribers()
    return subscribers
