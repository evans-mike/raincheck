from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from bson.objectid import ObjectId

from models import Event, EventUpdate, Place, Subscriber, Time, Forecast

router = APIRouter()


def fetch_new_forecast(event: dict):
    """
    Base method to take an event dict and fetch a new forecast
    """
    place = event["place"]
    place['lat'], place['lon'] = Place.get_lat_lon_for_address(place['address'])
    place['gridId'], place['gridX'], place['gridY'] = Place.get_gridpoints_by_lat_lon(place['lat'], place['lon'])

    time = event['time']

    forecast = Forecast.get_forecast_for_time_and_place(place['gridId'], place['gridX'], place['gridY'], time['startDateTime'])
    # TODO: need some rules around this
    event['forecast'] = forecast

    return event


@router.post("/event", response_description="Create a new event", status_code=status.HTTP_201_CREATED, response_model=Event)
def create_event(request: Request, event: Event = Body(...)): # can be empty request

    event = jsonable_encoder(event)
    event["_id"] = str(ObjectId())

    event = fetch_new_forecast(event)

    new_event = request.app.database["events"].insert_one(event) # note this is the only place where we insert_one new document
    created_event = request.app.database["events"].find_one(
        {"_id": new_event.inserted_id}
    )

    return created_event


@router.get("/events", response_description="List all events", response_model=List[Event])
def list_events(request: Request):

    events = list(request.app.database["events"].find(limit=100))
    return events


@router.get("/event/{id}", response_description="Get a single event by id", response_model=Event)
def find_event(id: str, request: Request):

    if (event := request.app.database["events"].find_one({"_id": id})) is not None:
        return event
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID {id} not found")


# @router.delete("/event/{id}", response_description="Delete a event")
# def delete_event(id: str, request: Request, response: Response):
#     delete_result = request.app.database["events"].delete_one({"_id": id})

#     if delete_result.deleted_count == 1:
#         response.status_code = status.HTTP_204_NO_CONTENT
#         return response

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID {id} not found")


@router.post("/event/{id}/place", response_description="Update event place", status_code=status.HTTP_201_CREATED, response_model=Place)
def set_place(request: Request, id: str, place: Place = Body(...)):

    event = request.app.database["events"].find_one(
        {"_id": id}
    )
    event['place'] = jsonable_encoder(place)

    updated_event = fetch_new_forecast(event)

    request.app.database["events"].update_one(
        {"_id": id},
        {"$set": {"place": event['place'], "forecast": event['forecast']}}
        )

    return updated_event['place']


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


@router.post("/event/{id}/subscriber", response_description="Create a new subscriber", status_code=status.HTTP_201_CREATED, response_model=Subscriber)
def set_subscriber(request: Request, id: str, subscriber: Subscriber = Body(...)):

    subscriber = jsonable_encoder(subscriber)
    new_subscriber = request.app.database["events"].update_one(
        {"_id": id},
        {"$set": {"subscriber": subscriber}}
        )
    updated_event = request.app.database["events"].find_one(
        {"_id": id}
    )

    return updated_event['subscriber']


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


@router.post("/event/{id}/time", response_description="Update event time", status_code=status.HTTP_201_CREATED, response_model=Time)
def set_time(request: Request, id: str, time: Time = Body(...)):

    event = request.app.database["events"].find_one(
        {"_id": id}
    )
    event = jsonable_encoder(event)
    event['time'] = jsonable_encoder(time)

    updated_event = fetch_new_forecast(event)

    request.app.database["events"].update_one(
        {"_id": id},
        {"$set": {"time": event['place'], "forecast": event['forecast']}}
        )

    return updated_event['time']


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