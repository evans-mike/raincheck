from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Location, LocationUpdate

router = APIRouter()


@router.post("/", response_description="Create a new location", status_code=status.HTTP_201_CREATED, response_model=Location)
def create_location(request: Request, location: Location = Body(...)):

    location = jsonable_encoder(location)
    new_location = request.app.database["locations"].insert_one(location)
    created_location = request.app.database["locations"].find_one(
        {"_id": new_location.inserted_id}
    )

    return created_location


@router.get("/", response_description="List all locations", response_model=List[Location])
def list_locations(request: Request):

    locations = list(request.app.database["locations"].find(limit=100))
    return locations


@router.get("/{id}", response_description="Get a single location by id", response_model=Location)
def find_location(id: str, request: Request):

    if (location := request.app.database["locations"].find_one({"_id": id})) is not None:
        return location
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Location with ID {id} not found")


@router.put("/{id}", response_description="Update a location", response_model=Location)
def update_location(id: str, request: Request, location: LocationUpdate = Body(...)):
    
    location = {k: v for k, v in location.dict().items() if v is not None}
    if len(location) >= 1:
        update_result = request.app.database["locations"].update_one(
            {"_id": id}, {"$set": location}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Location with ID {id} not found")

    if (
        existing_location := request.app.database["locations"].find_one({"_id": id})
    ) is not None:
        return existing_location

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Location with ID {id} not found")


@router.delete("/{id}", response_description="Delete a location")
def delete_location(id: str, request: Request, response: Response):
    delete_result = request.app.database["locations"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Location with ID {id} not found")