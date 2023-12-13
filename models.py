import uuid
from typing import Optional
from pydantic import BaseModel, Field

class Location(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    address: str = Field(...)
    lat: str = Field(...)
    lon: str = Field(...)
    gridId: str = Field(...)
    gridX: str = Field(...)
    gridY: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "address": "123 E Main StLouisville, KY 40202",
                "lat": "...",
                "lon": "...",
                "gridId": "...",
                "gridX": "...",
                "gridY": "..."
            }
        }

class LocationUpdate(BaseModel):
    address: Optional[str]
    lat: Optional[str]
    lon: Optional[str]
    gridId: Optional[str]
    gridX: Optional[str]
    gridY: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "address": "123 E Main StLouisville, KY 40202",
                "lat": "-85.7501",
                "lon": "38.2564",
                "gridId": "LMK",
                "gridX": "50",
                "gridY": "78"
            }
        }