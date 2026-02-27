from pydantic import BaseModel, Field
from typing import Optional

from models.location_model import LocationModel

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

    def to_log(self) -> str:
        return f"{self.iPK}:{self.iFavoriteFK}:{self.iLocationFK}"

class FavoriteLocationFrontModel(FavoriteLocationModel):
    location: LocationModel = Field(..., description="즐겨찾기에 등록된 장소 정보")

class FavoriteLocationListModel(BaseModel):
    location_list: list[FavoriteLocationFrontModel] = Field(..., description="즐겨찾기에 등록된 장소 목록")
