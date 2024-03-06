from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from models import Subscription
from database.subscriptions import (
    create_db_subscription,
    get_db_subscription,
    get_db_subscription_by_phone,
    get_all_db_subscriptions,
    delete_db_subscription,
)

router = APIRouter(
    prefix="",
    tags=["Subscriptions"],
)


@router.post(
    "/",
    response_description="Create a new subscription",
    status_code=status.HTTP_201_CREATED,
    response_model=Subscription,
)
def create_subscription(request: Request, subscription: Subscription = Body(...)):

    subscription = jsonable_encoder(subscription)
    created_subscription = create_db_subscription(subscription)
    return created_subscription


@router.get(
    "/{subscription_id}",
    response_description="Get subscription by subscription_id",
    status_code=status.HTTP_200_OK,
    response_model=Subscription,
)
def get_subscription(request: Request, subscription_id: str):

    if (subscription := get_db_subscription(subscription_id)) is not None:
        return subscription
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Subscription with subscription_id {subscription_id} not found",
    )


@router.get(
    "/phone/{phone}",
    response_description="Get subscription by phone number",
    status_code=status.HTTP_200_OK,
    response_model=Subscription,
)
def get_subscription_by_phone(request: Request, phone: str):

    if (subscription := get_db_subscription_by_phone(phone)) is not None:
        return subscription
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Subscription with phone {phone} not found",
    )


@router.get(  # FAILED database.core.NotFoundError: Subscription all not found
    "/all",
    response_description="List all subscriptions",
    status_code=status.HTTP_200_OK,
    response_model=List[Subscription],
)
def get_all_subscriptions(request: Request):

    subscriptions = get_all_db_subscriptions()
    return subscriptions


@router.delete(
    "/{subscription_id}",
    response_description="Delete a subscription",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_subscription(subscription_id: str, request: Request):

    deleted_subscription = delete_db_subscription(subscription_id)
    if deleted_subscription:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Subscription with subscription_id {subscription_id} not found",
    )
