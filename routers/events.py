from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from typing import List
from fastapi.encoders import jsonable_encoder
from models import Event
from database.events import (
    update_db_event,
    add_db_event,
    delete_db_event,
    get_db_event,
    get_db_events,
    get_all_db_events,
)
from tools.forecast_utilities import Forecast

router = APIRouter(
    prefix="",
    tags=["Events"],
)


@router.put(
    "/event/{event_id}",
    response_description="Update event by ID",
    response_model=Event,
)
def update_event(request: Request, event_id: str, event: Event = Body(...)):
    event = jsonable_encoder(event)
    updated_event = update_db_event(event_id, event)
    return updated_event


@router.post(  # FAILED TypeError: URL is not valid or contains user credentials.
    "{subscription_id}/event/",
    response_description="Add event to subscription",
    response_model=Event,
)
def add_event(request: Request, subscription_id: str, event: Event = Body(...)):
    event = jsonable_encoder(event)
    updated_event = add_db_event(subscription_id, event)
    return updated_event


@router.delete(
    "/event/{event_id}",
    response_description="Delete event by ID",
    response_model=int,
)
def delete_event(request: Request, event_id: str):
    deleted_event = delete_db_event(event_id)
    if deleted_event:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Subscription with ID {id} not found",
    )


@router.get(
    "/event/{event_id}",
    response_description="Get event by ID",
    response_model=Event,
)
def get_event(request: Request, event_id: str):
    event = get_db_event(event_id)
    event = Forecast(event)
    return event


@router.get(  # FAILED database.core.NotFoundError: Subscription 65e8d8cc17b2e490c9c912bc not found
    "/{subscription_id}/events",
    response_description="Get events by subscription ID",
    response_model=List[Event],
)
def get_events(request: Request, subscription_id: str):
    events = get_db_events(subscription_id)
    for event in events:
        event = Forecast(event)
    return events


@router.get(
    "/events",
    response_description="Get all events",
    response_model=List[Event],
)
def get_all_events(request: Request):
    events = get_all_db_events()
    for event in events:
        event = Forecast(event)
    return events
