from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Event, Place, PlaceUpdate, Subscriber, SubscriberUpdate, Time, TimeUpdate

router = APIRouter()

# TODO: consolidate everything into the events database and use update_one and $set and $push
# TODO: add checks to see if eventId exists

@router.post("/event", response_description="Create a new event", status_code=status.HTTP_201_CREATED, response_model=Event)
def create_event(request: Request, event: Event = Body(...)):

    event = jsonable_encoder(event)
    new_event = request.app.database["events"].insert_one(event)
    created_event = request.app.database["events"].find_one(
        {"_id": new_event.inserted_id}
    )

    return created_event


@router.get("/events", response_description="List all events", response_model=List[Event])
def list_events(request: Request):

    events = list(request.app.database["events"].find(limit=100))
    return events


@router.get("/event/{eventId}", response_description="Get a single event by id", response_model=Event)
def find_event(eventId: str, request: Request):

    if (event := request.app.database["events"].find_one({"_id": eventId})) is not None:
        return event
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID {eventId} not found")


# @router.delete("/event/{eventId}", response_description="Delete a event")
# def delete_event(id: str, request: Request, response: Response):
#     delete_result = request.app.database["events"].delete_one({"_id": eventId})

#     if delete_result.deleted_count == 1:
#         response.status_code = status.HTTP_204_NO_CONTENT
#         return response

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID {eventId} not found")


@router.post("/event/{eventId}/place", response_description="Create a new place", status_code=status.HTTP_201_CREATED, response_model=Place)
def create_place(request: Request, place: Place = Body(...)):

    place = jsonable_encoder(place)
    place['lat'], place['lon'] = Place.get_lat_lon_for_address(place['address'])
    place['gridId'], place['gridX'], place['gridY'] = Place.get_gridpoints_by_lat_lon(place['lat'], place['lon'])
    new_place = request.app.database["places"].insert_one(place)
    created_place = request.app.database["places"].find_one(
        {"_id": new_place.inserted_id}
    )

    return created_place


@router.get("/event/{eventId}/places", response_description="List all places", response_model=List[Place])
def list_places(request: Request):

    places = list(request.app.database["places"].find({"eventId": eventId}))
    return places


@router.get("/event/{eventId}/place/{placeId}", response_description="Get a single place by id", response_model=Place)
def find_place(placeId: str, request: Request):

    if (place := request.app.database["places"].find_one({"_id": placeId})) is not None:
        return place
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Place with ID {placeId} not found")


@router.put("/event/{eventId}/place/{placeId}", response_description="Update a place", response_model=Place)
def update_place(placeId: str, request: Request, place: PlaceUpdate = Body(...)):
    
    place = {k: v for k, v in place.dict().items() if v is not None}
    if len(place) >= 1:
        update_result = request.app.database["places"].update_one(
            {"_id": placeId}, {"$set": place}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Place with ID {placeId} not found")

    if (
        existing_place := request.app.database["places"].find_one({"_id": placeId})
    ) is not None:
        return existing_place

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Place with ID {placeId} not found")


# @router.delete("/event/{eventId}/place/{placeId}", response_description="Delete a place")
# def delete_place(id: str, request: Request, response: Response):
#     delete_result = request.app.database["places"].delete_one({"_id": placeId})

#     if delete_result.deleted_count == 1:
#         response.status_code = status.HTTP_204_NO_CONTENT
#         return response

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Place with ID {placeId} not found")


@router.post("/event/{eventId}/subscriber", response_description="Create a new subscriber", status_code=status.HTTP_201_CREATED, response_model=Subscriber)
def create_subscriber(request: Request, subscriber: Subscriber = Body(...)):

    subscriber = jsonable_encoder(subscriber)
    new_subscriber = request.app.database["subscribers"].insert_one(subscriber)
    created_subscriber = request.app.database["subscribers"].find_one(
        {"_id": new_subscriber.inserted_id}
    )

    return created_subscriber


@router.get("/event/{eventId}/subscribers", response_description="List all subscribers", response_model=List[Subscriber])
def list_subscribers(request: Request):

    subscribers = list(request.app.database["subscribers"].find({"eventId": eventId}))
    return subscribers


@router.get("/event/{eventId}/subscriber/{id}", response_description="Get a single subscriber by id", response_model=Subscriber)
def find_subscriber(id: str, request: Request):

    if (subscriber := request.app.database["subscribers"].find_one({"_id": id})) is not None:
        return subscriber
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscriber with ID {id} not found")


@router.put("/event/{eventId}/subscriber/{id}", response_description="Update a subscriber", response_model=Subscriber)
def update_subscriber(id: str, request: Request, subscriber: SubscriberUpdate = Body(...)):
    
    subscriber = {k: v for k, v in subscriber.dict().items() if v is not None}
    if len(subscriber) >= 1:
        update_result = request.app.database["subscriber"].update_one(
            {"_id": id}, {"$set": subscriber}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscriber with ID {id} not found")

    if (
        existing_subscriber := request.app.database["subscriber"].find_one({"_id": id})
    ) is not None:
        return existing_subscriber

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Place with ID {id} not found")


# @router.delete("/event/{eventId}/subscriber/{id}", response_description="Delete a subscriber")
# def delete_place(id: str, request: Request, response: Response):
#     delete_result = request.app.database["subscribers"].delete_one({"_id": id})

#     if delete_result.deleted_count == 1:
#         response.status_code = status.HTTP_204_NO_CONTENT
#         return response

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscriber with ID {id} not found")


@router.post("/event/{eventId}/time", response_description="Create a new time", status_code=status.HTTP_201_CREATED, response_model=Time)
def create_time(request: Request, time: Time = Body(...)):

    time = jsonable_encoder(time)
    new_time = request.app.database["times"].insert_one(time)
    created_time = request.app.database["times"].find_one(
        {"_id": new_time.inserted_id}
    )

    return created_time


@router.get("/event/{eventId}/times", response_description="List all times", response_model=List[Time])
def list_times(request: Request):

    times = list(request.app.database["times"].find({"eventId": eventId}))
    return times


@router.get("/event/{eventId}/time/{timeId}", response_description="Get a single time by id", response_model=Time)
def find_time(id: str, request: Request):

    if (time := request.app.database["times"].find_one({"_id": timeId})) is not None:
        return time
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Time with ID {timeId} not found")


@router.put("/event/{eventId}/time/{timeId}", response_description="Update a time", response_model=Time)
def update_time(id: str, request: Request, time: TimeUpdate = Body(...)):
    
    time = {k: v for k, v in time.dict().items() if v is not None}
    if len(time) >= 1:
        update_result = request.app.database["time"].update_one(
            {"_id": timeId}, {"$set": time}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Time with ID {timeId} not found")

    if (
        existing_time := request.app.database["time"].find_one({"_id": timeId})
    ) is not None:
        return existing_time

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Place with ID {timeId} not found")


# @router.delete("/event/{eventId}/time/{timeId}", response_description="Delete a time")
# def delete_place(id: str, request: Request, response: Response):
#     delete_result = request.app.database["times"].delete_one({"_id": timeId})

#     if delete_result.deleted_count == 1:
#         response.status_code = status.HTTP_204_NO_CONTENT
#         return response

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Time with ID {timeId} not found")