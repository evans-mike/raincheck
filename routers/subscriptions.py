from fastapi import APIRouter, Body, Request, Response, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from typing import List, Annotated
from bson.objectid import ObjectId
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from models import Event, Subscriber, Subscription, Time, Place
from database.core import DB, NotFoundError
from database.subscriptions import (
    create_db_subscription,
    get_db_subscription,
    update_db_subscription,
    get_all_db_subscriptions,
    delete_db_subscription,
)

router = APIRouter(
    prefix="/subscriptions",
)


#######auth########

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# def fake_decode_token(token):
#     return User(
#         username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
#     )

# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     user = fake_decode_token(token)
#     return user


# @router.get("/users/me")
# async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
#     return current_user

##############


@router.post(
    "/subscriber",
    response_description="Create a new subscriber",
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
    response_model=Subscription,
)
def create_subscriber(subscriber: Subscriber = Body(...)):
    subscriber = jsonable_encoder(subscriber)
    created_subscriber = Subscriber.create_subscriber(subscriber)
    return created_subscriber


# this one has been refactored with database.subscriptions abstract methods
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


@router.post(
    "/{id}/event",
    response_description="Create a new subscriber event",
    status_code=status.HTTP_201_CREATED,
    # response_model=Event, # WIP: would like to enforce a response model
)
def create_event(request: Request, id: str, body: Event = Body(...)):

    result = request.app.database["subscriptions"].find_one({"_id": id})
    body = jsonable_encoder(body)
    body["_event_id"] = str(ObjectId())

    request.app.database["subscriptions"].update_one(
        {"_id": id}, {"$push": {"events": body}}
    )

    if (
        result := request.app.database["subscriptions"].find_one(
            {"events": {"$elemMatch": {"_event_id": body["_event_id"]}}},
            {"events.$": 1},
        )
    ) is not None:
        return result
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Event with ID {body['_event_id']} not found",
    )


@router.get(
    "/{id}/events",
    response_description="Get events by subscriber_id",
    # response_model=List[Event], # WIP: would like to enforce a response model
)
def fetch_subscriber_events(id: str, request: Request):

    if (
        result := request.app.database["subscriptions"].find_one(
            {"_id": id}, {"events": 1}
        )
    ) is not None:
        return result
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Subscription with ID {id} not found",
    )


# PUT endpoint for updating an event
@router.put(
    "/{id}/event/{event_id}",
    response_description="Update an event",
    response_model=Event,
)
def update_event(id: str, event_id: str, request: Request, event: Event = Body(...)):

    updated_event = request.app.database["subscriptions"].update_one(
        {"_id": id, "events._event_id": event_id}, {"$set": {"events.$": event}}
    )
    if updated_event.modified_count == 0:
        raise HTTPException(
            status_code=404, detail=f"Event with id {event_id} not found"
        )

    return request.app.database["subscriptions"].find_one(
        {"_id": id, "events._event_id": event_id}, {"events.$": 1}
    )


# @router.delete("/event/{id}", response_description="Delete a event")
# def delete_event(id: str, request: Request, response: Response):
#     delete_result = request.app.database["subscriptions"].delete_one({"_id": id})

#     if delete_result.deleted_count == 1:
#         response.status_code = status.HTTP_204_NO_CONTENT
#         return response

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID {id} not found")


# @router.post(
#     "/event/{id}/place",
#     response_description="Update event place",
#     status_code=status.HTTP_201_CREATED,
#     response_model=Place,
# )
# def set_place(request: Request, id: str, place: Place = Body(...)):

#     event = request.app.database["subscriptions"].find_one({"_id": id})
#     event["place"] = jsonable_encoder(place)

#     updated_event = fetch_new_forecast(event)

#     request.app.database["subscriptions"].update_one(
#         {"_id": id}, {"$set": {"place": event["place"], "forecast": event["forecast"]}}
#     )

#     return updated_event["place"]


# @router.put("/event/{id}/place/{placeId}", response_description="Update a place", response_model=Place)
# def update_place(placeId: str, request: Request, place: Place = Body(...)):

#     place = {k: v for k, v in place.dict().items() if v is not None}
#     if len(place) >= 1:
#         update_result = request.app.database["places"].update_one(
#             {"_id": placeId}, {"$set": place}
#         )

#         if update_result.modified_count == 0:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Place with ID {placeId} not found")

#     if (
#         existing_place := request.app.database["places"].find_one({"_id": placeId})
#     ) is not None:
#         return existing_place

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Place with ID {placeId} not found")


# @router.delete("/event/{id}/place/{placeId}", response_description="Delete a place")
# def delete_place(id: str, request: Request, response: Response):
#     delete_result = request.app.database["places"].delete_one({"_id": placeId})

#     if delete_result.deleted_count == 1:
#         response.status_code = status.HTTP_204_NO_CONTENT
#         return response

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Place with ID {placeId} not found")


# @router.post(
#     "/event/{id}/subscriber",
#     response_description="Create a new subscriber",
#     status_code=status.HTTP_201_CREATED,
#     response_model=Subscriber,
# )
# def set_subscriber(request: Request, id: str, subscriber: Subscriber = Body(...)):

#     subscriber = jsonable_encoder(subscriber)
#     new_subscriber = request.app.database["subscriptions"].update_one(
#         {"_id": id}, {"$set": {"subscriber": subscriber}}
#     )
#     updated_event = request.app.database["subscriptions"].find_one({"_id": id})

#     return updated_event["subscriber"]


# @router.get("/event/{id}/subscribers", response_description="List all subscribers", response_model=List[Subscriber])
# def list_subscribers(request: Request):

#     subscribers = list(request.app.database["subscribers"].find({"id": id}))
#     return subscribers


# @router.get("/event/{id}/subscriber/{id}", response_description="Get a single subscriber by id", response_model=Subscriber)
# def find_subscriber(id: str, request: Request):

#     if (subscriber := request.app.database["subscribers"].find_one({"_id": id})) is not None:
#         return subscriber
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscriber with ID {id} not found")


# @router.put("/event/{id}/subscriber/{id}", response_description="Update a subscriber", response_model=Subscriber)
# def update_subscriber(id: str, request: Request, subscriber: Subscriber = Body(...)):

#     subscriber = {k: v for k, v in subscriber.dict().items() if v is not None}
#     if len(subscriber) >= 1:
#         update_result = request.app.database["subscriber"].update_one(
#             {"_id": id}, {"$set": subscriber}
#         )

#         if update_result.modified_count == 0:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscriber with ID {id} not found")

#     if (
#         existing_subscriber := request.app.database["subscriber"].find_one({"_id": id})
#     ) is not None:
#         return existing_subscriber

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Place with ID {id} not found")


# @router.delete("/event/{id}/subscriber/{id}", response_description="Delete a subscriber")
# def delete_place(id: str, request: Request, response: Response):
#     delete_result = request.app.database["subscribers"].delete_one({"_id": id})

#     if delete_result.deleted_count == 1:
#         response.status_code = status.HTTP_204_NO_CONTENT
#         return response

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscriber with ID {id} not found")


# @router.post(
#     "/event/{id}/time",
#     response_description="Update event time",
#     status_code=status.HTTP_201_CREATED,
#     response_model=Time,
# )
# def set_time(request: Request, id: str, time: Time = Body(...)):

#     event = request.app.database["subscriptions"].find_one({"_id": id})
#     event = jsonable_encoder(event)
#     event["time"] = jsonable_encoder(time)

#     updated_event = fetch_new_forecast(event)

#     request.app.database["subscriptions"].update_one(
#         {"_id": id}, {"$set": {"time": event["place"], "forecast": event["forecast"]}}
#     )

#     return updated_event["time"]


# @router.get("/event/{id}/times", response_description="List all times", response_model=List[Time])
# def list_times(request: Request):

#     times = list(request.app.database["times"].find({"id": id}))
#     return times


# @router.get("/event/{id}/time/{timeId}", response_description="Get a single time by id", response_model=Time)
# def find_time(id: str, request: Request):

#     if (time := request.app.database["times"].find_one({"_id": timeId})) is not None:
#         return time
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Time with ID {timeId} not found")


# @router.put("/event/{id}/time/{timeId}", response_description="Update a time", response_model=Time)
# def update_time(id: str, request: Request, time: Time = Body(...)):

#     time = {k: v for k, v in time.dict().items() if v is not None}
#     if len(time) >= 1:
#         update_result = request.app.database["time"].update_one(
#             {"_id": timeId}, {"$set": time}
#         )

#         if update_result.modified_count == 0:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Time with ID {timeId} not found")

#     if (
#         existing_time := request.app.database["time"].find_one({"_id": timeId})
#     ) is not None:
#         return existing_time

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Place with ID {timeId} not found")


# @router.delete("/event/{id}/time/{timeId}", response_description="Delete a time")
# def delete_place(id: str, request: Request, response: Response):
#     delete_result = request.app.database["times"].delete_one({"_id": timeId})

#     if delete_result.deleted_count == 1:
#         response.status_code = status.HTTP_204_NO_CONTENT
#         return response

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Time with ID {timeId} not found")
