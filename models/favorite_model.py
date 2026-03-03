from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime

from models.location_model import LocationModel
from models.image_model import ImageModel

class FavoriteModel(BaseModel):
    iPK: int = Field(..., example=0)
    iUserFK: int = Field(..., example=1)
    strName: str = Field(..., max_length=255, example="즐겨찾기 이름")

    def to_log(self) -> str:
        return f"{self.iPK}:{self.iUserFK}:{self.strName}"

class FavoriteListModel(BaseModel):
    favorite_list: list[FavoriteModel] = Field(..., description="즐겨찾기 목록")

###############################################################################################################################################################

class FavoriteLocationModel(BaseModel):
    iPK: Optional[int] = Field(default=0, example=0)
    iFavoriteFK: int = Field(..., example=1)
    iLocationFK: int = Field(..., example=1)
    dtFavorite: datetime = Field(..., example="2026-03-03 12:34:56", description="즐겨찾기 등록 일시")

    @field_serializer('dtFavorite')
    def serialize_dtFavorite(self, dt: datetime, _info):
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def to_log(self) -> str:
        return f"{self.iPK}:{self.iFavoriteFK}:{self.iLocationFK}"

class FavoriteLocationFrontModel(FavoriteLocationModel):
    location: LocationModel = Field(..., description="즐겨찾기에 등록된 장소 정보")

class FavoriteLocationListModel(BaseModel):
    location_list: list[FavoriteLocationFrontModel] = Field(..., description="즐겨찾기에 등록된 장소 목록")

###############################################################################################################################################################

class FavoriteImageModel(BaseModel):
    iPK: Optional[int] = Field(default=0, example=0)
    iFavoriteFK: int = Field(..., example=1)
    iImageFK: int = Field(..., example=1)
    dtFavorite: datetime = Field(..., example="2026-03-03 12:34:56", description="즐겨찾기 등록 일시")

    @field_serializer('dtFavorite')
    def serialize_dtFavorite(self, dt: datetime, _info):
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def to_log(self) -> str:
        return f"{self.iPK}:{self.iFavoriteFK}:{self.iImageFK}"

class FavoriteImageFrontModel(FavoriteImageModel):
    image: ImageModel = Field(..., description="즐겨찾기에 등록된 이미지 정보")

class FavoriteImageListModel(BaseModel):
    image_list: list[FavoriteImageFrontModel] = Field(..., description="즐겨찾기에 등록된 이미지 목록")
